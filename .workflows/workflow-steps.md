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

**5a. Verify tools** (see environments module → Verifying the environment):

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
7. **After Scene 1 renders successfully** (e.g. `npx remotion still` produces a clean image), **launch Remotion Studio in the background and open it for the user** — see the live-preview module. Build the remaining scenes with Studio running so each new scene appears via hot reload as it's written. Never run more than one Studio instance at a time.
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
