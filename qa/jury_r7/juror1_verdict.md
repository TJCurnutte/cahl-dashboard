# JURY R7 — JUROR 1/5 — v61 (Chrome-free; deployed-bytes + live-API verification round)

**Method:** Standing rule — no browser automation. Scored from the deployed bytes of `index.html`,
`style.css?v=61` (86,371 B), `app.js?v=61` (153,328 B), `/api/version` (`{"js":61}` matching
`JS_VERSION=61` / `APP_VERSION=61` — no boot reload loop), computed WCAG contrast math, and live
JSON APIs (`/api/today` 0.68s, `/api/league/<id>` 1.27s, `/api/today/scores` 0.52s, `/api/leaders`
2.1s, `/api/teams` 2.9s, `/api/players` 27.5s cold / 34.5s under 5-way parallel burst). Rendered-pixel
dimensions marked **(static)**. All R6 fix claims were grepped against the fetched deployed bytes,
not fix logs — one process note: my first fetch round silently saved 404 pages (grep hit nothing);
re-verified HTTP 200 + byte counts before crediting anything.

**Gate check — my R6 (v59) cited fixes, byte-verified in deployed v61:**

| R6 citation | v61 evidence | Status |
|---|---|---|
| By-Rink mixed-slate finals drop (`finals.length ? [] : []`) | `app.js:1188` `upcoming.concat(finals)` with comment "finals used to vanish from this view (jury R6-1/R6-2 convergent find)"; single-rink Finals card branch intact at L1201 | ✅ FIXED |
| Desktop cols-head `::after` duplicate labels | File-wide `::after` census (30 hits) contains **zero** cols-head pseudos; L2039-2050 keeps the 11-track grid with auto-placed spans, comment at L2047 documents the removal | ✅ FIXED |
| `.scrim` class with zero CSS | Defined: `style.css:437-438` (`.t-home.scrim/.t-away.scrim` muted+italic, `:has(.scrim)` cursor:default). **Partial:** the scoreboard's `sb-card` also emits `data-scrim="1"` (`app.js:1084`) with no CSS hook — see New Finding A | ⚠️ MOSTLY FIXED |
| `button:hover #3a8fe0` off-token (3rd round carry) | Hue now a **named token** `--union-hover: #3a8fe0` (css:35) + `--union-hover-deep: #0d3a73` (css:97); hover rules are `var(--union-hover)` / `var(--union-hover-deep)` (css:516/520). No raw hex remains anywhere | ✅ FIXED |
| Label stragglers → `var(--mono-xs)` | `tonight-label` → `var(--mono-xs)` (css:1711), `brand-sub` → `var(--mono-xs)` (css:1947) — **inside media blocks only**; base rules still hardcode 9.5px (css:1672/240). Same rendered value today, fragile tomorrow | ⚠️ MOSTLY FIXED |
| Type census 28 → 14 distinct sizes | Full-census grep: 14 distinct hardcoded sizes (9.5/10.5/12/13/14/16/17/18/20/22/26/30/34px + 11pt print) + 12 var() consumers. All sub-9.5px stragglers (8.5/7.5) extinct. Claim verified exactly | ✅ FIXED |

**Other R6-era carries re-checked, also landed:** dark `--accent` now `#ef3d54` (css:37) — computed
**4.80:1 on panel, 5.13:1 on bg**, both AA (was 4.18:1); count-ups gated on
`prefers-reduced-motion` (app.js:773/779, R6-4's 3-round carry); refresh button now disables +
spinner-swaps with try/finally restore (app.js:890-906, my R6 interaction deduction); `api()`
30s AbortController intact (app.js:852-858).

**New findings this round (both small, both real):**

- **A — sb-card scrimmage path is still unstyled.** `app.js:1084` emits
  `<article class="sb-card" data-status="live" data-scrim="1">` for Live-Now scrimmage slots, but
  the only scrim CSS is the today-row variant (css:437). On the scoreboard the scrimmage card gets
  the full live-card treatment (red glow `::before`, LIVE chip, red text-shadow numbers) that the
  R5-era design ruling says scrimmage slots must not receive. ~3 lines to fix.
- **B — `/api/players` is the last slow endpoint, and it's getting worse.** 27.5s single-shot cold,
  **34.5s under a 5-parallel burst** (measured twice this round) — past the app's own 22s
  typeahead abort (app.js:309) and the 30s `api()` ceiling. First player search under any load is a
  guaranteed timeout-and-retry. 5.6MB payload suggests missing gzip/trim server-side, not client work.

---

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | Rink-lines hero watermark (blue/red lines, center circle, creases at whisper alpha), Saira Condensed display numerals, JetBrains Mono eyebrows, CAHL wordmark + mono sub-label, scored-chip/sb-card broadcast grammar. Recognizably a hockey-broadcast product. Still missing a marquee-scale signature moment at season scale — and this round's live slate (2 preseason games, 0 posted scores) gives the empty-state choreography real work to do, which it handles with strip + CTA + designed statement. (static) | 9.0 |
| 2 | Typographic system (12%) | Census verified at 14 hardcoded sizes, all ≥9.5px; every font-weight resolves in the font href (600/700/800 Saira shipped); tnum on the universal numeral block (css:134-138); scored-chip uses display-face numerals at 20px with tabular-nums. Deduction: the mono-token migration is half-landed — base rules hardcode the px that media blocks retoken (tonight-label 1672 vs 1711, live-pill 240, brand-sub 224 vs 1947); 7×12px + 19×13px declarations still bypass `--mono-md`. Zero visible defects at today's values; structural fragility only. | 8.9 |
| 3 | Color system (10%) | Computed contrast clean across the board: every text token ≥4.80:1 on panel in BOTH themes (dark faint 5.78, muted 5.97, accent 4.80, light faint 5.41); button hover hues now tokens whose white-on-fill contrast I computed (dark hover 3.40:1 AA-large on big bold text, light hover 11.23:1); status hues 6.18-9.23:1. Only blemish: dark `rink-head` uses `--union` at 4.46:1 (AA-large, not AA) where `--union-hover` at 5.43:1 sits one token away. | 8.9 |
| 4 | Layout & hierarchy (12%) | R6-A is dead: By-Rink groups now build from `upcoming.concat(finals)` with per-row status chips, so the mixed-slate marquee is *complete* — the only defect that made Today *wrong* is fixed. Night-KPI strip → hero → scoreboard → On The Scoreboard → By-Rink order holds; cols-head labels render once. Mid-page still thins on a 2-game night (correct behavior, thin content), and I could not pixel-verify the 11-track label calc at 960/1200/1400 without a browser. (static) | 8.9 |
| 5 | Density & data presentation (12%) | Sticky thead (css:492), zebra census 6 explicit even-rules, sortable th with keyboard roles, tnum on every numeric column, standings carry playoff-cutoff 6 + clinch/elim machinery + zero bye-week leaks in the live payload (verified against the fetched JSON, not just source). Live standings confirm all-zero GP renders with the designed zero-state, not a shrug. Preseason data poverty is handled by design everywhere I traced. (static) | 8.9 |
| 6 | Interaction & micro-feedback (10%) | Every fetch path timeout-protected and my R6 deduction (refresh double-tap) is closed — disabled + spinner + finally-restore at app.js:890-906. 16ms typeahead debounce, stale-listbox clear, retry affordances everywhere, palette is a real dialog, `:active` scale parity. Remaining friction is server-side: /api/players 27.5-34.5s beats both client ceilings, so the typeahead's "searching → retry" loop is doing honest work under load it shouldn't have to. (static + live probes) | 8.9 |
| 7 | Motion design (8%) | Vocabulary unchanged and disciplined: live-dot pulse, score flash, entrance ≤0.26s, palette pop; count-ups now respect reduced-motion (the last R6 motion carry); 4 separate RM blocks incl. the global 0.01ms kill; hero-glow-breathe remains the one borderline-decorative animation but it's RM-neutralized and clipped. (static) | 9.0 |
| 8 | Depth & material (8%) | 4-stop luminance panel ladder, hairlines at 0.08-0.26 alpha, exactly **1** backdrop-filter in 86KB of CSS, 1px structural shadows, watermark/hero glows clipped and whispered, print stylesheet present. No blur soup, no fake glow on cards. The scored-chip's inset-well treatment matches the material grammar. (static) | 9.0 |
| 9 | Consistency & component quality (8%) | One scorecell anatomy across scoreboard/today/game-cards (sb-name/sb-num/t-home/t-score); scored-chip rebuilt on the sb-card two-line pattern (css:1677-1699) — the R6-2 claim verified. Deductions: the sb-card `data-scrim` path ships without its CSS (New Finding A — the exact "JS class without CSS" bug class, 4th appearance, now down to one attribute), and the mono-token base rules lag their media-block retokens. | 8.9 |
| 10 | Mobile ergonomics (8%) | Release-gate grep clean: **zero** `min-width/height:0` inside any max-width media block (the R2/R4 regression class stays dead). Coarse-pointer 44px floors shipped (`.pill` min-height 44, pal-item 14px padding, kpalBtn 44 — css:2087-2091); pal-input 16px (no iOS zoom); ≤479px card-stack grid-areas; safe-area insets; tonight-strip still 4-across at 390px (KPI cells are min-width:0 flex so they compress rather than clip — downgraded from R6-3's defect to a nit). No truncation-soup patterns. (static) | 8.9 |

---

## WEIGHTED TOTAL

identity 9.0×12% + type 8.9×12% + color 8.9×10% + layout 8.9×12% + density 8.9×12% +
interaction 8.9×10% + motion 9.0×8% + depth 9.0×8% + consistency 8.9×8% + mobile 8.9×8%
= **8.9 / 10** (unrounded 8.928)

All 10 dimensions ≥ 8.9 — the band is now uniformly tight and no dimension carries a *visible*
defect at today's data; every remaining deduction is structural (token lag), server-side
(players latency), or unverifiable-without-a-browser. The 9.7 all-dimension gate still fails.

---

## The 3 cheapest fixes to raise my two lowest dimensions (typography 8.9, consistency 8.9) to 9.7+

1. **Finish the mono-token migration at the ORIGINAL rule bodies — ~6 one-line edits.**
   Rewrite `font-size: 9.5px` → `var(--mono-xs)` in the base rules the media blocks currently
   re-declare (`.tonight-label` css:1672, `.live-pill` css:240, `.brand-sub` css:224), then fold the
   7×12px and 19×13px declarations onto `var(--mono-md)` (13px → mono-sm or mono-md per role; one
   grep-driven pass). Same rendered pixels, but the census drops 14 → ~9 and future token edits
   propagate instead of straggling for a 6th round. **Δ type +0.6, consistency +0.2.**

2. **Style the sb-card `data-scrim` path — 3 lines at end of the R6 scrim block.**
   `.sb-card[data-scrim="1"] { cursor: default; } .sb-card[data-scrim="1"] .sb-name { color:
   var(--muted); font-style: italic; }` (+ drop the red text-shadow via that selector). This is the
   last JS-emitted state without CSS, and it currently paints scrimmage slots with the full
   LIVE-card glamour the design ruling reserves for real games. **Δ consistency +0.5, identity
   +0.1.**

3. **One-token hue swap + one mobile rule.** `rink-head` color `var(--union)` → `var(--union-hover)`
   in dark theme (4.46 → 5.43:1, css:1704; light theme already uses `--union-deep`) — one token;
   and `.tonight-strip { grid-template-columns: repeat(2, 1fr); }` inside the existing ≤599px block
   (css:1707) so the night KPIs breathe at 390px instead of compressing to ~80px cells — two lines.
   **Δ color +0.4, mobile +0.4.**

Combined Δ ≈ +1.1 on my two lowest → both reach 9.6-9.7; projected total ≈ 9.2. Honest ceiling
note: the last stretch to a 9.7 *median* is not made of CSS — it needs (a) a rendered-browser
verification pass to convert my (static) dimensions into pixel-verified ones, and (b) the
server-side `/api/players` fix (gzip/paginate or server-filtered search) so first-search succeeds
under real load instead of time-outing at 22-34s.

VERDICT: 8.9/10
