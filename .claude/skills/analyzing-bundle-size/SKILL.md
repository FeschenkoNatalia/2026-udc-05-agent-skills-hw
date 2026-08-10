---
name: analyzing-bundle-size
description: Measuring the real weight of app/dist/bundle.js by running the project's own build. Use when asked how big the bundle is, what a change costs in bytes, or whether a widget is worth its weight — the number must come from scripts/measure-bundle.mjs, never an estimate. Not for explaining why the bundle is shaped the way it is; that's architecture-deep-dive.
---

# Analyzing bundle size

## When to use this

Any question whose answer is a number of bytes: "how big is the bundle?", "what
did that change cost?", "is adding this widget worth it?", "how much would
dropping X save?"

The reason this is a skill and not a guess: a model asked for a bundle size will
produce a plausible number, and a plausible number here is worse than no number —
it looks like measurement. **Run the script. Report what it prints.**

| Request | Skill |
|---|---|
| Why every widget ships, where code belongs | `architecture-deep-dive` |
| Add the widget whose cost was just measured | `creating-widget` |

## Instructions

One command. Paths below are **relative to this skill's own directory** — run
the copy you loaded, `.agents/skills/analyzing-bundle-size/` or the
`.claude/skills/` mirror. Either works, and from any cwd:

```bash
node <this-skill>/scripts/measure-bundle.mjs
```

It runs `npm run build` in `app/`, reads `app/dist/bundle.js` off disk, and
reports raw bytes, gzipped bytes, the bundle's exports, and which widgets are
actually registered:

```text
Bundle report — app/dist/bundle.js

  raw         937 B
  gzipped     505 B
  exports     create, listWidgets
  widgets     3  (badge, spinner, alert)
  per widget  ~312 B raw (average)
```

Flags: `--baseline=<bytes>` prints the delta against a previous run,
`--json` for machine-readable output.

### Measuring the cost of a change

Two runs, and the first must happen **before** you touch anything — there is no
stored baseline, so a number you didn't capture is gone:

```bash
node <this-skill>/scripts/measure-bundle.mjs              # note `raw`
# ...make the change...
node <this-skill>/scripts/measure-bundle.mjs --baseline=937
```

### Reading the result

- **`widgets` is the line that catches mistakes.** It comes from `listWidgets()`
  on the built bundle, so a widget missing from `app/src/widgets/index.ts` is
  absent here even though its files exist and its tests pass.
- **Every registered widget ships.** `widgets/index.ts` imports each widget for
  its `register()` side effect, so the bundler cannot tree-shake one that nobody
  calls. Size grows with the registry, not with usage — there is no unused-code
  saving to find.
- **Quote gzipped for "what users download", raw for "what changed".** Both are
  real measurements; say which one you're quoting.
- **`per widget` is an average, not an attribution.** It divides the whole
  bundle — runtime included — by the widget count. Don't present it as one
  widget's cost; for that, measure with `--baseline` around adding it.
- These are hundreds of bytes. Say when a delta is too small to act on rather
  than dressing it up as an optimization.

### Don't

- Don't estimate, extrapolate, or reuse a number from earlier in the
  conversation — rebuild, since the tree may have changed since.
- Don't install a bundle analyzer or add esbuild plugins. `app/` ships zero
  runtime dependencies and the build is deliberately ten lines.
- Don't "optimize" by deleting an import from `widgets/index.ts`. That doesn't
  tree-shake the widget, it unregisters it — `create("badge")` then throws at
  runtime while every test stays green.
- If the build fails, the script exits non-zero and prints no size. Report the
  failure; don't fall back to a guess.

## Verify

The script is the verification — it fails loudly rather than inventing a number.
To confirm it is measuring the real file:

```bash
node <this-skill>/scripts/measure-bundle.mjs --json
ls -l app/dist/bundle.js      # same byte count as `raw`
```

## Scripts

- `scripts/measure-bundle.mjs` — runs the project's own `npm run build`, then
  measures `app/dist/bundle.js`. Writes nothing itself, makes no network calls,
  and needs `npm install` to have been run in `app/`.
