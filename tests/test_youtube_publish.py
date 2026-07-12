import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))

from publish_podcast import Episode
from youtube_publish import (
    CAPTION_TIMING_VERSION,
    CAPTION_TRANSLATION_BATCH_SIZE,
    YOUTUBE_CAPTION_SCOPE,
    YouTubeCredentials,
    build_timed_srt,
    existing_caption_ids,
    normalize_caption_text,
    render_video,
    retry_empty_translation,
    transcribe_segments,
    translate_segments_to_japanese,
    upload_caption,
    update_caption,
    upload_video,
    video_body,
)


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
        self.assertIn(YOUTUBE_CAPTION_SCOPE, credentials.google_credentials().scopes)

    def test_video_metadata_defaults_to_private(self):
        with patch.dict(os.environ, {}, clear=True):
            body = video_body(
                self.episode(), {"base_url": "https://example.test"},
                {"privacy_status": "private", "category_id": "22", "tags": ["Decision Design"]},
            )
        self.assertEqual(body["status"]["privacyStatus"], "private")
        self.assertEqual(body["snippet"]["categoryId"], "22")
        self.assertIn("Podcast RSS", body["snippet"]["description"])
        self.assertEqual(body["snippet"]["defaultLanguage"], "en")

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

    def test_caption_upload_returns_caption_id(self):
        youtube = MagicMock()
        youtube.captions.return_value.insert.return_value.execute.return_value = {"id": "caption123"}
        with patch("youtube_publish.MediaFileUpload"):
            caption_id = upload_caption(youtube, "video123", Path("captions.srt"))
        self.assertEqual(caption_id, "caption123")
        body = youtube.captions.return_value.insert.call_args.kwargs["body"]
        self.assertEqual(body["snippet"]["language"], "en")
        self.assertFalse(body["snippet"]["isDraft"])

    def test_transcription_segments_drive_exact_srt_times(self):
        client = MagicMock()
        client.audio.transcriptions.create.return_value.segments = [
            {"start": 1.25, "end": 3.5, "text": "First sentence."},
            {"start": 4.0, "end": 6.75, "text": "Second sentence."},
        ]
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "audio.mp3"
            audio.write_bytes(b"audio")
            segments = transcribe_segments(client, audio)
        srt = build_timed_srt(segments)
        self.assertIn("00:00:01,250 --> 00:00:03,500", srt)
        self.assertIn("00:00:04,000 --> 00:00:06,750", srt)
        kwargs = client.audio.transcriptions.create.call_args.kwargs
        self.assertEqual(kwargs["model"], "whisper-1")
        self.assertEqual(kwargs["timestamp_granularities"], ["segment"])

    def test_brand_name_is_normalized_in_english_captions(self):
        self.assertEqual(normalize_caption_text("InSynergy builds systems."), "Insynergy builds systems.")
        self.assertEqual(normalize_caption_text("INSYNERGY’s work."), "Insynergy’s work.")
        self.assertEqual(normalize_caption_text("Visit insynergy."), "Visit Insynergy.")

    def test_japanese_translation_preserves_segment_ids_and_timing(self):
        client = MagicMock()
        client.responses.create.return_value.output_text = json.dumps({"translations": {
            "segment_0": "最初の文です。",
            "segment_1": "次の文です。",
        }}, ensure_ascii=False)
        segments = [
            {"start": 0.2, "end": 1.5, "text": "First."},
            {"start": 1.8, "end": 3.2, "text": "Second."},
        ]
        translated = translate_segments_to_japanese(client, segments, "test-model")
        srt = build_timed_srt(segments, translated)
        self.assertIn("最初の文です。", srt)
        self.assertIn("00:00:01,800 --> 00:00:03,200", srt)
        request = client.responses.create.call_args.kwargs
        self.assertEqual(request["text"]["format"]["type"], "json_schema")
        self.assertTrue(request["text"]["format"]["strict"])
        translation_schema = request["text"]["format"]["schema"]["properties"]["translations"]
        self.assertEqual(translation_schema["required"], ["segment_0", "segment_1"])

    def test_japanese_translation_is_batched(self):
        client = MagicMock()
        segments = [
            {"start": float(index), "end": float(index + 1), "text": f"Segment {index}."}
            for index in range(CAPTION_TRANSLATION_BATCH_SIZE + 1)
        ]
        first = {f"segment_{index}": f"翻訳{index}" for index in range(CAPTION_TRANSLATION_BATCH_SIZE)}
        second = {"segment_0": "最後の翻訳"}
        client.responses.create.side_effect = [
            MagicMock(output_text=json.dumps({"translations": first}, ensure_ascii=False)),
            MagicMock(output_text=json.dumps({"translations": second}, ensure_ascii=False)),
        ]
        translated = translate_segments_to_japanese(client, segments, "test-model")
        self.assertEqual(len(translated), len(segments))
        self.assertEqual(translated[-1], "最後の翻訳")
        self.assertEqual(client.responses.create.call_count, 2)

    def test_empty_structured_translation_retries_one_segment(self):
        client = MagicMock()
        client.responses.create.side_effect = [
            MagicMock(output_text=json.dumps({"translations": {"segment_0": ""}}, ensure_ascii=False)),
            MagicMock(output_text="再試行した翻訳です。"),
        ]
        segments = [{"start": 0.0, "end": 1.0, "text": "Retry this."}]
        self.assertEqual(
            translate_segments_to_japanese(client, segments, "test-model"),
            ["再試行した翻訳です。"],
        )
        self.assertEqual(client.responses.create.call_count, 2)

    def test_empty_translation_retry_must_return_text(self):
        client = MagicMock()
        client.responses.create.return_value.output_text = "Japanese text"
        self.assertEqual(retry_empty_translation(client, "English text", "model"), "Japanese text")

    def test_caption_upload_supports_japanese_and_update(self):
        youtube = MagicMock()
        youtube.captions.return_value.insert.return_value.execute.return_value = {"id": "ja123"}
        youtube.captions.return_value.update.return_value.execute.return_value = {"id": "en123"}
        with patch("youtube_publish.MediaFileUpload"):
            self.assertEqual(upload_caption(youtube, "video", Path("ja.srt"), "ja", "日本語"), "ja123")
            self.assertEqual(update_caption(youtube, "en123", Path("en.srt")), "en123")
        insert_body = youtube.captions.return_value.insert.call_args.kwargs["body"]
        self.assertEqual(insert_body["snippet"]["language"], "ja")
        self.assertEqual(insert_body["snippet"]["name"], "日本語")
        update_call = youtube.captions.return_value.update.call_args.kwargs
        self.assertEqual(update_call["part"], "id")
        self.assertEqual(update_call["body"], {"id": "en123"})

    def test_caption_timing_version_is_explicit(self):
        self.assertEqual(CAPTION_TIMING_VERSION, "audio-transcription-v2")

    def test_existing_caption_ids_supports_resuming_after_partial_run(self):
        youtube = MagicMock()
        youtube.captions.return_value.list.return_value.execute.return_value = {"items": [
            {"id": "english-id", "snippet": {"language": "en", "name": "English"}},
            {"id": "japanese-id", "snippet": {"language": "ja", "name": "日本語"}},
            {"id": "automatic", "snippet": {"language": "en", "name": ""}},
        ]}
        self.assertEqual(
            existing_caption_ids(youtube, "video-id"),
            {"en": "english-id", "ja": "japanese-id"},
        )


if __name__ == "__main__":
    unittest.main()
