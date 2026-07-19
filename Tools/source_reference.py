"""Fail-closed source references shared by podcast and YouTube publication."""

from __future__ import annotations

import re
from typing import Any, Mapping
from urllib.parse import urlsplit

DEFAULT_INSIGHTS_BASE_URL = "https://insynergy.io/insights"
INSIGHT_PATH = re.compile(r"^/insights/[a-z0-9]+(?:-[a-z0-9]+)*$")


class SourceReferenceError(RuntimeError):
    pass


def validate_canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "insynergy.io"
        or parsed.query
        or parsed.fragment
        or not INSIGHT_PATH.fullmatch(parsed.path)
    ):
        raise SourceReferenceError(
            "Fail closed: source must be an exact "
            "https://insynergy.io/insights/{slug} URL without query or fragment"
        )
    return url


def episode_insight_url(episode: Any, config: Mapping[str, Any]) -> str:
    overrides = config.get("insight_urls", {})
    if isinstance(overrides, Mapping):
        override = overrides.get(episode.slug) or overrides.get(episode.id)
        if override:
            return validate_canonical_url(str(override))
    base = str(config.get("insights_base_url", DEFAULT_INSIGHTS_BASE_URL)).rstrip("/")
    return validate_canonical_url(f"{base}/{episode.slug}")


def episode_source_reference(episode: Any, config: Mapping[str, Any]) -> dict[str, str]:
    if not str(episode.title).strip():
        raise SourceReferenceError("Fail closed: source title is missing")
    if episode.published.utcoffset() is None:
        raise SourceReferenceError("Fail closed: source publication time must include a timezone")
    return {
        "canonicalUrl": episode_insight_url(episode, config),
        "sourceTitle": str(episode.title),
        "sourcePublisher": "Insynergy Insights",
        "sourceLanguage": "en",
        "publishedAt": episode.published.isoformat(),
    }


def validate_body_reference(body: str, canonical_url: str) -> None:
    validate_canonical_url(canonical_url)
    if body.count(canonical_url) != 1:
        raise SourceReferenceError(
            "Fail closed: exact canonical source URL must appear once in derivative content"
        )
