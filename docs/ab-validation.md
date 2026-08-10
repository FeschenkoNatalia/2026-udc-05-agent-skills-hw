# A/B validation (Task D)

**Skill under test:** `creating-widget`
**Prompt (same for A and B):** the change request from `materials/ab-task.md`
(add an `alert` widget) — pasted verbatim, not reworded between runs.
**Tool used:** Claude Code (Opus 5) · 2026-08-10 · `ws05/FeschenkoNatalia`

**Preconditions.** A: the skill was present in `.agents/skills/` and mirrored into
`.claude/skills/`, and was invoked as the run's first action. B: no
`creating-widget` existed anywhere in the tree (repo-wide search for
`*creating-widget*` returned nothing) — absent, not merely renamed.

## Result

Both runs produced the same three files and left `core/registry.ts` untouched:
`widgets/alert/alert.ts` (factory + module-level `register("alert", createAlert)`),
`widgets/alert/alert.test.ts` (2 colocated cases), and the side-effect import in
`widgets/index.ts`. Both: `AlertProps extends WidgetProps`, named exports, no
`any`, `props.tone ?? "info"` mirroring `createBadge`. Both green on `npm test`
(3 files / 7 tests) and `npm run typecheck`.

| Aspect | A (skill available) | B (skill removed) |
|---|---|---|
| File location, `register()`, colocated test | correct | correct |
| Named exports / no `any` | yes | yes |
| Wired into `widgets/index.ts` | yes | yes |
| ID-collision check before writing | yes — `grep -rn 'register("'` | not run |
| Discovery before first write | 4 calls / 1 tool round | 8 file reads / 4 tool rounds |
| Bundle `listWidgets()` check | **run** — `[ 'badge', 'spinner', 'alert' ]` | **not run** — stopped at tests + typecheck |

## Conclusion

Read down the table: **three rows are ties, three are not.**

**No difference in the output** (rows 1–3). Same files, same structure, same
exports, same wiring. `app/AGENTS.md` and the two example widgets already teach
the convention, so B copied it correctly without the skill.

**The entire gap is two skipped checks** (rows 4 and 6). B never ran the
ID-collision `grep`, and never ran `npm run build` + `listWidgets()`. The second
is the one that matters: it is the *only* check that catches a forgotten
`index.ts` import, because tests and `tsc` stay green without it — every test
imports its widget directly. B's import was correct by luck, not by verification.
Neither check is inferable from reading `badge.ts`, which is exactly why the
codebase alone could not supply them.

**Plus cost** (row 5): one tool round instead of four.

**Verdict:** keep the skill for its checks, not its pattern — the pattern is
already in the repo. Its value would grow on a repo with no example widget to
copy.

> **Later change to `alert.ts`.** After this comparison, review flagged that
> `props.message` was interpolated into HTML unescaped, so all three widgets were
> hardened with a shared `escapeHtml` helper and runtime `tone`/`size` narrowing.
> That is a change to the artifact both runs produced, not to the comparison:
> neither A nor B escaped anything, so the row-by-row result above stands as
> recorded. Worth noting that **the skill did not catch it either** — the version
> run in this comparison checked wiring and registration in `## Verify`, not
> output safety. The current skill has since gained an output-safety check there.
