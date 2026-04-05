#!/usr/bin/env python3
"""
Generate speech from text using a Hugging Face Transformers text-to-speech model.

Typical output is WAV (PCM). MP3 is supported if pydub and a system FFmpeg install are available.

Examples (from skills/text-to-speech/ with uv venv; see SKILL.md):
  uv run python hf_tts.py --model facebook/mms-tts-eng --text "Hello world" -o out.wav
  uv run python hf_tts.py --model facebook/mms-tts-eng --text-file script.txt -o out.wav --dtype float16 --device cuda:0
  uv run python hf_tts.py --model suno/bark --text "Hi there" -o out.wav --trust-remote-code --pipe-kwargs "{\"voice_preset\":\"v2/en_speaker_6\"}"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _parse_dtype(name: str):
    import torch

    mapping = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    if name not in mapping:
        raise argparse.ArgumentTypeError(f"dtype must be one of: {', '.join(mapping)}")
    return mapping[name]


def _resolve_device(name: str | None):
    import torch

    if name is None or name == "auto":
        return 0 if torch.cuda.is_available() else -1
    if name == "cpu":
        return -1
    return name


def _load_text(args: argparse.Namespace) -> str:
    if args.text is not None and args.text_file is not None:
        print("Use either --text or --text-file, not both.", file=sys.stderr)
        sys.exit(2)
    if args.text is not None:
        return args.text
    if args.text_file is not None:
        path = Path(args.text_file)
        return path.read_text(encoding="utf-8")
    print("Provide --text or --text-file.", file=sys.stderr)
    sys.exit(2)


def _to_numpy_audio(audio):
    import numpy as np

    if hasattr(audio, "cpu"):
        audio = audio.cpu().numpy()
    return np.asarray(audio).squeeze()


def _write_wav(path: Path, audio, sampling_rate: int) -> None:
    import numpy as np
    import soundfile as sf

    audio = np.asarray(audio, dtype=np.float32).squeeze()
    audio = np.clip(audio, -1.0, 1.0)
    sf.write(str(path), audio, sampling_rate, subtype="PCM_16")


def _write_mp3(path: Path, audio, sampling_rate: int) -> None:
    import tempfile

    from pydub import AudioSegment

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        _write_wav(tmp_path, audio, sampling_rate)
        seg = AudioSegment.from_wav(str(tmp_path))
        seg.export(str(path), format="mp3")
    finally:
        tmp_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthesize speech with a Hugging Face text-to-speech model (Transformers pipeline).",
    )
    parser.add_argument("--model", required=True, help="Hub model id (e.g. facebook/mms-tts-eng).")
    parser.add_argument("--text", "-t", default=None, help="Input text.")
    parser.add_argument("--text-file", default=None, help="Read input text from this UTF-8 file.")
    parser.add_argument(
        "--output",
        "-o",
        default="tts_output.wav",
        help="Output path. Extension .wav or .mp3 (default: %(default)s).",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help='Torch device: "auto", "cpu", "cuda", "cuda:0", etc. (default: auto).',
    )
    parser.add_argument(
        "--dtype",
        type=_parse_dtype,
        default="float32",
        help="Model dtype: float32, float16, or bfloat16 (default: float32).",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Pass trust_remote_code=True when loading (needed for some models, e.g. Bark).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed (sets transformers set_seed).",
    )
    parser.add_argument(
        "--forward-params",
        default=None,
        metavar="JSON",
        help='JSON object passed as forward_params to the pipeline call, e.g. \'{"speaker_embeddings": ...}\' '
        "(advanced; often needs a small Python wrapper for tensors).",
    )
    parser.add_argument(
        "--pipeline-kwargs",
        default=None,
        metavar="JSON",
        help="JSON object merged into pipeline(...) constructor (e.g. model_kwargs, torch_dtype).",
    )
    parser.add_argument(
        "--pipe-kwargs",
        default=None,
        metavar="JSON",
        help="JSON object merged into the pipeline __call__ (same call as forward_params in many cases; "
        "prefer --forward-params for pipe(text, forward_params=...)).",
    )

    args = parser.parse_args()
    text = _load_text(args)

    if args.seed is not None:
        from transformers import set_seed

        set_seed(args.seed)

    import torch
    from transformers import pipeline

    device = _resolve_device(args.device)
    pipeline_kwargs: dict = {
        "task": "text-to-speech",
        "model": args.model,
        "dtype": args.dtype,
    }
    if device != -1:
        pipeline_kwargs["device"] = device
    if args.trust_remote_code:
        pipeline_kwargs["trust_remote_code"] = True

    if args.pipeline_kwargs:
        extra = json.loads(args.pipeline_kwargs)
        if not isinstance(extra, dict):
            print("--pipeline-kwargs must be a JSON object.", file=sys.stderr)
            sys.exit(2)
        pipeline_kwargs.update(extra)

    pipe = pipeline(**pipeline_kwargs)

    forward_params = None
    if args.forward_params:
        forward_params = json.loads(args.forward_params)
        if forward_params is not None and not isinstance(forward_params, dict):
            print("--forward-params must be a JSON object.", file=sys.stderr)
            sys.exit(2)

    pipe_call_kwargs: dict = {}
    if args.pipe_kwargs:
        pipe_call_kwargs = json.loads(args.pipe_kwargs)
        if not isinstance(pipe_call_kwargs, dict):
            print("--pipe-kwargs must be a JSON object.", file=sys.stderr)
            sys.exit(2)

    if forward_params is not None:
        speech = pipe(text, forward_params=forward_params, **pipe_call_kwargs)
    else:
        speech = pipe(text, **pipe_call_kwargs)

    if not isinstance(speech, dict) or "audio" not in speech or "sampling_rate" not in speech:
        print(
            "Unexpected pipeline output; expected dict with 'audio' and 'sampling_rate'. "
            f"Got: {type(speech).__name__}",
            file=sys.stderr,
        )
        sys.exit(1)

    audio = _to_numpy_audio(speech["audio"])
    sr = int(speech["sampling_rate"])
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    suffix = out.suffix.lower()
    if suffix == ".wav":
        _write_wav(out, audio, sr)
    elif suffix == ".mp3":
        try:
            _write_mp3(out, audio, sr)
        except ImportError as e:
            print(
                "MP3 export requires pydub and FFmpeg. Install: uv pip install pydub "
                "and ensure ffmpeg is on PATH. Error:",
                e,
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print(
            f"Unknown extension {out.suffix!r}; use .wav or .mp3.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(f"Wrote {out.resolve()} ({sr} Hz)")


if __name__ == "__main__":
    main()
