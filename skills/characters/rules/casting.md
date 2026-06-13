# Casting — Designing a Project Cast

A **cast** is the set of characters that appear in a project's video. It is declared once in `projects/<project>/characters/cast.yaml`, scaffolded into `projects/<project>/remotion/src/cast.ts`, and referenced from scenes via a shared `<Character>` wrapper.

## Naming

- **ids are kebab-case** and describe the role, not the look: `narrator`, `customer`, `support-agent`, `customer-1`, `customer-2`.
- Stable across the project — renaming an id means updating every scene that uses it. Pick the name once.
- One canonical look per id. If the same role needs two looks (day vs. night, formal vs. casual), make them two ids: `narrator-day`, `narrator-night`.

## `cast.yaml` shape

```yaml
narrator:
  library: react-peeps
  hair: LongBangs
  face: Cute
  body: BlazerBlackTee
  accessory: None

customer:
  library: react-peeps
  hair: ShortCurly
  face: Smile
  body: Hoodie
```

Each top-level key is a character id. Every spec must include `library: react-peeps` and the props that library expects (see `rules/react-peeps.md`).

Per-character `strokeColor` / `backgroundColor` can be set in `cast.yaml` but are **ignored** by the generated `<Character>` wrapper — the skill's house style applies the same colors to every cast member so they read as one set. To change the cast-wide colors, edit the constants at the top of the generated `Character.tsx` (or `[characters.peeps_style]` in `config.toml` for the skill-wide default).

## The `<Character>` wrapper

The wrapper is **generated for you** by `scripts/scaffold_cast.py --component <path>`. It bakes in the skill's react-peeps "house style":

- Circular wrapper (`borderRadius: 50%`, `overflow: hidden`)
- Solid indigo background (`#818CF8` by default — from `[characters.peeps_style].circle_bg` in `config.toml`)
- Black line art (`strokeColor: #000000`)
- White body / clothes silhouette (`backgroundColor: #FFFFFF`)
- Thin white rim around the circle (border width scales with character size)
- Soft drop shadow with a hint of indigo glow

All visual constants are declared at the top of the generated file. To retheme the whole cast in one project, edit those constants — every `<Character>` instance picks up the change.

The wrapper's API:
```tsx
<Character id="narrator" size={400} face="Smile" style={{ position: 'absolute', bottom: 80, left: 100 }} />
```

- `id` — cast member id (typed `CharacterId` from the generated `cast.ts`).
- `size` — diameter of the circle in pixels (default `380`).
- `face` — optional per-frame face override (see Pattern 5 in `rules/animation.md`). Falls back to the canonical face from `cast.yaml`.
- `style` — merged into the wrapper div for positioning / transforms.

To regenerate the wrapper from scratch (e.g. after pulling new defaults from the skill):
```bash
uv run --project ../../.. python ../../../skills/characters/scripts/scaffold_cast.py \
    ../characters/cast.yaml -o src/cast.ts \
    --component src/components/Character.tsx --force
```

## When to add a new character vs. reuse one

**Add a new character when:**
- The role is different (presenter vs. audience member).
- The character appears alongside another character in the same scene (two visible roles = two ids).
- Two looks of the "same person" need to coexist (`narrator-day` / `narrator-night`).

**Reuse the same character when:**
- The same role appears in multiple scenes and should look identical.
- A character is off-screen in some scenes — they don't need a new id just because they aren't visible.

## Cross-scene continuity

The point of the cast is that `narrator` in scene 1 and `narrator` in scene 5 are the same component instance, with the same props. If you find yourself wanting to "tweak the narrator's hair just for scene 3," resist it — either commit to the new look (rename the cast member, update everywhere) or skip the tweak. Mid-video drift is the failure mode the cast model is designed to prevent.

## How casting flows through the workflow

1. **Step 1 (Concept Definition)** — the agent asks whether the video has characters and at what roles.
2. **Step 3 (Video Plan)** — the plan's "Cast" section lists every character as a table row.
3. **Step 5f (Project Initialization)** — the agent writes `cast.yaml` from the plan's Cast table and runs the scaffolder.
4. **Step 6 (Scene Implementation)** — scenes import `<Character id="…" />` instead of the avatar library directly.
