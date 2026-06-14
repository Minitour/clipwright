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
