"""Canonical Insight source references shared by podcast publication targets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
import re
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

import yaml


DEFAULT_INSIGHTS_BASE_URL = "https://insynergy.io/insights"
MAX_SOURCE_HTML_BYTES = 2 * 1024 * 1024


class SourceReferenceError(RuntimeError):
    pass


@dataclass(frozen=True)
class RemoteSource:
    canonical_url: str
    og_url: str
    og_image: str


class SourcePageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonical_url = ""
        self.og_url = ""
        self.og_image = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonical_url = values.get("href", "").strip()
        if tag.lower() != "meta":
            return
        property_name = values.get("property", "").lower()
        if property_name == "og:url":
            self.og_url = values.get("content", "").strip()
        elif property_name == "og:image":
            self.og_image = values.get("content", "").strip()


def _source_frontmatter(path: Path) -> dict[str, Any]:
    try:
        document = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SourceReferenceError(f"Could not read Insight source {path}: {exc}") from exc
    if not document.startswith("---\n"):
        raise SourceReferenceError(f"Insight source has no YAML frontmatter: {path}")
    try:
        header, _body = document[4:].split("\n---", 1)
        value = yaml.safe_load(header)
    except (ValueError, yaml.YAMLError) as exc:
        raise SourceReferenceError(f"Invalid Insight frontmatter in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SourceReferenceError(f"Insight frontmatter must be a mapping: {path}")
    return value


def _source_date(value: Any, path: Path) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    try:
        return date.fromisoformat(str(value)).isoformat()
    except (TypeError, ValueError) as exc:
        raise SourceReferenceError(f"Insight frontmatter date must be ISO-8601 in {path}") from exc


def validate_canonical_url(url: str, base_url: str = DEFAULT_INSIGHTS_BASE_URL) -> str:
    parsed = urlparse(url)
    base = urlparse(base_url.rstrip("/"))
    expected_prefix = base.path.rstrip("/") + "/"
    if (
        parsed.scheme != "https"
        or parsed.netloc != base.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not parsed.path.startswith(expected_prefix)
        or parsed.path.endswith("/")
    ):
        raise SourceReferenceError(
            f"Source URL must be a canonical child of {base_url.rstrip('/')}: {url}"
        )
    slug = parsed.path[len(expected_prefix):]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SourceReferenceError(f"Source URL has an invalid Insight slug: {url}")
    return url


def episode_insight_url(episode: Any, config: Mapping[str, Any]) -> str:
    base_url = str(config.get("insights_base_url", DEFAULT_INSIGHTS_BASE_URL)).rstrip("/")
    overrides = config.get("insight_urls", {})
    if isinstance(overrides, Mapping):
        override = overrides.get(episode.slug) or overrides.get(episode.id)
        if override:
            return validate_canonical_url(str(override), base_url)
    return validate_canonical_url(f"{base_url}/{episode.slug}", base_url)


def episode_source_reference(episode: Any, config: Mapping[str, Any]) -> dict[str, str]:
    metadata = _source_frontmatter(episode.source)
    overrides = getattr(episode, "source_reference", {}) or {}
    if not isinstance(overrides, Mapping):
        raise SourceReferenceError(f"Episode source_reference must be a mapping: {episode.manifest}")
    resolved = {
        "title": overrides.get("title") or metadata.get("title"),
        "slug": overrides.get("slug") or metadata.get("slug"),
        "date": overrides.get("published_at") or metadata.get("date"),
        "language": overrides.get("language") or metadata.get("language"),
        "status": overrides.get("status") or metadata.get("status"),
        "publisher": overrides.get("publisher") or metadata.get("name") or "Insynergy Insights",
    }
    required = ("title", "slug", "date", "language", "status")
    missing = [key for key in required if resolved.get(key) in (None, "")]
    if missing:
        raise SourceReferenceError(
            f"Insight source is missing frontmatter field(s) {', '.join(missing)}: {episode.source}"
        )
    if str(resolved["status"]).lower() not in {"published", "locked"}:
        raise SourceReferenceError(f"Insight source is not published: {episode.source}")
    return {
        "canonicalUrl": episode_insight_url(episode, config),
        "sourceTitle": str(resolved["title"]).strip(),
        "sourceSlug": str(resolved["slug"]).strip(),
        "sourcePublisher": str(resolved["publisher"]).strip(),
        "sourceLanguage": str(resolved["language"]).strip(),
        "publishedAt": _source_date(resolved["date"], episode.source),
    }


def validate_body_reference(body: str, canonical_url: str, base_url: str = DEFAULT_INSIGHTS_BASE_URL) -> None:
    validate_canonical_url(canonical_url, base_url)
    if body.count(canonical_url) != 1:
        raise SourceReferenceError(
            "Exact canonical source URL must appear once in derivative content"
        )


def validate_remote_source(
    reference: Mapping[str, str],
    opener: Callable[..., Any] = urlopen,
) -> RemoteSource:
    canonical_url = reference["canonicalUrl"]
    request = Request(canonical_url, headers={"User-Agent": "Insynergy-Podcast/1.0 (+https://insynergy.io/)"})
    try:
        with opener(request, timeout=20) as response:
            status = int(getattr(response, "status", 200))
            content_type = str(response.headers.get("Content-Type", "")).split(";", 1)[0].lower()
            html_bytes = response.read(MAX_SOURCE_HTML_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise SourceReferenceError(f"Insight source is not publicly reachable: {canonical_url}: {exc}") from exc
    if status != 200:
        raise SourceReferenceError(f"Insight source returned HTTP {status}: {canonical_url}")
    if content_type != "text/html":
        raise SourceReferenceError(f"Insight source is not HTML ({content_type or 'unknown'}): {canonical_url}")
    if len(html_bytes) > MAX_SOURCE_HTML_BYTES:
        raise SourceReferenceError(f"Insight source HTML exceeds the download limit: {canonical_url}")
    parser = SourcePageParser()
    parser.feed(html_bytes.decode("utf-8", errors="replace"))
    page_canonical = urljoin(canonical_url, parser.canonical_url)
    og_url = urljoin(canonical_url, parser.og_url)
    og_image = urljoin(canonical_url, parser.og_image)
    if page_canonical != canonical_url:
        raise SourceReferenceError(
            f"Insight canonical mismatch: expected {canonical_url}, found {page_canonical or 'missing'}"
        )
    if og_url != canonical_url:
        raise SourceReferenceError(
            f"Insight og:url mismatch: expected {canonical_url}, found {og_url or 'missing'}"
        )
    parsed_image = urlparse(og_image)
    if parsed_image.scheme != "https" or not parsed_image.netloc:
        raise SourceReferenceError(f"Insight og:image is missing or not HTTPS: {canonical_url}")
    return RemoteSource(page_canonical, og_url, og_image)
