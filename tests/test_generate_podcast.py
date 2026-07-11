import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.modules.setdefault("dotenv", SimpleNamespace(load_dotenv=lambda: False))
sys.path.insert(0, str(Path(__file__).parents[1] / "Tools"))
import generate_podcast as gp


class PodcastTests(unittest.TestCase):
    def test_frontmatter_is_parsed_and_removed(self):
        metadata, body = gp.parse_frontmatter('---\ntitle: "A Title"\ntags: [ai, governance]\n---\n# Body')
        self.assertEqual(metadata["title"], "A Title")
        self.assertEqual(metadata["tags"], ["ai", "governance"])
        self.assertEqual(body, "# Body")

    def test_markdown_symbols_are_removed(self):
        cleaned = gp.clean_markdown("# Heading\n\n- **Strong** [claim](https://example.com) ![chart](x.png)\n\n[^1]: note")
        self.assertEqual(cleaned, "Heading\n\nStrong claim chart")

    def test_japanese_and_quote_path(self):
        with tempfile.TemporaryDirectory() as temp:
            vault = Path(temp) / '書類 "引用"'
            note = vault / "40_Outputs" / "Insight" / "日本語.md"
            note.parent.mkdir(parents=True)
            note.write_text("text", encoding="utf-8")
            config = gp.Config(vault.resolve(), Path("40_Outputs/Insight"), "m", "tts-1", "nova")
            self.assertEqual(gp.resolve_input_path("日本語.md", config), note.resolve())

    def test_output_names(self):
        vault = Path("/vault")
        paths = gp.output_paths(vault / "Insights" / "hello.md", vault)
        self.assertEqual(paths.script, vault / "Podcast/Scripts/hello-podcast.md")
        self.assertEqual(paths.audio, vault / "Podcast/Audio/hello.mp3")

    def test_overwrite_prevention(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "exists"
            path.touch()
            with self.assertRaises(gp.PodcastError):
                gp.ensure_writable([path], overwrite=False)
            gp.ensure_writable([path], overwrite=True)

    def test_long_text_is_split_without_loss(self):
        text = "First sentence. " + ("word " * 30) + "Final sentence."
        chunks = gp.split_tts_text(text, max_chars=50)
        self.assertTrue(all(0 < len(chunk) <= 50 for chunk in chunks))
        self.assertEqual(" ".join(chunks), " ".join(text.split()))

    def test_empty_api_response(self):
        client = SimpleNamespace(responses=SimpleNamespace(create=lambda **kwargs: SimpleNamespace(output_text="  ")))
        with self.assertRaisesRegex(gp.PodcastError, "empty script"):
            gp.generate_script(client, "model", "prompt")

    def test_metadata_json(self):
        vault = Path("/vault")
        source = vault / "Insights" / "note.md"
        paths = gp.output_paths(source, vault)
        config = gp.Config(vault, Path("Insights"), "text-model", "tts-1", "nova")
        data = gp.build_metadata(title="Note", source=source, paths=paths, vault=vault, script="Two words", duration=8, generated_at="now", config=config, voice="nova", audio_created=True)
        encoded = json.dumps(data)
        self.assertEqual(json.loads(encoded)["word_count"], 2)
        self.assertEqual(data["audio_file"], "Podcast/Audio/note.mp3")


if __name__ == "__main__":
    unittest.main()
