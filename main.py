#!/usr/bin/env python3
"""
main.py – Orchestrates the end‑to‑end pipeline:

  1. Scrape Fort Collins video‑archive for the past <months> months.
  2. Download all MP4s (unless --skip-download).
  3. Extract audio, transcribe with Groq’s Distil‑Whisper, and (optionally) tag
     speakers with a Groq chat‑completion call.
  4. Emit one Markdown file per meeting, ready for RAG ingestion.

Example:
    python main.py --months 24           # two‑year backlog
    python main.py --months 6 --skip-download --skip-transcribe
"""

import argparse
import json
import pathlib
from config import VIDEO_DIR, OUTPUT_DIR
import config
import scrape_archive
import downloader
import transcribe_groq           # uses Distil‑Whisper + Groq chat tagging
import build_markdown


def _update_manifest_local_paths() -> pathlib.Path:
    """
    Add 'local_mp4' keys to each manifest entry so later stages know where
    the file lives on disk.
    """
    manifest_path = VIDEO_DIR / "manifest.json"
    data = json.loads(manifest_path.read_text())
    for entry in data:
        mp4_name = f'{entry["date"]}_{entry["title"].replace(" ", "_")}.mp4'
        entry["local_mp4"] = str(VIDEO_DIR / mp4_name)
    manifest_path.write_text(json.dumps(data, indent=2))
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Council‑tube → Markdown pipeline")
    parser.add_argument(
        "--months",
        type=int,
        default=config.MONTHS_BACK,
        help="How far back to fetch meetings (default from config.py).",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Assume MP4s already present; skip the download step.",
    )
    parser.add_argument(
        "--skip-transcribe",
        action="store_true",
        help="Skip Groq transcription (requires existing JSON with 'words').",
    )
    parser.add_argument(
        "--no-chat-tag",
        action="store_true",
        help="Disable Groq chat speaker‑labelling; leaves 'speaker = Unknown'.",
    )
    args = parser.parse_args()

    # ── 1. Adjust time window dynamically ────────────────────────────────────
    config.MONTHS_BACK = args.months

    # ── 2. Scrape archive & write manifest.json ──────────────────────────────
    print(">>> Scraping Fort Collins video archive …")
    scrape_archive.save_manifest()

    # ── 3. Download MP4s (optional) ──────────────────────────────────────────
    if not args.skip_download:
        print(">>> Downloading MP4 files …")
        downloader.run()
    else:
        print(">>> Skipping download step.")

    # ── 4. Patch manifest with local file paths ──────────────────────────────
    manifest_json = _update_manifest_local_paths()

    # ── 5. Transcribe + optional speaker tagging ─────────────────────────────
    if not args.skip_transcribe:
        print(">>> Transcribing audio with Groq Distil‑Whisper …")
        transcribe_groq.PROCESS_CHAT = not args.no_chat_tag
        transcribe_groq.process_all(manifest_json)
    else:
        print(">>> Skipping transcription step.")

    # ── 6. Build Markdown outputs ────────────────────────────────────────────
    print(">>> Building Markdown files …")
    build_markdown.run(manifest_json)

    print(f"✅  Done!  Markdown files are in “{OUTPUT_DIR}”.\n")


if __name__ == "__main__":
    main()
