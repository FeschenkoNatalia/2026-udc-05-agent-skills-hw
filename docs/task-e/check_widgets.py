"""Renders the built widget bundle in a real browser and checks what came out.

Task E (bonus) — driven by the community `webapp-testing` skill vendored at
`.agents/skills/webapp-testing/`. Server lifecycle is handled by that skill's
`scripts/with_server.py`, so this file is Playwright logic only, per its
SKILL.md.

Run from the repo root:

    python .agents/skills/webapp-testing/scripts/with_server.py \
        --server "python -m http.server 8765" --port 8765 \
        -- python docs/task-e/check_widgets.py
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8765/docs/task-e/harness.html"
SHOT = Path(__file__).parent / "harness.png"

EXPECTED_WIDGETS = {"badge", "spinner", "alert"}

console_lines: list[str] = []
page_errors: list[str] = []


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 700})

        page.on("console", lambda m: console_lines.append(f"{m.type}: {m.text}"))
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        page.goto(URL)
        page.wait_for_load_state("networkidle")

        registered = page.locator("#registered").inner_text()
        cases = page.locator(".case")
        rendered = [
            cases.nth(i).get_attribute("data-widget") for i in range(cases.count())
        ]

        page.screenshot(path=str(SHOT), full_page=True)
        browser.close()

    print(f"URL        : {URL}")
    print(f"registered : {registered}")
    print(f"cases      : {len(rendered)} -> {', '.join(rendered)}")
    print(f"screenshot : {SHOT}")
    print("console    :")
    for line in console_lines:
        print(f"  {line}")

    failures = []

    for name in sorted(EXPECTED_WIDGETS):
        if name not in registered:
            failures.append(f"{name!r} missing from listWidgets()")

    # Every widget factory returns markup, so an empty box means the string
    # arrived but rendered to nothing.
    if len(rendered) != 7:
        failures.append(f"expected 7 cases, rendered {len(rendered)}")

    if "tooltip-missing" not in rendered:
        failures.append("unregistered-widget case did not render")

    # A pageerror is an uncaught exception; the expected registry throw is
    # caught in the harness and only shows up as a console error.
    if page_errors:
        failures.append(f"uncaught page errors: {page_errors}")

    if not any('Unknown widget "tooltip"' in line for line in console_lines):
        failures.append("registry did not throw on the unregistered name")

    print()
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print("OK: all widgets rendered in a real browser; registry threw as expected")
    return 0


if __name__ == "__main__":
    sys.exit(main())