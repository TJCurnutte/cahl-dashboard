# UI/UX JURY — R6, Juror 2/5 — MOBILE LENS (390×844)

Site: https://cahl.neural-forge.io · Deployed build verified: `/api/version` → `{"js":59}`, markup loads `style.css?v=59` + `app.js?v=59`, inline `window.APP_VERSION = 59`. Judged from deployed v59 bytes (style.css 85.4 KB / 2076 lines, app.js 151.4 KB) plus live API payloads (`/api/today`, `/api/league/{id}`). No browser automation; all rules traced from shipped source at the 390px viewport.

**Data context (honesty rule):** preseason thin — 2 upcoming games (both Chiller Dublin, 7:40/8:50 PM), standings all zeros, leaders all value 0. Per brief, penalized **only where design could compensate** (empty states, skeletons, marquee).

## Scores

| # | Dimension | Evidence at 390px | Score |
|---|---|---|---|
| 1 | Visual identity | Broadcast identity ships on mobile: rink-lines hero watermark (blue lines/red line/center circle, .05–.11 alpha), 2px union→accent header stripe, live-pill, CBJ-only hues. Saira Condensed numerals at 30–34px on the scoreboard. Distinctly hockey, never generic admin. | 9.6 |
| 2 | Typographic system | Three-stack discipline: Saira Condensed display (.sb-num 30→34px, .tonight-num 22px, .pace-stat 26px), JetBrains Mono labels collapsed to 3 tokens (--mono-xs/sm/md = 9.5/10.5/11.5px), tabular-nums forced on every numeric surface (line 134). Hierarchy survives 390px; 8.5–9.5px micro-labels are the cost of density at this width. | 9.4 |
| 3 | Color system | Goal Red strictly live/interactive (live pill, LIVE chip, sb-num live tint, .t-win uses --win not red); Union Blue structural (rink heads, pos-chips, pills); tint-based depth via panel→panel-3 ladder. Both themes' muted/faint re-tuned ≥4.5:1 with computed worst-case ratios documented in CSS. | 9.7 |
| 4 | Layout & hierarchy | v57 enrichment reads well on mobile: tonight-strip 4-KPIs → 2×2 at ≤599px, scored-strip auto-fill minmax(170px,1fr), by-rink h3 grouping. <480px today-rows re-grid into stacked cards (time|board, home, away, rink). Deductions: scored-chip "A – B" truncates at 390px (5-word names); upcoming games fall out of the by-rink branch when any final exists (JS: `upcoming.concat(finals.length ? [] : [])`) so late-night Final+Upcoming mixes collapse to one grouping — order-of-play lost. | 9.4 |
| 5 | Density & data presentation | Tables <900px are display:block + overflow-x:auto with 44px min-widths, first-column sticky, two-layer self-hiding right-edge fade + "swipe ›" chip, zebra via color-mix, tabular numerals. Sticky `th` top:0 is ineffective inside the block-table scroll container (header scrolls away with content) — nitpick, not a defect at this width. | 9.2 |
| 6 | Interaction & micro-feedback | Pull-to-refresh with progressive-opacity spinner hint; btn-press scale on pointerdown; nav :active 0.7 + transparent tap-highlight; 30s API ceiling + silent retry + render-token stale guard; loadTeamContent watchdogs at 8s/20s so skeletons can never be final state; toast confirms refresh. <100ms answered everywhere. | 9.7 |
| 7 | Motion design | Inventory audited line-by-line: LIVE dot/breathe, score-flash, entrance rise-in/fade-in with capped 5-child stagger, hero glow breathe, pull-to-refresh spinner — nothing decorative. Three full reduced-motion blocks + global 0.01ms transition kill; palette-safe. | 9.6 |
| 8 | Depth & material | Luminance-stacked surfaces (#070b12→#1a2334), hairline borders at 8–26% alpha, --blur:none with only the palette overlay at 3px (functional focus dim), shadows minimal on dark. No blur soup, no fake shadows. | 9.7 |
| 9 | Consistency & component quality | One scorecell anatomy (t-score pill w/ inset well, live-badge variant, em-dash empty placeholder — never the word "none"); chips/pills/badges (status-chip, race-badge, award-badge, pos-chip, strk, elim) all share mono+999px-radius+tint construction; sortable headers uniform `↓/↑`; scrimmages render muted non-links so fake matchups stop reading as data bugs. Inline `style=` on team-head headings is the only system leak. | 9.4 |
| 10 | Mobile ergonomics | v55 tap-floor verified: header cluster min-height/width 44px, nav 44/56px (48px on coarse pointers), th/td 44px, tl-game −11px hit extension, palette input 16px (no iOS zoom), safe-area insets on nav/main/toast/data-note, PTR, iOS tap-flash parity, swipe affordance. Remaining sub-44px: .pill ≈40.8px (level/day filters, 7-in-a-row thumb-cluster), .pal-item ≈38.2px, kpalBtn ≈33px wide. Same-team day filters sit in the stretch zone. Truncation tamed: ellipsis on names + self-hiding live-pill label; only scored-chip truncates. | 9.3 |

**WEIGHTED TOTAL: 9.5**/10
(identity 9.6×.12 + type 9.4×.12 + color 9.7×.10 + layout 9.4×.12 + density 9.2×.12 + interaction 9.7×.10 + motion 9.6×.08 + depth 9.7×.08 + consistency 9.4×.08 + mobile 9.3×.08 = 9.492 → 9.5)

Note: v57's scoreboard-first skeleton weakens in a specific preseason case — `liveNow.length` gates `scoreboardHtml`, and a Final-only slate (early evening before games post) renders no hero scoreboard at all. Not deducted further: design already compensates via tonight-strip + scored-strip, and the no-games empty state is a proper card, not a blank.

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Raise mobile touch floors on the shared controls (mobile 9.3→9.7, +0.03 weighted).** One append-only block: `@media (hover:none), (pointer:coarse){ .pill{min-height:44px} .pal-item{padding:14px 10px} #kpalBtn{min-width:44px} }` — same padding-only pattern as the R4 header fix. Est. delta +0.03.
2. **Recover the by-rink branch for mixed slates (layout 9.4→9.7, +0.04 weighted).** Change `upcoming.concat(finals.length ? [] : [])` → `upcoming.concat(finals)` so Final+Upcoming keeps rink grouping and chronological order; the single-`<h3>`-per-rink list handles mixed status since each row already carries its own chip. Est. delta +0.04.
3. **Stop scored-chip truncation with a two-line chip (layout/consistency +0.03 combined).** Replace the one-line "Home – Away" ellipsis with stacked home/away lines and the score right-aligned — matches the sb-card anatomy already in the system; no truncation possible at 320px. Est. delta +0.03.

Post-fix estimate: 9.6 weighted. The residual is structural — 390px cannot show the desktop header-over-both-groups craft or sticky-table headers, and preseason zero-leaders is a data ceiling design has already absorbed (empty states, watchdogs, em-dash placeholders).

VERDICT: 9.5/10
