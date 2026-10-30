# Tests

Browser and data tests for The Capital Map. They check the built site (`data.js`, `index.html`) and the SQLite export, not the Markdown alone, so **run `python3 tools/build.py` first**.

## Setup (once)

```
pip install playwright
python -m playwright install chromium
```

The suites launch Playwright's **full** Chromium (`channel="chromium"`), not the lighter headless shell. The headless shell doesn't open new tabs, so the Ctrl+click checks in `test_links`, `test_about` and `test_flows` would crash. To use a browser that's already installed, set `CAPMAP_CHROME` to its path.

## Running

```
python3 tests/run_tests.py . tests/out --mode auto --suite test_<branch> [other suites]
```

- **`quick`** runs the named suites plus the smoke set (`test_links`, `test_hubs`, `test_public`, `test_flows`), at desktop width only. Use it for content-only branches: pages, flows, quals, questions, docs. It takes about 1–3 minutes.
- **`full`** runs every suite at 1366, 390 and 360 px. Use it for engine or layout changes (`assets/`, `tools/`, `index.html`, `_headers`, `robots.txt`).
- **`auto`** picks between them from the files the branch changed.
- One suite on its own: `python3 tests/suites/test_<name>.py . tests/out`
- Output goes to `tests/out/`, which is git-ignored. It holds screenshots and logs.

**Read the results before pushing.** A suite fails on any failed check *or* any browser console error.

## Rules for changing a test

- **Tests change in the same PR as the change they test.** That's why they live in the repo.
- **A failing test means either the code or the expectation is wrong. Decide which before you edit.** If an earlier test's expectation has to change on purpose (a new page shifts an order, say), change it with a dated comment and list it in the PR body.
- **Worked examples are recomputed, not copied.** A test builds the expected figure from its formula, such as `f"{1.01 ** 12:.4f}"`, so a wrong number on the page fails.
- **Reject rules are tested with a deliberately bad record**, built on a throwaway copy of the site (`test_links`, `test_figures`, `test_flowset` and others do this). A rule that's never seen bad input proves nothing.
- **Pinned tables** (`EXPECT`, `PLAN`, `FLOWS`, `PATH`, `GROUPS`, `BRANCHES`) are the agreed state. Update them when the agreed state changes, never to make a failure go away.

## The suites

There's one suite per branch or feature: `test_howtothink`, `test_marketsmove`, `test_quals`, `test_failures` and so on. Each file's docstring says what it covers. Several suites also guard content rules: neutral wording, timeless wording, no quotations lifted from source material, and credited sources.

## Not in this folder

The pre-commit **privacy scan** is kept outside this public repo on purpose, because its blocklist is itself private. Run it before every commit, as well as these tests.
