import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "Tools"))
import publish_podcast as pp


class PublishingTests(unittest.TestCase):
    def test_distribution_policy_keeps_youtube_off_rss(self):
        show = pp.load_show()
        self.assertEqual(show["distribution"]["youtube"], "direct_api")
        self.assertEqual(show["youtube"]["delivery"], "direct_api")
        self.assertFalse(show["youtube"]["rss_ingestion"])

    def test_manifest_loads_stable_episode_id(self):
        episodes = pp.load_episodes()
        self.assertEqual(episodes[0].id, "DD-001")
        self.assertEqual(episodes[0].voice_style, "executive")

    def test_manifest_can_seed_an_existing_youtube_video(self):
        episode = next(ep for ep in pp.load_episodes() if ep.id == "DD-017")
        self.assertEqual(episode.youtube_video_id, "OXF7nVRN2kQ")

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
        self.assertIn("https://insynergy.io/insights/", xml)
        self.assertIn("Read the full Insynergy Insight", xml)

    def test_placeholder_email_is_rejected_for_deployment(self):
        with patch.dict("os.environ", {"PODCAST_EMAIL": "REPLACE_WITH_PUBLIC_EMAIL"}):
            show = pp.load_show()
        self.assertTrue(show["contact_email"].startswith("REPLACE_"))

    def test_index_uses_brand_navigation_and_episode_player(self):
        episode = pp.load_episodes()[0]
        show = pp.load_show()
        page = pp.create_index(show, [(episode, Path("episode.mp3"), 60)])
        self.assertIn('class="brand"', page)
        self.assertIn('id="episodes"', page)
        self.assertIn("insynergy-wave.png", page)
        self.assertIn(show["spotify_url"], page)
        self.assertIn("Listen on Spotify", page)
        self.assertNotIn("Georgia", page)


if __name__ == "__main__":
    unittest.main()
