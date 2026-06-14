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
- **Shared workspace environments**: All projects share a single Python virtual environment at the workspace root (managed by `uv` with the root `pyproject.toml`). Never create per-project `pyproject.toml`, `.venv`, or `uv.lock` files. For Node.js, use npm workspaces so Remotion dependencies are hoisted to the workspace root `node_modules`. See the **Shared Environments** module for details.
- **Project isolation** (source code): Each video lives in its own directory under `projects/`. Projects are independent — never share source code or state across project boundaries. Environments and dependencies, however, are shared at the workspace level.
- **Plan approval before implementation**: In Step 3, write the video plan to `projects/<project>/plan/PLAN.md` and present it in the conversation. Do **not** proceed to implementation until the user has **explicitly approved** the plan.
- **Audio-driven timing**: Always plan voiceover from the start (Step 2), not as an afterthought. Generate speech as **individual per-segment audio files** (one per scene/beat), not a single monolithic track. Derive visual segment durations from measured audio lengths plus a small padding (~300 ms), so speech and visuals stay synchronized without silence gaps.
- **Frame-aware layout**: Design all content to fill the target frame. For portrait/vertical formats (9:16), use the full canvas height and width — do not place small, centered cards with excessive padding. When embedding ManimGL clips, ensure the Manim logical frame is configured for the target aspect ratio and that mobjects are scaled and positioned to use the available space. Use `objectFit: "cover"` for embedded video and verify content isn't tiny.
- **Cast-first character design**: When a video features characters (narrator, presenter, customer, etc.), define them once in a project cast and reuse those identities across scenes. Use the `characters` skill (react-peeps based). Scenes render cast members via a shared `<Character>` wrapper; never re-spec a character's look inline in a scene file.
- **Preview before polish**: Get rough animations working before fine-tuning timing, colors, and transitions. Working ugly beats broken beautiful.
- **Preserve user assets**: Never modify or overwrite user-provided assets (videos, images, audio). Copy or reference them in place.

---

## Project Rules

The rules below are declared as `type: local` entries in `capabilities.yaml` and installed by `capa install` into `.claude/rules/<id>.md`. They are loaded into your standing instructions via `@` imports here so Claude Code resolves them on every invocation (the `.claude/rules/` directory is not auto-loaded by the harness — the imports are what wire them in).

Add a new rule by: (1) dropping an `.md` under `./rules/`, (2) adding a `type: local` entry to `rules:` in `capabilities.yaml` pointing at it, (3) adding an `@` import below, (4) re-running `capa install`.

@.claude/rules/variants-as-compositions.md
@.claude/rules/auto-launch-studio.md
@.claude/rules/brand-icons-via-simple-icons.md

---

## Workflow Modules

Detailed reference guidance is split across modules in `.workflows/` and loaded below. Add a new module by dropping an `.md` under `.workflows/`, declaring it in `capabilities.yaml` under `workflows:`, and adding an `@` import here.

@.workflows/engine-selection.md
@.workflows/configuration.md
@.workflows/project-structure.md
@.workflows/variants.md
@.workflows/live-preview.md
@.workflows/environments.md
@.workflows/workflow-steps.md
@.workflows/quick-reference.md
