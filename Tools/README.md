# Obsidian Insight → Podcast

英語のObsidian Insight記事から、OpenAI Responses APIで英語の一人語り原稿を作成し、Speech APIでMP3を生成するCLIです。

## 新規チャットからの一気通貫公開

このプロジェクトを開いた新規Codexチャットでは、次の定型文だけで記事登録、Podcast生成、RSS配信、YouTube公開、英語字幕、PRマージ、公開確認まで実行します。詳細な実行規約はリポジトリ直下の `AGENTS.md` にあります。

```text
DD-004として、次のMarkdown記事からPodcastを作成し、RSS配信とYouTube公開（英語字幕を含む）まで一気通貫で実行してください。
'/absolute/path/to/article.md'
```

既定値は10分、`academic` voice style、即時公開です。時間や話し方を変える場合だけ、定型文に「8分・executive」のように追記してください。

## 1. 必要環境

- Python 3.12以上
- OpenAI APIキー（API利用には課金が発生します）
- 長い原稿を複数MP3へ分割する場合は `ffmpeg`
- Windows PowerShellまたはmacOS/Linuxのシェル

2026年7月11日にOpenAI公式ドキュメントを確認した実装です。公式Python SDKは確認時点の最新系列 `openai 2.38.0` 以上（破壊的変更を避けるため3.0未満）を使用します。テキスト生成にはResponses APIの `client.responses.create(...)` と `response.output_text`、音声生成には `client.audio.speech.with_streaming_response.create(...)` を使用します。既定値は `gpt-5.4-mini`、`tts-1-hd`、`nova` です。現時点でSpeech endpointに掲載され、非推奨扱いでないモデルは `tts-1` と `tts-1-hd`、対応音声は `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` です。`gpt-5.4-mini` のコンテキスト上限は400,000トークンです。Speech APIの入力上限4,096文字に対し、本ツールは安全幅を取り3,800文字以下に分割します。

公式資料: [Models](https://developers.openai.com/api/docs/models)、[TTS-1](https://developers.openai.com/api/docs/models/tts-1)、[All models](https://developers.openai.com/api/docs/models/all)、[公式Python SDK](https://github.com/openai/openai-python/releases)

## 2. インストール

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r Tools/requirements.txt
brew install ffmpeg
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r Tools\requirements.txt
winget install Gyan.FFmpeg
```

`ffmpeg` は原稿が1リクエストに収まる場合は不要です。複数チャンクでは各MP3を一時ディレクトリに保存し、concat demuxerとストリームコピーで1つのMP3へ結合します。

## 3. `.env` の設定

`Tools/.env.example` を `Tools/.env` または作業ディレクトリの `.env` にコピーし、APIキーを設定します。

```env
OPENAI_API_KEY=sk-...
OBSIDIAN_VAULT_PATH=/Users/ryojimorii/Documents/書類 - MacBook Air 13" M4 2025/Obsidian Vault
INSIGHTS_DIRECTORY=40_Outputs/Insight
OPENAI_TEXT_MODEL=gpt-5.4-mini
OPENAI_TTS_MODEL=tts-1-hd
OPENAI_TTS_VOICE=nova
```

APIキーをソースコードやGitへ保存しないでください。VaultとInsightsのパスは分離されており、`INSIGHTS_DIRECTORY` はVaultからの相対パスです。

## 4. 基本コマンド

Vaultからの相対パス（空白・日本語・ダブルクォートを含むパスは全体をシングルクォートで囲む）:

```bash
python Tools/generate_podcast.py '40_Outputs/Insight/記事ファイル名.md'
```

記事ファイル名だけでも `INSIGHTS_DIRECTORY` 内を検索します。

```bash
python Tools/generate_podcast.py '記事ファイル名.md'
```

絶対パス:

```bash
python Tools/generate_podcast.py '/Users/ryojimorii/Documents/書類 - MacBook Air 13" M4 2025/Obsidian Vault/40_Outputs/Insight/記事ファイル名.md'
```

PowerShell:

```powershell
python Tools\generate_podcast.py '40_Outputs/Insight/記事ファイル名.md'
```

## 5. オプション

```text
--duration MINUTES  想定時間（既定8分、1以上）
--voice VOICE       TTS音声を上書き
--overwrite         既存の対象成果物を置換
--script-only       原稿とメタデータだけを生成
--audio-only        既存の原稿から音声とメタデータを生成
--dry-run           API呼び出しも書き込みもせず計画を表示
```

`--script-only` と `--audio-only` は同時指定できません。例:

```bash
python Tools/generate_podcast.py '40_Outputs/Insight/記事ファイル名.md' --duration 8 --voice 'nova' --overwrite
```

## 6. 出力先

入力が `40_Outputs/Insight/example-insight.md` の場合:

```text
Podcast/Scripts/example-insight-podcast.md
Podcast/Audio/example-insight.mp3
Podcast/Metadata/example-insight.json
```

フロントマターに `slug` があれば、安全なファイル名に正規化して使用します。同名ファイルがある場合は既定で停止し、`--overwrite` 指定時だけ置換します。原稿検証に失敗した場合、原稿は診断用に残し、音声は生成しません。

## 7. 課金とAPI制限

通常実行はResponses APIとSpeech APIを呼び出すため、OpenAIアカウントに課金されます。`--dry-run` と単体テストはAPIを呼びません。レート制限、利用枠、認証、ネットワーク障害が起きると処理は非0で終了し、失敗した処理とAPIエラーを表示します。自動リトライはSDK標準挙動の範囲に限定し、二重課金を避けるためCLI独自の無制限リトライは行いません。

## 8. 長文分割と結合

原稿を文末境界、次に空白境界で最大3,800文字へ分割します。各チャンクをMP3化し、1個ならそのまま保存、複数なら `ffmpeg` でロスレス結合します。一時チャンクは正常終了・異常終了のどちらでも削除されます。TTSレスポンスや生成ファイルが空なら異常終了します。

## 9. エラーと対処

- `OPENAI_API_KEY is not set`: `.env` のキーと実行ディレクトリを確認します。
- `Input ... was not found`: Vault設定と引用符、相対パスを確認します。
- `Refusing to overwrite`: 別名にするか、意図的な場合だけ `--overwrite` を付けます。
- `Script validation failed`: 残された原稿を確認します。URL追加、長さ、Markdown、Decision Design定義が原因として表示されます。
- `ffmpeg is required`: 上記の方法で導入し、`ffmpeg -version` が通ることを確認します。
- `429` / rate limit: 利用枠とレート制限を確認し、時間を空けて再実行します。原稿作成済みなら `--audio-only` を利用できます。
- モデルまたは音声エラー: アカウントのモデルアクセスと `.env` の値を確認します。

## 10. テスト

外部APIを呼ばない標準ライブラリのテストです。

```bash
python -m unittest discover -s tests -v
```

実API呼び出しは単体テスト対象外です。本番前に `--dry-run` でパスを確認してください。

## 11. GitHub Actions

`.github/workflows/publish-podcast.yml` は、`main`への対象ファイルのpushまたはActions画面から実行できます。

1. 対象記事をリポジトリの `Insights/` に置きます。
2. `Podcast/Episodes/<ID>/episode.yml` を追加し、`podcast: true`、`status: published`を設定します。
3. Repository settingsの **Secrets and variables → Actions** にSecret `OPENAI_API_KEY`とVariable `PODCAST_EMAIL`を登録します。
4. `main`へpushするか、**Actions → Publish podcast → Run workflow** を開きます。
5. 完了後、Pagesで公開され、Workflow runの **Artifacts** からも取得できます。

RunnerからローカルのObsidian Vaultは参照できません。APIキーや `.env` はコミットせず、生成物は既定で30日保持されるArtifactとして受け取ります。

## 12. Podcast Publishing Platform

公開設定は `Podcast/podcast.yml`、各Episodeの唯一の編集元は `Podcast/Episodes/<ID>/episode.yml` です。`DD-001`形式のIDは変更不可のRSS GUIDおよびID3タグとして使われます。

```text
Insight push
  → podcast: true / status: published を検証
  → 変更された原文だけを生成
  → Voice Style適用
  → intro + 本編 + outro（素材がある場合）
  → ID3タグ・カバー埋め込み
  → RSS・番組ページ生成
  → Artifact保存
  → GitHub Pages公開
```

`voice_style` は `executive`, `academic`, `keynote` から選び、`Podcast/podcast.yml` で原稿方向とTTS音声を管理します。`intro.mp3`と`outro.mp3`は任意です。

GitHub Actionsには次を設定します。

- Repository Secret `OPENAI_API_KEY`
- Repository Variable `PODCAST_EMAIL`（RSSに公開される専用連絡先）
- Settings → Pages → Source: **GitHub Actions**

公開URL:

- Website: `https://insynergy-jp.github.io/Insynergy-Podcast/`
- RSS: `https://insynergy-jp.github.io/Insynergy-Podcast/podcast.xml`

ローカル検証（API生成済みファイルが必要）:

```bash
python Tools/run_pipeline.py
xmllint --noout Podcast/Public/podcast.xml
```

原文SHA-256が前回のメタデータと一致するEpisodeは再生成しないため、不要なAPI課金を防止します。全件を意図的に再生成する場合のみActionsの `force_regeneration` を有効にします。

## 13. YouTube Publishing

Podcast生成後、`Tools/youtube_publish.py` はMP3と番組カバーから1920×1080のMP4を作成し、YouTube Data API v3へアップロードします。`Podcast/podcast.yml` の `youtube.enabled` が有効で、次のGitHub Actions Secretsがすべて設定されている場合だけ実行されます。未設定時はPodcastとPagesの公開を妨げず、安全にスキップします。

### 配信方針（固定）

- Apple Podcasts: RSS配信
- Spotify: RSS配信
- Amazon Music / Audible: RSS配信
- YouTube / YouTube Music: YouTube Data APIによる直接公開

YouTubeのRSS ingestionは使用しません。`Podcast/podcast.yml` の `youtube.delivery: direct_api` と `youtube.rss_ingestion: false` がこの運用方針の編集元です。YouTube StudioへRSSを接続すると同じエピソードが重複するため、RSSフィードは登録しないでください。YouTubeでは、直接公開した動画をPodcast再生リストへ追加してPodcastとして管理します。

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

初期値は `public`（公開）です。Repository Variable `YOUTUBE_PRIVACY_STATUS` を `private` または `unlisted` に変更すれば、確認後の手動公開運用にも切り替えられます。未監査の外部向けAPIプロジェクトでは、APIからアップロードした動画が非公開に制限される場合があります。

YouTube動画の静止画とカスタムサムネイルには、対応する
`https://insynergy.io/insights/<slug>` ページの `og:image` を使用します。取得した画像は
1280×720のJPEGへ変換し、YouTubeの2MB制限以内になるまで圧縮します。Insight側のslugが
Podcastのslugと異なる場合は、`Podcast/podcast.yml` の
`youtube.insight_urls` にPodcast slugと正しい記事URLの対応を追加してください。記事ページまたは
OG画像を取得できない場合は、公開処理を止めずに従来のPodcastカバーへフォールバックします。
既存動画も、メタデータに `youtube_thumbnail_version` がない場合は動画を再アップロードせず、
カスタムサムネイルだけを更新します。

各動画には、最終MP3を `whisper-1` で文字起こしして得た発話区間タイムスタンプから英語SRTを作成します。原稿の文字数を音声全体へ均等配分しないため、発話速度やポーズに字幕表示が追従します。文字起こし時の大文字化にかかわらず、ブランド名は常に `Insynergy` へ正規化します。さらに各英語区間を小分けにして同じ区間境界のまま日本語へ翻訳し、英語・日本語の2トラックを自動登録します。既存の英語字幕は更新し、日本語字幕だけを追加するため、動画や字幕トラックを重複作成しません。処理再開時にはYouTube上の既存トラックも照合します。動画と字幕のIDは `Podcast/Metadata/*.json` に保存されます。字幕登録には `youtube.force-ssl` OAuth scopeが必要です。字幕対応前に作成したrefresh tokenは、`Tools/youtube_auth.py` を再実行して更新してください。

字幕文字起こしモデルは `whisper-1`、日本語翻訳モデルは既定で `gpt-5.4-mini` です。翻訳モデルだけを変更する場合はRepository Variableまたは環境変数 `OPENAI_CAPTION_TRANSLATION_MODEL` を設定します。

### 初回OAuth設定

1. Google Cloudでプロジェクトを作成し、YouTube Data API v3を有効化します。
2. OAuth同意画面を設定し、「デスクトップアプリ」のOAuthクライアントJSONをダウンロードします。
3. ローカルで次を実行し、ブラウザで対象YouTubeチャンネルを承認します。

```bash
python Tools/youtube_auth.py '/path/to/client_secret.json'
```

4. 表示された3つの値をGitHub Actions Secretsへ保存します。クライアントJSONとトークンはGitへコミットしないでください。

ローカル実行:

```bash
python Tools/youtube_publish.py
python Tools/youtube_publish.py --episode DD-003
```

アップロード済み動画のIDとURLは各 `Podcast/Metadata/*.json` に保存され、同じエピソードの重複アップロードを防止します。生成MP4は `Podcast/YouTube/` に一時配置され、Gitでは追跡しません。
