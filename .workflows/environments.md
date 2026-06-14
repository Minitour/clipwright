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
