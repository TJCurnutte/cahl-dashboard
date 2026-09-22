# JURY R10 — JUROR 1/5 — v70 (Chrome-free; deployed-bytes + live-API verify-and-score round)

**Method:** Standing rule — no browser automation. Scored from the deployed bytes of
`index.html` (13,161 B), `style.css?v=70` (88,845 B), `app.js?v=70` (157,005 B),
`landing.css?v=70` (8,892 B), `/api/version` = `{"js":70}` with `const JS_VERSION = 70`
and `window.APP_VERSION = 70` in `index.html` (sync verified, no boot reload loop), plus
live JSON APIs. Every fetched asset header-checked (HTTP 200, correct Content-Type,
plausible size) before grepping. Diffed against my own saved v67 copies
(`jury_r9/style_v67.css`, `landing_v67.css`, `app_v67.js`) so every claim below is a
hunk-level verification, not fix-log trust. Computed WCAG in Python. All rendered-pixel
claims remain **(static)**.

**Gate check — my R9 cited fixes, byte-verified in deployed v70:**

| R9 citation | v70 evidence | Status |
|---|---|---|
| (1) landing.css type census quantized to the 8-step scale (only 13/14/16/20/26/30/34 px remain; tokens for the rest) | Full census of landing.css: **exactly** {13×2, 14×4, 16×4, 20×1, 26×2, 30×1, 34×1} = 15 literal decls, zero off-scale values. The R9 ad-hoc scale is gone line-by-line: 11px→`var(--mono-sm)`, 12.5px→13, 13.5px→14 (×2), 15px→14, 17px→16, 19px→20, 44px hero→34, 32px→30, 27px→26, 17px CTA→16. Landing now ALSO consumes `var(--mono-xs)` ×2 and `var(--mono-sm)` ×4. The forked scale and the app scale are one system. | ✅ FIXED (full) |
| (2) Today sponsor strip uses the same serif lockup as the landing (dual-mark defect closed) | `app.js:1239` now ships `<img src="/static/img/upright-lockup.png">` — the `upright-crown.png` reference is **deleted**; census of app.js+index.html+both stylesheets: **0** crown refs, 2 lockup refs (strip + landing card). `landing.css:190` retunes the strip img (height 20px, `max-width:150px; object-fit:contain`) for the 1192×394 wide lockup. One sponsor mark product-wide. | ✅ FIXED |
| (3) CTA hover `--union-hover` darkened to #2b71c4 | `style.css:35` `--union-hover: #2b71c4` (comment documents the R9-4 darkening). Computed: **4.93:1 with the white label** (idle #1f6cb8 5.39:1). Both hover rules in the cascade consume the token; the 3.40:1 #3a8fe0 hover is dead. Landing `.gate-cta:hover`/`.lp-cta-sm` now consume bare `var(--union-cta)`/`var(--union-hover)` — and the raw-hex **var() fallbacks are dropped from landing.css entirely** (census: zero `var(--x, #hex)`). | ✅ FIXED |
| (4) palette `:focus-within` cue added | `style.css:783` `.pal-input-row:focus-within { box-shadow: inset 0 0 0 2px var(--union); border-radius: inherit; }` — new rule sits directly above the input rules whose `:focus` resets are unchanged, so the cue paints on the row, not the input. 3-round carry closed. | ✅ FIXED |
| (5) dup light-theme `.rink-head` rule deleted | v67 carried the rule at BOTH `style.css:1720` and inside the light block; v70 diff shows exactly one deletion and one census hit remains (`style.css:1720`, single light override `color: var(--union-deep)`). No duplicate in the file. | ✅ FIXED |
| (6) landing raw-hex var() fallbacks dropped | Diff hunks at landing L99/105/132-133/169-170/202 all lose the `#1f6cb8`/`#3a8fe0`/`#b8925e` fallbacks. Census: **0** raw-hex fallbacks in landing.css. | ✅ FIXED |

**Bonus verified in the same diff (not cited by me, credited anyway):** `.lp-nav`
`backdrop-filter: blur(10px)` **removed** (L43 now `background: var(--bg)` with the
reason in the comment) — the R9-2/R9-4 material deviation is gone; product-wide
backdrop-filter census is back to **1** (the palette scrim, style.css:765).
`.lp-cta-sm` min-height 42→**44px** — the 2px-under-floor nav CTA is fixed. R9-4's
leader-row dead-link conditional also landed at Players `leaderSection` (app.js:282) and
Analytics (app.js:2521) with the same `p.player_id ? … : ''` ternary, plus `?? '-'`
fallbacks on stat cells (698-710, 2186-2208) — empty-index rows now render dashes instead
of `undefined`. All three functions are guarded no-ops on empty args (app.js:2582, 2588),
so the conditional tr affords nothing it can't deliver.

**Standing ledger re-verified, still holds in v70:** `concat(finals)` (app.js), refresh
busy-state, count-up RM gate (app.js:799/805), api() 30s AbortController, typeahead
180ms debounce + stale-clear, watchdog 8s/40s above the 30s ceiling, hash routing +
TABS-guard (lp- anchors provably inert to the router), cold-index copy "up to ~30s"
(L533), dataStamp minute-ticker (paintStamp + setInterval 60000, app.js:2919-2923),
pal-input 16px, tap-highlight transparent, coarse-pointer 44px floors (10 `min-height:44+px`
hits; the proper media-block scan shows zero `min-height:0` regressions — the 6
`min-width:0` hits are text-shrink `flex` clauses on brand/live-pill, not controls),
tnum ×20, sticky ×2 + coarse first-col freeze, zebra ×6, Saira Condensed 600/700/800 in
the font href, error-escape census **0** raw `${data.error}` / `${e.message}` (esc() 153×),
JS font-size literals **0**.

**Live API (measured this round, labeled):** `/api/today` 0.9s — 0 games, **0** Bye Week /
Team Blue / Team Red strings. `/api/league/current` 1.6s — designed empty shape
(leaders/standings/playoffs all `[]`), the September zero-state renders as designed.
`/api/players` single-shot **6.4s warm / 1.52MB gzipped (5.52MB decoded, 5,862 players)**
— best-ever warm figure. 5-parallel burst: **3/5 at 7.1-8.9s, 2 stragglers at 28.7s**
(R9: uniform 30-34s). The brief notes Supabase persistence wiring shipped in v70
env-gated (memory→Supabase→/tmp→rebuild hydrate chain); latency residue is credibly
pending creds, not design — I score the measured client-relevant state.

---

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | Landing carries the identity asset end-to-end: crest nav + 260px hero crest with softened light-theme drop shadow, "Every Game. Every Stat. One Dashboard.", four gold-chip feature cards, honest non-affiliation note, sponsor lockup card, footer CTA. Rink-lines watermark at 0.07 alpha pinned to outer margins, rink-radial blue/red backdrop, Saira display. Now with **one** sponsor mark and **one** CTA hue family (idle #1f6cb8 5.39:1, hover #2b71c4 4.93:1, both AA) across every surface. Remaining gap is unverifiable pixels (watermark registration, crest rendering), not design debt. (static) | 9.5 |
| 2 | Typographic system (12%) | **One type system, finally, in both files.** style.css: 8 sanctioned literals (13×19, 14×10, 16×20, 18×2, 20×15, 26×3, 30×2, 34×2) + one 11pt print rule; landing.css: the same 8 values only, zero off-scale; app.js: zero. Mono tokens consumed in both files (`--mono-xs/sm/md` with tokens at style.css:2017-2019). The last 0.3 is intrinsic: 73 literals remain at original rule bodies where the design's own tiers could be named tokens — the scale is disciplined but not yet fully token-named. (static) | 9.6 |
| 3 | Color system (10%) | Computed both themes: dark text 16.90 / muted 8.34 / faint 5.78 / accent 4.80 / sponsor-gold 6.42 on panel; light text 17.31 / faint 5.41 / sponsor-gold 6.18 on white. CTA idle 5.39:1, **hover 4.93:1 — every CTA state now AA with its white label**. No off-token hexes; sponsor gold consumed via `var(--sponsor-gold)` with no fallback hexes. Remaining blemish: the light-theme sponsor card keeps `background: var(--panel)` (white) under the 0.466-mean-luminance lockup (byte-decoded in R9, PNG byte-identical in v70: sha f041e084…) ≈ 2.03:1 in light theme only. | 9.6 |
| 4 | Layout & hierarchy (12%) | Landing: nav → hero → features → about → sponsor → footer, centered measure; app: Night-KPI → hero → scoreboard → On The Scoreboard → By-Rink with `concat(finals)` verified and the sponsor strip anchoring Today's long tail. The stray duplicate light-theme rule is gone from the cascade (one `.rink-head` override remains, correctly ordered). Light landing backdrop drops to two restrained radials. Still can't pixel-verify the 11-track cols-head or hero wrap without a browser — the only (static) residue. (static) | 9.4 |
| 5 | Density & data presentation (12%) | tnum ×20, sticky thead + coarse first-col freeze, zebra ×6, table-as-scroll-container at ≤699px. Live payloads: 0 hygiene violations in today/league; empty league renders the designed zero-state; Players rows with absent stats now render `—` dashes instead of `undefined` (new `?? '-'` guards). 5,862-player index serves at 6.4s warm, 1.52MB wire. No jiggling-column patterns found in the census. (static + live payload) | 9.5 |
| 6 | Interaction & micro-feedback (10%) | Every fetch path ceiling-protected, retry affordances on every error path, all three gate CTAs wired, palette focus cue now visible (union ring on the input row). Measured: players burst 3/5 at 7-9s (server work clearly parallelizing) but **2 stragglers at 28.7s still exceed the 22s typeahead abort** — a first-search cold hit can still lose the coin flip; Supabase wiring is shipped but env-gated pending creds. (static + live probes) | 9.3 |
| 7 | Motion design (8%) | Vocabulary unchanged: live-dot pulse, score flash, live-breathe, palette spinner — all RM-covered (4 style.css blocks + landing block + JS gate). Landing transitions enumerated inside its RM block (L217); nav blur removal also removed a transition carrier. lp-hero crest shadow is static (correct). No decorative motion added in v70's 3 files. (static) | 9.4 |
| 8 | Depth & material (8%) | Product-wide backdrop-filter census: **1** (palette scrim blur(3px)). The R9 flag (.lp-nav blur 10px) is deleted with an in-comment rationale. 4-stop luminance ladder, hairlines, single soft shadows; sponsor card lift is a 2px translateY + border-color shift. No blur soups, no fake shadows anywhere in the 97.7KB of shipped CSS. (static) | 9.5 |
| 9 | Consistency & component quality (8%) | One scorecell anatomy; one sponsor mark (crown deleted, lockup everywhere, strip img retuned for the wide aspect); one CTA hue family; error-escape class stays closed file-wide; the leader-link conditional now ships at all three render sites with the same ternary shape. Deduction: keyboard reachability — `.pacemaker` LEAGUE LEADERS cards (app.js:649) are `onclick` divs with no `role`/`tabindex`/Enter path, and the landing gate dialog still has no Escape/inert wiring. (static) | 9.6 |
| 10 | Mobile ergonomics (8%) | Release-gate greps clean (no `min-height/width:0` on controls inside any @media; the 6 `min-width:0` hits are flex text-shrink clauses). 44px floors ×10 verified; **`.lp-cta-sm` now 44px** (was 42); nav blur removal also removes an iOS sticky-blur repaint cost; safe-area, tap-highlight, pal-input 16px, table scrollport at 699px, landing 719/430 breakpoints with retuned type. Remaining: nothing flagged in bytes; pixel-level thumb verification still (static). (static) | 9.6 |

---

## WEIGHTED TOTAL

identity 9.5×12% + type 9.6×12% + color 9.6×10% + layout 9.4×12% + density 9.5×12% +
interaction 9.3×10% + motion 9.4×8% + depth 9.5×8% + consistency 9.6×8% + mobile 9.6×8%
= **9.5 / 10** (unrounded 9.498)

Lineage: 8.9 → 9.3 → 9.4 → 9.5 (R7→R8→R9→R10). All six R9-cited fixes byte-verified
shipped — second consecutive round with zero partial credit — plus three uncited
fixes (nav blur removal, lp-cta-sm 44px, `?? '-'` stat guards) credited from the same
diff. The 9.7 all-dimension gate still fails: no dimension is at 9.7, and the two
lowest (interaction 9.3, layout 9.4) are held by measured server latency and the
absence of a rendered-browser pass, not by CSS debt.

---

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Raise the typeahead abort to the shared 30s ceiling — one constant.** The measured
   players burst tail (28.7s) sits between the 22s typeahead timeout and the 30s api()
   AbortController: a first-search user can still see "timed out" for a request the app
   itself would have completed 8s later. Aligning the typeahead ceiling with api()'s 30s
   (the watchdog already swaps copy at 8s/40s) removes the last client-side coin flip.
   **Δ interaction +0.2, density +0.1.**

2. **One rule for the light-theme sponsor card.** `html[data-theme="light"]
   .lp-sponsor-card { background: var(--inset); }` (the treatment the app already uses
   for inset media) lifts the 0.466-luminance lockup off pure white ≈2.03:1 → ~2.4:1, or
   a light-specific brightness filter on `.lp-sponsor-card img`. **Δ color +0.2,
   identity +0.1.**

3. **Keyboard-reach the LEAGUE LEADERS strip — 3 attributes + 1 handler.** `.pacemaker`
   cards (app.js:649) are onclick divs: add `role="button" tabindex="0"` + Enter/Space
   (or emit `<button class="pacemaker">`) so the signature strip is reachable without a
   pointer. Same pattern already solved for leader rows. **Δ consistency +0.1,
   interaction +0.1.**

Combined Δ ≈ +0.8 spread across interaction/color/density/consistency; with the Supabase
creds landing (server tail → warm-state parity) and one rendered-browser pass converting
the remaining (static) claims to pixel-verified, the 9.7-per-dimension gate is reachable
next round.

VERDICT: 9.5/10
