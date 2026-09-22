# UI/UX JURY — R2, Juror 4/5 — INTERACTION LENS
Subject: https://cahl.neural-forge.io v51 · 2026-09-03
Method note: Chrome remote debugging was disabled by the owner mid-round, so **runtime scoring is (static analysis) + live API timing**; the one desktop screenshot (Today/1440×900, `today_desktop.png`) predates the switch. Round-1 defect re-verification is code-path-verified against the deployed `app.js?v=51` / `style.css?v=51`.

## Round-1 defect re-verification (mandated)
| Claimed fix | Verdict | Evidence |
|---|---|---|
| Team-tab hang (watchdog + retry) | **FIXED** | `loadTeamContent` L1774–2008: 8s "Still loading" nudge → 20s `teamErrorHtml` ("Timed out after 20s" + Retry button), AbortController @25s, try/catch/**finally** clears both watchdogs and writes error card — skeleton cannot be a final state |
| League zero-API first-run | **FIXED** | `renderLeague` L1240–1246: no saved league → auto-selects `state.leagues[0]` via `chooseLeague` (persists + loads content) |
| Stale typeahead messages | **FIXED** (team box) | `taClearStale` L381–393 wipes retry/muted text on every new query; 180ms debounce L417–421; result guarded by `input.value !== q` re-checks |
| Hash deep-link `/#team` | **FIXED** (minor gap) | boot reads hash **before** `setTab` (L2683–2685, correctly ordered), `replaceState` mirroring L928–932. Gap: `TABS.includes(bootHash)` rejects `#Team`/#TEAM` and there is no `hashchange` routing reaction (listener string present but never registers a handler) — back/forward doesn't re-render |

## Interaction findings (harshest lens)
1. **Backend serializes concurrent requests** (live, severe): rapid-typing burst of 6 lookup queries → one query **30.8s to first byte**, another 29.2s; parallel tab-load burst `/api/players` (5.6MB) 27.1s. Client mitigations are real — per-keystroke `lookupCtrl.abort()` L329, debounce, 220ms typeahead timer + value re-checks, kpal seq-guard + own controller — so the *UI* shouldn't show stale text, but the palette can legitimately sit on "Searching the league…" for tens of seconds on a cold index. Warm repeat: 1.55s. Perceived-performance drag is real and measured.
2. **Version-guard reload loop (live, verified):** index ships `window.APP_VERSION = 43`, `app.js` demands `JS_VERSION = 51` → scripted `location.reload()` on **every** first load of a session (sessionStorage only suppresses repeats). Every visit starts with a full page reload: perceived first paint cost + jarring flash.
3. **Render race on rapid tab switching** (static analysis): `loadActiveTab` writes skeleton then `await render*` with **no tab/sequence guard after await**; every `render*` ends `setMainHtml(html)`. Rapid Today→Team→Today lets the slow Team response paint Team content into the Today view (self-heals on next tab click, but wrong-content flash is possible).
4. **Refresh double-fire:** `$refresh.disabled = true` synchronously → HTML-disabled buttons can't re-click: single + rapid mashing is safe (static analysis). **But `refreshAll` has no try/finally** — if `loadActiveTab` throws before `catch`... (covered) — the residual risk is a network-level throw outside `api()`'s own catch; button could stay spinner+disabled. Low probability, nonzero.
5. **Dead legacy code shipping a visible bug:** `_legacyBindTeamSearch` (L675) is never called, yet remains in the bundle with `'No teams match\\u2026'` — a literal backslash-u string users would see if ever reactivated. Dead weight, zero risk today, sloppy.
6. Sort clicks: delegated `th[data-sort][data-rt]` handler toggles dir, re-renders from client cache — fast, no refetch (static analysis). ⌘K palette: seq-guarded server lookup with dedicated AbortController, clamped arrows, Enter runs item, Escape closes, backdrop click closes — clean.
7. **Zero stuck-loading states** — code-path sweep: today/league/team/players/analytics + league Sessions/Calendar/Compare sub-sections all pair `skeletonHtml()` with a catch → `.error` write; team adds the 8s/20s watchdog; players shows explicit error+Retry states. Only residual: `refreshAll` without try/finally (finding 4).

## Scoring table (weights per brief)
| # | Dimension | Evidence (one line) | Score |
|---|---|---|---|
| 1 | Visual identity | Real product: Chiller oval mark, rink-night navy/red, LIVE pill, condensed scoreboard faces — not generic admin | 8.5 |
| 2 | Typographic system | Saira Condensed ×28 / JetBrains Mono ×54 / Inter body, tabular-nums ×36 — verified in shipped CSS | 8.0 |
| 3 | Color system | Goal Red #e8253c rationed to live/interactive, --win green, tint depth; light-theme pink wash + blue banner excursion | 8.5 |
| 4 | Layout & hierarchy | Marquee hero + two-up slate reads well; Today card bottom-right dead zone (9 vs 10 rows); empty-state gaps | 7.5 |
| 5 | Density & data presentation | Sticky `th` top+left, zebra ×6, sortable everywhere, tabular-nums; 100-row cap w/ Show-all | 7.5 |
| 6 | Interaction & micro-feedback | Debounce/abort/seq-guards all present, but backend serialization = multi-second stalls; version-guard reload on every boot; render race | 7.0 |
| 7 | Motion design | 11 keyframes all semantic (live-pulse, score-flash, shimmer, fade); full reduced-motion kill + `transition-duration:0` global; count-up 400ms ease-out | 8.0 |
| 8 | Depth & material | Luminance-stacked --bg/--bg-raise/--panel, hairlines; exactly 1 blur (palette overlay 3px) — no blur soup | 8.5 |
| 9 | Consistency & component quality | One scorecell anatomy, chips/pills/badges from one system, 14 :focus-visible, 26 inline-onclick legacy patterns linger | 8.0 |
| 10 | Mobile ergonomics | 23 breakpoints, 44px targets ×2, coarse-pointer rules; card-fallback presence not exercised (no runtime) | 7.0 |

**WEIGHTED TOTAL: 7.8/10**
(exact 7.85 → 7.8)

## 3 cheapest fixes with most score upside
1. **Sync `window.APP_VERSION` to 51 in the HTML template** (one-line): kills the guaranteed reload on every visit; first-load feels instant. Δ ≈ +0.4–0.6 (interaction, layout-perceived).
2. **Sequence-guard `loadActiveTab`** (capture `state.tab` before await, compare before `setMainHtml`; ~6 lines): removes wrong-tab content flash under rapid tab switching. Δ ≈ +0.3–0.4 (interaction).
3. **try/finally in `refreshAll`** (+ honor `prefers-reduced-motion`-safe restore of the label, ~4 lines): closes the only remaining stuck-control path. Δ ≈ +0.2 (interaction, consistency).

(Systemic, outside front-end: backend request serialization is the single biggest perceived-performance ceiling — worth an infra ticket.)

VERDICT: 7.8/10
