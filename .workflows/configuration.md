## Global Configuration (`config.toml`)

The `config.toml` file at the workspace root defines default preferences for every project. **Read this file at the start of every workflow** — before Step 1 — and use its values throughout.

### How configuration flows

1. **Agent reads `config.toml`** at workflow start.
2. **Step 1 (Concept Definition)** — present the user with the configured defaults (resolution, FPS, style). The user can accept or override per-project.
3. **Step 3 (Video Plan)** — the plan document records the effective values (config defaults merged with any per-project overrides).
4. **Step 5 (Project Initialization)** — use the effective values to configure ManimGL's `custom_config.yml` and Remotion's composition dimensions/FPS.
5. **Step 6 (Scene Implementation)** — apply brand colors, fonts, and style preferences when coding scenes. Reference config values through constants, not hardcoded literals.
6. **Step 10 (Final Render)** — use the configured codec, format, and CRF for rendering.

### Configuration sections

| Section | Controls |
|---------|----------|
| `[brand]` | Name, colors (primary, accent, background, text, muted), fonts (heading, body, code), logo |
| `[video]` | Default width, height, FPS |
| `[video.output]` | Codec, format, CRF quality |
| `[video.presets.*]` | Platform-specific overrides (youtube, youtube-shorts, instagram-reel, tiktok, 4k, etc.) |
| `[audio]` | Volume levels for voiceover, music, and sound effects; voiceover provider and voice |
| `[manim]` | Background color, text color, quality preset |
| `[remotion]` | TailwindCSS preference |
| `[characters]` | Default avatar library, art direction, default stroke color, skin-tone palette |
| `[style]` | Animation style, default transition, caption position, watermark toggle |

### Per-project overrides

A project's plan document (`PLAN.md`) is the authoritative source for that project's settings. When the user specifies values that differ from `config.toml`, record them in the plan and use the plan values. The config file is never modified per-project — it represents the user's global defaults.

### Platform presets

When the user names a target platform (e.g. "YouTube Shorts"), look up `[video.presets.youtube-shorts]` and use its width, height, and FPS instead of the top-level `[video]` values. The user can also specify a preset in Step 1 by name.
