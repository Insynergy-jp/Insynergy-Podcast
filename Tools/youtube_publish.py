#!/usr/bin/env python3
"""Render podcast episodes as MP4 files and upload them to YouTube."""

from __future__ import annotations

import argparse
import hashlib
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
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, UnidentifiedImageError

from publish_podcast import ROOT, Episode, generated_paths, load_episodes, load_show
from source_reference import (
    SourceReferenceError,
    episode_insight_url,
    episode_source_reference,
    validate_body_reference,
)


YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_CAPTION_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_SCOPES = [YOUTUBE_UPLOAD_SCOPE, YOUTUBE_CAPTION_SCOPE]
CAPTION_TIMING_VERSION = "audio-transcription-v1"
ENGLISH_CAPTION_TEXT_VERSION = "insynergy-normalization-v1"
CAPTION_TRANSCRIPTION_MODEL = "whisper-1"
DEFAULT_CAPTION_TRANSLATION_MODEL = "gpt-5.4-mini"
CAPTION_TRANSLATION_BATCH_SIZE = 20
OG_THUMBNAIL_VERSION = "insynergy-insight-og-v1"
LEGACY_YOUTUBE_THUMBNAIL_TEMPLATE_VERSION = "insynergy-youtube-editorial-v1"
YOUTUBE_THUMBNAIL_TEMPLATE_VERSION = "insynergy-youtube-editorial-v2"
YOUTUBE_DETAILS_VERSION = "insynergy-youtube-details-v2"
YOUTUBE_DESCRIPTION_VERSION = YOUTUBE_DETAILS_VERSION
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
    try:
        return episode_insight_url(episode, config)
    except SourceReferenceError as exc:
        raise YouTubePublishError(str(exc)) from exc


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


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
        if bold else
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf")
    )
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name, size=size)
    return ImageFont.load_default()


def thumbnail_text(episode: Episode) -> str:
    text = (episode.youtube_thumbnail_text or episode.youtube_title or episode.title).strip()
    if len(text) <= 58:
        return text
    for separator in (": ", ". ", " — ", "—", "? "):
        first = text.split(separator, 1)[0].strip(" .:—?")
        if 18 <= len(first) <= 58:
            return first
    return text[:55].rsplit(" ", 1)[0].rstrip(" .:—?") + "…"


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if current and width > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _hex_rgb(value: str, fallback: str) -> tuple[int, int, int]:
    selected = value.strip() if re.fullmatch(r"#[0-9A-Fa-f]{6}", value.strip()) else fallback
    return tuple(int(selected[index:index + 2], 16) for index in (1, 3, 5))


def _gradient_text(
    canvas: Image.Image,
    position: tuple[int, int],
    text: str,
    font: Any,
    start_color: str,
    end_color: str,
) -> None:
    mask = Image.new("L", canvas.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text(position, text, font=font, fill=255, stroke_width=1, stroke_fill=255)
    left, top, right, bottom = mask.getbbox() or (0, 0, 1, 1)
    start = _hex_rgb(start_color, "#35D8F2")
    end = _hex_rgb(end_color, "#3978F6")
    gradient = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    pixels = gradient.load()
    span = max(1, right - left - 1)
    for x in range(left, right):
        ratio = (x - left) / span
        color = tuple(round(a + (b - a) * ratio) for a, b in zip(start, end))
        for y in range(top, bottom):
            pixels[x, y] = (*color, 255)
    canvas.alpha_composite(Image.composite(gradient, Image.new("RGBA", canvas.size), mask))


def _draw_boundary_nodes(canvas: Image.Image, card_origin: tuple[int, int], accent: str) -> None:
    x0, y0 = card_origin
    y = y0 + 266
    end_x = x0 + 206
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    color = _hex_rgb(accent, "#69AAFF")
    glow_draw.line((x0 + 30, y, end_x, y), fill=(*color, 170), width=4)
    for x in (x0 + 42, x0 + 94, x0 + 146, end_x):
        glow_draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(*color, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=8))
    canvas.alpha_composite(glow)
    draw = ImageDraw.Draw(canvas)
    draw.line((x0 + 30, y, end_x, y), fill=(225, 252, 255, 235), width=3)
    for x in (x0 + 42, x0 + 94, x0 + 146, end_x):
        draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(*color, 230), outline="#FFFFFF", width=3)


def wave_symbol_path(config: Mapping[str, Any], root: Path = ROOT) -> Path | None:
    configured = str(config.get("wave_symbol", "")).strip()
    if not configured:
        return None
    candidate = (root / configured).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise YouTubePublishError("youtube.thumbnail.wave_symbol must be inside the repository") from exc
    if not candidate.is_file():
        raise YouTubePublishError(f"YouTube thumbnail Wave Symbol not found: {candidate}")
    return candidate


def thumbnail_render_sha256(
    source_sha256: str,
    headline: str,
    config: Mapping[str, Any],
    wave_sha256: str = "",
    emphasis: str = "",
) -> str:
    template_version = (
        YOUTUBE_THUMBNAIL_TEMPLATE_VERSION
        if emphasis else LEGACY_YOUTUBE_THUMBNAIL_TEMPLATE_VERSION
    )
    payload = {
        "source_sha256": source_sha256,
        "headline": headline,
        "template_version": template_version,
        "eyebrow": str(config.get("eyebrow", "DECISION DESIGN")),
        "brand": str(config.get("brand", "INSYNERGY")),
        "accent": str(config.get("accent", "#69AAFF")),
        "wave_sha256": wave_sha256,
    }
    if emphasis:
        payload.update({
            "gradient_start": str(config.get("gradient_start", "#35D8F2")),
            "gradient_end": str(config.get("gradient_end", "#3978F6")),
            "boundary_nodes": bool(config.get("boundary_nodes", True)),
            "emphasis": emphasis,
        })
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def prepare_thumbnail(
    source: Path,
    destination: Path,
    headline: str = "Decision Design",
    config: Mapping[str, Any] | None = None,
    root: Path = ROOT,
    emphasis: str = "",
) -> None:
    config = config or {}
    if not source.is_file() or source.stat().st_size == 0:
        raise YouTubePublishError(f"Open Graph source image is missing or empty: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(source) as opened:
            original = ImageOps.exif_transpose(opened).convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise YouTubePublishError(f"Open Graph source is not a valid image: {source}") from exc

    background = ImageOps.fit(original, (1280, 720), method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(radius=18))
    background = ImageEnhance.Brightness(background).enhance(0.22).convert("RGBA")
    canvas = Image.new("RGBA", (1280, 720), "#080B10")
    canvas.alpha_composite(background)
    overlay = Image.new("RGBA", canvas.size, (5, 9, 16, 120))
    canvas.alpha_composite(overlay)
    draw = ImageDraw.Draw(canvas)

    accent = str(config.get("accent", "#69AAFF"))
    if emphasis:
        draw.rounded_rectangle((746, 92, 1190, 628), radius=24, fill="#FFFFFF")
    else:
        draw.rounded_rectangle(
            (746, 92, 1190, 628),
            radius=24,
            fill=(255, 255, 255, 28),
            outline=(255, 255, 255, 70),
            width=2,
        )
    card = ImageOps.fit(original, (412, 504), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, card.width, card.height), radius=18, fill=255)
    canvas.paste(card, (762, 108), mask)
    if emphasis and bool(config.get("boundary_nodes", True)):
        _draw_boundary_nodes(canvas, (762, 108), accent)

    draw.rounded_rectangle((80, 88, 92, 142), radius=6, fill=accent)
    eyebrow_font = _font(24, bold=True)
    draw.text((112, 96), str(config.get("eyebrow", "DECISION DESIGN")), font=eyebrow_font, fill=accent, spacing=4)

    headline = headline.strip() or "Decision Design"
    match = re.search(rf"(?<!\w){re.escape(emphasis)}(?!\w)", headline, flags=re.IGNORECASE) if emphasis else None
    if match:
        prefix = headline[:match.start()].strip()
        focus = headline[match.start():match.end()]
        suffix = headline[match.end():].strip()
        supporting_font = _font(55, bold=True)
        prefix_lines = _wrap_text(draw, prefix, supporting_font, 590) if prefix else []
        suffix_lines = _wrap_text(draw, suffix, supporting_font, 590) if suffix else []
        y = 188
        for line in prefix_lines[-1:]:
            draw.text((80, y), line, font=supporting_font, fill="#FFFFFF", stroke_width=1, stroke_fill="#0B111B")
            y += 76
        focus_size = 220
        while focus_size >= 100:
            focus_font = _font(focus_size, bold=True)
            if draw.textbbox((0, 0), focus, font=focus_font)[2] <= 590:
                break
            focus_size -= 4
        _gradient_text(
            canvas,
            (80, y - 22),
            focus,
            focus_font,
            str(config.get("gradient_start", "#35D8F2")),
            str(config.get("gradient_end", "#3978F6")),
        )
        y += focus_size - 8
        for line in suffix_lines[:1]:
            draw.text((80, y), line, font=supporting_font, fill="#FFFFFF", stroke_width=1, stroke_fill="#0B111B")
    else:
        font_size = 68
        while font_size >= 46:
            headline_font = _font(font_size, bold=True)
            lines = _wrap_text(draw, headline, headline_font, 590)
            if len(lines) <= 4:
                break
            font_size -= 4
        line_height = font_size + 13
        y = 190
        for line in lines[:4]:
            draw.text((80, y), line, font=headline_font, fill="#FFFFFF", stroke_width=1, stroke_fill="#0B111B")
            y += line_height

    draw.line((80, 580, 650, 580), fill=(255, 255, 255, 55), width=2)
    brand_x = 80
    wave = wave_symbol_path(config, root)
    if wave:
        try:
            with Image.open(wave) as opened_wave:
                symbol = ImageOps.contain(
                    ImageOps.exif_transpose(opened_wave).convert("RGBA"),
                    (118, 74),
                    method=Image.Resampling.LANCZOS,
                )
        except (OSError, UnidentifiedImageError) as exc:
            raise YouTubePublishError(f"Wave Symbol is not a valid image: {wave}") from exc
        canvas.alpha_composite(symbol, (80, 604))
        brand_x = 218
    brand_font = _font(25, bold=True)
    draw.text((brand_x, 606), str(config.get("brand", "INSYNERGY")), font=brand_font, fill="#FFFFFF")
    draw.text((brand_x, 644), "JUDGMENT ARCHITECTURE FOR THE AGE OF AI", font=_font(15), fill=(190, 202, 219))

    rgb = canvas.convert("RGB")
    for quality in (92, 86, 80, 72, 64):
        rgb.save(destination, "JPEG", quality=quality, optimize=True, progressive=True)
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


def thumbnail_is_fresh(
    metadata: Mapping[str, Any],
    insight_page_url: str | None = None,
    source_image_url: str | None = None,
    source_sha256: str | None = None,
    render_sha256: str | None = None,
    template_version: str = YOUTUBE_THUMBNAIL_TEMPLATE_VERSION,
) -> bool:
    return bool(
        metadata.get("youtube_thumbnail_version") == OG_THUMBNAIL_VERSION
        and metadata.get("youtube_thumbnail_source_url")
        and metadata.get("youtube_thumbnail_insight_url")
        and (
            insight_page_url is None
            or metadata.get("youtube_thumbnail_insight_url") == insight_page_url
        )
        and (
            source_image_url is None
            or metadata.get("youtube_thumbnail_source_url") == source_image_url
        )
        and (
            source_sha256 is None
            or metadata.get("youtube_thumbnail_source_sha256") == source_sha256
        )
        and metadata.get("youtube_thumbnail_template_version") == template_version
        and (
            render_sha256 is None
            or metadata.get("youtube_thumbnail_render_sha256") == render_sha256
        )
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


def video_body(
    episode: Episode,
    show: Mapping[str, Any],
    config: Mapping[str, Any],
    next_episode_url: str | None = None,
) -> dict[str, Any]:
    base_url = str(show["base_url"]).rstrip("/")
    article_url = insight_url(episode, config)
    sections = [f"Episode overview:\n{episode.description}"]
    if episode.series_title:
        sequence = f" · Episode {episode.series_sequence}" if episode.series_sequence else ""
        sections.append(f"Series: {episode.series_title}{sequence}")
    if next_episode_url:
        sections.append(f"Watch next:\n{next_episode_url}")
    sections.extend([
        f"Read the full Insynergy Insight:\n{article_url}",
        f"Listen and subscribe: {base_url}/\n"
        f"Podcast RSS: {base_url}/podcast.xml",
        "Decision Design is a judgment architecture framework proposed by Ryoji Morii, "
        "founder of Insynergy Inc., for structuring authority, accountability, and "
        "decision boundaries in AI-augmented organizations.",
    ])
    description = "\n\n".join(sections)
    try:
        validate_body_reference(
            description,
            article_url,
            str(config.get("insights_base_url", DEFAULT_INSIGHTS_BASE_URL)),
        )
    except SourceReferenceError as exc:
        raise YouTubePublishError(str(exc)) from exc
    return {
        "snippet": {
            "title": (episode.youtube_title or episode.title)[:100],
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


def details_fingerprint(details: Mapping[str, Any]) -> str:
    snippet = details.get("snippet", {})
    canonical = json.dumps(snippet, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def description_is_fresh(
    metadata: Mapping[str, Any], article_url: str, expected_fingerprint: str | None = None
) -> bool:
    return bool(
        metadata.get("youtube_description_version") == YOUTUBE_DESCRIPTION_VERSION
        and metadata.get("youtube_description_insight_url") == article_url
        and (
            expected_fingerprint is None
            or metadata.get("youtube_details_sha256") == expected_fingerprint
        )
    )


def update_video_details(youtube: Any, video_id: str, body: Mapping[str, Any]) -> None:
    snippet = body.get("snippet")
    if not isinstance(snippet, Mapping):
        raise YouTubePublishError("YouTube video body is missing its snippet")
    youtube.videos().update(
        part="snippet",
        body={"id": video_id, "snippet": dict(snippet)},
    ).execute()


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


def next_episode_url(
    episode: Episode, episodes_by_id: Mapping[str, Episode], root: Path = ROOT
) -> str | None:
    if not episode.next_episode_id:
        return None
    target = episodes_by_id.get(episode.next_episode_id)
    if target is None:
        return None
    video_id = target.youtube_video_id
    if not video_id:
        _, _, metadata_path = generated_paths(target, root)
        if metadata_path.is_file():
            try:
                video_id = json.loads(metadata_path.read_text(encoding="utf-8")).get("youtube_video_id")
            except (OSError, json.JSONDecodeError):
                video_id = None
    return f"https://youtu.be/{video_id}" if video_id else None


def publish_episode(
    youtube: Any,
    episode: Episode,
    show: Mapping[str, Any],
    config: Mapping[str, Any],
    root: Path = ROOT,
    openai_client: Any | None = None,
    episodes_by_id: Mapping[str, Episode] | None = None,
) -> str | None:
    script, audio, metadata_path = generated_paths(episode, root)
    if not audio.is_file() or not script.is_file() or not metadata_path.is_file():
        raise YouTubePublishError(f"Generated podcast assets are missing for {episode.id}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    try:
        metadata["sourceReference"] = episode_source_reference(episode, config)
    except SourceReferenceError as exc:
        raise YouTubePublishError(str(exc)) from exc
    video_id = metadata.get("youtube_video_id")
    if not video_id and episode.youtube_video_id:
        video_id = episode.youtube_video_id
        metadata.update({
            "youtube_video_id": video_id,
            "youtube_url": f"https://youtu.be/{video_id}",
        })
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"YouTube video recovered: {episode.id} ({video_id})")
    article_url = insight_url(episode, config)
    related_url = next_episode_url(episode, episodes_by_id or {}, root)
    details = video_body(episode, show, config, related_url)
    details_sha256 = details_fingerprint(details)
    thumbnail: Path | None = None
    thumbnail_page_url: str | None = None
    thumbnail_source_url: str | None = None
    thumbnail_config = config.get("thumbnail", {})
    if not isinstance(thumbnail_config, Mapping):
        raise YouTubePublishError("youtube.thumbnail must be a mapping")
    headline = thumbnail_text(episode)
    thumbnail_template_version = (
        YOUTUBE_THUMBNAIL_TEMPLATE_VERSION
        if episode.youtube_thumbnail_emphasis
        else LEGACY_YOUTUBE_THUMBNAIL_TEMPLATE_VERSION
    )
    wave = wave_symbol_path(thumbnail_config, root)
    wave_sha256 = hashlib.sha256(wave.read_bytes()).hexdigest() if wave else ""
    source_image = root / "Podcast" / "YouTube" / f"{episode.slug}.og-image"
    candidate = root / "Podcast" / "YouTube" / f"{episode.slug}.thumbnail.jpg"
    try:
        thumbnail_page_url, thumbnail_source_url = fetch_insight_og_image(
            episode, config, source_image
        )
        thumbnail_source_sha256 = hashlib.sha256(source_image.read_bytes()).hexdigest()
        thumbnail_render_hash = thumbnail_render_sha256(
            thumbnail_source_sha256,
            headline,
            thumbnail_config,
            wave_sha256,
            episode.youtube_thumbnail_emphasis,
        )
        if not video_id or not thumbnail_is_fresh(
            metadata,
            thumbnail_page_url,
            thumbnail_source_url,
            thumbnail_source_sha256,
            thumbnail_render_hash,
            thumbnail_template_version,
        ):
            prepare_thumbnail(
                source_image,
                candidate,
                headline,
                thumbnail_config,
                root,
                episode.youtube_thumbnail_emphasis,
            )
            thumbnail = candidate
    except YouTubePublishError as exc:
        cover_source = root / str(show["cover"])
        if cover_source.is_file() and cover_source.stat().st_size:
            thumbnail_page_url = article_url
            thumbnail_source_url = f"{str(show['base_url']).rstrip('/')}/cover.jpg"
            thumbnail_source_sha256 = hashlib.sha256(cover_source.read_bytes()).hexdigest()
            thumbnail_render_hash = thumbnail_render_sha256(
                thumbnail_source_sha256,
                headline,
                thumbnail_config,
                wave_sha256,
                episode.youtube_thumbnail_emphasis,
            )
            if not video_id or not thumbnail_is_fresh(
                metadata,
                thumbnail_page_url,
                thumbnail_source_url,
                thumbnail_source_sha256,
                thumbnail_render_hash,
                thumbnail_template_version,
            ):
                prepare_thumbnail(
                    cover_source,
                    candidate,
                    headline,
                    thumbnail_config,
                    root,
                    episode.youtube_thumbnail_emphasis,
                )
                thumbnail = candidate
            print(
                f"Warning: {exc}; rendered the podcast-cover fallback for {episode.id}",
                file=sys.stderr,
            )
        else:
            print(f"Warning: {exc}; using the podcast cover for {episode.id}", file=sys.stderr)
    if not video_id:
        video = root / "Podcast" / "YouTube" / f"{episode.slug}.mp4"
        render_video(audio, thumbnail or root / str(show["cover"]), video)
        video_id = upload_video(youtube, video, details)
        metadata.update({
            "youtube_video_id": video_id,
            "youtube_url": f"https://youtu.be/{video_id}",
            "youtube_description_version": YOUTUBE_DESCRIPTION_VERSION,
            "youtube_description_insight_url": article_url,
            "youtube_details_sha256": details_sha256,
        })
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"YouTube uploaded: {episode.id} https://youtu.be/{video_id}")
    else:
        print(f"YouTube video fresh: {episode.id} ({video_id})")
        if not description_is_fresh(metadata, article_url, details_sha256):
            update_video_details(youtube, str(video_id), details)
            metadata.update({
                "youtube_description_version": YOUTUBE_DESCRIPTION_VERSION,
                "youtube_description_insight_url": article_url,
                "youtube_details_sha256": details_sha256,
            })
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(f"YouTube description updated: {episode.id} ({article_url})")
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
                "youtube_thumbnail_source_sha256": thumbnail_source_sha256,
                "youtube_thumbnail_template_version": thumbnail_template_version,
                "youtube_thumbnail_render_sha256": thumbnail_render_hash,
                "youtube_thumbnail_text": headline,
                "youtube_thumbnail_emphasis": episode.youtube_thumbnail_emphasis,
                "youtube_thumbnail_wave_symbol_sha256": wave_sha256,
                "youtube_thumbnail_fallback": (
                    "podcast-cover" if thumbnail_source_url.endswith("/cover.jpg") else None
                ),
            })
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(f"YouTube editorial thumbnail updated: {episode.id} ({thumbnail_source_url})")
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
    all_episodes = load_episodes()
    episodes_by_id = {episode.id: episode for episode in all_episodes}
    episodes = [e for e in all_episodes if e.podcast and e.status == "published"]
    if episode_id:
        episodes = [e for e in episodes if e.id == episode_id]
        if not episodes:
            raise YouTubePublishError(f"Published episode not found: {episode_id}")
    for episode in episodes:
        publish_episode(youtube, episode, show, config, episodes_by_id=episodes_by_id)
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
