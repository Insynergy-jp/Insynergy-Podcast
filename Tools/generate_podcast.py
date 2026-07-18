#!/usr/bin/env python3
"""Generate an English podcast script and MP3 from an Obsidian Markdown note."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

try:
    from dotenv import load_dotenv
except ImportError:  # Keep --dry-run and pure helper tests usable before installation.
    def load_dotenv() -> bool:
        return False


DECISION_DESIGN_DEFINITION = (
    "Decision Design is a judgment architecture framework proposed by Ryoji Morii, "
    "founder of Insynergy Inc., for structuring authority, accountability, and "
    "decision boundaries in AI-augmented organizations."
)
DEFAULT_VAULT = '/Users/ryojimorii/Documents/書類 - MacBook Air 13" M4 2025/Obsidian Vault'
DEFAULT_INSIGHTS = "40_Outputs/Insight"
DEFAULT_TEXT_MODEL = "gpt-5.4-mini"
DEFAULT_TTS_MODEL = "tts-1-hd"
DEFAULT_VOICE = "nova"
TTS_MAX_CHARS = 3800  # Below the Speech API's 4096-character input limit.
VALID_TTS_MODELS = {"tts-1", "tts-1-hd"}
VALID_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}


class PodcastError(RuntimeError):
    """An expected, user-actionable failure."""


class ResponsesClient(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class Config:
    vault_path: Path
    insights_directory: Path
    text_model: str
    tts_model: str
    voice: str


@dataclass(frozen=True)
class OutputPaths:
    script: Path
    audio: Path
    metadata: Path


def load_config(env: Mapping[str, str] | None = None) -> Config:
    load_dotenv()
    values = os.environ if env is None else env
    vault = Path(values.get("OBSIDIAN_VAULT_PATH", DEFAULT_VAULT)).expanduser().resolve()
    insights = Path(values.get("INSIGHTS_DIRECTORY", DEFAULT_INSIGHTS))
    if insights.is_absolute():
        raise PodcastError("INSIGHTS_DIRECTORY must be relative to OBSIDIAN_VAULT_PATH.")
    return Config(
        vault_path=vault,
        insights_directory=insights,
        text_model=values.get("OPENAI_TEXT_MODEL", DEFAULT_TEXT_MODEL),
        tts_model=values.get("OPENAI_TTS_MODEL", DEFAULT_TTS_MODEL),
        voice=values.get("OPENAI_TTS_VOICE", DEFAULT_VOICE),
    )


def resolve_input_path(argument: str, config: Config) -> Path:
    supplied = Path(argument).expanduser()
    candidates = [supplied] if supplied.is_absolute() else [config.vault_path / supplied]
    if not supplied.is_absolute() and len(supplied.parts) == 1:
        candidates.append(config.vault_path / config.insights_directory / supplied)
    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(config.vault_path)
        except ValueError as exc:
            raise PodcastError(f"Input must be inside the configured vault: {resolved}") from exc
        if resolved.is_file():
            if resolved.suffix.lower() != ".md":
                raise PodcastError(f"Input is not a Markdown file: {resolved}")
            return resolved
    raise PodcastError("Input Markdown file was not found. Checked: " + ", ".join(map(str, candidates)))


def read_markdown(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PodcastError(f"Input is not valid UTF-8: {path}") from exc
    except OSError as exc:
        raise PodcastError(f"Could not read input file {path}: {exc}") from exc


def parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    if not markdown.startswith("---"):
        return {}, markdown
    match = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", markdown, re.DOTALL)
    if not match:
        return {}, markdown
    metadata: dict[str, Any] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line or raw_line.lstrip().startswith("#"):
            continue
        key, value = raw_line.split(":", 1)
        key, value = key.strip(), value.strip().strip('"\'')
        if key:
            if value.startswith("[") and value.endswith("]"):
                metadata[key] = [v.strip().strip('"\'') for v in value[1:-1].split(",") if v.strip()]
            else:
                metadata[key] = value
    return metadata, markdown[match.end():]


def clean_markdown(markdown: str) -> str:
    """Remove non-narrative Markdown while preserving claims and attribution."""
    _, body = parse_frontmatter(markdown)
    body = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.DOTALL)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"\[\[([^]|]+)(?:\|([^]]+))?\]\]", lambda m: m.group(2) or m.group(1), body)
    body = re.sub(r"(?m)^\s*\[\^[^]]+\]:.*$", "", body)
    body = re.sub(r"\[\^[^]]+\]", "", body)
    body = re.split(r"(?im)^#{0,6}\s*(references|bibliography|sources|footnotes)\s*$", body)[0]
    body = re.sub(r"(?m)^\s*(?:[-*+]\s+)?https?://\S+\s*$", "", body)
    body = re.sub(r"https?://\S+", "", body)
    body = re.sub(r"(?m)^\s*(?:published|updated|author|slug|tags|date)\s*:.*$", "", body, flags=re.I)
    body = re.sub(r"(?m)^[ \t]{0,3}#{1,6}[ \t]*", "", body)
    body = re.sub(r"(?m)^[ \t]*>[ \t]?", "", body)
    body = re.sub(r"(?m)^[ \t]*(?:[-*+][ \t]+|\d+[.)][ \t]+)", "", body)
    body = re.sub(r"[*_~`]+", "", body)
    body = html.unescape(body)
    paragraphs = []
    seen = set()
    for paragraph in re.split(r"\n\s*\n", body):
        normalized = re.sub(r"\s+", " ", paragraph).strip()
        key = normalized.casefold()
        if normalized and key not in seen:
            seen.add(key)
            paragraphs.append(normalized)
    return "\n\n".join(paragraphs)


def build_prompt(source_text: str, metadata: Mapping[str, Any], duration: int, style: str = "executive") -> str:
    target_words = duration * 140
    return f"""Create a ready-to-read English podcast narration from the source below.

Audience: executives, CIOs, AI governance leaders, and researchers.
Format: one host, natural spoken prose only; no headings or bullet lists.
Tone: calm, intellectually rigorous, and restrained.
Voice style: {style}. Executive means concise, composed, authoritative, and practical;
academic means analytical, precise, measured, and conceptually rigorous; keynote means
clear, resonant, forward-looking, and restrained. Apply the selected style without theatricality.
Length: about {target_words} words for approximately {duration} minutes.
Open by stating the central question. Near the end, concisely synthesize practical implications.
End by naturally connecting Insynergy with Decision Design.
Do not say “In this article” or “Welcome back.” Do not invent facts, statistics, quotations,
or attributions. Preserve the source's claims, nuance, proper nouns, numbers, and attribution.
If Decision Design must be defined, reproduce this sentence exactly and do not paraphrase it:
“{DECISION_DESIGN_DEFINITION}”

Source title: {metadata.get('title', '')}
Source content:
{source_text}
"""


def build_condense_prompt(script: str, metadata: Mapping[str, Any], duration: int, style: str = "executive") -> str:
    target_words = duration * 140
    minimum_words = round(target_words * 0.9)
    maximum_words = round(target_words * 1.1)
    return f"""Condense the English podcast narration below to fit its intended duration.

Source title: {metadata.get('title', '')}
Voice style: {style}.
Target length: {target_words} words for approximately {duration} minutes.
Required range: {minimum_words} to {maximum_words} words. Do not exceed {maximum_words} words.
Return only the revised ready-to-read narration, with no headings, bullets, notes, or commentary.
Preserve the central argument, factual claims, numbers, proper nouns, attribution, nuance,
and the closing connection between Insynergy and Decision Design. Do not add facts, URLs,
statistics, quotations, or attributions. Condense repetition and secondary examples first.

Narration to condense:
{script}
"""


def should_retry_overlong(errors: Sequence[str]) -> bool:
    return any(error.startswith("Script is too long") for error in errors)


def generate_script(client: Any, model: str, prompt: str, *, max_output_tokens: int | None = None) -> str:
    request: dict[str, Any] = {"model": model, "input": prompt}
    if max_output_tokens is not None:
        request["max_output_tokens"] = max_output_tokens
    try:
        response = client.responses.create(**request)
    except Exception as exc:
        raise PodcastError(f"OpenAI Responses API failed: {exc}") from exc
    text = getattr(response, "output_text", None)
    if not isinstance(text, str) or not text.strip():
        raise PodcastError("OpenAI Responses API returned an empty script.")
    return text.strip()


def validate_script(script: str, source: str, duration: int) -> list[str]:
    errors: list[str] = []
    if not script.strip():
        return ["The generated script is empty."]
    source_urls = set(re.findall(r"https?://[^\s)>]+", source))
    added_urls = set(re.findall(r"https?://[^\s)>]+", script)) - source_urls
    if added_urls:
        errors.append("The script added URL(s) absent from the source: " + ", ".join(sorted(added_urls)))
    if "Decision Design is a " in script and DECISION_DESIGN_DEFINITION not in script:
        errors.append("The required Decision Design definition was changed or incomplete.")
    markdown_marks = len(re.findall(r"(?m)^\s*(?:#{1,6}|[-*+]\s|\d+[.)]\s)|[*_`]{2,}", script))
    if markdown_marks > 3:
        errors.append("Too many Markdown/list markers remain in the narration.")
    words = len(re.findall(r"\b[\w’'-]+\b", script, flags=re.UNICODE))
    target = duration * 140
    if words < target * 0.65:
        errors.append(f"Script is too short ({words} words; expected roughly {target}).")
    elif words > target * 1.4:
        errors.append(f"Script is too long ({words} words; expected roughly {target}).")
    return errors


def split_tts_text(text: str, max_chars: int = TTS_MAX_CHARS) -> list[str]:
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise PodcastError("Cannot synthesize empty text.")
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        pieces: list[str] = []
        while len(sentence) > max_chars:
            split_at = sentence.rfind(" ", 0, max_chars + 1)
            if split_at <= 0:
                split_at = max_chars
            pieces.append(sentence[:split_at].strip())
            sentence = sentence[split_at:].strip()
        if sentence:
            pieces.append(sentence)
        for piece in pieces:
            candidate = f"{current} {piece}".strip()
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = piece
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks


def generate_audio_chunks(client: Any, chunks: Sequence[str], model: str, voice: str, directory: Path) -> list[Path]:
    paths: list[Path] = []
    for index, chunk in enumerate(chunks, start=1):
        path = directory / f"chunk-{index:04d}.mp3"
        try:
            with client.audio.speech.with_streaming_response.create(
                model=model, voice=voice, input=chunk, response_format="mp3"
            ) as response:
                response.stream_to_file(path)
        except Exception as exc:
            raise PodcastError(f"OpenAI Text-to-Speech failed on chunk {index}/{len(chunks)}: {exc}") from exc
        if not path.is_file() or path.stat().st_size == 0:
            raise PodcastError(f"Text-to-Speech returned empty audio for chunk {index}.")
        paths.append(path)
    return paths


def combine_audio(parts: Sequence[Path], destination: Path) -> None:
    if not parts:
        raise PodcastError("No audio chunks were generated.")
    if len(parts) == 1:
        shutil.copyfile(parts[0], destination)
        return
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise PodcastError("ffmpeg is required to combine multiple audio chunks; see Tools/README.md.")
    list_file = parts[0].parent / "concat.txt"
    lines = ["file '" + str(part).replace("'", "'\\''") + "'" for part in parts]
    list_file.write_text("\n".join(lines), encoding="utf-8")
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(destination)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode != 0 or not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise PodcastError(f"ffmpeg could not combine audio: {result.stderr.strip() or 'unknown error'}")


def output_paths(source: Path, vault: Path, slug: str | None = None) -> OutputPaths:
    stem = str(slug or source.stem).strip() or source.stem
    stem = re.sub(r"[\\/:*?\"<>|]", "-", stem).strip(". ") or source.stem
    return OutputPaths(
        script=vault / "Podcast" / "Scripts" / f"{stem}-podcast.md",
        audio=vault / "Podcast" / "Audio" / f"{stem}.mp3",
        metadata=vault / "Podcast" / "Metadata" / f"{stem}.json",
    )


def yaml_quote(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def script_document(script: str, *, title: str, source: str, duration: int, generated_at: str, config: Config, voice: str) -> str:
    fields = {
        "title": title,
        "source": source,
        "type": "podcast_script",
        "language": "en",
        "estimated_duration_minutes": duration,
        "generated_at": generated_at,
        "text_model": config.text_model,
        "tts_model": config.tts_model,
        "voice": voice,
    }
    frontmatter = "\n".join(f"{key}: {value if isinstance(value, int) else yaml_quote(value)}" for key, value in fields.items())
    return f"---\n{frontmatter}\n---\n\n{script.strip()}\n"


def narration_from_script_document(document: str) -> str:
    _, body = parse_frontmatter(document)
    return body.strip()


def build_metadata(*, title: str, source: Path, paths: OutputPaths, vault: Path, script: str, duration: int, generated_at: str, config: Config, voice: str, audio_created: bool) -> dict[str, Any]:
    relative = lambda path: path.relative_to(vault).as_posix()
    return {
        "title": title,
        "source_file": relative(source),
        "script_file": relative(paths.script),
        "audio_file": relative(paths.audio) if audio_created else "",
        "language": "en",
        "estimated_duration_minutes": duration,
        "character_count": len(script),
        "word_count": len(re.findall(r"\b[\w’'-]+\b", script, flags=re.UNICODE)),
        "generated_at": generated_at,
        "text_model": config.text_model,
        "tts_model": config.tts_model,
        "voice": voice,
    }


def ensure_writable(paths: Sequence[Path], overwrite: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        raise PodcastError("Refusing to overwrite existing file(s): " + ", ".join(map(str, existing)) + ". Use --overwrite to replace them.")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def create_openai_client() -> Any:
    if not os.getenv("OPENAI_API_KEY"):
        raise PodcastError("OPENAI_API_KEY is not set. Add it to Tools/.env or the environment.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise PodcastError("The openai package is not installed. Run: pip install -r Tools/requirements.txt") from exc
    return OpenAI()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("input", help="Markdown path, relative to the vault or absolute within it")
    result.add_argument("--duration", type=int, default=8, help="Estimated duration in minutes (default: 8)")
    result.add_argument("--voice", help="TTS voice")
    result.add_argument("--style", choices=("executive", "academic", "keynote"), default="executive", help="Narration style profile")
    result.add_argument("--overwrite", action="store_true", help="Allow replacement of existing outputs")
    modes = result.add_mutually_exclusive_group()
    modes.add_argument("--script-only", action="store_true", help="Generate script and metadata only")
    modes.add_argument("--audio-only", action="store_true", help="Synthesize audio from the existing script")
    result.add_argument("--dry-run", action="store_true", help="Print planned operations without API calls or writes")
    return result


def run(args: argparse.Namespace) -> None:
    if args.duration < 1:
        raise PodcastError("--duration must be at least 1 minute.")
    config = load_config()
    voice = args.voice or config.voice
    if config.tts_model not in VALID_TTS_MODELS:
        raise PodcastError(f"Unsupported/non-current TTS model: {config.tts_model}. Choose one of: {', '.join(sorted(VALID_TTS_MODELS))}")
    if voice not in VALID_VOICES:
        raise PodcastError(f"Unsupported voice: {voice}. Choose one of: {', '.join(sorted(VALID_VOICES))}")
    source = resolve_input_path(args.input, config)
    raw = read_markdown(source)
    source_metadata, _ = parse_frontmatter(raw)
    paths = output_paths(source, config.vault_path, source_metadata.get("slug"))
    title = str(source_metadata.get("title") or source.stem)
    source_relative = source.relative_to(config.vault_path).as_posix()
    planned = ["read existing script and generate audio"] if args.audio_only else ["generate and validate podcast script"]
    if not args.script_only:
        planned.append("generate MP3 audio (splitting and combining when needed)")
    planned.append("write metadata JSON")
    if args.dry_run:
        print("DRY RUN — no API calls or files will be written")
        print(f"Input:    {source}")
        print(f"Script:   {paths.script}")
        print(f"Audio:    {paths.audio}")
        print(f"Metadata: {paths.metadata}")
        print("Plan:     " + "; ".join(planned))
        return

    targets = [paths.metadata, paths.audio] if args.audio_only else [paths.script, paths.metadata] + ([] if args.script_only else [paths.audio])
    ensure_writable(targets, args.overwrite)
    generated_at = datetime.now(timezone.utc).isoformat()
    client = create_openai_client()
    if args.audio_only:
        if not paths.script.is_file():
            raise PodcastError(f"Existing podcast script not found: {paths.script}")
        script = narration_from_script_document(read_markdown(paths.script))
    else:
        cleaned = clean_markdown(raw)
        if not cleaned:
            raise PodcastError("No narratable content remained after Markdown cleaning.")
        script = generate_script(client, config.text_model, build_prompt(cleaned, source_metadata, args.duration, args.style))
        atomic_write_text(paths.script, script_document(script, title=title, source=source_relative, duration=args.duration, generated_at=generated_at, config=config, voice=voice))

    errors = validate_script(script, raw, args.duration)
    if not args.audio_only and should_retry_overlong(errors):
        script = generate_script(
            client,
            config.text_model,
            build_condense_prompt(script, source_metadata, args.duration, args.style),
            max_output_tokens=max(1024, args.duration * 210),
        )
        atomic_write_text(
            paths.script,
            script_document(
                script,
                title=title,
                source=source_relative,
                duration=args.duration,
                generated_at=generated_at,
                config=config,
                voice=voice,
            ),
        )
        errors = validate_script(script, raw, args.duration)
    if errors:
        raise PodcastError("Script validation failed; audio was not generated. " + " ".join(errors))

    audio_created = False
    if not args.script_only:
        paths.audio.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="podcast-audio-") as directory:
            parts = generate_audio_chunks(client, split_tts_text(script), config.tts_model, voice, Path(directory))
            temporary_audio = paths.audio.with_name(paths.audio.stem + ".tmp.mp3")
            combine_audio(parts, temporary_audio)
            temporary_audio.replace(paths.audio)
        audio_created = True
    metadata = build_metadata(title=title, source=source, paths=paths, vault=config.vault_path, script=script, duration=args.duration, generated_at=generated_at, config=config, voice=voice, audio_created=audio_created)
    atomic_write_text(paths.metadata, json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    print(f"Script: {paths.script}")
    if audio_created:
        print(f"Audio: {paths.audio}")
    print(f"Metadata: {paths.metadata}")


def main() -> int:
    try:
        run(parser().parse_args())
        return 0
    except PodcastError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
