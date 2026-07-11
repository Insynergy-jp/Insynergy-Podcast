#!/usr/bin/env python3
"""Build ID3-tagged episodes, a podcast RSS feed, and a static Pages site."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import yaml
from mutagen.id3 import APIC, COMM, TALB, TIT2, TPE1, TPOS, TRCK, TXXX, ID3
from mutagen.mp3 import MP3


ROOT = Path(__file__).resolve().parents[1]
ITUNES = "http://www.itunes.com/dtds/podcast-1.0.dtd"
CONTENT = "http://purl.org/rss/1.0/modules/content/"
ET.register_namespace("itunes", ITUNES)
ET.register_namespace("content", CONTENT)


class PublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class Episode:
    id: str
    number: int
    title: str
    slug: str
    description: str
    published: datetime
    status: str
    podcast: bool
    duration_minutes: int
    voice_style: str
    source: Path
    episode_type: str
    manifest: Path


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PublishError(f"Could not load YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PublishError(f"YAML root must be a mapping: {path}")
    return value


def load_show(root: Path = ROOT) -> dict[str, Any]:
    show = load_yaml(root / "Podcast" / "podcast.yml")
    email = os.getenv("PODCAST_EMAIL", str(show.get("contact_email", ""))).strip()
    show["contact_email"] = email
    required = ["title", "description", "language", "author", "base_url", "cover", "id_prefix"]
    missing = [key for key in required if not str(show.get(key, "")).strip()]
    if missing:
        raise PublishError("Missing show field(s): " + ", ".join(missing))
    return show


def parse_episode(path: Path, root: Path = ROOT) -> Episode:
    data = load_yaml(path)
    required = ["id", "episode", "title", "slug", "published", "status", "source"]
    missing = [key for key in required if data.get(key) in (None, "")]
    if missing:
        raise PublishError(f"{path}: missing field(s): {', '.join(missing)}")
    published = data["published"]
    if isinstance(published, str):
        published = datetime.fromisoformat(published)
    if not isinstance(published, datetime) or published.tzinfo is None:
        raise PublishError(f"{path}: published must include a timezone")
    source = (root / str(data["source"])).resolve()
    try:
        source.relative_to(root.resolve())
    except ValueError as exc:
        raise PublishError(f"{path}: source is outside the repository") from exc
    return Episode(
        id=str(data["id"]), number=int(data["episode"]), title=str(data["title"]),
        slug=str(data["slug"]), description=str(data.get("description", "")),
        published=published, status=str(data["status"]), podcast=bool(data.get("podcast", False)),
        duration_minutes=int(data.get("duration_minutes", 8)), voice_style=str(data.get("voice_style", "executive")),
        source=source, episode_type=str(data.get("episode_type", "full")), manifest=path,
    )


def load_episodes(root: Path = ROOT) -> list[Episode]:
    episodes = [parse_episode(path, root) for path in sorted((root / "Podcast" / "Episodes").glob("*/episode.yml"))]
    ids, numbers, slugs = set(), set(), set()
    prefix = str(load_show(root)["id_prefix"])
    for episode in episodes:
        if not re.fullmatch(rf"{re.escape(prefix)}-\d{{3,}}", episode.id):
            raise PublishError(f"Invalid episode ID {episode.id}; expected {prefix}-001 format")
        for value, seen, label in ((episode.id, ids, "ID"), (episode.number, numbers, "number"), (episode.slug, slugs, "slug")):
            if value in seen:
                raise PublishError(f"Duplicate episode {label}: {value}")
            seen.add(value)
        if not episode.source.is_file():
            raise PublishError(f"Source file not found: {episode.source}")
    return episodes


def generated_paths(episode: Episode, root: Path = ROOT) -> tuple[Path, Path, Path]:
    return (
        root / "Podcast" / "Scripts" / f"{episode.slug}-podcast.md",
        root / "Podcast" / "Audio" / f"{episode.slug}.mp3",
        root / "Podcast" / "Metadata" / f"{episode.slug}.json",
    )


def ffprobe_duration(path: Path) -> int:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise PublishError("ffprobe is required (installed with ffmpeg)")
    result = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise PublishError(f"ffprobe failed for {path}: {result.stderr.strip()}")
    return max(1, round(float(result.stdout.strip())))


def combine_brand_audio(body: Path, destination: Path, root: Path = ROOT) -> None:
    parts = [path for path in (root / "Podcast/Assets/intro.mp3", body, root / "Podcast/Assets/outro.mp3") if path.is_file()]
    destination.parent.mkdir(parents=True, exist_ok=True)
    if len(parts) == 1:
        shutil.copyfile(body, destination)
        return
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise PublishError("ffmpeg is required to add intro/outro audio")
    command = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
    for part in parts:
        command.extend(["-i", str(part)])
    command.extend(["-filter_complex", f"concat=n={len(parts)}:v=0:a=1[out]", "-map", "[out]", "-codec:a", "libmp3lame", "-b:a", "192k", str(destination)])
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise PublishError(f"ffmpeg audio composition failed: {result.stderr.strip()}")


def apply_id3(path: Path, episode: Episode, show: dict[str, Any], cover: Path) -> None:
    audio = MP3(path)
    if audio.tags is None:
        audio.add_tags()
    tags: ID3 = audio.tags
    tags.delall("APIC")
    tags.add(TIT2(encoding=3, text=episode.title))
    tags.add(TALB(encoding=3, text=str(show["title"])))
    tags.add(TPE1(encoding=3, text=str(show["author"])))
    tags.add(TRCK(encoding=3, text=str(episode.number)))
    tags.add(TPOS(encoding=3, text="1"))
    tags.add(COMM(encoding=3, lang="eng", desc="Description", text=episode.description))
    tags.add(TXXX(encoding=3, desc="EPISODE_ID", text=episode.id))
    tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover.read_bytes()))
    audio.save(v2_version=3)


def duration_text(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def build_public(root: Path = ROOT, strict_email: bool = False) -> Path:
    show = load_show(root)
    if strict_email and ("@" not in show["contact_email"] or show["contact_email"].startswith("REPLACE_")):
        raise PublishError("Set PODCAST_EMAIL to a public podcast contact address before deployment")
    episodes = [e for e in load_episodes(root) if e.podcast and e.status == "published"]
    episodes.sort(key=lambda e: (e.published, e.number), reverse=True)
    public = root / "Podcast" / "Public"
    audio_dir, assets_dir = public / "audio", public / "assets"
    audio_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    cover = root / str(show["cover"])
    if not cover.is_file():
        raise PublishError(f"Cover not found: {cover}")
    shutil.copyfile(cover, assets_dir / "cover.jpg")

    published: list[tuple[Episode, Path, int]] = []
    for episode in episodes:
        _, source_audio, metadata_path = generated_paths(episode, root)
        if not source_audio.is_file():
            raise PublishError(f"Generated audio not found for {episode.id}: {source_audio}")
        target = audio_dir / f"{episode.id.lower()}-{episode.slug}.mp3"
        combine_brand_audio(source_audio, target, root)
        apply_id3(target, episode, show, cover)
        seconds = ffprobe_duration(target)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
        metadata.update({"episode_id": episode.id, "episode": episode.number, "published": episode.published.isoformat(), "duration_seconds": seconds, "public_audio_file": target.relative_to(public).as_posix()})
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        published.append((episode, target, seconds))

    feed = create_feed(show, published)
    feed_path = public / "podcast.xml"
    ET.indent(feed, space="  ")
    feed_path.write_bytes(ET.tostring(feed, encoding="utf-8", xml_declaration=True))
    (public / "index.html").write_text(create_index(show, published), encoding="utf-8")
    (public / ".nojekyll").touch()
    return feed_path


def create_feed(show: dict[str, Any], episodes: list[tuple[Episode, Path, int]]) -> ET.Element:
    base = str(show["base_url"]).rstrip("/")
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    for tag, value in (("title", show["title"]), ("link", base + "/"), ("description", show["description"]), ("language", show["language"]), ("copyright", show.get("copyright", ""))):
        ET.SubElement(channel, tag).text = str(value)
    ET.SubElement(channel, f"{{{ITUNES}}}author").text = str(show["author"])
    ET.SubElement(channel, f"{{{ITUNES}}}summary").text = str(show["description"])
    ET.SubElement(channel, f"{{{ITUNES}}}explicit").text = str(bool(show.get("explicit", False))).lower()
    ET.SubElement(channel, f"{{{ITUNES}}}image", {"href": base + "/assets/cover.jpg"})
    category = ET.SubElement(channel, f"{{{ITUNES}}}category", {"text": str(show["category"])})
    if show.get("subcategory"):
        ET.SubElement(category, f"{{{ITUNES}}}category", {"text": str(show["subcategory"])})
    owner = ET.SubElement(channel, f"{{{ITUNES}}}owner")
    ET.SubElement(owner, f"{{{ITUNES}}}name").text = str(show["author"])
    ET.SubElement(owner, f"{{{ITUNES}}}email").text = str(show["contact_email"])
    for episode, audio, seconds in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = episode.title
        ET.SubElement(item, "description").text = episode.description
        ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = f"urn:insynergy:podcast:{episode.id}"
        ET.SubElement(item, "pubDate").text = format_datetime(episode.published)
        url = f"{base}/audio/{audio.name}"
        ET.SubElement(item, "enclosure", {"url": url, "length": str(audio.stat().st_size), "type": "audio/mpeg"})
        ET.SubElement(item, f"{{{ITUNES}}}episode").text = str(episode.number)
        ET.SubElement(item, f"{{{ITUNES}}}episodeType").text = episode.episode_type
        ET.SubElement(item, f"{{{ITUNES}}}duration").text = duration_text(seconds)
        ET.SubElement(item, f"{{{ITUNES}}}explicit").text = "false"
    return rss


def create_index(show: dict[str, Any], episodes: list[tuple[Episode, Path, int]]) -> str:
    esc = lambda value: html.escape(str(value), quote=True)
    cards = "\n".join(f'<article><span>{esc(e.id)} · Episode {e.number}</span><h2>{esc(e.title)}</h2><p>{esc(e.description)}</p><audio controls preload="metadata" src="audio/{esc(a.name)}"></audio></article>' for e, a, _ in episodes)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(show["title"])}</title><link rel="alternate" type="application/rss+xml" title="Podcast RSS" href="podcast.xml"><style>body{{margin:0;background:#071525;color:#f3eadc;font:17px/1.6 system-ui,sans-serif}}main{{max-width:920px;margin:auto;padding:48px 24px}}header{{display:grid;grid-template-columns:minmax(180px,320px) 1fr;gap:42px;align-items:center;margin-bottom:56px}}img{{width:100%;border-radius:4px}}h1{{font:clamp(2.4rem,6vw,5rem)/1.05 Georgia,serif;margin:.2em 0}}article{{border-top:1px solid #a96f42;padding:32px 0}}article span{{color:#d59660;letter-spacing:.08em}}h2{{font:2rem Georgia,serif}}audio{{width:100%}}a{{color:#f3c38f}}@media(max-width:650px){{header{{grid-template-columns:1fr}}}}</style></head><body><main><header><img src="assets/cover.jpg" alt="{esc(show["title"])}"><div><p>INSYNERGY</p><h1>{esc(show["title"])}</h1><p>{esc(show["description"])}</p><a href="podcast.xml">RSS Feed</a></div></header>{cards}</main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict-email", action="store_true")
    args = parser.parse_args()
    try:
        path = build_public(strict_email=args.strict_email)
        print(f"Feed: {path}")
        return 0
    except PublishError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
