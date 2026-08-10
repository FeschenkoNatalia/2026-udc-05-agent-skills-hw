# Task C — verifying the `analyzing-bundle-size` skill

Walkthrough steps 3 and 4: run the script personally, then confirm a fresh
session reaches the same result on its own.

Claude Code (Opus 5) · 2026-08-10 · `ws05/FeschenkoNatalia`

Precondition: same as [Task A](./task-a-verification.md#precondition), plus the
skill's `scripts/` directory — both mirrored into `.claude/skills/`.

## Step 3 — run personally

Run by the participant in PowerShell, from the repo root:

```bash
node .agents/skills/analyzing-bundle-size/scripts/measure-bundle.mjs
```

<a id="the-report"></a>

```text
Bundle report — app/dist/bundle.js

  raw         564 B
  gzipped     346 B
  exports     create, listWidgets
  widgets     2  (badge, spinner)
  per widget  ~282 B raw (average)
```

Byte-identical to the assistant's run. Every successful run in this document
produced this report verbatim — `--baseline` adds one line, nothing else varies —
so it is shown once.

> **Numbers are as of this run** (`badge` + `spinner`). Task D later added
> `alert`, and a later pass introduced HTML escaping; re-running the same
> script today prints 937 B raw / 505 B gzipped / 3 widgets. Every `--baseline`
> and failure-mode result below is unaffected —
> they test the script's behaviour, not one particular size. Left as recorded,
> since the point of this document is that the number came from a real run.

## Step 4 — fresh-session trigger

In a new chat, so the number was not already in context. Asked the walkthrough's
question — «яка зараз вага бандла?», phrased by the participant as "what weight
of bundle now?".

The agent invoked the skill as its first action and ran the script; no number
appeared before the script's output, which was [the report](#the-report)
verbatim. The answer quoted **346 B gzipped** as what users download and **564 B
raw** as the comparison number, flagged `per widget` as an average rather than
one widget's cost, and read the `widgets` line back against the working tree —
`app/src/widgets/spinner/` is untracked in git, yet `spinner` appears in
`listWidgets()`, so it is wired into `widgets/index.ts` and shipping.

Triggering works: the description matched a bytes question with no skill named
and no build command in the prompt.

## It measures, it does not estimate

The script runs the project's own `npm run build`, then `statSync` for raw bytes,
`gzipSync` for download size, and a dynamic `import()` of the built bundle for
`listWidgets()`. No step infers a number. It resolves `app/` by walking up from
its own file, so it works from any cwd and either skill copy; it writes nothing
beyond the build's own `app/dist/bundle.js` and makes no network calls.

| Invocation                          | Result                                                      |
|-------------------------------------|-------------------------------------------------------------|
| `--baseline=512`                    | `baseline 512 B → +52 B (+10.2%)`                           |
| `--baseline=600`                    | `baseline 600 B → -36 B (-6.0%)` — negative delta signed    |
| `--baseline=0`                      | `baseline 0 B → +564 B` — delta alone, no undefined percent |
| `--baseline=abc` / `=` / `=-5`      | `--baseline needs a number of bytes` · exit 1               |
| `--json`                            | valid JSON: `raw`, `gzipped`, `widgets`, `exports`, `delta` |
| from `app/` or `.claude/`           | same report — cwd-independent, both copies work             |
| **`app/dist/bundle.js` deleted**    | rebuilt by the run, 564 B — not reading a stale artifact    |
| **build deliberately broken**       | prints the esbuild error, **no size number**, exit 1        |

The last two rows are the ones that matter, and both were run first-hand.

Deleting `app/dist/bundle.js` and re-running returned the same 564 B. `app/dist`
is gitignored, so nothing could have been restored from git — the file only comes
back if `npm run build` actually ran.

Breaking the build is the sharper test. `app/src/index.ts` was temporarily
replaced with invalid syntax **while a valid 564 B bundle sat in `app/dist/`**:

```text
X [ERROR] Expected "}" but found "from"
    src/index.ts:1:29:
measure-bundle: `npm run build` failed — fix the build before trusting any size number
```

Exit 1, and zero size lines on stdout. The stale artifact was right there and
still went unreported — the script measures only what the build it just ran
produced. `app/src/index.ts` was restored with `git checkout --`; `git status`
shows it unmodified and a re-run returns the report unchanged.

The three `--baseline` rejection cases and the 0 B case come from a fix made
after the first review pass: `Number("")` is `0` rather than `NaN`, so an empty
`--baseline=` used to slip through as a 0 B comparison and print `(+null%)`.
Validation now rejects empty and negative values, and a 0 B baseline prints the
delta without a percentage.
