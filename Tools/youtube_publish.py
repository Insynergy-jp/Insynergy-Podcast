#!/usr/bin/env python3
"""Render podcast episodes as MP4 files and upload them to YouTube."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from mutagen.mp3 import MP3

from publish_podcast import ROOT, Episode, generated_paths, load_episodes, load_show


YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"


class YouTubePublishError(RuntimeError):
    pass


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
            scopes=[YOUTUBE_UPLOAD_SCOPE],
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
        "[0:v]scale=1080:1080:force_original_aspect_ratio=decrease,"
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


def publish_episode(youtube: Any, episode: Episode, show: Mapping[str, Any], config: Mapping[str, Any], root: Path = ROOT) -> str | None:
    _, audio, metadata_path = generated_paths(episode, root)
    if not audio.is_file() or not metadata_path.is_file():
        raise YouTubePublishError(f"Generated podcast assets are missing for {episode.id}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("youtube_video_id"):
        print(f"YouTube fresh: {episode.id} ({metadata['youtube_video_id']})")
        return None
    video = root / "Podcast" / "YouTube" / f"{episode.slug}.mp4"
    render_video(audio, root / str(show["cover"]), video)
    video_id = upload_video(youtube, video, video_body(episode, show, config))
    metadata.update({"youtube_video_id": video_id, "youtube_url": f"https://youtu.be/{video_id}"})
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"YouTube uploaded: {episode.id} https://youtu.be/{video_id}")
    return video_id


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
