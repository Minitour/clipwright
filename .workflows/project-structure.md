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
