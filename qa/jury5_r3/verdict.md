# CAHL Jury R3 — Juror 5/5 · PRODUCT CREDIBILITY lens · v52 · 2026-09-03

Method: static-source + API audit (owner-mandated Chrome-free round). Live-fetched: `/` (index.html),
`/static/js/app.js?v=52` (2943 lines, `node --check` PASS), `/static/css/style.css?v=52` (1950 lines),
`/api/today`, `/api/version`. Fetched artifacts + this verdict in `qa/jury5_r3/`.
Trajectory: R1 6.6 → R2 7.2 → R3 7.3. Still the panel's weakest lens.

## API verification

- `/api/version` → `{"js":52}` — matches `JS_VERSION = 52` (app.js:10) and `window.APP_VERSION = 52`
  (index.html:132). R2's reload-on-boot defect **verified fixed**.
- `/api/today` → **18 games, all real**: Dead Batteries, Purple Koolaid, Elmwood Iron Bucs, Ruckmoor
  Cannons, Goal Miners (Thursday), Hawaii 5-Hole (Thu), Nomads, White Lightning, Beerzerkers,
  Nite Caps, Mr. Mulch, District 5, Stingers… Real facilities (Chiller Easton/North/Dublin/Ice Works,
  NTPRD Chiller, OhioHealth Ice Haus). **Zero** Team Blue/Red scrimmage slots, **zero** Bye Week
  placeholders, zero placeholder names. Slate is clean.

## Fix verification (R2 → R3, my lens)

| R2 defect | v52 status |
|---|---|
| APP_VERSION 43 vs JS 51 reload-on-boot | **FIXED** — 52 = 52 = 52; self-heal branch retained for future bumps |
| "tonight 12:02 PM" stamp contradiction | **FIXED** — `UPDATED HH:MM`, `hour12:false`, no time-words (app.js:2708-2715); index.html:106 |
| Bye Week phantom game on Today tab | **FIXED at ingest** — `renderToday` is the sole writer of `state.todayGames` (app.js:1172) and `/api/today` returns zero Bye rows; standings filter retained (app.js:2264) |
| "vs"/"scrim" rendered in upcoming score cells | **STILL SHIPS** — app.js:1070 writes `<span class="t-score t-score-empty">vs</span>` (or `scrim`) into every unplayed row; the R2 defect verbatim |
| Saira 800 used but not loaded | **STILL SHIPS** — fonts link loads Saira Condensed 600/700 only (index.html:28); `var(--display)` + weight 800 at style.css:214 (.brand-text), 1341 (.team-watermark), 1357 (.lead-pts) → synthesized faux-bold |
| verBadge remnant ("verify zero references") | **FAILS the mandate** — badge element stays in HTML (hidden, index.html:85); JS still queries and labels it (app.js:21-22 `$ver.textContent = 'v' + JS_VERSION`); `.ver-badge` CSS block survives (style.css:259-266). Invisible to users but not removed |
| hero-next missing-opponent "vs @" dangle | **STILL SHIPS** — recent_result got its empty-opponent guard (app.js:1244 `hasOpp`), but the next_game line (1251) interpolates `ng.opponent` unguarded → "vs " dangle when ChillerStats omits the name. Guard was added to one of two sibling sites |
| /api/players cold latency | not re-timed this round (interaction lens owns it; tracked by R2-4) |

## New findings (R3)

1. **CRED-1 — literal escape sequence ships to users.** app.js:687 byte-verified via od:
   `box.innerHTML = '<div class="typeahead-item muted">No teams match\\u2026</div>'` — the double
   backslash in a single-quoted string means the Team-tab search empty state renders
   **"No teams match\u2026"** with a visible backslash-u glyph. `node --check` passes either way,
   which is why three fix rounds missed it. Sibling line 683 (`Loading teams\u2026`) is correct.
2. **Remaining "tonight" phrasing.** The stamp was cleaned, but headline copy still ships:
   "TONIGHT'S PACEMAKERS" (app.js:597, Players tab signature strip) and "Every game on tonight's
   Chiller slate" (app.js:1088, Today tab howto). Both are false at 12:00:01 AM; R2's
   "no remaining 'tonight' phrasing" mandate is only half-met.
3. **Score column header still "Score"** (not MATCH as mandated) at app.js:1105/1109 — and every
   empty upcoming cell beneath it displays the placeholder word "vs"/"scrim". All 18 games are
   unplayed at time of audit, so the marquee surface is 18 rows of "vs" placeholders in a column
   labeled Score. This is the strongest remaining hobby-project tell.
4. **Dead string:** palette group label "Tonight" (app.js:2873 ternary fallback) is unreachable —
   items are only page/team/player kinds. Placeholder copy from an earlier design.
5. **Off-token constants persist** despite the token layer: amber rgba(240,162,75) family ×5
   (form-chip.otl, streak-badge.otl, tl-game.otl, award-card.first-place, race-badge.alive +
   .my-team-star via --otl #f0a24b), raw `#fff` on .t-score.live-badge (style.css:708),
   `rgba(232,37,60,*)` ×16 as a second, brighter red outside `--accent` (comment admits
   "Goal Red, brightened for dark bg" vs locked #CE1126), rgba(42,127,212,*) Union-blue
   interaction washes ×18. Not user-visible as "wrong" but they are the drift the token system
   was supposed to prevent; casing/stamp/copy polish rounds have never touched them.

## Scoring (weights per brief)

| Dimension | Evidence (one line) | Score |
|---|---|---|
| 1. Visual identity 12% | CBJ broadcast identity reads (mono caps labels, display numerals, LIVE grammar) but TONIGHT'S PACEMAKERS + dead "Tonight" palette group copy a different hour | 6.5 |
| 2. Typographic system 12% | Saira/Inter/JetBrains Mono wired broadly; 3 `--display` 800 hooks synthesize bold (font ships 600/700 only) | 7.0 |
| 3. Color system 10% | CBJ tokens real, but off-token constants persist: amber ×5, raw #fff, brighter red ×16, Union washes ×18 | 7.3 |
| 4. Layout & hierarchy 12% | 11-track cols-head grid with calc() labels + <600px hide; hero/credit/nav collisions from R1/R2 stay fixed in source | 7.6 |
| 5. Density & data presentation 12% | Sticky theads, zebra, sortable th's, tabular-nums on shared table scope; ingest-level Bye filter confirmed at the single state writer | 7.6 |
| 6. Interaction & micro-feedback 10% | render-token guard, hashchange listener + boot-hash restore, 180ms debounce + stale-clear all verified in source | 7.8 |
| 7. Motion design 8% | LIVE pulse, score flash, entrance stagger; 3 reduced-motion guards; scrim rows muted non-clickable | 8.2 |
| 8. Depth & material 8% | Flat hairline surfaces, luminance tokens, no blur soup; faint/AA tokens raised both themes | 7.9 |
| 9. Consistency & component quality 8% | One scorecell anatomy, but empty cell = placeholder words vs/scrim, literal `\u2026` glyph, dead "Tonight" group, verBadge remnant | 6.8 |
| 10. Mobile ergonomics 8% | <480px card stack + cols-head hide in source; 44px targets re-declared; but cols-head overrides re-declared at EOF (cascade risk) — residual risk unverified (static) | 6.5 |

**Weighted total: 7.3/10**

## The 3 cheapest fixes (highest score lift)

1. **Empty-score-cell semantics** (delta ≈ +0.6 weighted): replace app.js:1070 `vs`/`scrim`
   strings with an em-dash `–` (or blank cell + status chip), rename the column header
   Score → MATCH (app.js:1105/1109), and drop the "scrim" word for muted Team Blue/Red slots.
   Kills the #1 hobby tell on the marquee surface; lifts consistency +0.8.
2. **Load Saira Condensed 800** (delta ≈ +0.4): add 800 to the Google Fonts URL (index.html:28) —
   one-URL change ends synthetic bold on brand-text, team-watermark, lead-pts; lifts type +0.7.
3. **Copy/dead-chrome sweep** (delta ≈ +0.4): fix `\\u2026` → real `…` (app.js:687), rename
   TONIGHT'S PACEMAKERS → LEAGUE LEADERS, palette group "Tonight" → "Pages", delete `#verBadge`
   (index.html:85) + `$ver` (app.js:21-22) + `.ver-badge` CSS (style.css:259-266), and add the
   missing `ng.opponent` guard at app.js:1251. ~8 line edits; every console-visible credibility
   defect in this lens is gone afterwards.

VERDICT: 7.3/10
