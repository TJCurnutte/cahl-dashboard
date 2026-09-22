# JURY R6 — JUROR 1/5 — v59 (Chrome-free; source + live-API audit)

**Method:** Chrome automation is disabled by owner directive (standing rule). Scored from the
deployed bytes of `index.html`, `style.css?v=59` (85,364 B), `app.js?v=59` (151,365 B),
`/api/version` (`{"js":59}` — matches `JS_VERSION=59`, `APP_VERSION=59`, so no boot reload loop),
live JSON APIs, computed WCAG contrast math, and a 6-endpoint parallel burst. Dimensions that
would normally need rendered-pixel verification are marked **(static)** — scored from cascade-
resolved CSS/JS with line-level evidence. Prior-round fix claims were re-grepped against the
deployed bytes, not the fix logs; that discipline caught 9 dead claims in R5.

**Gate check — v59 release claims, byte-verified:**

| Claim | Evidence | Status |
|---|---|---|
| loadTeamContent self-recursion fixed | `app.js:2464` `window.loadTeamContent = loadTeamContent;` — single assignment of the function ref, no wrapper | ✅ FIXED |
| api() timeout (R4/R5 carry, 3 rounds) | `app.js:856-860` `new AbortController()` + `setTimeout(abort, 30000)` on the generic `api()`; comment cites the jury finding | ✅ FIXED |
| autoToggle zero feedback (carry, 3 rounds) | CSS:245-246 `.live-pill:has(#autoToggle:checked)` restyles pill + dot to `--win`; label updated to honest "Live status — click to toggle" | ✅ FIXED |
| Contrast carry (`--faint` 2.90:1 light) | R1-E pass L1853-1861 overrides `:root`: dark `--faint #7a8ca5` = 5.37:1 on panel; light `#5b6c85` = 5.35:1 on white (computed) | ✅ FIXED |
| Saira 800 faux-bold (carry) | Google Fonts href ships `Saira+Condensed:wght@600;700;800`; every `font-weight:800` rule resolves | ✅ FIXED |
| Hash routing + boot-race | `app.js:977` hashchange listener; `:2830` bootHash read BEFORE `setTab` with lowercase normalization | ✅ FIXED |
| Typeahead stale listbox | `taClearStale()` L404-419 swaps stale retry/error text for "Searching…" on new input | ✅ FIXED |
| Off-token hover `#3a8fe0` (carry) | STILL PRESENT at CSS:511 `button:hover { background:#3a8fe0 }` — third round carrying | ⚠️ OPEN |
| v57 Today enrichment | night KPI strip (`app.js:1150-1157`: Games/Rinks/Live-now/First-puck), scoreboard strip, By-Rink grouping (L1181-1199), rink-watermark hero (CSS:1590-1627) | ✅ SHIPPED — but see Defect R6-A |

**New defect found this round — Defect R6-A (the sharpest thing I can hand the owner):**
`todayPageHtml()` builds the By-Rink slate from `upcoming.concat(finals.length ? [] : [])`
(`app.js:1182`). That ternary appends nothing in every case, so **on any night with games at 2+
rinks, FINAL games vanish from the Today tab** — the Finals card renders only in the single-rink
`else` branch (L1193-1196). Preseason single-rink nights hide it today; it fires on the first real
multi-rink night. One-token fix (`concat(finals)`). Also found: `.scrim` class is emitted
(`app.js:1123,1126`) but defined **nowhere** in style.css (0 grep hits) — the recurring
"new JS class ships without its CSS" bug class from R1, again. And the desktop cols-head
labels render twice — real spans *and* `::after` pseudos both paint "Time/Home/Score/Away/Rink"
(CSS:2026-2049 defines the pseudos with the same content as the auto-placed spans at L1115),
a doubled-label artifact no pixel-verification round has caught.

---

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | Broadcast DNA is genuinely assembled now: rink-lines hero watermark (blue lines/red line/center circle/creases, CBJ hues at 0.08-0.11 alpha, CSS:1590-1627), Saira Condensed numerals (sb-num 30px), JetBrains Mono eyebrows/labels, CAHL wordmark + mono sub-label brand stack. Recognizably a hockey product, not a generic admin. Missing: one signature marquee moment at season scale — the "empty state" is a designed *statement* ("No goal data yet — season hasn't started", L2401-2402) rather than a broadcast asset (static). | 8.7 |
| 2 | Typographic system (12%) | Three-tier system held everywhere I traced: Saira Condensed 800 display (600/700/800 all shipped in the font href — faux-bold carry closed), Inter body, JetBrains Mono labels; tabular-nums on the universal numeral selector block (CSS:134-138: `table, .num, .sb-num, .t-score…`), mono scale tokens `--mono-xs/sm/md` defined AND applied to `.eyebrow/th/.status-chip/.sb-meta/.pal-grp` (L1995-1999). Stragglers: `.tonight-label` hardcodes 8.5px (L1665), `.brand-sub` 8.5px, live-pill 9.5px — micro-label sizes still scatter below the token floor. | 8.6 |
| 3 | Color system (10%) | Token discipline is strong: full CBJ palette (Union `#2a7fd4`/`#0057b8`, Goal Red `#e8253c`/`#ce1126`, Silver `#a2aaad`), luminance-stacked 4-deep panel ladder, status hues separated from brand. Computed contrast: every text token ≥4.55:1 on its surfaces in BOTH themes after the R1-E override — the old 2.90:1 light-faint carry is dead. Two blemishes: dark `--accent #e8253c` = **4.18:1 on panel** (sub-AA for the 9.5px red LIVE labels; `#ef3d54` = 5.13:1 at near-identical hue is a one-token fix), and `button:hover #3a8fe0` (CSS:511) is off-token third round running. | 8.6 |
| 4 | Layout & hierarchy (12%) | Marquee-vs-long-tail distinction is real: night-KPI strip → my-team hero → scoreboard → "On The Scoreboard" → by-rink groups. Desktop today header is an 11-track grid with computed `calc()` label positions that resolve label-over-column at 960/1200/1400 (±20px constant). But Defect R6-A breaks the marquee's completeness on multi-rink nights (finals dropped), and the cols-head double-label artifact (real spans + ::after pseudos) is a visible desktop defect. All-empty night renders strip + CTA + "No games posted yet." — correct order, thin mid-page. (static) | 8.5 |
| 5 | Density & data presentation (12%) | The strongest dimension: sticky thead (CSS:487), zebra on board/standings/roster (L2010-2016 with explicit even:hover), fully sortable tables (`sortTh()` with data-sort, keyboard focusable th[tabindex][role=button]), tnum on every numeric column, standings with playoff-cutoff line + clinch/elim states + streak chips, roster with per-GP rates. Zero-state design is a statement, not a shrug. No jiggle: min-width:0/minmax guards throughout. (static) | 8.8 |
| 6 | Interaction & micro-feedback (10%) | Every fetch path is now timeout-protected (generic api() 30s AbortController closes the 3-round infinite-skeleton carry; team path 8s/20s watchdogs; palette 15s/45s). 16ms typeahead debounce + stale-listbox clear; skeleton shimmer; button:active scale(0.97); retry buttons on every error state; toast role=status. Palette is a real dialog (aria-modal, role=listbox, focus management). Still missing: busy/disabled state on the refresh button during in-flight refresh — a double-tap fires parallel refreshes. (static) | 8.6 |
| 7 | Motion design (8%) | Vocabulary is disciplined: live-dot-pulse, score-flash (scale 1.35 + red), breathe on LIVE pill, entrance rise-in/fade-in ≤0.26s, palette pop. Three separate prefers-reduced-motion blocks neutralize every animation class incl. `transition-duration: 0.01ms` global kill. Nothing decorative found. Deduction: the hero-glow-breathe (4.5s infinite) is atmosphere rather than information — the one borderline-decorative animation. | 8.9 |
| 8 | Depth & material (8%) | Luminance-stacked surfaces done properly: 4-stop panel ladder, hairline borders at 0.08-0.26 alpha, 41 hairline usages vs exactly **1** backdrop-filter in the file, shadows are 1px structural (`inset 0 -1px`/`0 -2px`), no blur soups, no fake glows on cards. Watermark/hero glows sit at whisper opacity and are clipped (`overflow:hidden` on the card). Print stylesheet included. The `radial-gradient` hero wash is on-palette and subtle. | 8.8 |
| 9 | Consistency & component quality (8%) | One scorecell anatomy (sb-name/sb-num/status-chip/t-score) reused across scoreboard, today rows, game cards; chips/pills/badges from one system (status-chip, pos-chip, hero-record, award-badge all share border+radius+mono grammar). Deductions: `.scrim` class emitted with zero CSS (system hole), `.tonight-label`/`.brand-sub` off the mono token scale, `#3a8fe0` hover, cols-head label duplication. Append-only pass count is now high but I found no *dead* tokens this round — the mono tokens are actually wired. | 8.5 |
| 10 | Mobile ergonomics (8%) | 44px floors verified at source on nav links (44/56), themeToggle/refreshBtn (min 44), kpalBtn/live-pill (44 in ≤430 pass) — and the R2/R4 regression class (`min-h/w:0` inside max-width media) is **absent**: the only two `min-width:0` hits in a media block are at ≤699px on text containers (flex overflow guards), not controls. ≤479px stacks today rows into cards with explicit grid-areas; cols-head hidden <900 (a hidden header beats a smashed one); safe-area insets on nav + data-note; 16px inputs (no iOS zoom); -webkit-tap-highlight + :active parity; header wraps at <700. data-note sits in scroll flow, not the fixed nav. No truncation-soup patterns found. (static) | 8.7 |

---

## WEIGHTED TOTAL

identity 8.7×12% + type 8.6×12% + color 8.6×10% + layout 8.5×12% + density 8.8×12% +
interaction 8.6×10% + motion 8.9×8% + depth 8.8×8% + consistency 8.5×8% + mobile 8.7×8%
= **8.7 / 10** (unrounded 8.66)

Every dimension ≥ 8.5; none reaches the 9.7 gate. The all-dimensions gate fails.

---

## The 3 cheapest fixes to lift my two lowest dimensions (layout 8.5, consistency 8.5) to 9.7+

1. **Fix the By-Rink finals drop — `app.js:1182`.** Change
   `upcoming.concat(finals.length ? [] : [])` to build the rink groups from
   `upcoming.concat(finals)` and render a Finals subgroup (or a Final card) inside each rink.
   One token + ~6 lines of render logic. This is the only defect that makes the Today
   marquee *wrong* rather than merely thin. **Δ layout +0.7, consistency +0.25.**

2. **Kill the desktop cols-head double label — `style.css:2026-2049`.** The 11-track desktop
   rule auto-places the real spans (grid-area:auto) AND paints `::after` pseudos with the
   same "Time/Home/Score/Away/Rink" strings. Hide the span text (or keep spans textless and
   let pseudos carry the label). ~4 lines. A doubled header label on the marquee is the kind
   of pixel artifact that caps a visual round at 9. **Δ layout +0.4, consistency +0.3.**

3. **Ship the missing classes + token strays: define `.scrim`/`[data-scrim]` styling
   (≈3 lines: muted color + no pointer events), darken dark-theme accent to `#ef3d54` (one
   token, 4.18→5.13:1 on panel), and retoken `button:hover #3a8fe0`→`var(--union)`,
   `.tonight-label`/`.brand-sub`→`var(--mono-xs)` scale. Five one-line edits, all
   mechanical. Closes the last off-token hue (third round carried) and the last
   "JS class without CSS" hole. **Δ consistency +0.45, color +0.3.**

Combined Δ ≈ +1.35 on my card → both lowest dimensions reach 9.7+, total ≈ 9.4 —
still shy of the 9.7 all-dimension gate, which now requires a marquee-scale signature
moment and a live multi-rink night verified in a real browser.

VERDICT: 8.7/10
