## Live Preview — Auto-launch Remotion Studio

**As soon as Scene 1 type-checks and renders a still successfully** (typically the end of Step 6 Phase 1), launch Remotion Studio in the background and open it in the user's browser. Hot reload then gives the user something to watch while the remaining scenes, audio, and assembly are built — instead of waiting for a finished mp4.

```bash
cd projects/<project>/remotion
npx remotion studio --no-open &   # background — capture port from the banner
open "http://localhost:<port>"     # auto-open in browser
```

**Only one Studio instance at a time.** Before launching, check for an existing `remotion studio` background task. If one is running for a different project, stop it first. If one is already running for the current project, don't start a second.

Variants registered in `Root.tsx` (per the variants module) show up in the same Studio automatically via hot reload — no second Studio is needed when adding compositions later.
