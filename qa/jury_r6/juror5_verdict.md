# Jury R6 — Juror 5/5 — PRODUCT CREDIBILITY lens (v59, deployed bytes)

Method (Chrome-free, per constraint): fetched deployed `/` shell (8,466 B), `app.js?v=59` (151,232 B), `style.css?v=59` (85,288 B), plus live APIs: `/api/version` → `{"js":59}` (shell links both assets `?v=59` — deploy verified), `/api/today` (0.28s), `/api/teams` (85 KB, 0.27s), `/api/leaders` (0.24s), `/api/league/<Sunday B East>` (1.1s), `/api/team/<Goodfellas>` (14.7 KB, 0.9s), `/api/players/lookup?q=ackley` (0.71s), `/api/players` (40.0s single-shot, 2.0 MB). WCAG math recomputed on v59 tokens. No browser automation; all claims byte- or payload-verified against prod.

## v59 gate verification (task-mandated checks)

| Check | Result | Evidence |
|---|---|---|
| `/api/version` | **PASS** | `{"js":59}`; shell `<link href=".../style.css?v=59">` + `<script src=".../app.js?v=59">` |
| `window.loadTeamContent = loadTeamContent` (recursion-kill) | **PASS** | Direct function binding with a source comment that explicitly forbids the arrow-shadow form (`window.loadTeamContent = (id, r) => …` = infinite recursion); all 6 call sites pass `(state.teamId, refresh)` correctly; retry button passes `true` |
| v57 Today night KPI strip | **PASS** | `tonight-strip` renders Games / Rinks / Live now (`—` when zero) / First puck (earliest ParsedTime); CSS has `.tonight-kpi:nth-child(3) .tonight-num{color:var(--accent)}` + ≤599px squeeze (gap 6px, padding 10px 4px 8px) |
| v57 By-Rink grouping | **PASS** | Slate groups by venue (`Chiller ` prefix stripped), renders `By Rink` card with per-rink `h3.rink-head` + counts when >1 rink; single-rink falls back to the cols list |
| Regression re-checks | **CLEAN** | 0 `PACEMAKERS`, 0 `vs @`, 0 `verBadge`, 0 double-escaped `\u2026`, 0 Byes/TBD in today/league/team payloads |

## R5 → R6 fix ledger (my R5 predictions)

| R5 fix | Status | Evidence |
|---|---|---|
| 1. autoToggle on-state feedback | **SHIPPED** | `.live-pill:has(#autoToggle:checked){color/border/background}` + `:has(…) .live-pill-dot{background:var(--win)}`; title now reads "Live status — click to toggle 30s auto-refresh" (accurate). The last "clicked it, nothing happened" control is dead. |
| 2. Token the button hover + `.section-h` | **NOT SHIPPED** | `button:hover{background:#3a8fe0}` still present (1 hit); `.section-h` does not exist; inline `style="margin-top:…"` in JS render strings grew 6 → 22 occurrences (7× `margin-top:18px` h3s); 49 inline styles total. Second round ignored. |
| 3. `api()` abort+timeout | **SHIPPED** | `api()` now has AbortController + hard 30s ceiling + one silent retry on network/5xx + cache key; comment cites "jury R4/R5 systemic finding — the last infinite-wait path." Infinite-skeleton class is dead on every tab. |

## Dimension scores (v59)

| # | Dimension | Evidence (one line) | Score |
|---|---|---|---|
| 1 | Visual identity | CBJ token stack locked end-to-end (Union Blue #2a7fd4 / Goal Red #e8253c / Silver; light theme re-tuned to #0057b8 / #ce1126, all on-hue); rink-lines watermark + broadcast-bug + Saira 800 watermarks; tonight-strip adds a broadcast "at a glance" band. One leak: the generic-blue hover on the primary control reads off-brand in light mode. | 9.0 |
| 2 | Typographic system | Raw `JetBrains Mono` font-family declarations cleaned to **0** (R5's 2 are gone); tnum block, Saira 600/700/800 loaded, mono on every label. BUT the px census went **28 → 29 distinct font sizes** (7.5–34px), `--mono-md` still defined/unused, `.tl-game.otl{font-size:8px}` residue survives. Scale tokens still don't exist; the append-overlay habit continues. | 8.6 |
| 3 | Color system | 44 `var(--accent)` uses, all live/interactive/lead; win/loss/tie semantic set; light-theme accent #ce1126 passes AA on white (5.63:1). **New verified defect: dark-theme accent #e8253c on panel surfaces = 4.18:1** (4.47 on bg) — below AA-4.5 for the 9.5–10px live labels it colors (live-pill, status-live, tonight Live-now numeral). Plus the two-round-old `#3a8fe0` hover leak. | 8.0 |
| 4 | Layout & hierarchy | Ordering is now marquee-correct: night KPI strip → my-team hero (or designed CTA) → LIVE scoreboard → On The Scoreboard chips → By-Rink slate (per-rink counts) → Finals → League Leaders; GD viz ships an honest preseason empty state ("No goal data yet — season hasn't started"); hash deep-links. Remaining: League-tab leaders tables still render five alphabetical rows of `0` with no framing, and one `recent_result` render site lacks the hero's `hasOpp` guard (empty team names → blank `0-0` card). | 9.0 |
| 5 | Density & data presentation | Sticky theads ×2, zebra ×21, sortable th with aria-sort, tnum alignment, scrimmage rows muted/non-clickable, 44px tap floors; By-Rink grouping is the right long-tail taming; heat/gd separate value cells hold. All-zero standings columns are truthful data, not layout debt. | 9.0 |
| 6 | Interaction & micro-feedback | autoToggle checked-state feedback shipped; `api()` 30s ceiling + silent retry; typeahead debounce + stale-clear + retry rows; toast `role="status"`; lookup 0.27–0.71s. Residual: `/api/players` measured **40.0s** (2.0 MB) this round — the 22s client abort + partial-retry + "timed out + Retry" card handles it honestly, but a first leaderboard visit is still a guaranteed 22s skeleton (backend, not design). | 9.0 |
| 7 | Motion design | 11 keyframes, each used ≤1 place: live pulse/breathe (status), score-flash (event), shimmer (skeleton only), rise-in/pal-pop (entrance), hero-next-pulse (CTA); 4 reduced-motion blocks; backdrop blur exactly 1 (palette scrim). hero-glow-breathe is the only decorative-leaning one. | 9.0 |
| 8 | Depth & material | 1 backdrop-filter total, hairline `rgba` borders, 35 box-shadows all inset/soft, watermark ≤0.06 alpha, both themes re-tuned token-for-token; no blur soup, no fake shadows. | 9.0 |
| 9 | Consistency & component quality | One scorecell anatomy and one chip/pill system hold everywhere incl. tonight-strip and palette groups. But 28 inline `onclick=` handlers coexist with delegated `data-` systems (45), inline styles grew to 49, `.section-h` was never created, off-token hover persists — the R5 "two idioms" finding is now three-rounds-old and slightly worse. | 8.2 |
| 10 | Mobile ergonomics | 7× explicit 44px floors; ≤430 header compaction is padding/typography-only; ≤479 four-area card stacks; tonight-strip mobile squeeze shipped; `-webkit-tap-highlight-color` + `:active` parity + `button:active scale(.97)`; focus-visible ×14; ellipsis + `min-width:0` truncation guards on pill labels. | 9.0 |

## WEIGHTED TOTAL

identity 1.080 + type 1.032 + color 0.800 + layout 1.080 + density 1.080 + interaction 0.900 + motion 0.720 + depth 0.720 + consistency 0.656 + mobile 0.720 = **8.8/10**

Lineage: R3 7.3 → R4 8.4 → R5 8.4 → **R6 8.8**. Two of three R5 fixes shipped and their dimensions moved (interaction 7.5→9.0, layout 8.5→9.0); the ignored fix (color/consistency token debt) is exactly where the score is still stuck.

## Data poverty: what DESIGN can still fix vs what only real season data fixes

**Design-fixable (all verified absent or partial today):**
- League-tab leaders tables: apply the GD viz's own `hasGoals`-style gate — if every `value===0`, render "No stats yet — season starts Sun Sep 6" (real dates already exist in `upcoming`) instead of five alphabetical `0` rows.
- Guard the second `recent_result` render site with the same `hasOpp` check the hero already has (empty opponent names currently produce a blank `0-0` card).
- Preseason framing: label the League standings table "0 GP — season hasn't started" rather than showing 0-0-0 rows bare; a "show more" cut on the 253-team picker typeahead; the empty-hero CTA already ships ("Set your team to pin…").
- dataStamp still shows page-load time as "UPDATED HH:MM" — print the backend's actual cache age or drop the claim.

**Only real season data fixes:** all-zero league standings (6 × 0 pts), team form 0-0-0 with empty timeline, `player_id: null` in league leader rows (rows can't deep-link to profiles), and the 40s/2 MB `/api/players` payload. No CSS makes an unplayed season have scores; the job is to not look broken while saying so — the GD empty state proves this team knows how.

## 3 cheapest fixes toward 9.7-per-dimension

1. **Lift dark-theme accent to AA** — one token: `--accent: #f24158` in dark (verified 4.98:1 on panel; #f0324a = 4.62 also passes), keep #e8253c only in glows/borders. Fixes every 9.5–10px live label at once. Δ ≈ +0.17 weighted (color 8.0→9.0, identity 9.0→9.3).
2. **Cash the two-round-old R5 fix #2** — `button:hover{background:color-mix(in srgb, var(--union) 84%, white)}` + one `.section-h` class replacing the 7 inline `margin-top:18px` h3s (and sweep the other 15 inline margins). Δ ≈ +0.09 weighted (consistency 8.2→8.9, color +0.1).
3. **Zero-season framing for League leaders + second `recent_result` guard** — the `value===0` empty-state gate and `hasOpp` ternary are ~6 lines total and complete the design-side share of data poverty. Δ ≈ +0.08 weighted (layout 9.0→9.4, consistency +0.1).

Ceiling with all three: ≈ 9.1. The residual gap to 9.7 is type-scale tokens (29 px sizes → real scale), one interaction idiom (28 inline onclicks), and real season data — the first two are one focused CSS/JS pass; the last is the calendar's.

## Residual credibility risks (static-verification limits)

- `/api/players` at 40s/2 MB single-shot: client handles it honestly (22s abort, partial-retry ×4, Retry button), but first-visit leaderboard latency is a product-credibility tax no frontend can pay down.
- dataStamp = page-load time, not data age (semantic fib a data-journalism reader could catch).
- Live detection remains a time heuristic (≤100min window); a postponed game could show LIVE — needs live data to confirm.
- (static) All findings from deployed bytes + API payloads; no rendering verification possible under the no-Chrome constraint.

VERDICT: 8.8/10
