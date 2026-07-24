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

    def test_generate_script_can_cap_revision_output(self):
        requests = []

        def create(**kwargs):
            requests.append(kwargs)
            return SimpleNamespace(output_text="Revised narration")

        client = SimpleNamespace(responses=SimpleNamespace(create=create))
        self.assertEqual(
            gp.generate_script(client, "model", "prompt", max_output_tokens=2100),
            "Revised narration",
        )
        self.assertEqual(requests, [{"model": "model", "input": "prompt", "max_output_tokens": 2100}])

    def test_condense_prompt_sets_a_hard_word_limit(self):
        prompt = gp.build_condense_prompt("Original narration", {"title": "Title"}, 10, "academic")
        self.assertIn("Target length: 1400 words", prompt)
        self.assertIn("Required range: 1260 to 1540 words", prompt)
        self.assertIn("Do not exceed 1540 words", prompt)
        self.assertIn("Voice style: academic", prompt)

    def test_definition_revision_prompt_requires_exact_definition(self):
        prompt = gp.build_definition_revision_prompt(
            "Decision Design is a governance architecture discipline.",
            {"title": "Title"},
            10,
            "academic",
        )
        self.assertIn(gp.DECISION_DESIGN_DEFINITION, prompt)
        self.assertIn("Include the following sentence exactly once", prompt)
        self.assertIn("Change only what is necessary to repair the definition", prompt)
        self.assertIn("Required range: 1260 to 1540 words", prompt)

    def test_only_overlong_scripts_trigger_revision(self):
        self.assertTrue(gp.should_retry_overlong(["Script is too long (2800 words; expected roughly 1400)."]))
        self.assertFalse(gp.should_retry_overlong(["Script is too short (200 words; expected roughly 1400)."]))
        self.assertFalse(gp.should_retry_overlong(["Too many Markdown/list markers remain in the narration."]))

    def test_only_definition_errors_trigger_definition_revision(self):
        self.assertTrue(gp.should_retry_definition([gp.DECISION_DESIGN_DEFINITION_ERROR]))
        self.assertFalse(gp.should_retry_definition(["Script is too short (200 words; expected roughly 1400)."]))

    def test_run_revises_an_incorrect_decision_design_definition_once(self):
        with tempfile.TemporaryDirectory() as temp:
            vault = Path(temp).resolve()
            source = vault / "Insights" / "note.md"
            source.parent.mkdir(parents=True)
            source.write_text(
                "---\ntitle: Definition Test\n---\n\nDecision Design is a governance architecture discipline.",
                encoding="utf-8",
            )
            first_script = "Decision Design is a governance architecture discipline. " + "context " * 100
            revised_script = gp.DECISION_DESIGN_DEFINITION + " " + "context " * 100
            responses = iter((first_script, revised_script))
            requests = []

            def create(**kwargs):
                requests.append(kwargs)
                return SimpleNamespace(output_text=next(responses))

            client = SimpleNamespace(responses=SimpleNamespace(create=create))
            config = gp.Config(vault, Path("Insights"), "model", "tts-1", "nova")
            args = SimpleNamespace(
                input="Insights/note.md",
                duration=1,
                voice=None,
                style="academic",
                overwrite=False,
                script_only=True,
                audio_only=False,
                dry_run=False,
            )
            with patch.object(gp, "load_config", return_value=config), patch.object(
                gp, "create_openai_client", return_value=client
            ):
                gp.run(args)

            self.assertEqual(len(requests), 2)
            self.assertIn("repair its Decision Design definition", requests[1]["input"])
            script = (vault / "Podcast/Scripts/note-podcast.md").read_text(encoding="utf-8")
            self.assertIn(gp.DECISION_DESIGN_DEFINITION, script)
            self.assertNotIn("governance architecture discipline", script)

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
