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
    ENGLISH_CAPTION_TEXT_VERSION,
    CAPTION_TRANSLATION_BATCH_SIZE,
    OG_THUMBNAIL_VERSION,
    YOUTUBE_DESCRIPTION_VERSION,
    YOUTUBE_CAPTION_SCOPE,
    YouTubeCredentials,
    build_timed_srt,
    captions_are_fresh,
    create_synced_caption_files,
    description_is_fresh,
    existing_caption_ids,
    fetch_insight_og_image,
    insight_url,
    normalize_caption_text,
    prepare_thumbnail,
    publish_episode,
    render_video,
    retry_empty_translation,
    set_video_thumbnail,
    thumbnail_is_fresh,
    transcribe_segments,
    translate_segments_to_japanese,
    upload_caption,
    update_caption,
    update_video_details,
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
            episode_type="full", youtube_video_id=None, manifest=Path("episode.yml"),
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
        self.assertIn("Episode overview", body["snippet"]["description"])
        self.assertIn(
            "https://insynergy.io/insights/judgment-not-meaning",
            body["snippet"]["description"],
        )
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
            self.assertIn("scale=1920:1080", command[command.index("-filter_complex") + 1])

    def test_insight_url_uses_slug_and_supports_explicit_override(self):
        episode = self.episode()
        self.assertEqual(
            insight_url(episode, {}),
            "https://insynergy.io/insights/judgment-not-meaning",
        )
        self.assertEqual(
            insight_url(episode, {"insight_urls": {
                "judgment-not-meaning": "https://insynergy.io/insights/custom-slug",
            }}),
            "https://insynergy.io/insights/custom-slug",
        )

    def test_insight_url_rejects_noncanonical_override(self):
        with self.assertRaisesRegex(Exception, "Fail closed"):
            insight_url(self.episode(), {"insight_urls": {
                "judgment-not-meaning": "https://www.insynergy.io/insights/custom-slug?utm=x",
            }})

    def test_fetches_og_image_from_insight_page(self):
        class Response:
            def __init__(self, data, content_type):
                self.data = data
                self.headers = {"Content-Type": content_type}

            def read(self, _size):
                return self.data

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        html = (
            b'<html><head><meta content="https://images.example.test/og&amp;v=1.png" '
            b'property="og:image"></head></html>'
        )
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "og-image"
            with patch("youtube_publish.urlopen", side_effect=[
                Response(html, "text/html; charset=utf-8"),
                Response(b"image bytes", "image/png"),
            ]):
                page_url, image_url = fetch_insight_og_image(self.episode(), {}, destination)
            self.assertEqual(page_url, "https://insynergy.io/insights/judgment-not-meaning")
            self.assertEqual(image_url, "https://images.example.test/og&v=1.png")
            self.assertEqual(destination.read_bytes(), b"image bytes")

    @patch("youtube_publish.shutil.which", return_value="/usr/bin/ffmpeg")
    @patch("youtube_publish.subprocess.run")
    def test_thumbnail_is_converted_to_16_by_9_jpeg_under_limit(self, run, _which):
        run.return_value.returncode = 0
        run.return_value.stderr = ""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.png"
            destination = root / "thumbnail.jpg"
            source.write_bytes(b"image")

            def create_output(command, **_kwargs):
                destination.write_bytes(b"jpeg")
                return run.return_value

            run.side_effect = create_output
            prepare_thumbnail(source, destination)
            command = run.call_args.args[0]
            filter_value = command[command.index("-vf") + 1]
            self.assertIn("scale=1280:720", filter_value)
            self.assertIn("pad=1280:720", filter_value)
            self.assertEqual(destination.read_bytes(), b"jpeg")

    def test_custom_thumbnail_is_uploaded_and_versioned(self):
        youtube = MagicMock()
        with patch("youtube_publish.MediaFileUpload"):
            set_video_thumbnail(youtube, "video123", Path("thumbnail.jpg"))
        youtube.thumbnails.return_value.set.assert_called_once()
        kwargs = youtube.thumbnails.return_value.set.call_args.kwargs
        self.assertEqual(kwargs["videoId"], "video123")
        self.assertTrue(thumbnail_is_fresh({
            "youtube_thumbnail_version": OG_THUMBNAIL_VERSION,
            "youtube_thumbnail_insight_url": "https://insynergy.io/insights/example",
            "youtube_thumbnail_source_url": "https://images.example.test/example.png",
        }))
        self.assertFalse(thumbnail_is_fresh({}))

    def test_existing_video_description_is_updated_without_reupload(self):
        youtube = MagicMock()
        body = video_body(
            self.episode(),
            {"base_url": "https://example.test"},
            {"category_id": "22"},
        )
        update_video_details(youtube, "video123", body)
        youtube.videos.return_value.update.assert_called_once()
        kwargs = youtube.videos.return_value.update.call_args.kwargs
        self.assertEqual(kwargs["part"], "snippet")
        self.assertEqual(kwargs["body"]["id"], "video123")
        self.assertIn("Episode overview", kwargs["body"]["snippet"]["description"])
        article_url = "https://insynergy.io/insights/judgment-not-meaning"
        self.assertTrue(description_is_fresh({
            "youtube_description_version": YOUTUBE_DESCRIPTION_VERSION,
            "youtube_description_insight_url": article_url,
        }, article_url))
        self.assertFalse(description_is_fresh({}, article_url))

    def test_existing_video_gets_og_thumbnail_without_reupload(self):
        episode = self.episode()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "Podcast" / "Scripts"
            audio = root / "Podcast" / "Audio"
            metadata = root / "Podcast" / "Metadata"
            scripts.mkdir(parents=True)
            audio.mkdir(parents=True)
            metadata.mkdir(parents=True)
            (scripts / f"{episode.slug}-podcast.md").write_text("script", encoding="utf-8")
            (audio / f"{episode.slug}.mp3").write_bytes(b"audio")
            metadata_path = metadata / f"{episode.slug}.json"
            metadata_path.write_text(json.dumps({
                "youtube_video_id": "existing-video",
                "youtube_caption_timing": CAPTION_TIMING_VERSION,
                "youtube_english_caption_text_version": ENGLISH_CAPTION_TEXT_VERSION,
                "youtube_caption_id": "en-id",
                "youtube_japanese_caption_id": "ja-id",
            }), encoding="utf-8")
            with (
                patch("youtube_publish.fetch_insight_og_image", return_value=(
                    "https://insynergy.io/insights/judgment-not-meaning",
                    "https://images.example.test/og.png",
                )),
                patch("youtube_publish.prepare_thumbnail"),
                patch("youtube_publish.set_video_thumbnail") as set_thumbnail,
                patch("youtube_publish.upload_video") as upload,
                patch("youtube_publish.update_video_details") as update_details,
            ):
                video_id = publish_episode(
                    MagicMock(), episode, {
                        "cover": "Podcast/Assets/cover.jpg",
                        "base_url": "https://example.test",
                    }, {}, root
                )
            self.assertEqual(video_id, "existing-video")
            upload.assert_not_called()
            update_details.assert_called_once()
            set_thumbnail.assert_called_once()
            saved = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["youtube_description_version"], YOUTUBE_DESCRIPTION_VERSION)
            self.assertEqual(
                saved["youtube_description_insight_url"],
                "https://insynergy.io/insights/judgment-not-meaning",
            )
            self.assertEqual(saved["youtube_thumbnail_version"], OG_THUMBNAIL_VERSION)
            self.assertEqual(
                saved["youtube_thumbnail_source_url"], "https://images.example.test/og.png"
            )

    def test_manifest_video_id_is_persisted_before_later_api_failure(self):
        from dataclasses import replace

        episode = replace(self.episode(), youtube_video_id="recovered-video")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "Podcast" / "Scripts"
            audio = root / "Podcast" / "Audio"
            metadata = root / "Podcast" / "Metadata"
            scripts.mkdir(parents=True)
            audio.mkdir(parents=True)
            metadata.mkdir(parents=True)
            (scripts / f"{episode.slug}-podcast.md").write_text("script", encoding="utf-8")
            (audio / f"{episode.slug}.mp3").write_bytes(b"audio")
            metadata_path = metadata / f"{episode.slug}.json"
            metadata_path.write_text(json.dumps({
                "youtube_thumbnail_version": OG_THUMBNAIL_VERSION,
                "youtube_thumbnail_insight_url": "https://insynergy.io/insights/judgment-not-meaning",
                "youtube_thumbnail_source_url": "https://images.example.test/og.png",
            }), encoding="utf-8")
            with (
                patch("youtube_publish.upload_video") as upload,
                patch("youtube_publish.update_video_details", side_effect=RuntimeError("quota exceeded")),
            ):
                with self.assertRaisesRegex(RuntimeError, "quota exceeded"):
                    publish_episode(
                        MagicMock(), episode, {
                            "cover": "Podcast/Assets/cover.jpg",
                            "base_url": "https://example.test",
                        }, {}, root
                    )
            upload.assert_not_called()
            saved = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["youtube_video_id"], "recovered-video")
            self.assertEqual(saved["youtube_url"], "https://youtu.be/recovered-video")

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

    def test_english_only_update_does_not_retranslate_japanese(self):
        client = MagicMock()
        client.audio.transcriptions.create.return_value.segments = [
            {"start": 0.0, "end": 1.0, "text": "InSynergy."},
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "audio.mp3"
            english = root / "captions.en.srt"
            audio.write_bytes(b"audio")
            create_synced_caption_files(client, audio, english)
            self.assertIn("Insynergy.", english.read_text(encoding="utf-8"))
        client.responses.create.assert_not_called()

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
        self.assertEqual(CAPTION_TIMING_VERSION, "audio-transcription-v1")
        self.assertEqual(ENGLISH_CAPTION_TEXT_VERSION, "insynergy-normalization-v1")

    def test_fresh_caption_metadata_needs_no_youtube_lookup(self):
        self.assertTrue(captions_are_fresh({
            "youtube_caption_timing": CAPTION_TIMING_VERSION,
            "youtube_english_caption_text_version": ENGLISH_CAPTION_TEXT_VERSION,
            "youtube_caption_id": "en-id",
            "youtube_japanese_caption_id": "ja-id",
        }))
        self.assertFalse(captions_are_fresh({
            "youtube_caption_timing": CAPTION_TIMING_VERSION,
            "youtube_caption_id": "en-id",
            "youtube_japanese_caption_id": "ja-id",
        }))

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
