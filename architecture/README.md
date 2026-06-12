# architecture/ — fleet system map

Self-portrait of the whole `E:/automation` fleet. Tracked in #94 — **design iteration**, not yet the finished `/system-map` skill.

**Source of truth is [`ARCHITECTURE.md`](ARCHITECTURE.md)** — the layered, fixed-schema description of the system (compute → connectivity → enabling tools → working apps → governance). The visual is generated *from* that doc, so the knowledge lives in words first and the picture can't go stale.

## The visual: `system-map.html` → `system-map.png`

A **light-theme, horizontal, Janis-style** infographic — grouped zone panels, every project a card with a one-line description. Built as **hand-authored HTML/CSS**, chosen over Mermaid so each block carries real text and the layout is fully controlled.

**Replicable by design:** the template and the data are separate. All content lives in one `const DATA = {…}` object near the bottom of `system-map.html` (governance / access / edge / compute / enabling / web / pipe / external + principles); the CSS + a small `render()` lay it out. Updating the map = edit the data object — the `/system-map` skill will populate it from `hooks/projects.toml` (membership + the `architecture_ignore` list), each repo's README/CLAUDE.md (descriptions), and `ARCHITECTURE.md` (layer assignment).

### Local specs — kept out of git 🔒

The committed `DATA.compute` (and the committed `system-map.png`) show **placeholder** hardware specs. Real GPU/CPU/RAM are personal detail, so they live in **`system-map.local.js`** (gitignored via `*.local.*`). `system-map.html` loads it with a plain `<script>` tag — works under `file://`, no CORS — and merges `window.LOCAL` over the placeholders. Missing on a fresh checkout → harmless 404, placeholders stay.

```powershell
cp system-map.local.example.js system-map.local.js   # then edit in your specs
```

So a local render shows your real specs; anything pushed (PNG, HTML, the issue, Slack) shows placeholders.

### Render

Data is inline, so **no web server is needed** (unlike a `fetch()`-based page) — render straight from `file://`:

```powershell
cd architecture
# measure first (DIMS logged to stderr), then screenshot at that size:
& "C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu `
  --enable-logging=stderr --v=0 --virtual-time-budget=8000 --window-size=400,300 `
  --screenshot=_m.png "file:///$($PWD.Path -replace '\\','/')/system-map.html"   # read "DIMS w h"
& "C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu `
  --hide-scrollbars --force-device-scale-factor=2 --window-size=<w>,<h> `
  --virtual-time-budget=8000 --screenshot=system-map.png "file:///$($PWD.Path -replace '\\','/')/system-map.html"
```

### Render gotchas (kept from the Mermaid exploration)

1. Measure the page's `scrollWidth/scrollHeight` (logged to console as `DIMS w h`), then size the screenshot window to it — no empty canvas, nothing clipped.
2. If a future variant `fetch()`es a sibling file, `file://` blocks it via CORS — serve over `http://` then. Inline data (as here) avoids it.
3. Verify legibility by cropping the rendered PNG to full-res regions (e.g. with PIL) and inspecting — the on-screen thumbnail downscales too far to trust.

> History: an earlier dark, vertical **Mermaid** auto-layout lost too much information and was retired in favour of this doc-first HTML/CSS approach.
