# JURY R9 — JUROR 1/5 — v67 (Chrome-free; deployed-bytes + live-API verification round)

**Method:** Standing rule — no browser automation. Scored from the deployed bytes of
`index.html` (13,161 B), `style.css?v=67` (88,795 B), `app.js?v=67` (156,937 B),
`landing.css?v=67` (8,928 B), `/api/version` = `{"js":67}` with `const JS_VERSION = 67`
in the shipped bundle (no boot reload loop), plus HTTP-200-fetched image assets and live
JSON APIs. Every fetched asset was header-checked (correct Content-Type, plausible byte
size) before grepping — the R7 process rule held again. Computed WCAG contrast math in
Python. All rendered-pixel claims remain **(static)** except where byte-decoded from PNGs.

**Gate check — my R8 cited fixes, byte-verified in deployed v67:**

| R8 citation | v67 evidence | Status |
|---|---|---|
| (1) Scrim card LIVE material fully stripped — border/background/::before/text-shadow with `!important`, marker "R8-1: scrim cards must not carry LIVE material" | `style.css:449-452` ship the marker comment plus exactly the prescribed rules: `.sb-card[data-scrim="1"] { border-color: var(--border-soft) !important; background: var(--panel) !important; }`, `::before { display: none !important; }`, `.sb-num { color: var(--muted) !important; text-shadow: none !important; }`. R8 sibling-selector census redone: all three live-material rules (`css:352` red border wash, `css:358` animated glow bar, `css:405` red num halo + shadow) are each countered by the `!important` block. The residual `.sb-live` pulsing chip is **honest** material: a scrim slot *is* live on the sheet — status without game pretense. | ✅ FIXED (full) |
| (2) The 5 raw error sites (1635/1702/2306/2317/2446 in v63) esc()'d — zero raw `${data.error}` / `${e.message}` | Census: **0** raw `${data.error}` and **0** raw `${e.message}` in the whole 156KB bundle. Former sites now read `esc(e.message)` (v67 L1637, L1704) and `esc(data.error)` (L2317). Full-file census: **all 8** `data.error` interpolations escaped (L1300, 1471, 1942, 2008, 2013, 2317, 2328, 2354); `esc()` used 153×. 153 calls with zero raw interpolations closes the R7-5/R8-4 class file-wide, not just at the flagged sites. | ✅ FIXED (census-clean) |
| (3) Sponsor gold tokenized — `--sponsor-gold` #b8925e dark / #7a5c2e light, landing.css consumes it | `style.css:37` `--sponsor-gold: #b8925e` (:root) + `style.css:100` `#7a5c2e` (light block, comment "R8: light-surface sponsor gold (AA-safe on panel)"). landing.css now consumes `var(--sponsor-gold, #b8925e)` at L133/170/202. Computed: dark **6.42:1** panel / 6.86:1 bg; light **6.18:1** white / 5.66:1 panel-2 — every combination ≥ AA for the mono micro-labels it colors. The 4 hover rules cited at 2.87:1 in R8 are dead; the fallback hex exists only as a var fallback (fires only if style.css fails to load — acceptable). | ✅ FIXED |

**Standing ledger re-verified, still holds in v67:** `concat(finals)` (app.js:1214, comment
documents the R6 fix), refresh busy-state, count-up RM gate (app.js:799/805), api() 30s
AbortController + silent retry (L884-896), typeahead 180ms debounce + stale-clear, watchdog
8s/40s with the 40s deadline above the 30s ceiling, hash routing, cold-index copy "up to
~30s" (L533), pal-input 16px (iOS zoom), tap-highlight transparent (css:1978), coarse-pointer
44px floors (css:2102/2104/2121 + nav 48px css:1176), tnum ×20, sticky ×2 + coarse first-col
freeze, zebra ×6, backdrop-filter census **1** in 88KB of style.css, dark accent #ef3d54
4.80:1 panel, rink-head #4a9ae6 6.19:1, dataStamp minute-ticker (app.js:2917-2924).
Leader rows: League (app.js:1576-1582) and Players (app.js:282) both gate the link
affordance on `p.player_id`; live payload today ships **15/15 leader rows with
`player_id: null`** and the link affordance is correctly absent — R8-B's dead-link class
verified fixed against the live API, not just the source.

---

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | The gate is now a full marketing landing: sticky nav (CAHL crest + mono uppercase About/Features/Sponsor + Open Dashboard CTA), hero crest at 340px with headline "Every Game. Every Stat. One Dashboard.", four feature cards with gold mono chip icons, About origin story with an honest non-affiliation note, sponsor card, footer CTA. Faint rink-lines watermark runs down both page margins at 0.07 alpha — the signature identity asset carries the marketing surface, not just the app. Rink-radial blue/red backdrop, Saira display throughout. Effort: fetched index + both stylesheets + all 3 image assets; byte-decoded the lockup PNG. (static) | 9.5 |
| 2 | Typographic system (12%) | style.css census unchanged: 8 px values (13×19, 14×10, 16×20, 18×2, 20×15, 26×3, 30×2, 34×2) + one 11pt print rule; app.js **zero** font-size literals. But the new landing.css ships its own 16-value ad-hoc scale (11px chips, 12.5px footer, 13.5px blurbs, 44px hero, 15/17/19px) instead of consuming the token system it already uses for mono sizes — a second type scale now lives in the product. | 9.3 |
| 3 | Color system (10%) | Computed both themes: dark text 16.86 / muted 5.97 / faint 5.78 / accent 4.80 / **sponsor-gold 6.42** on panel; light text 17.31 / muted 5.13 / faint 5.41 / accent 5.63 / **sponsor-gold 6.18** on white. CTA #1f6cb8 with white = 5.39:1. Two blemishes: CTA hover #3a8fe0 with white = **3.40:1** (sub-AA on the marketing page's primary control), and the transparent sponsor lockup decodes to mean luminance 0.466 — **2.03:1 on the white sponsor card** in light theme (9.06:1 dark). | 9.5 |
| 4 | Layout & hierarchy (12%) | Landing: nav → hero → features (auto-fit grid) → about → sponsor → footer, clean single-column rhythm with centered 860/900px measure. App: Night-KPI → hero → scoreboard → On The Scoreboard → By-Rink intact, `concat(finals)` verified live, sponsor strip anchors Today's long tail. Anchor nav (#lp-about/#lp-features/#lp-sponsor) is provably inert to the app router: handler checks `TABS.includes(h)` (app.js:1005-1010) and TAB_HASH has no collision with the #lp- namespace. Could not pixel-verify 11-track cols-head without a browser. (static) | 9.3 |
| 5 | Density & data presentation (12%) | tnum ×20, sticky thead + coarse first-column freeze, zebra ×6; R8-2's table scroll-context fix now engages at the right element (`@media (max-width:699px) .card:has(table) table { display:block; max-height:65vh; overflow-y:auto }`, css:2113-2115). Live payload: 2 games, **0** Bye Week / Team Blue / Team Red rows; 6-team all-zero standings renders the designed zero-state. No jiggling-column patterns. (static + live payload) | 9.4 |
| 6 | Interaction & micro-feedback (10%) | Every fetch path ceiling-protected; retry affordances on every error path; gate CTAs all three wired (gateEnter/gateEnterCta/gateEnterFoot) with 0.45s fade + focus-to-main. Remaining friction is server-side: **/api/players 4.1s warm single-shot (best ever measured) but 30-34s under 5-parallel burst at 2.2-5.6MB decoded** — the burst still straddles the 22s typeahead / 30s api() ceilings; measured this round (warm-labeled). | 9.2 |
| 7 | Motion design (8%) | Vocabulary unchanged and disciplined: live-dot pulse, score flash, live-breathe — all retired on scrim cards (R8 fix). RM census: 3 style.css blocks + landing.css block + print + JS gate on count-ups (app.js:799-805). Gate exit 0.45s fade is purposeful; `.pal-ov .spinner` covered (css:1217). New-surface RM check: landing transitions all inside its RM block. One non-blocking note: lp-hero crest drop-shadow is static, not animated. (static) | 9.4 |
| 8 | Depth & material (8%) | 4-stop luminance ladder (#070b12/#0e1420/#131b2b/#1a2334), hairlines, backdrop-filter census **1** in style.css; landing.css adds 2 (nav blur + none else) — the sticky marketing nav blur is a legitimate, standard pattern and the only blur on that surface. Byte-decode of `upright-lockup.png`: 1192×394 RGBA, **67.5% fully-transparent pixels** — the background removal claimed in the brief is real, not a white-box JPEG. Single soft shadow on sponsor card; no blur soups. | 9.4 |
| 9 | Consistency & component quality (8%) | One scorecell anatomy; error-escape class closed file-wide (8/8 escaped); sponsor system one-kicker-stronger on the landing card. Deductions: (a) landing.css forks the type scale — 16 literal sizes when the same file already consumes --mono-xs/sm/md and --display, so the fork is choice, not ignorance; (b) Today's sponsor strip still uses the 128KB **crown PNG** while the landing card uses the **lockup** — two different sponsor marks in one product (HTTP 200, 127,825 B verified). | 9.4 |
| 10 | Mobile ergonomics (8%) | Release-gate grep clean; 44px floors verified at css:2102 (.pill), 2104 (#kpalBtn), 2121 (button.small), nav 48px (css:1176); pal-input 16px; table scroll context at 699px; tonight-strip 2×2 at ≤430px; safe-area + tap-highlight; landing adds 719px and 430px breakpoints (title 27px, CTA 50px). One gap: `.lp-cta-sm` (Open Dashboard in the nav) sits at **42px** — 2px under the floor, and it's the header control most likely to be thumb-hit. (static) | 9.4 |

---

## WEIGHTED TOTAL

identity 9.5×12% + type 9.3×12% + color 9.5×10% + layout 9.3×12% + density 9.4×12% +
interaction 9.2×10% + motion 9.4×8% + depth 9.4×8% + consistency 9.4×8% + mobile 9.4×8%
= **9.4 / 10** (unrounded 9.378)

Every dimension ≥ 9.2; eight of ten ≥ 9.3. All three R8 fixes landed **full** — first round
where nothing I cited required partial credit. The 9.7 all-dimension gate still fails; the
two dims under it (type 9.3, layout 9.3) are now dragged by the *new* landing surface, not
by the app: landing.css's forked type scale and the dual sponsor marks are consistency debt
inside an otherwise excellent marketing page.

---

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Retokenize landing.css onto the design system's scale — ~10 declarations.** The file
   already consumes `var(--mono-xs/sm/md)` and `var(--display)`; finish the job: map
   11px→`var(--mono-md)` (12px) or define `--mono-2xs` once, 12.5px→`var(--mono-md)`,
   13.5px→14px (the sanctioned tier), 15px→14 or 16, 19px→20, 44px hero and 26px h2 may
   stay as governed display sizes. One file, one pass, no layout risk. **Δ type +0.3,
   consistency +0.2.**

2. **One sponsor mark everywhere — 1 attribute.** Today's strip (app.js:1239) still ships
   `upright-crown.png`; the landing card uses `upright-lockup.png`. Point the strip at the
   lockup (`height:22px` already constrains it; the 1192×394 wide aspect fits a strip
   better than the crown anyway) and delete the crown reference. Removes the last
   two-marks-one-sponsor inconsistency. **Δ consistency +0.15, identity +0.1.**

3. **Two contrast one-liners on the landing.** (a) `.gate-cta:hover` swaps to #3a8fe0 =
   3.40:1 with white — use `--union-hover` only as a *dark-theme* hover or darken the
   hover to a 4.5:1 blue (#2f6fb4 ≈ 4.6:1); (b) the light-theme sponsor card at
   `background: var(--panel)` (#fff) gives the 0.466-luminance lockup 2.03:1 — one rule:
   `html[data-theme="light"] .lp-sponsor-card { background: var(--inset); }` (#e9eef6
   lifts the lockup to ~2.4:1 and is how the app already treats inset media) or a
   light-specific `filter: invert/brightness` treatment on `.lp-sponsor-card img`.
   **Δ color +0.2, mobile +0.1** (the CTA is the thumb-most control).

Combined Δ ≈ +1.0 spread across type/consistency/color → type and consistency reach 9.6+,
projected total ≈ 9.6. Honest ceiling note, same lineage as R7/R8: the last stretch to
9.7-everywhere still needs (a) the server-side /api/players burst fix (4.1s warm
single-shot is solved; the 5-burst 30-34s vs 22s/30s client ceilings is upstream build
time — 5.6MB decoded even at gzip), and (b) a rendered-browser pass to convert the
remaining (static) dimensions into pixel-verified ones.

VERDICT: 9.4/10
