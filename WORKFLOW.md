# Video Production — Agent Guidance

These are your instructions when creating and iterating on video projects. You act as a collaborative video production partner: you do not generate an entire video in one shot, you always work top-down (concept and structure first, then implementation), and you keep the user in the loop at key decision points.

---

## Guiding Principles

- **Configuration-first**: Read `config.toml` at the start of every workflow. It defines brand colors, fonts, resolution, audio levels, and style preferences. Use these values as defaults for every project unless the user explicitly overrides them. Never hardcode values that `config.toml` already provides.
- **Iterative and incremental**: Propose scenes, get the user's review, and implement only after approval. Show previews early and often.
- **Top-down construction**: Establish the overall narrative, structure, and timing before coding individual scenes or compositions.
- **Remotion-first composition**: Remotion is **always** the primary composition engine — it owns the final video timeline, scene sequencing, transitions, text, branding, and audio. ManimGL is a **supplementary** tool used only when a scene requires mathematical animations, algorithmic visualizations, or LaTeX-heavy diagrams. Those ManimGL clips are rendered to `.mp4` and embedded into the Remotion composition via `<OffthreadVideo>`. Never build a ManimGL-only project unless the user explicitly requests it.
- **Skill-driven development**: Always load the relevant skill before writing engine-specific code. Read the **remotion** skill (`skills/remotion/SKILL.md`) before writing Remotion code. Read the **manim** skill (`skills/manim/SKILL.md`) before writing ManimGL code. Then load specific rule files as needed for the task at hand (e.g. `rules/transitions.md`, `rules/tex.md`). After learning a new skill, call the `setup_tools` tool to activate it, then use `call_tool` to invoke the relevant tool.
- **Reuse skill scripts — never duplicate**: When a skill provides scripts (e.g. `skills/text-to-speech/scripts/kokoro_tts.py`), **call them directly** via `uv run python skills/...` or import their functions. If project-specific behavior is needed (e.g. batch processing, timeline generation), create a thin wrapper in the project's `scripts/` directory that delegates core work to the skill script. Never copy-paste skill code into project files.
- **Shared workspace environments**: All projects share a single Python virtual environment at the workspace root (managed by `uv` with the root `pyproject.toml`). Never create per-project `pyproject.toml`, `.venv`, or `uv.lock` files. For Node.js, use npm workspaces so Remotion dependencies are hoisted to the workspace root `node_modules`. See the **Shared Environments** section for details.
- **Project isolation** (source code): Each video lives in its own directory under `projects/`. Projects are independent — never share source code or state across project boundaries. Environments and dependencies, however, are shared at the workspace level.
- **Plan approval before implementation**: In Step 3, write the video plan to `projects/<project>/plan/PLAN.md` and present it in the conversation. Do **not** proceed to implementation until the user has **explicitly approved** the plan.
- **Audio-driven timing**: Always plan voiceover from the start (Step 2), not as an afterthought. Generate speech as **individual per-segment audio files** (one per scene/beat), not a single monolithic track. Derive visual segment durations from measured audio lengths plus a small padding (~300 ms), so speech and visuals stay synchronized without silence gaps.
- **Frame-aware layout**: Design all content to fill the target frame. For portrait/vertical formats (9:16), use the full canvas height and width — do not place small, centered cards with excessive padding. When embedding ManimGL clips, ensure the Manim logical frame is configured for the target aspect ratio and that mobjects are scaled and positioned to use the available space. Use `objectFit: "cover"` for embedded video and verify content isn't tiny.
- **Cast-first character design**: When a video features characters (narrator, presenter, customer, etc.), define them once in a project cast and reuse those identities across scenes. Use the `characters` skill (react-peeps based). Scenes render cast members via a shared `<Character>` wrapper; never re-spec a character's look inline in a scene file.
- **Preview before polish**: Get rough animations working before fine-tuning timing, colors, and transitions. Working ugly beats broken beautiful.
- **Preserve user assets**: Never modify or overwrite user-provided assets (videos, images, audio). Copy or reference them in place.

---

## Engine Selection Guide

**Remotion is always the base.** Every video project uses Remotion as the primary composition engine — it handles the final timeline, scene sequencing, transitions, typography, branding, and audio. ManimGL is used **only** for specific scenes that require mathematical animation, algorithmic visualization, or LaTeX rendering. Those clips are rendered to `.mp4` and embedded into the Remotion composition.

Use the table below to decide **which scenes within a project need ManimGL clips**:

| Scene Content | Engine | Role |
|---------------|--------|------|
| Math equations and proofs | ManimGL clip | Rendered to `.mp4`, embedded in Remotion via `<OffthreadVideo>` |
| Algorithm/data structure visualization | ManimGL clip | Rendered to `.mp4`, embedded in Remotion |
| 3D mathematical surfaces | ManimGL clip | Rendered to `.mp4`, embedded in Remotion |
| Title cards, text animations, typography | Remotion | Primary engine handles these directly |
| Explainer with talking head + overlays | Remotion | Video embedding, captions, sequencing, media compositing |
| Charts and data visualization | Remotion | Bar/pie/line charts, animated data-driven graphics |
| Social media content (reels, stories) | Remotion | Aspect ratio presets, text animations, transitions |
| Audio-reactive visuals | Remotion | Audio visualization, spectrum bars, waveforms |
| Motion graphics with web tech | Remotion | CSS animations, Three.js, Lottie, TailwindCSS |
| Map animations | Remotion | Mapbox integration, animated maps |
| Captioned/subtitled video | Remotion | SRT import, caption display, voiceover with local TTS |
| Characters/avatars in scenes | Remotion | react-peeps React components rendered into the timeline; animated with standard Remotion interpolate/spring |
| Statistics / data infographics | Infographic skills (`infographic-creator` et al.) + Remotion | Load the `infographic-creator` skill — it generates the AntV declarative syntax that renders to SVG. Embed the SVG inside the Remotion scene; animate via the wrapper. |
| Brand / tool / platform logos | Remotion + `simple-icons` | Look up via the canonical slug (see `node_modules/simple-icons/icons/` or `simple-icons.org`), import the icon as `siCamelCaseSlug`, render via a small `<BrandIcon icon={…} />` component. Plain text pill only when the slug genuinely doesn't exist. |

**Pipeline for ManimGL clips:** Render each ManimGL scene to `manim/output/`, copy the `.mp4` files into `remotion/public/manim/`, and reference them using `<OffthreadVideo>` in the Remotion composition. Remotion always produces the final deliverable.

---

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

---

## Project Directory Structure

All projects live under `projects/` at the workspace root. Each project is self-contained and **always contains both `manim/` and `remotion/` directories**, regardless of which engine the project primarily uses. This uniform structure means any project can incorporate either engine at any point without restructuring, and tooling/scripts can assume a consistent layout.

```
projects/<project-name>/
├── plan/
│   └── PLAN.md                  # Video plan and storyboard (Step 3 output)
├── characters/                   # Casting brief (only when the video has characters)
│   └── cast.yaml                 # Per-character library + props; compiled to cast.ts
├── manim/                        # ManimGL sub-project
│   ├── scenes/                   # Python scene files
│   │   ├── scene_01_intro.py
│   │   ├── scene_02_proof.py
│   │   └── ...
│   ├── assets/                   # Images, data files used by Manim scenes
│   ├── output/                   # Rendered media (gitignored)
│   └── custom_config.yml         # ManimGL configuration
├── remotion/                     # Remotion sub-project
│   ├── public/                   # Static assets (images, audio, video, manim renders)
│   ├── src/
│   │   ├── Root.tsx              # Composition registry
│   │   ├── cast.ts               # Generated from cast.yaml — typed cast record (when characters exist)
│   │   ├── components/           # Reusable visual components (incl. Character.tsx wrapper)
│   │   └── scenes/               # Individual scene compositions
│   ├── package.json
│   └── tsconfig.json
```

**When the project has no characters**, the `characters/` directory and `cast.ts` are simply absent.

**When ManimGL is not needed**, the `manim/` directory remains empty — it is ready if the project scope expands later.

**When both engines are used**, ManimGL renders its scenes into `manim/output/`, and those clips are copied into `remotion/public/manim/` and referenced from Remotion via `<OffthreadVideo>`.

---

## Variants — Multiple Compositions in One Project

When the user asks for "another version" of an existing video — a different aspect ratio (Instagram Reels, vertical), different cast, different palette, different language, different copy — **add a new `<Composition>` to the existing project's `Root.tsx`**. Do **not** clone the project directory.

This is the canonical Remotion pattern: one project can register many compositions that share the same scenes, components, cast, audio, fonts, brand constants, and build pipeline. Cloning fragments edits across two copies, duplicates `node_modules` and rendered assets, and lets the variants drift over time.

### Trigger phrases

Any of "give me another version", "a version with X", "an Instagram Reels version", "a portrait/landscape version", "the same but with X", "make a variant", or "show me how it would look with X".

### How to model each variant kind

| Variant kind | Implementation |
|---|---|
| **Different aspect ratio** (e.g. Instagram Reels, vertical, 4K) | Register a second `<Composition id="MainReel" component={MainVideo} width={1080} height={1920} ... />` alongside the primary one. Use `useVideoConfig()` inside scenes to detect dimensions and reflow layout. |
| **Different content** (icons, copy, cast, palette) | Parameterize the master `MainVideo` (or affected scenes) via `inputProps`. Register a second `<Composition id="MainVideoAlt" defaultProps={{ variant: 'alt' }} ... />`. Scenes read `useInputProps()` and switch behavior. |
| **Different cast** | Either declare both casts in `cast.yaml` and `cast-alt.yaml`, generate two `cast.ts` outputs, and pick via `inputProps`; or co-design the cast so both variants share ids and only the avatar library / style differs. |
| **Faster cut / different timing** | Register a separate `<Composition id="MainVideoFast" component={MainVideoFast} ... />` with its own duration and a sibling root component that reuses the same scenes but at compressed timings. See the `capa-launch` project for an existing example. |

### Litmus test: variant vs new project

If the only file that *needs* to differ between the two outputs is the `<Composition>` registration (or its `defaultProps`), it's a **variant** — same project, new composition. If the two outputs require different scene structures, different timelines, or different audio scripts, they're **separate projects**.

### Render a variant

```bash
cd projects/<project>/remotion
npx remotion render src/index.ts MainReel output/main-reel.mp4 --codec h264 --crf 18
```

Studio (see "Live preview" below) shows every registered composition automatically — the user can scrub each one without restarting anything.

---

## Live preview — Auto-launch Remotion Studio

**As soon as Scene 1 type-checks and renders a still successfully** (typically the end of Step 6 Phase 1), launch Remotion Studio in the background and open it in the user's browser. Hot reload then gives the user something to watch while the remaining scenes, audio, and assembly are built — instead of waiting for a finished mp4.

```bash
cd projects/<project>/remotion
npx remotion studio --no-open &   # background — capture port from the banner
open "http://localhost:<port>"     # auto-open in browser
```

**Only one Studio instance at a time.** Before launching, check for an existing `remotion studio` background task. If one is running for a different project, stop it first. If one is already running for the current project, don't start a second.

Variants registered in `Root.tsx` (per the section above) show up in the same Studio automatically via hot reload — no second Studio is needed when adding compositions later.

---

## Shared Environments

All projects share workspace-level environments to avoid per-project bloat. Never create per-project virtual environments, `pyproject.toml`, or standalone `package.json` files outside the standard structure.

### Python (ManimGL, TTS, and other tooling)

A single `pyproject.toml` at the **workspace root** declares all Python dependencies (`manimgl`, `kokoro`, `soundfile`, etc.). A single `.venv` lives at the workspace root, managed by `uv`.

```
video-master/
├── pyproject.toml        # All Python deps here
├── uv.lock
├── .python-version
├── .venv/                # Shared virtual environment
└── projects/
    └── my-video/
        └── manim/
            └── scenes/   # Import from the shared .venv
```

**Rules:**
- **Never** create `pyproject.toml`, `.venv`, or `uv.lock` inside a project directory.
- Run all Python commands via `uv run` from the workspace root, or use `uv run --project <workspace-root>` when the working directory must be elsewhere (e.g. inside `manim/` so `custom_config.yml` is picked up).
- When a new Python dependency is needed, add it at the root: `uv add <package>` (run from workspace root).

**Running ManimGL from a project's `manim/` directory** (so `custom_config.yml` is loaded):
```bash
cd projects/<project>/manim
uv run --project ../../.. manimgl scenes/<file>.py <SceneName>
```

### Node.js (Remotion)

Use **npm workspaces** so Remotion dependencies are hoisted to a single root-level `node_modules`. The workspace root has a `package.json` that declares project workspaces:

```jsonc
// video-master/package.json
{
  "private": true,
  "workspaces": ["projects/*/remotion"]
}
```

Each project's `remotion/package.json` declares its own dependencies as usual, but `npm install` at the workspace root hoists shared packages (React, Remotion core, Tailwind, etc.) to `video-master/node_modules/`. This avoids duplicating hundreds of megabytes per project.

**Rules:**
- Run `npm install` from the **workspace root**, not from individual project directories.
- Each project's `remotion/package.json` still lists its own deps — npm workspaces handle deduplication automatically.
- To add a dependency to a specific project: `npm install <package> -w projects/<project>/remotion` (from workspace root).
- To run scripts in a specific project: `npm run <script> -w projects/<project>/remotion` (from workspace root), or `cd projects/<project>/remotion && npx <command>`.

### Verifying the environment

At the start of **Step 5** (Project Initialization), verify that required tools are available. Do not proceed until all pass:

```bash
node -v          # Node.js (for Remotion)
uv --version     # Python environment manager
ffmpeg -version  # Media processing
```

If ManimGL is needed for the project:
```bash
uv run manimgl --version   # ManimGL (from shared .venv)
```

If any tool is missing, install it or guide the user before continuing. Do not assume tools are available just because they were available in a previous session or on a different machine.

---

## Development Workflow

Follow these steps when creating a video project. Skip steps that do not apply, but never skip planning (Steps 1–3) or user approval (Step 4).

**Path convention**: `<project>` refers to the project directory name only (e.g. `explainer-video`). All paths starting with `projects/` are relative to the workspace root.

### Step 1 — Concept Definition

Read `config.toml` first. Then help the user clarify what video they want to create. Present the configured defaults so the user knows what they're starting with and can override as needed.

**Gather:**
- **Topic and purpose** — What is the video about? Who is the audience?
- **Engine preference** — Does the user have a preference, or should you recommend one based on the Engine Selection Guide?
- **Target platform** — YouTube, YouTube Shorts, Instagram, TikTok, etc. If named, apply the matching `[video.presets.*]` from config. If not specified, use the top-level `[video]` defaults.
- **Duration target** — Approximate length in seconds or minutes.
- **Visual style** — Minimalist, colorful, 3b1b-style, corporate, playful, etc. Default animation style and transition come from `[style]`.
- **Resolution and format** — Confirm or override the config defaults (show the user what's configured).
- **Audio requirements** — Voiceover, background music, sound effects, or silent. Default volumes and voiceover provider come from `[audio]`.
- **Cast** — Will the video feature avatar characters? If yes: how many, what roles (narrator, customer, presenter…), and any art-direction preferences. Defaults (library, stroke color, skin tones) come from `[characters]`.
- **Assets provided** — Does the user have existing footage, images, or audio to incorporate?

**Target output:** A concise project brief (2–5 sentences) that captures the above, noting any deviations from `config.toml` defaults. Confirm it with the user before proceeding.

### Step 2 — Script and Storyboard

Develop the narrative structure of the video. This is the creative backbone — get it right before touching code.

**For educational/explainer videos:**
1. Write a **narration script** (what the voiceover or on-screen text says).
2. Break it into **beats** — logical segments that each convey one idea.
3. For each beat, describe the **visual action** (what the viewer sees).

**For animation/visualization videos:**
1. List the **key visual moments** — what appears, transforms, or disappears.
2. Define the **progression** — how one visual state leads to the next.
3. Note any **mathematical expressions**, data, or diagrams needed.

**For media-rich productions:**
1. Define the **content timeline** — when clips, images, and text appear.
2. Identify **transition points** between segments.
3. Note **audio cues** — when music, effects, or voiceover align with visuals.

**Output format:** A numbered list of scenes/beats, each with:
- Scene number and title
- Duration (approximate seconds)
- **Narration script** (the exact text to be spoken — always include this unless the video is explicitly silent)
- Visual description (what the viewer sees, which engine renders it)
- **Characters present** — Which cast members appear in this beat and what they do (narrating, reacting, gesturing). Omit if the video has no cast.
- Assets needed

**Audio must be planned here, not added later.** If the plan includes voiceover (the default unless the user says otherwise), write the narration script for every scene in this step. Each scene's duration estimate should be based on the narration length, not arbitrary fixed values.

Present this to the user for feedback before proceeding.

### Step 3 — Video Plan (Plan Document)

Formalize the storyboard into a structured plan. **Write it to `projects/<project>/plan/PLAN.md`** and present it in the conversation simultaneously.

**The plan document must include these sections:**

1. **Project Brief** — Topic, audience, engine, duration, target platform.
2. **Effective Configuration** — The resolved values for this project: resolution, FPS, codec, brand colors, fonts. Start from `config.toml` defaults and note any per-project overrides. This is the single source of truth for the project's technical and visual settings.
3. **Scene Breakdown** — Table of scenes with: number, title, duration, description, engine (if hybrid).
4. **Timeline** — Visual timeline showing scene order and cumulative duration.
5. **Visual Style Guide** — Colors (from `[brand.colors]` or overridden), fonts (from `[brand.fonts]` or overridden), animation style, transition type, reference examples.
6. **Asset Inventory** — List of all required assets: images, audio, video clips, fonts, data files. Mark each as "provided by user", "to be created", "from simple-icons" (for any tool/company/platform logo — check the library before listing as "to be sourced"), or "to be sourced". Include brand logo if `[brand.logo]` is configured and watermark is enabled.
7. **Cast** — Table of characters that appear in the video. Columns: id (kebab-case), role, key visual traits (hair, face, body, accessory). One row per character. This table is the source of truth that gets translated into `characters/cast.yaml` in Step 5f. Omit this section if the video has no characters.
8. **Audio Plan** — Voiceover script (if any), music tracks, sound effects, timing. Default volume levels from `[audio]`.
9. **Technical Specifications** — Resolution, FPS, codec, output format (from effective configuration).
10. **Open Questions** — Anything that needs user clarification before implementation.

Close the plan with a **"What I need from you"** checklist. State clearly that implementation will not begin until the user approves.

### Step 4 — User Approval

**Wait for the user to review and approve the plan.** Do not proceed to Step 5 until the user has explicitly confirmed.

Support:
- **Revisions** — Scene reordering, timing changes, style adjustments.
- **Partial approval** — "Approve scenes 1–3, let's rethink scene 4."
- **Asset delivery** — User may need time to provide audio, footage, or data.
- **Blanket approval** — User says "looks good, proceed" — resolve open questions using best judgment and list all resolutions.

When revising, always update the plan file in place. On approval, update the plan's status to `approved` and proceed.

### Step 5 — Project Initialization

Set up the project directory with the standard structure. Every project gets both `manim/` and `remotion/` directories.

**5a. Verify tools** (see Shared Environments → Verifying the environment):

Before creating anything, confirm that `node`, `uv`, and `ffmpeg` are on `PATH`. If ManimGL is needed, also verify `uv run manimgl --version`. If any tool is missing, stop and resolve it. Do not assume availability.

**5b. Create the project directory:**
```bash
mkdir -p projects/<project>/plan
mkdir -p projects/<project>/manim/scenes projects/<project>/manim/assets projects/<project>/manim/output
mkdir -p projects/<project>/remotion
```

Move the `PLAN.md` into `projects/<project>/plan/`.

**5c. Initialize Remotion** (always — Remotion is the base for every project):
1. Run `npx create-video@latest projects/<project>/remotion` (select the blank template).
2. Ensure the workspace root `package.json` has `"workspaces"` that includes `"projects/*/remotion"`. If not, create or update it.
3. Run `npm install` from the **workspace root** (not from the project's `remotion/` directory) so dependencies are hoisted.
4. Install additional dependencies as needed (e.g. `@remotion/three`, `@remotion/media-utils`). If `[remotion].tailwind` is `true` in config, include TailwindCSS setup. Use `npm install <pkg> -w projects/<project>/remotion` from the workspace root.
5. Set up `src/Root.tsx` with the planned compositions, using width/height/FPS from the plan's effective configuration.

**5d. Initialize ManimGL** (only if the plan includes ManimGL scenes):
1. Ensure `manimgl` is listed in the workspace root `pyproject.toml`. If not, add it: `uv add manimgl` (from workspace root). Never create a per-project `pyproject.toml`.
2. Create `projects/<project>/manim/custom_config.yml` using resolution, FPS, background color, and quality from the plan's effective configuration. Use the correct config schema for the installed ManimGL version — read the manim skill (`skills/manim/SKILL.md`) for the right schema.
3. Verify ManimGL works: `uv run manimgl --version`.

**5e. Python dependencies** for TTS or other tooling:

If the plan includes voiceover, ensure `kokoro` (or the configured TTS package) and `soundfile` are in the root `pyproject.toml`. Run `uv sync` from the workspace root. Never create per-project Python environments.

**5f. Initialize cast** (only if the plan includes characters):

1. Install react-peeps into the project's Remotion sub-project (from workspace root):
   ```bash
   npm install react-peeps -w projects/<project>/remotion --legacy-peer-deps
   ```
   The `--legacy-peer-deps` flag is needed because react-peeps' peer dep is React `^16.12` while Remotion projects use React 19.
2. Translate the plan's **Cast** table into `projects/<project>/characters/cast.yaml`. See `skills/characters/rules/casting.md` for the YAML shape.
3. Scaffold the typed cast **and** the starter wrapper in one command — from the project's `remotion/` directory:
   ```bash
   uv run --project ../../.. python ../../../skills/characters/scripts/scaffold_cast.py \
       ../characters/cast.yaml -o src/cast.ts \
       --component src/components/Character.tsx
   ```
   The generated `Character.tsx` bakes in the skill's react-peeps house style (circular avatar, indigo background, black stroke, white fill, thin white rim, soft drop shadow — defaults from `[characters.peeps_style]` in `config.toml`). The script refuses to overwrite an existing `Character.tsx` unless `--force` is also passed, so hand-edits are safe.
4. Verify the generated files type-check: `npx tsc --noEmit` (from the project's `remotion/`).

### Step 6 — Scene Implementation

Build each scene incrementally, following the approved plan. **Implement one scene at a time** — do not batch-implement the entire video.

**Before writing any engine-specific code**, load the relevant skill:
- **Remotion**: Read `skills/remotion/SKILL.md`, then load specific rule files for the features you need (e.g. `rules/animations.md`, `rules/transitions.md`, `rules/charts.md`).
- **ManimGL**: Read `skills/manim/SKILL.md`, then load specific rule files (e.g. `rules/tex.md`, `rules/3d.md`, `rules/creation-animations.md`).

#### Implementation order: Remotion first, then ManimGL clips

**Always build the Remotion composition first.** This establishes the video's structure, timing, transitions, and branding. Then implement ManimGL clips for scenes that need them, and embed them into the existing Remotion timeline.

**Phase 1 — Remotion scenes (all scenes):**
1. Create a `brand.ts` (or equivalent) in `remotion/src/` that exports all brand colors, fonts, and config values as named constants derived from the plan's effective configuration.
2. For each scene, create a component in `remotion/src/scenes/`.
3. Register it as a `<Composition>` in `remotion/src/Root.tsx` with correct duration, FPS, and dimensions.
4. Implement static layout first (positioning, text, images) — use the **full canvas**. For portrait (9:16), fill the vertical space; do not leave large empty regions.
5. **Brand / tool / platform references** — whenever a scene needs to show a tool, company, or platform (agent logos, integration grids, comparison tables, etc.), look it up in `simple-icons` first. Install with `npm install simple-icons -w projects/<project>/remotion`, verify the slug exists under `node_modules/simple-icons/icons/<slug>.svg`, then import the named icon (`import { siReact } from 'simple-icons'`) and render via a small `<BrandIcon>` component (template in `rules/brand-icons-via-simple-icons.md`). Do **not** invent slugs — verified-before-import is the same lesson the characters skill learned the hard way. Fall back to a text pill only when the slug genuinely doesn't exist.
6. Add animations using `useCurrentFrame()`, `interpolate()`, and `spring()`.
7. **After Scene 1 renders successfully** (e.g. `npx remotion still` produces a clean image), **launch Remotion Studio in the background and open it for the user** — see the "Live preview" section above. Build the remaining scenes with Studio running so each new scene appears via hot reload as it's written. Never run more than one Studio instance at a time.
8. For scenes that will contain ManimGL clips, add a placeholder `<OffthreadVideo>` with `objectFit: "cover"`. The actual `.mp4` will be placed later.
9. Add transitions between scenes using `<TransitionSeries>` if applicable.
10. When a scene uses characters, load the **characters** skill (`skills/characters/SKILL.md`) first. Reference cast via `<Character id="narrator" />` — never import `react-peeps` directly in scene files. See `rules/animation.md` for entrance, idle, gesture, and exit patterns.
11. Preview in Remotion Studio: `npx remotion studio` (from the project's `remotion/` directory).

**Phase 2 — ManimGL clips (only scenes that need them):**
1. Create the scene file in `manim/scenes/`.
2. Define the scene class extending `InteractiveScene`.
3. Implement mobject construction (shapes, text, equations).
4. **Scale and position content for the target frame.** For portrait formats, the logical frame is tall and narrow — scale `VGroup`s and use `self.frame.scale()` to fill the canvas. Verify content fills the exported frame and doesn't appear tiny.
5. Apply brand colors from the plan (use named constants with comments referencing config).
6. Add animations (`self.play(...)`, timing, `self.wait(...)`).
7. Preview: `uv run --project <workspace-root> manimgl scenes/<file>.py <SceneName>` (from `manim/` directory).
8. Render to file: add `-w` flag. Copy output to `remotion/public/manim/`.
9. Verify the clip looks correct when embedded in the Remotion composition at full resolution.

#### Frame utilization checklist (especially for portrait/vertical formats)

- [ ] ManimGL `custom_config.yml` has correct `pixel_width` / `pixel_height` matching the target aspect ratio.
- [ ] ManimGL `frame_width` and `frame_height` are set for the target ratio (e.g. 8.0 × ~14.22 for 9:16).
- [ ] All mobject groups are scaled to fill at least 80% of the logical frame.
- [ ] Remotion scenes use `flexbox` or explicit sizing to fill the full canvas — no small centered cards with excessive padding.
- [ ] Embedded ManimGL clips use `objectFit: "cover"` or `"contain"` and appear at a reasonable size.

#### Per-scene checklist
- [ ] Scene matches the plan description.
- [ ] Timing aligns with the planned duration.
- [ ] Visual style is consistent with the style guide (brand colors, fonts from effective configuration).
- [ ] No hardcoded magic numbers — use named constants for colors, durations, positions.
- [ ] Content fills the frame (no tiny diagrams floating in a large canvas).

After implementing each scene, briefly confirm with the user before moving to the next.

### Step 7 — Audio Integration

Add audio elements according to the audio plan. This step applies to Remotion (the primary composition engine); ManimGL clips are always rendered silent.

#### Voiceover — per-segment approach

**Never generate a single monolithic voiceover file.** Instead, produce one audio file per scene/beat so timing stays synchronized:

1. **Write per-segment text files** — one `.txt` per scene in `remotion/public/voice/` (e.g. `seg01.txt`, `seg02.txt`, …). Each file contains only the narration for that scene.

2. **Create a thin wrapper script** in `remotion/scripts/generate_voice_segments.py` that:
   - Reads `config.toml` for the TTS model and voice settings.
   - Iterates over `seg*.txt` files.
   - **Calls the skill script** for synthesis — import functions from `skills/text-to-speech/scripts/kokoro_tts.py` (or `hf_tts.py`) or invoke it via subprocess. Do **not** duplicate the synthesis code.
   - Writes `seg*.wav` files alongside the `.txt` files.
   - Measures each WAV duration and writes a **timeline JSON** (e.g. `src/data/timeline.json`) with `audioFrames`, `segmentDurations` (audio + ~300 ms padding), and `totalFrames`.

3. **Wire up an npm script** in `remotion/package.json`:
   ```json
   "generate-voice": "uv run --project ../../.. python scripts/generate_voice_segments.py"
   ```

4. **Import the timeline JSON** in the Remotion composition to drive segment durations and audio placement. Each `<Audio>` component is placed at the segment's start frame with `trimAfter` set to the audio's actual frame length (not the visual segment length).

5. **Audio-driven visual timing:** Visual segment durations = audio frames + padding (~300 ms / 18 frames at 60 fps). For scenes with ManimGL clips, use `max(audio + padding, minimumClipLength)` so the clip isn't cut short. The total composition frame count is `sum(segmentDurations) - (N-1) × transitionFrames`.

#### Background music
1. Import music files into `remotion/public/`.
2. Add as `<Audio>` with lower volume (from `[audio].music_volume`), spanning the full composition.
3. Consider fade-in/fade-out at video boundaries.

#### Sound effects
1. Load `rules/sfx.md` for sound effect patterns.
2. Place `<Audio>` components at precise frame offsets to sync with visual events.

#### Captions and subtitles
1. Load `rules/subtitles.md` and `rules/display-captions.md`.
2. Import or generate SRT/transcript data.
3. Display captions synced to the audio timeline.

### Step 8 — Assembly and Transitions

Combine individual scenes into the final video.

**Remotion assembly:**
1. Create a master composition in `remotion/src/Root.tsx` that sequences all scene compositions.
2. Use `<Series>` or `<TransitionSeries>` to chain scenes with transitions.
3. Load `rules/transitions.md` for transition patterns (fade, slide, wipe, etc.).
4. Add intro/outro sequences if planned.
5. Verify total duration matches the plan.

**ManimGL clip rendering** (for embedding in Remotion):
1. Render each ManimGL scene to file (`-w` flag) — output goes to `manim/output/`.
2. Copy clips to `remotion/public/manim/`.
3. Standalone ManimGL concatenation via FFmpeg is rarely needed — Remotion handles sequencing.

**Embedding ManimGL clips in Remotion** (the standard hybrid pipeline):
1. Render all ManimGL scenes to `manim/output/` with `-w`.
2. Copy rendered clips into `remotion/public/manim/` (e.g. `clip-qkv.mp4`).
3. Reference clips using `<OffthreadVideo src={staticFile("manim/clip-name.mp4")} style={{objectFit: "cover"}} />` in the Remotion scene components.
4. Remotion handles all transitions, text overlays, branding, and audio around and on top of the embedded clips.

### Step 9 — Preview and Refinement

Review the assembled video and iterate on quality.

**Preview methods:**
- **Remotion**: `cd remotion && npx remotion studio` — scrub the timeline, check every scene at full speed.
- **ManimGL**: `manimgl manim/scenes/<file>.py <SceneName>` — watch the animation in real-time.

**Quality checklist:**
- [ ] All scenes present and in correct order.
- [ ] Timing feels natural — no rushed or dragging segments.
- [ ] Animations are smooth — no jumps, pops, or glitches.
- [ ] Text is readable at target resolution.
- [ ] Colors and style are consistent throughout.
- [ ] Audio syncs with visuals (no drift).
- [ ] No placeholder content remains.

Report any issues to the user with specific timestamps and descriptions. Fix approved issues before rendering.

### Step 10 — Final Render

Render the finished video at production quality.

**Remotion render:**
```bash
cd remotion && npx remotion render src/index.ts <CompositionId> output/final.mp4
```

Use the codec, format, and CRF from the plan's effective configuration (sourced from `[video.output]` in `config.toml` unless overridden):
- `--codec` — value from `video.output.codec`.
- `--crf` — value from `video.output.crf`.
- `--scale` for resolution scaling if needed.
- `--concurrency` to control parallel rendering.

**ManimGL render:**
```bash
manimgl manim/scenes/<file>.py <SceneName> -w
```

Options:
- Default renders at the quality set in `manim/custom_config.yml`.
- Use `--uhd` for 4K output.
- Output lands in `manim/output/`.

**Post-render verification:**
1. Play the final file in a video player to verify end-to-end.
2. Check file size is reasonable for the target platform.
3. Confirm resolution, FPS, and codec match specifications.

Deliver the final video path to the user.

---

## Quick Reference: Common Patterns

### Verify environment (run at start of every project)
```bash
node -v && uv --version && ffmpeg -version
uv run manimgl --version   # if ManimGL is needed
```

### Adding a Python dependency (always at workspace root)
```bash
uv add <package>            # from workspace root
uv sync                     # ensure .venv is up to date
```

### Creating a new project
```bash
mkdir -p projects/my-video/plan
mkdir -p projects/my-video/manim/scenes projects/my-video/manim/assets projects/my-video/manim/output
mkdir -p projects/my-video/remotion
```

### Initializing the Remotion sub-project
```bash
npx create-video@latest projects/my-video/remotion
npm install                 # from workspace root — hoists deps via workspaces
```

### Adding a Remotion dependency
```bash
npm install <package> -w projects/<project>/remotion   # from workspace root
```

### Brand icons via simple-icons
```bash
# Install (per-project, in the Remotion workspace)
npm install simple-icons -w projects/<project>/remotion

# Confirm a slug exists before importing it
ls node_modules/simple-icons/icons/<slug>.svg
```
```tsx
import { siReact, type SimpleIcon } from "simple-icons";
// fill={`#${siReact.hex}`}  →  brand color
// d={siReact.path}           →  24×24 viewBox SVG path
```

### Previewing Remotion
```bash
cd projects/<project>/remotion
npx remotion studio
```

### Previewing ManimGL (interactive mode, using shared venv)
```bash
cd projects/<project>/manim
uv run --project ../../.. manimgl scenes/scene.py MyScene -se 15
```

### Rendering ManimGL clip to file
```bash
cd projects/<project>/manim
uv run --project ../../.. manimgl scenes/scene.py MyScene -w
# Then copy output to Remotion:
cp output/MyScene.mp4 ../remotion/public/manim/
```

### Rendering Remotion to file (final deliverable)
```bash
cd projects/<project>/remotion
npx remotion render src/index.ts MainVideo output/final.mp4
```

### Generating per-segment voiceover
```bash
cd projects/<project>/remotion
uv run --project ../../.. python scripts/generate_voice_segments.py
# Or from workspace root:
npm run generate-voice -w projects/<project>/remotion
```

### Concatenating ManimGL clips with FFmpeg (rare — usually embed in Remotion instead)
```bash
ffmpeg -f concat -safe 0 -i projects/<project>/manim/output/filelist.txt -c copy projects/<project>/manim/output/final.mp4
```

### Scaffolding the project cast + starter wrapper (from the project's `remotion/` directory)
```bash
uv run --project ../../.. python ../../../skills/characters/scripts/scaffold_cast.py \
    ../characters/cast.yaml -o src/cast.ts \
    --component src/components/Character.tsx
# Add --force to overwrite an existing Character.tsx (otherwise it's preserved).
```
