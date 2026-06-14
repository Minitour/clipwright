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

Studio (see live-preview module) shows every registered composition automatically — the user can scrub each one without restarting anything.
