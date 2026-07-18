#!/usr/bin/env python3
"""Render podcast episodes as MP4 files and upload them to YouTube."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from mutagen.mp3 import MP3
from openai import OpenAI

from publish_podcast import ROOT, Episode, generated_paths, load_episodes, load_show


YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_CAPTION_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_SCOPES = [YOUTUBE_UPLOAD_SCOPE, YOUTUBE_CAPTION_SCOPE]
CAPTION_TIMING_VERSION = "audio-transcription-v1"
ENGLISH_CAPTION_TEXT_VERSION = "insynergy-normalization-v1"
CAPTION_TRANSCRIPTION_MODEL = "whisper-1"
DEFAULT_CAPTION_TRANSLATION_MODEL = "gpt-5.4-mini"
CAPTION_TRANSLATION_BATCH_SIZE = 20
OG_THUMBNAIL_VERSION = "insynergy-insight-og-v1"
DEFAULT_INSIGHTS_BASE_URL = "https://insynergy.io/insights"
MAX_HTML_BYTES = 2 * 1024 * 1024
MAX_SOURCE_IMAGE_BYTES = 16 * 1024 * 1024
MAX_YOUTUBE_THUMBNAIL_BYTES = 2_000_000


class YouTubePublishError(RuntimeError):
    pass


class OpenGraphParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.image_url: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta" or self.image_url:
            return
        values = {str(name).lower(): value for name, value in attrs if value is not None}
        if str(values.get("property", "")).lower() == "og:image":
            content = str(values.get("content", "")).strip()
            if content:
                self.image_url = content


@dataclass(frozen=True)
class YouTubeCredentials:
    client_id: str
    client_secret: str
    refresh_token: str
    token_uri: str = "https://oauth2.googleapis.com/token"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "YouTubeCredentials | None":
        values = os.environ if env is None else env
        fields = {
            "client_id": values.get("YOUTUBE_CLIENT_ID", "").strip(),
            "client_secret": values.get("YOUTUBE_CLIENT_SECRET", "").strip(),
            "refresh_token": values.get("YOUTUBE_REFRESH_TOKEN", "").strip(),
        }
        if not any(fields.values()):
            return None
        missing = [name.upper() for name, value in fields.items() if not value]
        if missing:
            raise YouTubePublishError("Incomplete YouTube credentials: " + ", ".join(missing))
        return cls(**fields)

    def google_credentials(self) -> Credentials:
        return Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri=self.token_uri,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=YOUTUBE_SCOPES,
        )


def _read_response(response: Any, limit: int, label: str) -> bytes:
    data = response.read(limit + 1)
    if len(data) > limit:
        raise YouTubePublishError(f"{label} exceeds the {limit}-byte download limit")
    return data


def _https_url(value: str, label: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise YouTubePublishError(f"{label} must be an absolute HTTPS URL: {value}")
    return value


def insight_url(episode: Episode, config: Mapping[str, Any]) -> str:
    overrides = config.get("insight_urls", {})
    if isinstance(overrides, Mapping):
        override = overrides.get(episode.slug) or overrides.get(episode.id)
        if override:
            return _https_url(str(override), "Insight URL")
    base = str(config.get("insights_base_url", DEFAULT_INSIGHTS_BASE_URL)).rstrip("/")
    return _https_url(f"{base}/{episode.slug}", "Insight URL")


def fetch_insight_og_image(
    episode: Episode, config: Mapping[str, Any], destination: Path
) -> tuple[str, str]:
    page_url = insight_url(episode, config)
    headers = {"User-Agent": "Insynergy-Podcast/1.0 (+https://insynergy.io/)"}
    try:
        with urlopen(Request(page_url, headers=headers), timeout=20) as response:
            html_bytes = _read_response(response, MAX_HTML_BYTES, "Insight HTML")
        parser = OpenGraphParser()
        parser.feed(html_bytes.decode("utf-8", errors="replace"))
        if not parser.image_url:
            raise YouTubePublishError(f"Insight page has no og:image: {page_url}")
        image_url = _https_url(urljoin(page_url, parser.image_url), "Open Graph image URL")
        with urlopen(Request(image_url, headers=headers), timeout=30) as response:
            content_type = str(response.headers.get("Content-Type", "")).split(";", 1)[0].lower()
            if not content_type.startswith("image/"):
                raise YouTubePublishError(
                    f"Open Graph image returned an unsupported content type: {content_type or 'unknown'}"
                )
            image_bytes = _read_response(response, MAX_SOURCE_IMAGE_BYTES, "Open Graph image")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise YouTubePublishError(f"Could not fetch Insight Open Graph image for {episode.id}: {exc}") from exc
    if not image_bytes:
        raise YouTubePublishError(f"Open Graph image was empty: {image_url}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(image_bytes)
    return page_url, image_url


def prepare_thumbnail(source: Path, destination: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise YouTubePublishError("ffmpeg is required to prepare YouTube thumbnails")
    if not source.is_file() or source.stat().st_size == 0:
        raise YouTubePublishError(f"Open Graph source image is missing or empty: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    for quality in (2, 4, 6, 8, 12):
        command = [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(source),
            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,"
            "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0b0b0d,format=yuv420p",
            "-frames:v", "1", "-q:v", str(quality), "-update", "1", str(destination),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0 or not destination.is_file() or destination.stat().st_size == 0:
            raise YouTubePublishError("YouTube thumbnail conversion failed: " + result.stderr.strip())
        if destination.stat().st_size <= MAX_YOUTUBE_THUMBNAIL_BYTES:
            return
    raise YouTubePublishError(
        f"YouTube thumbnail remains larger than {MAX_YOUTUBE_THUMBNAIL_BYTES} bytes after conversion"
    )


def set_video_thumbnail(youtube: Any, video_id: str, thumbnail: Path) -> None:
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(str(thumbnail), mimetype="image/jpeg", resumable=False),
    ).execute()


def thumbnail_is_fresh(metadata: Mapping[str, Any]) -> bool:
    return bool(
        metadata.get("youtube_thumbnail_version") == OG_THUMBNAIL_VERSION
        and metadata.get("youtube_thumbnail_source_url")
        and metadata.get("youtube_thumbnail_insight_url")
    )


def render_video(audio: Path, cover: Path, destination: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise YouTubePublishError("ffmpeg is required to render YouTube videos")
    if not audio.is_file() or not cover.is_file():
        raise YouTubePublishError(f"Missing audio or cover: {audio}, {cover}")
    duration = float(MP3(audio).info.length)
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-framerate", "1", "-i", str(cover), "-i", str(audio),
        "-filter_complex",
        "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0b0b0d,format=yuv420p[v]",
        "-map", "[v]", "-map", "1:a:0", "-fps_mode", "vfr", "-c:v", "libx264", "-preset", "veryfast",
        "-tune", "stillimage", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
        "-t", f"{duration:.3f}", "-shortest", "-movflags", "+faststart", str(destination),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not destination.is_file() or destination.stat().st_size == 0:
        raise YouTubePublishError("ffmpeg video render failed: " + result.stderr.strip())


def video_body(episode: Episode, show: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
    base_url = str(show["base_url"]).rstrip("/")
    description = (
        f"{episode.description}\n\n"
        f"Listen and subscribe: {base_url}/\n"
        f"Podcast RSS: {base_url}/podcast.xml\n\n"
        "Decision Design is a judgment architecture framework proposed by Ryoji Morii, "
        "founder of Insynergy Inc., for structuring authority, accountability, and "
        "decision boundaries in AI-augmented organizations."
    )
    return {
        "snippet": {
            "title": episode.title[:100],
            "description": description[:5000],
            "tags": [str(tag) for tag in config.get("tags", [])],
            "categoryId": str(config.get("category_id", "22")),
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": str(os.getenv("YOUTUBE_PRIVACY_STATUS", config.get("privacy_status", "private"))),
            "selfDeclaredMadeForKids": False,
        },
    }


def upload_video(youtube: Any, video: Path, body: Mapping[str, Any]) -> str:
    request = youtube.videos().insert(
        part="snippet,status",
        body=dict(body),
        media_body=MediaFileUpload(str(video), chunksize=8 * 1024 * 1024, resumable=True),
    )
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response.get("id") if isinstance(response, dict) else None
    if not video_id:
        raise YouTubePublishError("YouTube upload completed without a video ID")
    return str(video_id)


def srt_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _field(value: Any, name: str) -> Any:
    if isinstance(value, Mapping):
        return value.get(name)
    return getattr(value, name, None)


def normalize_caption_text(text: str) -> str:
    """Keep brand spelling stable when speech transcription changes casing."""
    return re.sub(r"\binsynergy\b", "Insynergy", text, flags=re.IGNORECASE)


def transcribe_segments(client: Any, audio: Path) -> list[dict[str, Any]]:
    """Transcribe final audio so caption times follow speech and pauses."""
    try:
        with audio.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model=CAPTION_TRANSCRIPTION_MODEL,
                language="en",
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )
    except Exception as exc:
        raise YouTubePublishError(f"OpenAI audio transcription failed: {exc}") from exc
    segments: list[dict[str, Any]] = []
    for item in _field(transcription, "segments") or []:
        text = normalize_caption_text(str(_field(item, "text") or "").strip())
        start = _field(item, "start")
        end = _field(item, "end")
        if text and isinstance(start, (int, float)) and isinstance(end, (int, float)) and end > start:
            segments.append({"start": float(start), "end": float(end), "text": text})
    if not segments:
        raise YouTubePublishError("Audio transcription returned no timestamped segments")
    return segments


def retry_empty_translation(client: Any, text: str, model: str) -> str:
    prompt = (
        "Translate this English podcast caption into natural Japanese. "
        "Return only the non-empty Japanese translation.\n\n" + text
    )
    try:
        response = client.responses.create(model=model, input=prompt)
    except Exception as exc:
        raise YouTubePublishError(f"OpenAI Japanese caption retry failed: {exc}") from exc
    translation = getattr(response, "output_text", None)
    if not isinstance(translation, str) or not translation.strip():
        raise YouTubePublishError("Japanese caption translation remained empty after retry")
    return translation.strip()


def translate_segments_to_japanese(client: Any, segments: list[dict[str, Any]], model: str) -> list[str]:
    all_translations: list[str] = []
    for offset in range(0, len(segments), CAPTION_TRANSLATION_BATCH_SIZE):
        batch = segments[offset:offset + CAPTION_TRANSLATION_BATCH_SIZE]
        keys = [f"segment_{index}" for index in range(len(batch))]
        source = {key: segment["text"] for key, segment in zip(keys, batch)}
        prompt = (
            "Translate each English podcast caption segment into natural, concise Japanese. "
            "Preserve names, numbers, meaning, and segment boundaries. Return exactly one translation "
            "for every input key.\n\n"
            + json.dumps(source, ensure_ascii=False)
        )
        schema = {
            "type": "object",
            "properties": {
                "translations": {
                    "type": "object",
                    "properties": {key: {"type": "string"} for key in keys},
                    "required": keys,
                    "additionalProperties": False,
                }
            },
            "required": ["translations"],
            "additionalProperties": False,
        }
        try:
            response = client.responses.create(
                model=model,
                input=prompt,
                text={"format": {
                    "type": "json_schema",
                    "name": "caption_translations",
                    "strict": True,
                    "schema": schema,
                }},
            )
        except Exception as exc:
            raise YouTubePublishError(f"OpenAI Japanese caption translation failed: {exc}") from exc
        output = getattr(response, "output_text", None)
        if not isinstance(output, str):
            raise YouTubePublishError("Japanese caption translation returned no text")
        cleaned = re.sub(r"\A```(?:json)?\s*|\s*```\Z", "", output.strip(), flags=re.IGNORECASE)
        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise YouTubePublishError("Japanese caption translation returned invalid JSON") from exc
        translated = result.get("translations") if isinstance(result, dict) else None
        if not isinstance(translated, dict) or set(translated) != set(keys):
            raise YouTubePublishError("Japanese caption translation changed the segment count")
        by_key = {key: str(translated[key]).strip() for key in keys}
        for index, key in enumerate(keys):
            if not by_key[key]:
                by_key[key] = retry_empty_translation(client, str(batch[index]["text"]), model)
        all_translations.extend(by_key[key] for key in keys)
    return all_translations


def build_timed_srt(segments: list[dict[str, Any]], texts: list[str] | None = None) -> str:
    if not segments or (texts is not None and len(texts) != len(segments)):
        raise YouTubePublishError("Cannot create timed captions without matching segments")
    blocks = []
    for index, segment in enumerate(segments, start=1):
        text = segment["text"] if texts is None else texts[index - 1]
        blocks.append(
            f"{index}\n{srt_timestamp(segment['start'])} --> {srt_timestamp(segment['end'])}\n{text}"
        )
    return "\n\n".join(blocks) + "\n"


def create_synced_caption_files(
    client: Any, audio: Path, english: Path, japanese: Path | None = None
) -> None:
    segments = transcribe_segments(client, audio)
    english.parent.mkdir(parents=True, exist_ok=True)
    english.write_text(build_timed_srt(segments), encoding="utf-8")
    if japanese is not None:
        model = os.getenv("OPENAI_CAPTION_TRANSLATION_MODEL", DEFAULT_CAPTION_TRANSLATION_MODEL)
        translations = translate_segments_to_japanese(client, segments, model)
        japanese.write_text(build_timed_srt(segments, translations), encoding="utf-8")


def upload_caption(youtube: Any, video_id: str, caption: Path, language: str = "en", name: str = "English") -> str:
    response = youtube.captions().insert(
        part="snippet",
        body={"snippet": {"videoId": video_id, "language": language, "name": name, "isDraft": False}},
        media_body=MediaFileUpload(str(caption), mimetype="application/octet-stream", resumable=False),
    ).execute()
    caption_id = response.get("id") if isinstance(response, dict) else None
    if not caption_id:
        raise YouTubePublishError("YouTube caption upload completed without a caption ID")
    return str(caption_id)


def update_caption(youtube: Any, caption_id: str, caption: Path) -> str:
    response = youtube.captions().update(
        part="id",
        body={"id": caption_id},
        media_body=MediaFileUpload(str(caption), mimetype="application/octet-stream", resumable=False),
    ).execute()
    updated_id = response.get("id") if isinstance(response, dict) else None
    if not updated_id:
        raise YouTubePublishError("YouTube caption update completed without a caption ID")
    return str(updated_id)


def existing_caption_ids(youtube: Any, video_id: str) -> dict[str, str]:
    response = youtube.captions().list(part="snippet", videoId=video_id).execute()
    ids: dict[str, str] = {}
    for item in response.get("items", []) if isinstance(response, dict) else []:
        snippet = item.get("snippet", {}) if isinstance(item, dict) else {}
        caption_id = item.get("id") if isinstance(item, dict) else None
        language = snippet.get("language") if isinstance(snippet, dict) else None
        name = snippet.get("name") if isinstance(snippet, dict) else None
        if caption_id and language == "en" and name == "English":
            ids["en"] = str(caption_id)
        elif caption_id and language == "ja" and name == "日本語":
            ids["ja"] = str(caption_id)
    return ids


def captions_are_fresh(metadata: Mapping[str, Any]) -> bool:
    return bool(
        metadata.get("youtube_caption_timing") == CAPTION_TIMING_VERSION
        and metadata.get("youtube_english_caption_text_version") == ENGLISH_CAPTION_TEXT_VERSION
        and metadata.get("youtube_caption_id")
        and metadata.get("youtube_japanese_caption_id")
    )


def publish_episode(youtube: Any, episode: Episode, show: Mapping[str, Any], config: Mapping[str, Any], root: Path = ROOT, openai_client: Any | None = None) -> str | None:
    script, audio, metadata_path = generated_paths(episode, root)
    if not audio.is_file() or not script.is_file() or not metadata_path.is_file():
        raise YouTubePublishError(f"Generated podcast assets are missing for {episode.id}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    video_id = metadata.get("youtube_video_id")
    thumbnail: Path | None = None
    thumbnail_page_url: str | None = None
    thumbnail_source_url: str | None = None
    if not video_id or not thumbnail_is_fresh(metadata):
        source_image = root / "Podcast" / "YouTube" / f"{episode.slug}.og-image"
        candidate = root / "Podcast" / "YouTube" / f"{episode.slug}.thumbnail.jpg"
        try:
            thumbnail_page_url, thumbnail_source_url = fetch_insight_og_image(
                episode, config, source_image
            )
            prepare_thumbnail(source_image, candidate)
            thumbnail = candidate
        except YouTubePublishError as exc:
            print(f"Warning: {exc}; using the podcast cover for {episode.id}", file=sys.stderr)
    if not video_id:
        video = root / "Podcast" / "YouTube" / f"{episode.slug}.mp4"
        render_video(audio, thumbnail or root / str(show["cover"]), video)
        video_id = upload_video(youtube, video, video_body(episode, show, config))
        metadata.update({"youtube_video_id": video_id, "youtube_url": f"https://youtu.be/{video_id}"})
        print(f"YouTube uploaded: {episode.id} https://youtu.be/{video_id}")
    else:
        print(f"YouTube video fresh: {episode.id} ({video_id})")
    if thumbnail and thumbnail_page_url and thumbnail_source_url:
        try:
            set_video_thumbnail(youtube, str(video_id), thumbnail)
        except Exception as exc:
            print(f"Warning: YouTube thumbnail update failed for {episode.id}: {exc}", file=sys.stderr)
        else:
            metadata.update({
                "youtube_thumbnail_version": OG_THUMBNAIL_VERSION,
                "youtube_thumbnail_insight_url": thumbnail_page_url,
                "youtube_thumbnail_source_url": thumbnail_source_url,
            })
            print(f"YouTube Insight thumbnail updated: {episode.id} ({thumbnail_source_url})")
    if captions_are_fresh(metadata):
        print(f"YouTube synchronized captions fresh: {episode.id}")
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return str(video_id)
    had_recorded_japanese_caption = bool(metadata.get("youtube_japanese_caption_id"))
    remote_captions = existing_caption_ids(youtube, str(video_id))
    if not metadata.get("youtube_caption_id") and remote_captions.get("en"):
        metadata["youtube_caption_id"] = remote_captions["en"]
    if not metadata.get("youtube_japanese_caption_id") and remote_captions.get("ja"):
        metadata["youtube_japanese_caption_id"] = remote_captions["ja"]
    if not had_recorded_japanese_caption and remote_captions.get("en") and remote_captions.get("ja"):
        metadata.update({
            "youtube_caption_id": remote_captions["en"],
            "youtube_caption_language": "en",
            "youtube_japanese_caption_id": remote_captions["ja"],
            "youtube_japanese_caption_language": "ja",
            "youtube_caption_timing": CAPTION_TIMING_VERSION,
        })
        print(f"YouTube synchronized captions recovered: {episode.id}")
    captions_fresh = captions_are_fresh(metadata)
    if not captions_fresh:
        client = openai_client or OpenAI()
        english = root / "Podcast" / "YouTube" / f"{episode.slug}.en.srt"
        japanese = root / "Podcast" / "YouTube" / f"{episode.slug}.ja.srt"
        needs_timing_migration = metadata.get("youtube_caption_timing") != CAPTION_TIMING_VERSION
        needs_english_update = (
            needs_timing_migration
            or metadata.get("youtube_english_caption_text_version") != ENGLISH_CAPTION_TEXT_VERSION
            or not metadata.get("youtube_caption_id")
        )
        needs_japanese_update = needs_timing_migration or not metadata.get("youtube_japanese_caption_id")
        create_synced_caption_files(client, audio, english, japanese if needs_japanese_update else None)
        if metadata.get("youtube_caption_id") and needs_english_update:
            caption_id = update_caption(youtube, str(metadata["youtube_caption_id"]), english)
        elif not metadata.get("youtube_caption_id"):
            caption_id = upload_caption(youtube, str(video_id), english, "en", "English")
        else:
            caption_id = str(metadata["youtube_caption_id"])
        if metadata.get("youtube_japanese_caption_id") and needs_japanese_update:
            japanese_caption_id = update_caption(youtube, str(metadata["youtube_japanese_caption_id"]), japanese)
        elif not metadata.get("youtube_japanese_caption_id"):
            japanese_caption_id = upload_caption(youtube, str(video_id), japanese, "ja", "日本語")
        else:
            japanese_caption_id = str(metadata["youtube_japanese_caption_id"])
        metadata.update({
            "youtube_caption_id": caption_id,
            "youtube_caption_language": "en",
            "youtube_japanese_caption_id": japanese_caption_id,
            "youtube_japanese_caption_language": "ja",
            "youtube_caption_timing": CAPTION_TIMING_VERSION,
            "youtube_english_caption_text_version": ENGLISH_CAPTION_TEXT_VERSION,
        })
        print(f"YouTube synchronized captions uploaded: {episode.id} (en={caption_id}, ja={japanese_caption_id})")
    else:
        print(f"YouTube synchronized captions fresh: {episode.id}")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(video_id)


def run(episode_id: str | None = None) -> int:
    show = load_show()
    config = show.get("youtube", {})
    if not isinstance(config, dict) or not config.get("enabled", False):
        print("YouTube publishing is disabled")
        return 0
    credentials = YouTubeCredentials.from_env()
    if credentials is None:
        print("YouTube credentials are not configured; skipping upload")
        return 0
    youtube = build("youtube", "v3", credentials=credentials.google_credentials(), cache_discovery=False)
    episodes = [e for e in load_episodes() if e.podcast and e.status == "published"]
    if episode_id:
        episodes = [e for e in episodes if e.id == episode_id]
        if not episodes:
            raise YouTubePublishError(f"Published episode not found: {episode_id}")
    for episode in episodes:
        publish_episode(youtube, episode, show, config)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", help="Upload only one episode ID, for example DD-003")
    args = parser.parse_args()
    try:
        return run(args.episode)
    except (YouTubePublishError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
