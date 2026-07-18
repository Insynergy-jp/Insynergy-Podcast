# Insynergy Podcast Agent Instructions

## One-command episode publishing

When the user gives an episode ID and an absolute Markdown article path and explicitly asks to publish the podcast end to end, treat that request as authorization to complete this repository's normal publishing workflow:

1. Read the source article and confirm the requested `DD-NNN` ID is unused.
2. Copy the article into `Insights/` without changing its essay body. Add a top-level URL-safe `slug` only when needed by the generator.
3. Create `Podcast/Episodes/DD-NNN/episode.yml` using the requested ID and matching episode number.
4. Derive the English title, slug, and description from the article. Unless the user specifies otherwise, use:
   - `duration_minutes: 10`
   - `voice_style: academic`
   - `status: published`
   - `podcast: true`
   - `episode_type: full`
   - a publication timestamp in Asia/Tokyo
5. Run the dry run, all unit tests, and `git diff --check`.
6. Create a `codex/` branch, stage only the source article and episode manifest, commit, push, and open a PR.
7. Merge the PR into `main` after validation. Do not stop at PR creation when the user explicitly requested end-to-end publishing.
8. Monitor the `Publish podcast` GitHub Actions workflow through completion.
9. Verify all durable outputs on `origin/main`:
   - `Podcast/Scripts/<slug>-podcast.md`
   - `Podcast/Audio/<slug>.mp3`
   - `Podcast/Metadata/<slug>.json`
   - RSS entry in `Podcast/Public/podcast.xml`
   - GitHub Pages episode entry
   - `youtube_video_id` and `youtube_url`
   - `youtube_caption_id` and `youtube_caption_language: en`
   - `youtube_thumbnail_source_url`, `youtube_thumbnail_insight_url`, and
     `youtube_thumbnail_version: insynergy-insight-og-v1`
10. Report the public podcast site, RSS feed, YouTube URL, workflow run, and validation results.

## Fixed distribution policy

- Apple Podcasts: RSS
- Spotify: RSS
- Amazon Music / Audible: RSS
- YouTube / YouTube Music: direct YouTube Data API upload
- YouTube RSS ingestion: disabled; never connect or submit the podcast RSS feed to YouTube
- YouTube visibility: public from initial upload
- YouTube captions: automatically upload the English SRT generated from the final narration
- YouTube thumbnails: use the source Insight page's `og:image`, converted to a
  YouTube-safe 1280×720 JPEG; fall back to the podcast cover only when no Insight OG image is available

## Safety and consistency

- Preserve unrelated user changes and never use `git add -A` in a mixed worktree.
- Never print API keys, OAuth client secrets, or refresh tokens.
- Do not regenerate fresh episodes unless the source hash changed or the user explicitly requests force regeneration.
- Do not create duplicate YouTube videos or caption tracks; trust the IDs recorded in episode metadata.
- If credentials or required repository variables are missing, configure only what is necessary and request user action only when interactive authorization is unavoidable.
- A request that says only “create” or “draft” does not authorize GitHub merge or external publication. The standard prompt below explicitly does.

## Standard user prompt

The intended minimal request is:

```text
DD-NNNとして、次のMarkdown記事からPodcastを作成し、RSS配信とYouTube公開（英語字幕を含む）まで一気通貫で実行してください。
'<absolute-path-to-article.md>'
```
