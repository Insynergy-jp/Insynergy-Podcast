#!/usr/bin/env python3
"""Validate every published podcast episode's canonical Insight source."""

from __future__ import annotations

import sys

from publish_podcast import load_episodes, load_show
from source_reference import SourceReferenceError, episode_source_reference, validate_remote_source


def run() -> int:
    show = load_show()
    config = show.get("youtube", {})
    if not isinstance(config, dict):
        raise SourceReferenceError("Podcast YouTube configuration must be a mapping")
    episodes = [episode for episode in load_episodes() if episode.podcast and episode.status == "published"]
    failures: list[str] = []
    for episode in episodes:
        try:
            reference = episode_source_reference(episode, config)
            validate_remote_source(reference)
        except SourceReferenceError as exc:
            failures.append(f"{episode.id}: {exc}")
            print(f"Invalid source reference: {episode.id}: {exc}", file=sys.stderr)
            continue
        print(f"Validated source reference: {episode.id} {reference['canonicalUrl']}")
    if failures:
        raise SourceReferenceError(
            f"Source reference validation failed for {len(failures)} episode(s): "
            + "; ".join(failures)
        )
    print(f"Validated source references: {len(episodes)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except (SourceReferenceError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
