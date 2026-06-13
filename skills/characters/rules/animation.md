# Animating Characters Inside Remotion

`react-peeps` renders static SVG components. Animation happens at the **wrapper** level — transform, opacity, and position — driven by Remotion's `useCurrentFrame()`, `interpolate()`, and `spring()`. For deeper Remotion animation patterns, load the remotion skill's `rules/animations.md` and `rules/transitions.md`.

## Pattern 1 — Entrance: slide-in

```tsx
import { useCurrentFrame, interpolate } from 'remotion';
import { Character } from '../components/Character';

export const SceneIntro = () => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, 20], [-200, 80], {
    extrapolateRight: 'clamp',
  });
  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: 'clamp',
  });
  return (
    <Character
      id="narrator"
      style={{ position: 'absolute', bottom: 0, left: x, opacity }}
    />
  );
};
```

## Pattern 2 — Entrance: spring scale

```tsx
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';

const frame = useCurrentFrame();
const { fps } = useVideoConfig();
const scale = spring({ frame, fps, config: { damping: 12 } });

<Character id="customer" style={{ transform: `scale(${scale})` }} />
```

## Pattern 3 — Idle bob

Subtle vertical sine to make a character feel alive between gestures. Keep amplitude small (4–8px) — large motion reads as fidget.

```tsx
const frame = useCurrentFrame();
const { fps } = useVideoConfig();
const y = Math.sin((frame / fps) * Math.PI * 2 * 0.5) * 6; // 0.5 Hz, 6px amplitude

<Character id="narrator" style={{ transform: `translateY(${y}px)` }} />
```

## Pattern 4 — Gesture beat

Cued to the start of an audio segment (Step 7's per-segment voiceover). Use `spring()` for a quick "lift" at the segment boundary:

```tsx
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { timeline } from '../data/timeline'; // generated from voiceover

const frame = useCurrentFrame();
const { fps } = useVideoConfig();
const segmentStart = timeline.segments[2].startFrame; // beat aligned to scene 3
const lift = spring({
  frame: frame - segmentStart,
  fps,
  config: { damping: 10 },
});
const y = -lift * 12;

<Character id="narrator" style={{ transform: `translateY(${y}px)` }} />
```

## Pattern 5 — Expression swap

react-peeps lets you change `face` independently. Swap expressions on a beat to react to dialogue:

```tsx
import Peep from 'react-peeps';
import { cast } from '../cast';
import { useCurrentFrame } from 'remotion';

const frame = useCurrentFrame();
const reactAt = 45; // frame where the reaction lands
const spec = cast['customer'];
const face = frame >= reactAt ? 'Awe' : spec.face;

<Peep {...spec} face={face} />
```

This is the one case where bypassing the `<Character>` wrapper is OK — when the scene specifically needs a per-frame prop override. Keep the override local and short; if the same character needs the new look in multiple scenes, add a new cast id instead.

## Pattern 6 — Exit: fade + slide

```tsx
const frame = useCurrentFrame();
const exitStart = 90;
const x = interpolate(frame, [exitStart, exitStart + 20], [80, 280], {
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});
const opacity = interpolate(frame, [exitStart, exitStart + 20], [1, 0], {
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});

<Character id="narrator" style={{ left: x, opacity }} />
```

## Timing conventions

- **Entrance**: 15–25 frames at 60 fps (~250–400 ms).
- **Idle bob frequency**: 0.4–0.7 Hz — slower than a heartbeat.
- **Gesture lift**: 10–18 frames (~170–300 ms).
- **Exit**: same as entrance; symmetry feels natural.

These are starting points — tune per audio pacing.

## Performance

react-peeps renders once per frame. With a handful of characters on screen there's no measurable cost. If a scene has >10 simultaneous characters, memoize the inner SVG:

```tsx
const memoizedPeep = React.useMemo(() => <Peep {...spec} />, [spec]);
```

(Only do this if profiling shows it's needed — premature memoization adds noise.)
