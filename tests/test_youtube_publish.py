import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))

from publish_podcast import Episode
from youtube_publish import YouTubeCredentials, render_video, upload_video, video_body


class YouTubePublishingTests(unittest.TestCase):
    def episode(self):
        from datetime import datetime, timezone
        return Episode(
            id="DD-003", number=3, title="Judgment, Not Meaning", slug="judgment-not-meaning",
            description="A description.", published=datetime.now(timezone.utc), status="published",
            podcast=True, duration_minutes=10, voice_style="academic", source=Path("source.md"),
            episode_type="full", manifest=Path("episode.yml"),
        )

    def test_credentials_are_optional_or_complete(self):
        self.assertIsNone(YouTubeCredentials.from_env({}))
        credentials = YouTubeCredentials.from_env({
            "YOUTUBE_CLIENT_ID": "client", "YOUTUBE_CLIENT_SECRET": "secret",
            "YOUTUBE_REFRESH_TOKEN": "refresh",
        })
        self.assertEqual(credentials.refresh_token, "refresh")

    def test_video_metadata_defaults_to_private(self):
        body = video_body(
            self.episode(), {"base_url": "https://example.test"},
            {"privacy_status": "private", "category_id": "22", "tags": ["Decision Design"]},
        )
        self.assertEqual(body["status"]["privacyStatus"], "private")
        self.assertEqual(body["snippet"]["categoryId"], "22")
        self.assertIn("Podcast RSS", body["snippet"]["description"])

    @patch("youtube_publish.shutil.which", return_value="/usr/bin/ffmpeg")
    @patch("youtube_publish.MP3")
    @patch("youtube_publish.subprocess.run")
    def test_render_uses_h264_and_aac(self, run, mp3, _which):
        run.return_value.returncode = 0
        run.return_value.stderr = ""
        mp3.return_value.info.length = 8.25
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio, cover, output = root / "a.mp3", root / "cover.jpg", root / "out.mp4"
            audio.write_bytes(b"audio")
            cover.write_bytes(b"image")
            def create_output(command, **_kwargs):
                output.write_bytes(b"video")
                return run.return_value
            run.side_effect = create_output
            render_video(audio, cover, output)
            command = run.call_args.args[0]
            self.assertIn("libx264", command)
            self.assertIn("aac", command)
            self.assertIn("8.250", command)

    def test_resumable_upload_returns_video_id(self):
        youtube = MagicMock()
        request = youtube.videos.return_value.insert.return_value
        request.next_chunk.side_effect = [(None, None), (None, {"id": "abc123"})]
        with patch("youtube_publish.MediaFileUpload"):
            self.assertEqual(upload_video(youtube, Path("video.mp4"), {"snippet": {}, "status": {}}), "abc123")


if __name__ == "__main__":
    unittest.main()
