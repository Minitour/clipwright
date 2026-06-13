## Variants are new Compositions, not cloned projects

When the user asks for "another version" of an existing Remotion video — a different aspect ratio (Instagram Reels, vertical), different cast, different palette, different language, different copy — **add a new `<Composition>` to the existing project's `Root.tsx`**. Do **not** clone the project directory.

### Why

Remotion's composition model is built for this. Multiple compositions in one project share scenes, components, cast, audio, fonts, brand constants, and the build pipeline. Cloning fragments edits across copies, duplicates `node_modules` and rendered assets, and lets the variants drift over time.

### Trigger phrases

"give me another version", "a version with X", "an Instagram Reels version", "a portrait/landscape version", "the same but with X", "make a variant", "show me how it would look with X".

### How to model each variant kind

- **Different aspect ratio** — register a second `<Composition id="MainReel" component={MainVideo} width={1080} height={1920} ... />` alongside the primary one. Scenes use `useVideoConfig()` to detect dimensions and reflow.
- **Different content (icons, copy, cast, palette)** — parameterize the master `MainVideo` via `inputProps`. Register a second `<Composition id="MainVideoAlt" defaultProps={{ variant: 'alt' }} ... />`. Scenes read `useInputProps()` and branch.
- **Different cast** — declare both casts (`cast.yaml` + `cast-alt.yaml`), generate two `cast.ts` outputs, pick via `inputProps`. Or co-design one cast that both variants share.
- **Faster cut / different timing** — register a sibling root component with compressed timings as a separate `<Composition>`. See the `capa-launch` project for an example.

### Litmus test

If the only file that needs to differ between the two outputs is the `<Composition>` registration (or its `defaultProps`), it's a variant — same project, new composition. If the two outputs require different scene structures, different timelines, or different audio scripts, they're separate projects.
