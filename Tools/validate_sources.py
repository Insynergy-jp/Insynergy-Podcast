#!/usr/bin/env python3
"""Validate every publishable episode's Insynergy Insight source reference."""

from __future__ import annotations

import sys

from publish_podcast import load_episodes, load_show
from source_reference import SourceReferenceError, episode_source_reference


def run() -> int:
    show = load_show()
    config = show.get("youtube", {})
    if not isinstance(config, dict):
        raise SourceReferenceError("Fail closed: podcast YouTube configuration must be a mapping")
    episodes = [episode for episode in load_episodes() if episode.podcast and episode.status == "published"]
    for episode in episodes:
        episode_source_reference(episode, config)
    print(f"Validated source references: {len(episodes)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except (SourceReferenceError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
