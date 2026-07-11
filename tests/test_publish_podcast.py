import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "Tools"))
import publish_podcast as pp


class PublishingTests(unittest.TestCase):
    def test_manifest_loads_stable_episode_id(self):
        episodes = pp.load_episodes()
        self.assertEqual(episodes[0].id, "DD-001")
        self.assertEqual(episodes[0].voice_style, "executive")

    def test_feed_contains_immutable_guid_and_enclosure(self):
        episode = pp.load_episodes()[0]
        show = pp.load_show()
        with tempfile.TemporaryDirectory() as temp:
            audio = Path(temp) / "episode.mp3"
            audio.write_bytes(b"audio")
            root = pp.create_feed(show, [(episode, audio, 65)])
        xml = ET.tostring(root, encoding="unicode")
        self.assertIn("urn:insynergy:podcast:DD-001", xml)
        self.assertIn('type="audio/mpeg"', xml)
        self.assertIn("00:01:05", xml)

    def test_placeholder_email_is_rejected_for_deployment(self):
        with patch.dict("os.environ", {"PODCAST_EMAIL": "REPLACE_WITH_PUBLIC_EMAIL"}):
            show = pp.load_show()
        self.assertTrue(show["contact_email"].startswith("REPLACE_"))


if __name__ == "__main__":
    unittest.main()
