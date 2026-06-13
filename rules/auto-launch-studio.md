## Auto-launch Remotion Studio on first frame

**As soon as Scene 1 type-checks and renders a still successfully** (end of Step 6 Phase 1), launch Remotion Studio in the background and open it in the user's browser — without being asked. Hot reload gives the user something to watch while remaining scenes, audio, and assembly are built, instead of waiting for a finished mp4.

```bash
cd projects/<project>/remotion
npx remotion studio --no-open &   # background — capture port from banner
open "http://localhost:<port>"     # auto-open
```

### Only one Studio instance at a time

Before launching, check for an existing `remotion studio` background task and stop it if it's for a different project. If one is already running for the current project, don't start a second.

Variants registered via the `variants-as-compositions` rule appear in the same Studio automatically via hot reload — no second Studio is needed when adding compositions later.

### Headless fallback

Mention the URL to the user in plain text after launching so they can open it themselves if `open` fails (e.g. headless environments).
