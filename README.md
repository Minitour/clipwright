# clipwright

An AI-powered video production workspace. Describe the video you want, and the agent builds it for you — scene by scene, with your approval at every step.

Under the hood, clipwright combines [Remotion](https://www.remotion.dev/) (React-based video) and [ManimGL](https://github.com/3b1b/manim) (mathematical animation) into a single pipeline with local text-to-speech, brand-consistent styling, and platform-aware output. You don't need to know either tool — the agent handles the code.

## What You Can Make

- Explainer and educational videos
- Math and algorithm visualizations
- Social media content (YouTube Shorts, Reels, TikTok)
- Motion graphics and title sequences
- Narrated walkthroughs with auto-generated voiceover

## How It Works

1. **Tell the agent what you want** — topic, audience, platform, duration, style
2. **Review the plan** — the agent drafts a scene-by-scene storyboard for your approval
3. **Watch it come together** — scenes are built incrementally, with previews along the way
4. **Get your video** — rendered to your target format and resolution

The agent reads your preferences from `config.toml` (brand colors, fonts, resolution, audio settings) so every project starts with your defaults.

## Prerequisites

Install the following before your first project:

- [Node.js](https://nodejs.org/) 18+
- [Python](https://www.python.org/) 3.13+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [FFmpeg](https://ffmpeg.org/)

## Setup

```bash
git clone https://github.com/<your-username>/clipwright.git
cd clipwright
uv sync
npm install
```

## Configuration

Edit `config.toml` to set your defaults. Everything here is inherited by new projects automatically.

| Section | What you can customize |
|---------|------------------------|
| `[brand]` | Name, colors, fonts, logo |
| `[video]` | Resolution, FPS, codec, quality |
| `[video.presets.*]` | Platform targets (YouTube, Shorts, Reels, TikTok, 4K) |
| `[audio]` | Voiceover provider, voice model, volume levels |
| `[style]` | Animation style, transitions, caption position, watermark |

## Project Layout

Each video lives in its own directory under `projects/`. The agent creates and manages this structure for you.

```
clipwright/
├── config.toml          # Your global defaults
├── skills/              # Built-in capabilities (TTS, engine guides)
└── projects/
    └── my-video/
        ├── plan/        # Storyboard and spec
        ├── manim/       # Math animation scenes (when needed)
        └── remotion/    # Video composition (React)
```

## License

[MIT](LICENSE) — Antonio Zaitoun, 2026
