---
name: huggingface-text-to-speech
description: Generate speech audio from text using Hugging Face models (Transformers pipeline), CLI script, and WAV/MP3 export.
metadata:
  tags: tts, huggingface, transformers, audio, speech
---

## When to use

Use this skill when you need to synthesize voice audio from text with a model hosted on the Hugging Face Hub, run inference locally with the `transformers` **text-to-speech** pipeline, and save **WAV** (default) or **MP3** (optional).

## Prerequisites

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** for Python versions and environments (install once per machine).
- **Python 3.10+** — uv can install a matching interpreter (`uv python install 3.12`) or use one already on `PATH`.
- **PyTorch** — install the wheel for your platform ([PyTorch install](https://pytorch.org/get-started/locally/)); with uv you typically add `torch` in the same `uv pip install` line as below.

### One-time setup (from this skill directory)

```bash
uv venv
uv pip install "transformers[torch]" torch soundfile accelerate
```

Models download from the Hub automatically on first inference (cached under the Hugging Face cache).

**MP3 output** additionally requires `pydub` and a system **FFmpeg** binary on `PATH`:

```bash
uv pip install pydub
```

If you only need WAV, FFmpeg is not required.

## Script: `hf_tts.py`

The project provides a command-line helper: [`hf_tts.py`](./hf_tts.py).

It builds a `pipeline(task="text-to-speech", model=...)` (alias of the **text-to-audio** task), runs your text through the model, and writes:

- **`.wav`** — always supported (PCM via `soundfile`).
- **`.mp3`** — only if `pydub` and FFmpeg are available; otherwise use `.wav` or convert offline.

### Common usage

Run with **`uv run`** so the local `.venv` from setup is used (from `skills/text-to-speech/`):

```bash
uv run python hf_tts.py --model facebook/mms-tts-eng --text "Hello, world." -o speech.wav
```

Read long scripts from a file:

```bash
uv run python hf_tts.py --model facebook/mms-tts-eng --text-file narration.txt -o out.wav
```

Use GPU and half precision when appropriate:

```bash
uv run python hf_tts.py --model facebook/mms-tts-eng --text "Hello" -o out.wav --device cuda:0 --dtype float16
```

Models that use custom code on the Hub need the flag:

```bash
uv run python hf_tts.py --model suno/bark --text "Hello" -o bark.wav --trust-remote-code --pipe-kwargs "{\"voice_preset\":\"v2/en_speaker_6\"}"
```

### Arguments reference

| Argument | Description |
|----------|-------------|
| `--model` | **Required.** Hugging Face model id (e.g. `facebook/mms-tts-eng`). |
| `--text` / `-t` | Input string (mutually exclusive with `--text-file`). |
| `--text-file` | Path to a UTF-8 text file. |
| `--output` / `-o` | Output path; extension `.wav` or `.mp3` (default: `tts_output.wav`). |
| `--device` | `auto` (GPU if available else CPU), `cpu`, `cuda`, `cuda:0`, etc. |
| `--dtype` | `float32`, `float16`, or `bfloat16`. |
| `--trust-remote-code` | Set when the model repo requires executing custom modeling code. |
| `--seed` | Optional; passed to `transformers.set_seed`. |
| `--forward-params` | JSON object for `pipe(text, forward_params=...)`. Use when the docs show **forward_params** (e.g. SpeechT5 **speaker_embeddings** — tensors cannot be passed from JSON; use a tiny custom script for those). |
| `--pipe-kwargs` | JSON object merged into the pipeline `__call__` (e.g. Bark `voice_preset`). |
| `--pipeline-kwargs` | JSON object merged into `pipeline(...)` (e.g. extra `model_kwargs`). |

### How Hugging Face “installs” the model

No separate download step is required: the first pipeline load calls `from_pretrained` under the hood and caches weights in the Hugging Face cache (usually `~/.cache/huggingface` or `%USERPROFILE%\.cache\huggingface` on Windows). Re-runs reuse the cache unless you change the model id or revision.

### Choosing a model

- Browse the Hub with the **text-to-speech** / **text-to-audio** task filter and read each model card for language, quality, VRAM, and API quirks.
- **MMS TTS** (`facebook/mms-tts-eng`, etc.) works well with the default pipeline and no extra objects.
- **Bark** (`suno/bark`) typically needs `--trust-remote-code` and optional `voice_preset` via `--pipe-kwargs` (see example above).
- **FastSpeech2 + separate vocoder** (e.g. some ESPnet checkpoints) may require loading a **vocoder** object and passing it into `pipeline(...)` — that is model-specific; use `--pipeline-kwargs` only if the values are JSON-serializable, or extend `hf_tts.py` locally for that checkpoint.

### API reference (Transformers)

The pipeline returns a dict with **`audio`** (waveform) and **`sampling_rate`**, which the script writes to disk — the same pattern documented for VITS/MMS-style usage in Transformers.

## Limitations

- **`--forward-params` with tensors** (e.g. SpeechT5 speaker embeddings) cannot be expressed as plain JSON; load embeddings in Python and call `pipe(text, forward_params={"speaker_embeddings": ...})` in a short custom script.
- **MP3** depends on FFmpeg; without it, prefer **WAV** for lossless PCM and maximum compatibility with editors (e.g. Remotion).
