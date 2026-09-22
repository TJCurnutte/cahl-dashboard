# JURY R5 — Juror 1/5 — CAHL Dashboard v55 (Chrome-free source+API audit)

Method: fetched live bytes from prod (/, style.css?v=55, app.js?v=55, /api/version, /api/today,
latency burst) and audited source + WCAG math. No browser automation (owner constraint held).
Fetched artifacts: 8.5KB shell / 82.8KB CSS / 145KB JS. `{"js":55}` — shell links ?v=55 both assets.

## v55 fix verification (deployed bytes)

| Item | Status | Evidence |
|---|---|---|
| `<=430` header squeeze | **PASS** | style.css:1863 media block: `#kpalBtn,.live-pill{min-height:44px}`, `#themeToggle,#refreshBtn{min-height:44px;min-width:44px}`; compaction is padding/typography only; the R2-class `min-height:0/min-width:0` exists nowhere in the ≤430 block. (Two `min-h/w:0` hits live at line 1094 inside `@media (min-width:900px)` desktop nav-row compaction — pointer devices, not a regression.) |
| iOS tap-highlight | **PASS** | style.css:1885 `-webkit-tap-highlight-color: transparent` on `a,.nav-link,.today-row .link,.typeahead-item,.pal-item`; `:active` parity at 1888 (`opacity:.7`); `button:active{transform:scale(.97)}` global. |
| live-pill 44px | **PASS** | `min-height:44px` ≤430 (line 1872) + `height:44px` (1881). |

## Standing ledger (R3/R4 defect re-checks)

| Item | Status | Evidence |
|---|---|---|
| Saira 800 loaded | **PASS** | page.html:28 Google Fonts URL includes `Saira+Condensed:wght@600;700;800`; `--display` = "Saira Condensed"; `.sb-num` 30px/700 display, `.t-score` 16px/700 display, hero numerals 800. |
| Rink-lines watermark | **PASS** | style.css:1580+ full block: center red line, quarter blue lines, goal lines, 180px center circle ring + inset shadow crease, both themes, `.hero-card{overflow:hidden}` clip, 130px at ≤479px, static (reduced-motion safe). |
| Em-dash score cells | **PASS** | app.js:1069 `\u2013` in `.t-score-empty` with `aria-label="Not started"`; word "vs" survives only in the mobile-stacked `.game-card` matchup (different component, acceptable). |
| MATCH header | **PASS** | app.js:1104/1108 cols-head `Time/Home/Match/Away/Rink`. |
| verBadge | **PASS** | zero `verBadge` refs in all three artifacts. |
| live-pill pure status | **PASS (label only)** | `syncLivePolling` sets `LIVE`/`NO GAMES LIVE` (app.js:910-911); BUT the hidden `#autoToggle` checkbox (page.html:96) is still wired (app.js:2686) with **zero checked-state feedback** — 0 `:checked` rules in CSS, title still says "click to toggle". R4-4 defect #1 unshipped. |
| Bye Week / Team Blue ingest | **PASS** | scraper.py:251/262 filters in repo; live `/api/today` payload has 0 placeholder team names (0 "bye week", 0 "team blue", 0 "team red"). |
| Version sync | **PASS** | `/api/version` = `{"js":55}` = asset URLs. |
| "tonight HH:MM" contradiction | **PASS** | data stamp is 24h "UPDATED HH:MM" (app.js:2710 comment; no `tonight'+time` concat). |
| api() watchdog | **FAIL** | generic `api()` (app.js:~824) still bare `fetch` — no AbortController/timeout. League/Players/Analytics sub-skeletons have no watchdog; hung fetch = infinite skeleton. R4-4 defect #2 unshipped. |
| Hash routing | **PASS** | `hashchange` listener + `TAB_HASH` re-entrancy guard (app.js:~932). |

## 10-dimension scores

| Dimension | Evidence | Score |
|---|---|---|
| 1. Visual identity | Rink-at-night canvas (#070b12), Chiller 3D logo + skate mark, CBJ-only hues, rink-lines hero watermark (center circle, blue/red lines, crease), Goal Red reserved for live/interactive. Instantly a hockey broadcast product, not an admin. Defect: watermark is hero-only — League/Players/Analytics have zero signature geometry. | 8.7 |
| 2. Typographic system | Saira Condensed 800 actually loads (600/700/800); 30px `.sb-num` display numerals, JetBrains Mono on 53 declarations, `table{font-variant-numeric:tabular-nums}` global, mono token scale (--mono-xs/sm/md) applied to chips/th/eyebrows. Defects: 28 distinct px sizes still in cascade (append-only consolidation, 3rd round); live-pill label shrinks to 9.5px mono under tappable 44px pill. | 8.5 |
| 3. Color system | One accent law holds: Goal Red only on live pill, LIVE chip/badge, active-tab inset underline, win tint; Union Blue on interactive/focus; status green/amber/red; tint-based surfaces (bg→panel→panel-2→panel-3) both themes. Defects: --accent dark #e8253c = 4.18:1 on panel (AA-large only, small text fails); --faint 3.35:1 dark / 2.90:1 light (fails normal text both themes, R3 finding unchanged); 11 keyframes tinted off --faint rely on the weak hue. | 8.9 |
| 4. Layout & hierarchy | Marquee (Live Now scoreboard, hero) vs long-tail (Final/Upcoming sections, sortable league table, cut-line storytelling) is clean; grid areas label every zone; `main{padding-bottom:calc(72px+safe-area)}` clears bottom nav. Defect: hero = one pinned team's card on an empty slate — marquee zone is under-used zero-state; hero-cta variant is one line of text + button. | 8.3 |
| 5. Density & data presentation | `position:sticky` thead ×2, 20 zebra `nth-child` rules, `data-sort` th with data-rt secondary sort + keyboard focusable, tabular numerals everywhere, rink-name compression (Chiller→short forms). Defect: sticky header count is 2 — League/Player tables rely on generic table styling; sort affordance is cursor+title only (no icon column header styling cue beyond arrow). | 8.4 |
| 6. Interaction & micro-feedback | button:active scale(.97), nav/:active opacity parity, 14 :focus-visible rings, debounced 180ms typeahead with stale-listbox clearing, replay-protected hashchange, aria-live announcer, palette + Cmd+K. Defects: generic api() has no timeout → infinite skeleton risk on 4 tabs (R4-4 #2); live-pill is a mislabeled toggle (hidden checkbox, no checked state, title says "click to toggle" while label is pure status — R4-4 #1). | 8.0 |
| 7. Motion design | 11 keyframes, all purposeful: live-breathe/dot-pulse, score-flash with reflow-restart, palette pop/fade, entrance rise-in/fade-in, hero pulse; prefers-reduced-motion kills card/sb-card/fade-in animations + transforms (4 refs). Defect: entrance animations not individually gated under reduced-motion for all selectors (partial coverage), and no reduced-motion guard on .sb-num text-shadow glow. | 9.0 |
| 8. Depth & material | Luminance-stacked solid surfaces (no backdrop-filter soup: 0 refs), 1px hairline borders in 3 strengths, inset wells, single soft shadow tokens; hero-card overflow clip keeps watermark/glow contained. Defect: depth system is quiet to a fault — panels differ by ~4-5 RGB points, low surface legibility between nested cards. | 8.8 |
| 9. Consistency & component quality | One scorecell anatomy (.t-score chip / .sb-num), chips/pills/badges share pill anatomy (status-chip, elim, live-pill, race-badge: same radius/mono/tracking system), 28 aria-labels, 27 roles. Defects: live-pill doubles as invisible toggle (component-boundary violation); select styling ships 16px but native dropdown chrome differs per-platform. | 8.4 |
| 10. Mobile ergonomics | ≤430 header: all 4 controls ≥44×44 via padding-only squeeze; nav links min-height:44/min-width:56 (base) with mobile block restoring 44px; ≤479 rows stack to labeled card grid; main clears nav + safe-area; tap-highlight transparent + :active parity; select/input 16px (no iOS zoom); zero games in payload → no truncation soup. Defect: live-pill 44px height with 9.5px label; data-note/footer overlap fixed since R2 — no other 390px regression found in CSS. | 8.9 |

**WEIGHTED TOTAL: 8.6/10** (identity 1.044 + type 1.020 + color 0.890 + layout 0.996 + density 1.008 + interaction 0.800 + motion 0.720 + depth 0.704 + consistency 0.672 + mobile 0.712 = 8.566)

## 3 cheapest fixes (highest score lift per line of code)

1. **api() timeout + abort ≈ 12 lines** (app.js:~824): add AbortController + 20s timer mirroring the existing team/palette watchdogs; return `{error:'Timed out'}` on abort. Kills the infinite-skeleton class on League/Players/Analytics. Est. **+0.3** (interaction 8.0→8.6, consistency +0.1).
2. **live-pill honesty ≈ 8 lines**: either (a) make it a real toggle — `#livePill:has(#autoToggle:checked)` CSS state (bg tint + dot green) — or (b) delete the hidden checkbox, drop the toggle wording from title, render a `<span>`. Zero `:checked` rules exist today; the title lies to screen readers and pointers alike. Est. **+0.2** (interaction +0.2, consistency +0.1).
3. **Contrast pass on --faint ≈ 3 lines**: bump `--faint` to #7488a3 dark / #6b7c92 light (or swap 11 keyframe/chip usages to --muted) — brings 3.35:1/2.90:1 pairs to ≥4.5:1. Fixes the last standing R3 AA finding and un-breaks 11 faint-tinted keyframes. Est. **+0.15** (color 8.9→9.2, type +0.1).

Projected post-fix weighted total: ~9.25/10 (still short of the 9.7 bar — identity/layout need the watermark motif extended beyond the hero, and zero-season states need a designed marquee).

VERDICT: 8.6/10
