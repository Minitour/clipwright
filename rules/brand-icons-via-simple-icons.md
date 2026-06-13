## Brand / tool / platform icons — check `simple-icons` first

Before placing a text label for a tool, company, or platform anywhere in a video (agent name pills, integration grids, "as seen in" rows, comparison tables, social proof, footer logos, etc.), **check `simple-icons` first** — it ships ~3,000 official brand SVGs with each brand's hex color attached. Reach for plain text only when the target genuinely doesn't exist in the library.

### How to verify a slug exists (do this before importing)

The canonical slug list is `node_modules/simple-icons/icons/<slug>.svg` once installed, or `https://simple-icons.org/?q=<query>` / `https://github.com/simple-icons/simple-icons/blob/master/slugs.md` before install. Don't invent slugs — the react-peeps case showed that fabricated prop values are a real failure mode.

### Install (per-project, in the Remotion workspace)

```bash
npm install simple-icons -w projects/<project>/remotion
```

### Import (named, tree-shakable — preferred)

```tsx
import { siReact, siTypescript, type SimpleIcon } from 'simple-icons';
```

The naming convention is `si` + PascalCased slug (e.g. slug `claudecode` → `siClaudecode`, slug `react` → `siReact`). Each icon object exposes `title`, `slug`, `hex` (no `#` prefix), `path`, and `svg`.

### Canonical render component

Drop into `remotion/src/components/BrandIcon.tsx`:

```tsx
import React from "react";
import type { SimpleIcon } from "simple-icons";

export const BrandIcon: React.FC<{
  icon: SimpleIcon;
  size?: number;
  color?: string;       // override brand color (default = `#${icon.hex}`)
}> = ({ icon, size = 64, color }) => (
  <svg
    role="img"
    viewBox="0 0 24 24"
    width={size}
    height={size}
    fill={color ?? `#${icon.hex}`}
    aria-label={icon.title}
  >
    <title>{icon.title}</title>
    <path d={icon.path} />
  </svg>
);
```

### Dynamic lookup by string is a tree-shaking trap

If you must look up icons by a runtime string (e.g. an array of agent names), write an explicit small map of `name -> imported icon`:

```tsx
import { siReact, siTypescript, siNextdotjs, type SimpleIcon } from "simple-icons";

const ICONS: Record<string, SimpleIcon> = {
  react: siReact,
  typescript: siTypescript,
  nextjs: siNextdotjs,
};
```

Don't use `import * as icons from 'simple-icons'` — it pulls every icon into the bundle.

### Fallback rule

If `simple-icons` has no icon for the brand (verify by checking `node_modules/simple-icons/icons/` after install, not by guessing): use a text pill in the project's brand font. Don't substitute a different brand's icon "because it's close."

### Legal note

`simple-icons` is CC0-licensed but the brand marks themselves belong to their owners. Read https://github.com/simple-icons/simple-icons/blob/develop/DISCLAIMER.md before using icons in a commercial deliverable.
