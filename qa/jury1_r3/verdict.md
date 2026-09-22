# CAHL UI/UX Jury — R3, Juror 1/5 (v52) — STATIC-SOURCE + API AUDIT (browser disabled by owner)

Method: urllib fetch of / , /static/css/style.css?v=52 (1951 ln), /static/js/app.js?v=52 (2944 ln), /api/version|today|teams|leaders; WCAG contrast computed from hex; cascade/specificity read from source order. Paint-level items marked (static).

## R3 fix-list verification (deployed v52)
| Claim | Verdict | Line-level evidence |
|---|---|---|
| APP_VERSION sync, no boot reload | ✅ SHIPPED | index.html `window.APP_VERSION=52`; app.js L7-10 "old window.APP_VERSION dual-check is gone", `JS_VERSION=52`; /api/version `{"js":52}`; only self-heal on newer server (L12-16) |
| render-token guard | ✅ SHIPPED | app.js L953-973: `_renderToken`, `stale()` checked after every await (6 bail points, incl. error path L973) |
| refreshAll try/finally | ✅ SHIPPED | app.js L846-859: finally restores label + disabled=false even on throw |
| next-game dangle guard | ✅ SHIPPED | app.js L1915-1919: empty opponent → matchup renders team only, no bare "vs" |
| hashchange routing | ✅ SHIPPED | app.js L926-948 (listener, re-entrancy guard, replaceState), L2713-2720 boot hash restore before setTab |
| mono cascade 9 sizes → 3 at originals | ⚠️ PARTIAL | tokens --mono-xs/sm/md = 9.5/10.5/11.5 defined L1865-1867 but only 5 selectors consume them; cascaded result still 11 distinct mono sizes (8px .tl-game.otl, 8.5px .brand-sub, 9, 9.5, 10, 10.5, 11, 11.5, 12px) |
| --faint AA both themes | ✅ SHIPPED | override L1740-1747 dark #7a8ca5 → 5.75:1, light #5b6c85 → 4.97:1 on --bg (computed WCAG; earlier L26/L95 cascade-overridden) |
| live-pill pure status, dead toggle deleted | ❌ NOT SHIPPED | index.html still ships `<input type="checkbox" id="autoToggle">` inside the pill; CSS L232-233: "hidden auto-refresh checkbox stays functional: clicking the pill toggles it"; cursor:pointer L240, :hover L243, app.js L2684 wires change. Status STATES are pure (L247-256) but the control remains |
| viewport zoom restored | ✅ SHIPPED | index.html `initial-scale=1.0, viewport-fit=cover`, no maximum-scale/user-scalable |
| Saira 800 weight | ❌ NOT SHIPPED | font link loads `Saira+Condensed:wght@600;700` only; CSS demands 800 with var(--display) at L1341 (.team-watermark), L1357 (.lead-pts), L208/215 (header), L871-882 (cmp scores) → synthesized faux-bold on the key display numerals |
| Bye Week filtered at ingest | ✅ SHIPPED | scraper.py L262-267 filters at ingest; prod /api/today = 18 games, 0 bye rows. Client L1172 still assigns raw data.today (harmless; front-end regex L2264 remains as backstop) |
| rink watermark | ✅ DEFERRED as claimed | CSS .team-watermark L1339-1343 defined, zero JS emitters — dead but harmless |

## R1+R2 criticals re-verified (all intact)
- Watchdog retry states: app.js L1806-1815 (8s nudge / 20s hard error), Retry button L2040, typeahead retry items L424/426, players-index retry L614/618 ✅
- League first-run auto-select: L1268-1274 ✅
- Hero unclip: style.css L1580-1586 (hero-glow guard) + L1752-1758 (overflow-wrap anywhere, min-width:0) ✅
- Live-pill vocabulary: PARTIAL — status states pure, checkbox control remains (see above)
- Analytics heat/gd: full anatomy L1605-1723 (.heat-row/name/track/bar/val, .gd-strip/axis/line/dot/labels/abbr, .gd-empty) ✅

## Dimension scores
| Dimension | Evidence | Score |
|---|---|---|
| 1. Visual identity (12%) | CBJ tokens locked both themes (union #2a7fd4/#0057b8, accent #e8253c/#ce1126, silver); mono uppercase microcopy; broadcast display numerals; live pulse; dark rink-night default. No signature hero texture (watermark deferred); generic feather-style icons | 7.5 |
| 2. Typographic system (12%) | 3-family system w/ --display/--mono tokens; tabular-nums table-wide L1597-98. DEFECT: Saira 800 used but not loaded (faux-bold on scores/leaderboard); mono cascade still 11 sizes — tokens reach only 5 selectors | 6.5 |
| 3. Color system (10%) | Tokenized CBJ palette; accent discipline real (41 var(--accent) uses; live/elim/win/loss from tokens); --faint/--muted AA verified 5.75:1 / 4.97:1. DEFECT: button:hover #3a8fe0 (L517) is a third off-token blue; mint --win #2fd08c outside CBJ set | 8.5 |
| 4. Layout & hierarchy (12%) | Hero marquee vs sectioned long-tail; today 11-track header grid w/ calc-positioned group labels; <479px card grid-areas L1832-1853; main clears fixed nav (72px + safe-area). Accretion: .hero-team font-size declared 3× (L1179/1235/1277) | 8.0 |
| 5. Density & data presentation (12%) | Sticky thead z5 L493 + sticky first col L1161; zebra + hover L1879-1886; sortable th[data-sort] keyboard-operable (8 refs); two-layer scroll fade; 253-team / 18-game slates tamed | 8.5 |
| 6. Interaction & micro-feedback (10%) | Watchdog/retry everywhere; score flash + _flash; skeletons; 12 focus-visible sites; ⌘K palette; pull-to-refresh w/ busy guard; toast "Updated HH:MM". DEFECTS: live-pill still a control posing as status (title "click to toggle", hover shift, cursor); /api/teams 3.9s cold w/ no progressive signal beyond skeleton | 7.5 |
| 7. Motion design (8%) | 11 keyframes all functional (live-dot pulse 1.4s, flash 950ms, entrance stagger capped n+6); transitions tokenized; 3 reduced-motion blocks L1198/1282/1388; single backdrop-filter | 8.5 |
| 8. Depth & material (8%) | 5-step luminance ladder #070b12→#090d16→#0e1420→#131b2b→#1a2334 (distinct, computed); hairlines 8-14% alpha; hero-card overflow clips glow bleed; no blur soup, no fake shadows | 8.5 |
| 9. Consistency & component quality (8%) | One scorecell anatomy; chip/pill/badge all token-built; 0 dangling CSS vars (verified). DEFECTS: duplicate .heat-row/.gd-strip declarations L1327-38 vs L1605+ (two sources of truth); duplicate .live-pill block L1344-50 (always-live styling) that later block must out-cascade | 7.5 |
| 10. Mobile ergonomics (8%) | Nav 48px, buttons 44px, rows/cells 48px; <479 card stack; header compressed w/ ellipsis-guard pills; icon-only search <599; skip-link + a11y announcer; zoom restored. (static) — no paint/thumb-reach verification possible | 8.0 |

## WEIGHTED TOTAL
0.900 + 0.780 + 0.850 + 0.960 + 1.020 + 0.750 + 0.680 + 0.680 + 0.600 + 0.640 = **7.9/10**

## 3 cheapest high-delta fixes
1. **Add `;800` to the Saira Condensed Google Fonts URL** (index.html head, one token). Kills faux-bold on every display numeral (score cells, lead-pts, watermark, cmp scores). Est. delta: +0.25 (type 6.5→8.0 + identity/consistency spillover).
2. **Finish the mono consolidation**: swap the remaining raw 8/8.5/9/10/11/12px mono declarations to --mono-xs/sm/md (~25 declarations, mechanical grep-replace; keep 8px→9.5px upgrade for .tl-game.otl). Est. delta: +0.20 (type + consistency).
3. **Delete the #autoToggle checkbox + its change-listener** (app.js L2684-2690), make auto-refresh implicit while games are live, strip cursor:pointer/hover/title from the pill → truly pure status. Est. delta: +0.15 (interaction/consistency; closes the twice-flagged credibility nit).

## API timing (this run, single-shot)
/ 0.72s · style.css 0.83s · app.js 0.99s · /api/version 0.66s · /api/today 0.70s · /api/teams 3.90s (cold aggregate) · /api/leaders 1.03s — 18 games scheduled tonight, 0 live, 0 scored (September zero-data season: empty-score rendering path is the one under live test).
