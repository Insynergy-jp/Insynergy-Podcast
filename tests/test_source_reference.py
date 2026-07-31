import json
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))

from publish_podcast import Episode
from source_reference import (
    SourceReferenceError,
    episode_source_reference,
    validate_body_reference,
    validate_canonical_url,
    validate_remote_source,
)
from run_pipeline import persist_source_reference


class Response:
    def __init__(self, body: bytes, status: int = 200, content_type: str = "text/html; charset=utf-8"):
        self.body = body
        self.status = status
        self.headers = {"Content-Type": content_type}

    def read(self, _limit: int) -> bytes:
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class SourceReferenceTests(unittest.TestCase):
    def episode(self, source: Path) -> Episode:
        return Episode(
            id="DD-099", number=99, title="Podcast title", slug="source-slug",
            description="Description", published=datetime(2026, 7, 31, tzinfo=timezone.utc),
            status="published", podcast=True, duration_minutes=10, voice_style="academic",
            source=source, episode_type="full", youtube_video_id=None,
            manifest=Path("episode.yml"),
        )

    def write_source(self, directory: str, status: str = "published") -> Path:
        source = Path(directory) / "source.md"
        source.write_text(
            "---\n"
            "title: Original Insight title\n"
            "slug: original-insight-slug\n"
            "date: 2026-02-26\n"
            "language: en\n"
            f"status: {status}\n"
            "name: Insynergy Insights\n"
            "---\n\n# Article\n",
            encoding="utf-8",
        )
        return source

    def test_reference_uses_insight_frontmatter_not_episode_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = episode_source_reference(self.episode(self.write_source(directory)), {})
        self.assertEqual(reference["sourceTitle"], "Original Insight title")
        self.assertEqual(reference["sourceSlug"], "original-insight-slug")
        self.assertEqual(reference["publishedAt"], "2026-02-26")
        self.assertEqual(reference["canonicalUrl"], "https://insynergy.io/insights/source-slug")

    def test_unpublished_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            episode = self.episode(self.write_source(directory, "draft"))
            with self.assertRaisesRegex(SourceReferenceError, "not published"):
                episode_source_reference(episode, {})

    def test_locked_source_is_treated_as_published(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = episode_source_reference(
                self.episode(self.write_source(directory, "locked")), {}
            )
        self.assertEqual(reference["publishedAt"], "2026-02-26")

    def test_manifest_override_can_complete_legacy_frontmatter(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "legacy.md"
            source.write_text("---\nslug: legacy\n---\n\n# Legacy\n", encoding="utf-8")
            episode = replace(self.episode(source), source_reference={
                "title": "Legacy Insight",
                "slug": "legacy",
                "published_at": "2026-01-01",
                "language": "en",
                "status": "published",
            })
            reference = episode_source_reference(episode, {})
        self.assertEqual(reference["sourceTitle"], "Legacy Insight")
        self.assertEqual(reference["publishedAt"], "2026-01-01")

    def test_canonical_url_respects_the_configured_base(self):
        self.assertEqual(
            validate_canonical_url(
                "https://insynergy.io/insights/example",
                "https://insynergy.io/insights",
            ),
            "https://insynergy.io/insights/example",
        )
        with self.assertRaises(SourceReferenceError):
            validate_canonical_url("https://www.insynergy.io/insights/example?utm=x")

    def test_remote_source_requires_matching_canonical_og_url_and_image(self):
        url = "https://insynergy.io/insights/example"
        body = (
            f'<link rel="canonical" href="{url}">'
            f'<meta property="og:url" content="{url}">'
            '<meta property="og:image" content="https://images.example.test/og.png">'
        ).encode()
        result = validate_remote_source({"canonicalUrl": url}, opener=lambda *_args, **_kwargs: Response(body))
        self.assertEqual(result.canonical_url, url)
        self.assertEqual(result.og_image, "https://images.example.test/og.png")

    def test_remote_source_rejects_a_canonical_mismatch(self):
        url = "https://insynergy.io/insights/example"
        body = (
            '<link rel="canonical" href="https://insynergy.io/insights/other">'
            f'<meta property="og:url" content="{url}">'
            '<meta property="og:image" content="https://images.example.test/og.png">'
        ).encode()
        with self.assertRaisesRegex(SourceReferenceError, "canonical mismatch"):
            validate_remote_source({"canonicalUrl": url}, opener=lambda *_args, **_kwargs: Response(body))

    def test_body_requires_the_exact_source_url_once(self):
        url = "https://insynergy.io/insights/example"
        validate_body_reference(f"Read more: {url}", url)
        with self.assertRaises(SourceReferenceError):
            validate_body_reference(f"{url}\n{url}", url)

    def test_fresh_metadata_is_backfilled_without_regeneration(self):
        reference = {
            "canonicalUrl": "https://insynergy.io/insights/example",
            "publishedAt": "2026-02-26",
        }
        with tempfile.TemporaryDirectory() as directory:
            metadata = Path(directory) / "episode.json"
            metadata.write_text('{"source_sha256": "fresh"}\n', encoding="utf-8")
            self.assertTrue(persist_source_reference(metadata, reference))
            self.assertFalse(persist_source_reference(metadata, reference))
            saved = json.loads(metadata.read_text(encoding="utf-8"))
        self.assertEqual(saved["sourceReference"], reference)


if __name__ == "__main__":
    unittest.main()
