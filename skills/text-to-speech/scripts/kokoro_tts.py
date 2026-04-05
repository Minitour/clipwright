#!/usr/bin/env python3
"""
Synthesize speech with Kokoro ([hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)) via the `kokoro` package.

Requires: uv with workspace deps (`kokoro`, `soundfile`). Output is 24 kHz WAV.

Examples:
  uv run python skills/text-to-speech/scripts/kokoro_tts.py --text "Hello." -o out.wav
  uv run python skills/text-to-speech/scripts/kokoro_tts.py --text-file script.txt -o out.wav --voice af_heart
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_text(args: argparse.Namespace) -> str:
    if args.text is not None and args.text_file is not None:
        print("Use either --text or --text-file, not both.", file=sys.stderr)
        sys.exit(2)
    if args.text is not None:
        return args.text
    if args.text_file is not None:
        return Path(args.text_file).read_text(encoding="utf-8")
    print("Provide --text or --text-file.", file=sys.stderr)
    sys.exit(2)


def _write_wav(path: Path, audio, sampling_rate: int) -> None:
    import numpy as np
    import soundfile as sf

    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    arr = np.asarray(audio, dtype=np.float32).squeeze()
    arr = np.clip(arr, -1.0, 1.0)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), arr, sampling_rate, subtype="PCM_16")


def _synthesize_chunks(pipeline, text: str, voice: str):
    """Yield audio tensors/chunks from Kokoro (may be multiple segments for long text)."""
    import numpy as np

    for _, _, audio in pipeline(text, voice=voice):
        t = audio.detach().cpu().numpy() if hasattr(audio, "detach") else np.asarray(audio)
        yield np.asarray(t, dtype=np.float32).flatten()


def main() -> None:
    parser = argparse.ArgumentParser(description="Kokoro-82M TTS to WAV (24 kHz).")
    parser.add_argument("--text", "-t", default=None, help="Input string.")
    parser.add_argument("--text-file", default=None, help="UTF-8 text file.")
    parser.add_argument("--output", "-o", default="kokoro_out.wav", help="Output .wav path.")
    parser.add_argument(
        "--repo-id",
        default="hexgrad/Kokoro-82M",
        help="Hugging Face repo id for Kokoro weights (default: hexgrad/Kokoro-82M).",
    )
    parser.add_argument(
        "--lang-code",
        default="a",
        help="KPipeline lang_code (default: a — American English). See Kokoro docs.",
    )
    parser.add_argument(
        "--voice",
        default="af_heart",
        help="Voice id (default: af_heart). See VOICES.md on the model card.",
    )
    args = parser.parse_args()
    text = _load_text(args).strip()
    if not text:
        print("Empty input text.", file=sys.stderr)
        sys.exit(2)

    from kokoro import KPipeline

    pipeline = KPipeline(lang_code=args.lang_code, repo_id=args.repo_id)
    parts = list(_synthesize_chunks(pipeline, text, args.voice))
    if not parts:
        print("No audio generated.", file=sys.stderr)
        sys.exit(1)
    import numpy as np

    full = np.concatenate(parts)
    out = Path(args.output)
    _write_wav(out, full, 24000)
    print(f"Wrote {out.resolve()} (24000 Hz, Kokoro)")


if __name__ == "__main__":
    main()
