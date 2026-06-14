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
