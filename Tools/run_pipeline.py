#!/usr/bin/env python3
"""Run the manifest-driven podcast generation and publishing pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from publish_podcast import ROOT, PublishError, build_public, generated_paths, load_episodes, load_show
from source_reference import SourceReferenceError, episode_source_reference


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_fresh(source_hash: str, script: Path, audio: Path, metadata: Path) -> bool:
    if not all(path.is_file() for path in (script, audio, metadata)):
        return False
    try:
        data = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return data.get("source_sha256") == source_hash


def run(force: bool = False, strict_email: bool = False) -> None:
    show = load_show()
    profiles = show.get("voice_profiles", {})
    os.environ["OBSIDIAN_VAULT_PATH"] = str(ROOT)
    os.environ["INSIGHTS_DIRECTORY"] = "Insights"
    generated = 0
    for episode in load_episodes():
        if not episode.podcast or episode.status != "published":
            continue
        try:
            source_reference = episode_source_reference(episode, show.get("youtube", {}))
        except SourceReferenceError as exc:
            raise PublishError(str(exc)) from exc
        profile = profiles.get(episode.voice_style)
        if not isinstance(profile, dict) or not profile.get("voice"):
            raise PublishError(f"Unknown voice_style '{episode.voice_style}' in {episode.manifest}")
        script, audio, metadata = generated_paths(episode)
        source_hash = sha256(episode.source)
        if not force and is_fresh(source_hash, script, audio, metadata):
            print(f"Fresh: {episode.id}")
            continue
        command = [
            sys.executable, str(ROOT / "Tools/generate_podcast.py"),
            episode.source.relative_to(ROOT).as_posix(),
            "--duration", str(episode.duration_minutes),
            "--voice", str(profile["voice"]),
            "--style", episode.voice_style,
            "--overwrite",
        ]
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            raise PublishError(f"Generation failed for {episode.id}")
        data = json.loads(metadata.read_text(encoding="utf-8"))
        data.update({"episode_id": episode.id, "episode": episode.number, "voice_style": episode.voice_style, "source_sha256": source_hash, "sourceReference": source_reference})
        metadata.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        generated += 1
    feed = build_public(strict_email=strict_email)
    print(f"Generated episodes: {generated}")
    print(f"Published feed: {feed}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Regenerate even when the source hash matches")
    parser.add_argument("--strict-email", action="store_true", help="Require PODCAST_EMAIL to be configured")
    args = parser.parse_args()
    try:
        run(force=args.force, strict_email=args.strict_email)
        return 0
    except PublishError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
