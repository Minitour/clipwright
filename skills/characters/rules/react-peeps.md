# react-peeps — Prop Reference

`react-peeps` (npm: [`react-peeps`](https://www.npmjs.com/package/react-peeps)) renders Open Peeps illustrations as React components.

## Minimal usage

```tsx
import Peep from 'react-peeps';

<Peep
  hair="ShortVolumed"
  face="Cute"
  body="Hoodie"
  accessory="GlassRoundThick"
  strokeColor="#0F172A"
  backgroundColor="#F5D7B7"
/>
```

The component returns SVG. Wrap or position it with the standard Remotion layout primitives — its rendered size is controlled by the parent (it has no `width`/`height` props that map to a fixed pixel count; it fills its container).

## Props

| Prop | Library type | Common values |
|------|------|-------|
| `hair` | `HairType` | `ShortVolumed`, `Short`, `Long`, `LongBangs`, `LongCurly`, `Mohawk`, `Bun`, `Afro`, `Bald`. Case-sensitive. |
| `face` | `FaceType` | `Cute`, `Smile`, `Calm`, `Concerned`, `Tired`, `Awe`, `Solemn`, `Suspicious`, `Hectic`, `Rage`. |
| `body` | `BustPoseType \| StandingPoseType \| SittingPoseType` | **Bust** (chest-up): `Hoodie`, `Shirt`, `BlazerBlackTee`, `Turtleneck`, `Sweater`. **Standing** (full body): `BlazerWB`, `ShirtPantsBW`, `WalkingWB`. **Sitting**: `CrossedLegs`, `WheelChair`. Use bust poses for portrait-style explainer videos. |
| `accessory` | `AccessoryType` | `None`, `GlassRoundThick`, `GlassAviator`, `SunglassClubmaster`, `Eyepatch`. |
| `facialHair` | `FacialHairType` | `None`, `Goatee`, `Full`, `Handlebars`, `MoustacheThin`. |
| `strokeColor` | `string \| GradientType` | Outline color for the linework. |
| `backgroundColor` | `string \| GradientType` | Solid hex or `GradientType` object. |
| `wrapperBackground` | `string \| GradientType` | Background of the outer wrapper (for circular-mask compositions). |
| `style` | `CSSProperties` | Standard React style prop (positioning, transforms). |
| `circleStyle` | `CSSProperties` | Styles applied to the outer circle wrapper. |

The full prop-value list lives in `skills/characters/data/prop_enums.json`, extracted from the library's `.d.ts` files. The scaffolder validates against this file and the generated `cast.ts` imports the real `HairType` / `FaceType` / etc. types from `react-peeps` so prop typos fail at both scaffold time and TypeScript-check time. If the library publishes new values not in the JSON, extend `prop_enums.json` rather than disabling validation.

## Gradient backgrounds

react-peeps accepts a plain object literal for `backgroundColor` / `strokeColor` / `wrapperBackground`. The shape comes from the library's internal `GradientType` type alias (`lib/peeps/types.d.ts`) — it is **not** re-exported from the package root, so don't try `import { GradientType } from 'react-peeps'`. The scaffolder inlines an equivalent local type in the generated `cast.ts`.

```tsx
import Peep from 'react-peeps';

<Peep
  hair="ShortVolumed"
  face="Smile"
  body="Hoodie"
  backgroundColor={{ degree: 0, firstColor: '#60A5FA', secondColor: '#1E3A8A' }}
/>
```

In `cast.yaml`, express a gradient with friendlier `from`/`to` keys — the scaffolder maps them to the library's `firstColor` / `secondColor`:

```yaml
narrator:
  library: react-peeps
  hair: ShortVolumed
  face: Cute
  body: Hoodie
  backgroundColor:
    gradient:
      degree: 0
      from: "#60A5FA"
      to: "#1E3A8A"
      # optional: type: LinearGradient | RadialGradient (defaults to library default)
```

## Default visual treatment (house style)

The skill ships an opinionated default look for react-peeps characters, baked into the `Character.tsx` wrapper that `scripts/scaffold_cast.py --component` generates:

| Slot | Default | Source |
|---|---|---|
| Circle background | `#818CF8` indigo | `[characters.peeps_style].circle_bg` |
| Character stroke (line art) | `#000000` black | `[characters.peeps_style].character_stroke` |
| Character fill (body/clothes silhouette) | `#FFFFFF` white | `[characters.peeps_style].character_fill` |
| Circle border (thin rim) | `#FFFFFF` white | `[characters.peeps_style].border_color` |
| Border width | `0.012 × size` (min 3px) | `[characters.peeps_style].border_ratio` |
| Drop shadow | `0 14px 32px rgba(0,0,0,0.45), 0 0 24px rgba(129,140,248,0.18)` | `[characters.peeps_style].drop_shadow` |

react-peeps has **three independent color slots** (stroke, body fill, wrapper background); the house style keeps them consistent across every character in the cast so the avatars read as one set. Per-character `strokeColor`/`backgroundColor` from `cast.yaml` are intentionally **ignored** by the wrapper for that reason.

To recolor the whole cast in a project, edit the constants at the top of the generated `Character.tsx`. To change the skill-wide default, edit `[characters.peeps_style]` in the workspace `config.toml` — new projects (or `--force` re-generations) pick up the new defaults.

## Sizing inside Remotion

Use the generated `<Character>` wrapper and pass `size` (single diameter — the wrapper is always square):

```tsx
<Character id="narrator" size={400} />
```

For positioning inside an `AbsoluteFill`:

```tsx
<AbsoluteFill>
  <Character
    id="narrator"
    size={400}
    style={{ position: 'absolute', bottom: 80, left: 100 }}
  />
</AbsoluteFill>
```

If you need to bypass the house style for one scene (e.g. a per-frame face swap is the documented exception — see `rules/animation.md` Pattern 5), import `Peep` directly **only** for that scene and pass the matching colors so the look stays consistent.

## Animation hooks

`react-peeps` components are static SVGs from React's perspective — animate them by animating the wrapper (transform, opacity, position) or by interpolating props frame-by-frame (e.g. swap `face` from `Calm` → `Smile` at a beat). See `rules/animation.md`.
