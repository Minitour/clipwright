---
name: characters
description: Programmatic character/avatar design for Remotion videos using react-peeps. Defines a project cast in cast.yaml, scaffolds a typed cast.ts plus a Character.tsx wrapper with the skill's house style baked in (circular avatar, indigo background, black stroke, white fill, thin white rim, soft drop shadow).
metadata:
  tags: characters, avatars, cast, remotion, react-peeps
---

## When to use

Load this skill when a video plan includes any avatar/character — narrator, presenter, customer, mascot. The skill covers:

- **Designing a cast** — naming, roles, visual continuity across scenes.
- **Scaffolding** — translating a `cast.yaml` brief into a typed `cast.ts` and a starter `Character.tsx` wrapper.
- **Rendering** — using the cast in Remotion scenes via the shared `<Character>` wrapper.
- **Animation** — entrance, idle, gesture, and exit patterns inside Remotion.

Do **not** load this skill for projects with no characters.

## Hard rules

1. **Cast lives in `cast.yaml`, not in scene files.** Scenes import from `src/cast.ts` (which is generated from `cast.yaml`) and render via `<Character id="narrator" />`. Never instantiate `react-peeps` directly in a scene file — that breaks visual continuity and duplicates spec.
2. **One canonical look per character.** A character named `narrator` looks the same in scene 1 and scene 5. If two looks are needed, that's two characters (`narrator-day`, `narrator-night`).
3. **Defaults come from `[characters]` in `config.toml`.** The scaffolder reads the default library and the peeps house-style colors from there — don't hardcode these in `cast.yaml`.

## Which rule file to read

| Task | Rule file |
|------|-----------|
| Looking up react-peeps props (hair, face, body, accessory, colors) | `rules/react-peeps.md` |
| Designing a cast (naming, roles, when to add a character) | `rules/casting.md` |
| Animating a character (entrance, idle, gesture, exit) | `rules/animation.md` |

## Per-project setup

Run from the workspace root.

1. Install react-peeps into the project's Remotion sub-project:
   ```bash
   npm install react-peeps -w projects/<project>/remotion --legacy-peer-deps
   ```
   `--legacy-peer-deps` is needed because react-peeps' peer dep is React ^16.12 and modern Remotion projects use React 19.
2. Create `projects/<project>/characters/cast.yaml` from the plan's Cast table. See `rules/casting.md` for shape and naming.
3. Scaffold the typed cast **and** the starter `<Character>` wrapper in one step — from the project's `remotion/` directory:
   ```bash
   uv run --project ../../.. python ../../../skills/characters/scripts/scaffold_cast.py \
       ../characters/cast.yaml -o src/cast.ts \
       --component src/components/Character.tsx
   ```
   The wrapper is generated from the skill's react-peeps "house style" (circular avatar, indigo background, black stroke, white fill, thin white rim, soft drop shadow — values from `[characters.peeps_style]` in the workspace `config.toml`). The script **refuses to overwrite** an existing `Character.tsx` unless you also pass `--force`, so hand-edits are safe across re-runs.

   The generated wrapper has all visual constants at the top of the file — recolor or restyle the whole cast in one place by editing those constants.
4. Type-check:
   ```bash
   npx tsc --noEmit
   ```

## Using the cast in a scene

```tsx
// projects/<project>/remotion/src/scenes/SceneIntro.tsx
import { Character } from '../components/Character';

export const SceneIntro = () => (
  <AbsoluteFill style={{ background: '#0F172A' }}>
    <Character id="narrator" style={{ position: 'absolute', bottom: 0, left: 80 }} />
  </AbsoluteFill>
);
```

For animation patterns (slide-in, idle bob, gesture, exit) see `rules/animation.md`.

## Prop validation

`scaffold_cast.py` validates each character's prop values against `data/prop_enums.json` (extracted from react-peeps' installed `.d.ts` files). If the library publishes a new prop value not yet in the data file, extend the JSON rather than disabling validation — the goal is to catch typos like `hair: ShortVolumeD` at scaffold time, not at render time.

## Limitations

- **Monochrome by design.** react-peeps has exactly two color slots — `strokeColor` (line art) and `backgroundColor` (body/clothes silhouette). No separate skin tone, no per-feature colors. If you need per-feature color (skin / hair / clothes independent), this skill isn't the right tool — pick a different avatar library (e.g. avataaars, react-nice-avatar, DiceBear) and extend the skill.
- **SVG only.** If the plan calls for photoreal characters, this skill doesn't help.
- **React peer-dep mismatch.** react-peeps' peer dep is React `^16.12`. Install with `--legacy-peer-deps` on React 18+ projects.
