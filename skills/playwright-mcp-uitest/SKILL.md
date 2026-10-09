---
name: playwright-mcp-uitest
description: Drive a frontend dev server through real browser flows using the MCP playwright tools to verify UI/UX changes end-to-end. Use when the user wants to "smoke test", "verify in the browser", "跑一下看看", "用 playwright 测试", "走一遍流程", "自动测试 UX 改动", or any time a code change touches rendered UI behavior (banners, dialogs, navigation, localStorage-driven state, hotkeys, animations) that build + unit tests cannot exercise. Triggers also include: "帮我测一下"、"在浏览器里验证一下"、"过一遍 happy path"、"E2E"、"smoke test"、"UI 回归". Complements (does not replace) the `verify` / `run` skills — this one is specifically the MCP-playwright-driven path. Project-agnostic.
---

# Playwright MCP UI smoke test

Drive a running dev server with the MCP `mcp__playwright__browser_*` tools to verify UI/UX behavior that build + unit tests cannot reach. Use this skill any time you change rendered UI (banners, modals, hotkeys, localStorage-driven state, multi-step flows) and want to confirm it actually behaves correctly in a browser.

## Before you do anything: preflight

Run these once at the start of a session. If any check fails, fix it BEFORE invoking any `mcp__playwright__browser_*` tool (those tools will error and waste turns).

### 1. Is chromium present in the Playwright cache?

```bash
ls ~/.cache/ms-playwright/ | grep -E "^chromium-[0-9]"
```

If empty: `npx playwright install chromium` (downloads ~150MB, takes 30-90s).

### 2. Is the MCP playwright server configured to use the bundled chromium?

```bash
python3 -c "import json,pathlib; print(json.dumps(json.loads(pathlib.Path.home().joinpath('.claude.json').read_text()).get('mcpServers',{}).get('playwright',{}).get('args',[])))"
```

Look for `"--browser"` followed by `"chromium"`. If missing, the MCP server will default to `chrome` channel and fail with `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome`.

Fix:

```bash
python3 <<'PY'
import json, pathlib
p = pathlib.Path.home() / '.claude.json'
d = json.loads(p.read_text())
args = d['mcpServers']['playwright']['args']
if '--browser' not in args:
    args.extend(['--browser', 'chromium'])
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print('updated — RESTART Claude Code for change to take effect')
else:
    print('already configured')
PY
```

**Critical**: MCP servers load at Claude Code startup. Config edits don't hot-reload. If you just made the edit, tell the user they need to restart — don't waste turns calling playwright tools that will keep failing.

### 3. Does the chromium binary actually launch on this OS?

```bash
~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome --version 2>&1 | head -1
```

If it errors with missing `.so` files (common on bare WSL), install deps:

```bash
sudo npx playwright install-deps chromium
```

(Needs sudo. If you don't have sudo, suggest the user run it themselves.)

## The standard flow

```
1. Start the dev server in background
2. Wait for "Ready" / port-bound signal
3. Navigate to the relevant URL
4. Drive the UI (snapshot → click → type → snapshot)
5. Verify the observable behavior
6. Stop the dev server
```

### Start dev server cleanly

For Next.js / Vite / similar frontend projects:

```bash
# Use Bash with run_in_background:true, NOT a foreground call
npm run dev 2>&1
```

Then poll for readiness via the background output file — don't use a blind `sleep`. Most frameworks print a recognizable string:
- Next.js: `Ready in`
- Vite: `ready in`
- Astro: `Local`

If the project uses nvm and the system node is too old, prepend `source ~/.nvm/nvm.sh && nvm use <version> &&` to the dev command.

### Get the URL

Most dev servers print `Local: http://localhost:<port>` — read it from the background output. Don't hardcode 3000 (already-running servers will pick the next free port).

### Drive the UI

| Goal | Tool |
|---|---|
| Open a page | `mcp__playwright__browser_navigate` |
| See current DOM (preferred over screenshots) | `mcp__playwright__browser_snapshot` (returns a11y tree with refs) |
| Click an element | `mcp__playwright__browser_click` (use the `ref` from snapshot, not CSS selectors) |
| Type into input | `mcp__playwright__browser_type` |
| Fill multiple fields | `mcp__playwright__browser_fill_form` |
| Wait for text to appear/disappear | `mcp__playwright__browser_wait_for` (avoid blind sleep) |
| Read/seed localStorage, run arbitrary JS | `mcp__playwright__browser_evaluate` |
| Visual proof (for the user, not for you) | `mcp__playwright__browser_take_screenshot` |
| Inspect console errors | `mcp__playwright__browser_console_messages` |
| Inspect network | `mcp__playwright__browser_network_requests` |

**Prefer snapshot over screenshot for verification.** Snapshots give you structured a11y data you can reason about (element refs, roles, text). Screenshots are pixels — use them only when the user wants visual proof or when visual layout itself is what's being verified.

### Seed localStorage / cookies before navigating

For flows that depend on prior state (saved drafts, auth tokens, feature flags), use `browser_evaluate` AFTER an initial navigate to set the keys, THEN reload:

```js
// Inside browser_evaluate function:
() => {
  localStorage.setItem('fesimu:practicePaperDraft:v1', JSON.stringify({
    paperKey: 'practice:AP:A:__all__:令和5年',
    questionIds: ['q1','q2','q3'],
    questionIndex: 2,
    startedAt: Date.now() - 60000,
    answers: { q1: { chosen: 'ア', correct: true } },
    updatedAt: Date.now(),
  }));
  location.reload();
}
```

Note: you must navigate to the site origin FIRST — `localStorage` is per-origin and inaccessible from `about:blank`.

### Stop the dev server

```bash
pkill -f "next dev"     # or "vite", "astro dev", etc.
```

Or `kill <bash-id>` if you tracked it. Don't leave orphan processes — they hold the port and block the next test run.

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome` | MCP server using `chrome` channel | Add `--browser chromium` to args in `~/.claude.json`, restart Claude Code |
| Tool errors `Browser is already in use` | Old playwright session never closed | `mcp__playwright__browser_close`, then retry |
| Click does nothing / element not found | Stale snapshot ref | Take a fresh `browser_snapshot` then click using the new ref |
| `EADDRINUSE` on dev server start | Previous run not killed | `pkill -f "next dev"` (or whatever) before starting |
| `localStorage is not defined` in evaluate | Page is `about:blank` | Navigate to the site origin first |
| Headless chromium fails to launch on WSL | Missing system libs | `sudo npx playwright install-deps chromium` |
| Banner/modal you're testing flickers on then disappears before snapshot | React effect race | `browser_wait_for` with the text, OR sleep ~200ms via `browser_evaluate` |
| Hotkey tests don't fire | Focus is on the wrong element | Click into the document body first or use `browser_press_key` after focusing |

## When NOT to use this skill

- Pure logic/data-layer changes — use unit tests (`node --test` etc.), faster and don't need a browser.
- Type-only refactors — `tsc --noEmit` / `npm run build` is enough.
- The user just wants to know what code changed — read the diff, don't render it.
- Public-web scraping — use `playwright-scraper` skill instead (different concerns: stealth, headers, anti-bot).

## Honest reporting

If you ran the flow: state exactly what you exercised and what you observed (which buttons clicked, which assertions held). Don't say "all good" when you only loaded a page.

If you could NOT run the flow (chromium missing, dev server didn't start, MCP not restarted yet): say so explicitly and ask the user to do the manual walkthrough. **Do not** claim verification you didn't actually perform — this is the rule from the project's `verification-before-completion` skill and applies here too.
