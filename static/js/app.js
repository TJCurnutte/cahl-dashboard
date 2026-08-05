const $main = document.getElementById('main');
    const $refresh = document.getElementById('refreshBtn');
    const $auto = document.getElementById('autoToggle');
    const navLinks = document.querySelectorAll('.nav-link');

    let state = {
      tab: 'today',
      leagueId: localStorage.getItem('cahl-league') || '',
      leagueDay: localStorage.getItem('cahl-league-day') || '',
      teamId: localStorage.getItem('cahl-team') || '',
      auto: false,
      leagues: [],
      teams: [],
      allTeams: [],
      allTeamsLoading: false,
      playersLeague: localStorage.getItem('cahl-players-league') || '',
      playersDay: '',
      _sessions: null,
      sessionDate: '',
      calMonth: '',
      calDay: '',
      leaders: null,
      cache: {}
    };

    const TABS = ['today','league','team','players','analytics'];
    let autoTimer = null;

    function $(sel){ return document.querySelector(sel); }
    function fmtTime(t){ return t || 'TBD'; }

    // Escape scraped text (team/player names come from chillerstats.com) before HTML injection
    function esc(s) {
      return String(s == null ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // Desktop vs mobile context: body.is-desktop mirrors the 900px CSS breakpoint
    const desktopMQ = window.matchMedia('(min-width: 900px)');
    function syncViewportClass() {
      document.body.classList.toggle('is-desktop', desktopMQ.matches);
      document.body.classList.toggle('is-mobile', !desktopMQ.matches);
    }
    syncViewportClass();
    desktopMQ.addEventListener('change', syncViewportClass);

    // ---- Theme toggle (light <-> dark), persisted ----
    const rootEl = document.documentElement;
    const themeMeta = document.querySelector('meta[name="theme-color"]');
    function applyTheme(t) {
      rootEl.setAttribute('data-theme', t);
      localStorage.setItem('cahl-theme', t);
      if (themeMeta) themeMeta.setAttribute('content', t === 'dark' ? '#070d1a' : '#002654');
    }
    document.getElementById('themeToggle').addEventListener('click', () => {
      applyTheme(rootEl.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });

    // ---- Two-step league picker: day chips -> league pills ----
    const DAY_ORDER = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Other'];

    function leagueDay(name) {
      const n = (name || '').toLowerCase();
      if (n.includes('sunday')) return 'Sunday';
      if (n.includes('monday')) return 'Monday';
      if (/\btue\b|tuesday/.test(n)) return 'Tuesday';
      if (n.includes('wednesday')) return 'Wednesday';
      if (/\bthur\b|thursday/.test(n)) return 'Thursday';
      if (n.includes('friday')) return 'Friday';
      return 'Other';
    }

    function shortLeagueName(name) {
      let s = (name || '').trim();
      s = s.replace(/^(?:NTPRD Chiller\s+)?(Sunday|Monday|Tuesday|Tue|Wednesday|Thursday|Thur|Friday)\s*-?\s*/i, '');
      s = s.replace(/^NTPRD Chiller\s+/i, '');
      s = s.replace(/\s*-?\s*league\s*$/i, '');
      s = s.replace(/^-\s*/, '').trim();
      return s || name;
    }

    function leagueGroups() {
      const groups = {};
      DAY_ORDER.forEach(d => { groups[d] = []; });
      state.leagues.forEach(l => groups[leagueDay(l.name)].push(l));
      return groups;
    }

    function selectedLeagueDay() {
      if (state.leagueDay) return state.leagueDay;
      if (state.leagueId) {
        const l = state.leagues.find(x => x.id === state.leagueId);
        if (l) return leagueDay(l.name);
      }
      return '';
    }

    function pickerHtml() {
      const groups = leagueGroups();
      const day = selectedLeagueDay();
      let html = '<div class="picker-days">';
      DAY_ORDER.forEach(d => {
        if (!groups[d].length) return;
        html += `<span class="pill day-pill ${d === day ? 'active' : ''}" data-day="${d}" tabindex="0" role="button">${d}<span class="pill-count">${groups[d].length}</span></span>`;
      });
      html += '</div>';
      if (day && groups[day].length) {
        html += '<div class="picker-leagues">';
        groups[day].forEach(l => {
          html += `<span class="pill league-pill ${l.id === state.leagueId ? 'active' : ''}" data-lid="${l.id}" tabindex="0" role="button">${esc(shortLeagueName(l.name))}</span>`;
        });
        html += '</div>';
      }
      return html;
    }

    function currentLeagueName() {
      const l = state.leagues.find(x => x.id === state.leagueId);
      return l ? l.name : '';
    }

    async function chooseLeague(lid) {
      if (!lid) return;
      state.leagueId = lid;
      localStorage.setItem('cahl-league', lid);
      const l = state.leagues.find(x => x.id === lid);
      if (l) {
        state.leagueDay = leagueDay(l.name);
        localStorage.setItem('cahl-league-day', state.leagueDay);
      }
      if (state.tab === 'league') await renderLeague();
      else if (state.tab === 'team') await renderTeam();
      else if (state.tab === 'analytics') await renderAnalytics();
      else setTab('league');
    }

    function changeLeagueHtml() {
      return `<div class="picker-current">League: <b>${currentLeagueName()}</b> <span class="link" data-change-league>Change</span></div>`;
    }

    // ---- Players-tab division filter (independent of main league selection) ----
    function playersPickerHtml() {
      const groups = leagueGroups();
      const activeDay = state.playersDay || (state.playersLeague ? leagueDay(currentPlayersLeagueName()) : '');
      let html = '<div class="picker-days">';
      html += `<span class="pill day-pill ${!state.playersLeague ? 'active' : ''}" data-pl-all="1" tabindex="0" role="button">All CAHL</span>`;
      DAY_ORDER.forEach(d => {
        if (!groups[d].length) return;
        html += `<span class="pill day-pill ${d === activeDay ? 'active' : ''}" data-pl-day="${d}" tabindex="0" role="button">${d}<span class="pill-count">${groups[d].length}</span></span>`;
      });
      html += '</div>';
      if (activeDay && groups[activeDay] && groups[activeDay].length) {
        html += '<div class="picker-leagues">';
        groups[activeDay].forEach(l => {
          html += `<span class="pill league-pill ${l.id === state.playersLeague ? 'active' : ''}" data-pl-lid="${l.id}" tabindex="0" role="button">${esc(shortLeagueName(l.name))}</span>`;
        });
        html += '</div>';
      }
      return html;
    }

    function currentPlayersLeagueName() {
      const l = state.leagues.find(x => x.id === state.playersLeague);
      return l ? l.name : '';
    }

    function leaderSection(title, list, valKey) {
      if (!list || !list.length) return '';
      const rows = list.map(p =>
        `<tr class="link" onclick="selectPlayer('${p.team_id || ''}','${p.player_id || ''}')"><td class="num">${p.rank || ''}</td><td><span class="link">${esc(p.name)}</span></td><td>${esc(p.team)}</td><td class="num">${p[valKey] ?? p.value ?? 0}</td></tr>`
      ).join('');
      return `<h3 style="margin-top:16px">${title}</h3><table><thead><tr><th>#</th><th>Player</th><th>Team</th><th class="num">${title}</th></tr></thead><tbody>${rows}</tbody></table>`;
    }

    // ---- Global team search with typeahead ----
    function teamSearchHtml() {
      return `<div class="team-search">
        <input id="teamSearch" type="text" placeholder="Type a team name\u2026" autocomplete="off" autocapitalize="off" spellcheck="false" />
        <div id="teamSuggest" class="typeahead" style="display:none"></div>
      </div>`;
    }

    async function loadAllTeams() {
      if (state.allTeams.length || state.allTeamsLoading) return;
      state.allTeamsLoading = true;
      try {
        const res = await fetch('/api/teams');
        const data = await res.json();
        if (Array.isArray(data)) state.allTeams = data;
      } catch (e) { /* typeahead keeps showing loading */ }
      state.allTeamsLoading = false;
      // refresh any visible dropdown now that data arrived
      const input = $('#teamSearch');
      if (input && input.value.trim()) input.dispatchEvent(new Event('input'));
    }

    async function pickSearchedTeam(teamId, leagueId) {
      state.teamId = teamId;
      localStorage.setItem('cahl-team', teamId);
      if (leagueId) {
        state.leagueId = leagueId;
        localStorage.setItem('cahl-league', leagueId);
        const l = state.leagues.find(x => x.id === leagueId);
        if (l) {
          state.leagueDay = leagueDay(l.name);
          localStorage.setItem('cahl-league-day', state.leagueDay);
        }
        state.teams = []; // force refetch of this league's roster
      }
      await renderTeam();
    }

    function bindTeamSearch() {
      const input = $('#teamSearch');
      const box = $('#teamSuggest');
      if (!input || !box) return;

      input.addEventListener('focus', () => { loadAllTeams(); });

      input.addEventListener('input', () => {
        const q = input.value.trim().toLowerCase();
        if (!q) { box.style.display = 'none'; box.innerHTML = ''; return; }
        const matches = state.allTeams.filter(t => t.name.toLowerCase().includes(q)).slice(0, 8);
        if (!state.allTeams.length) {
          box.innerHTML = '<div class="typeahead-item muted">Loading teams\u2026</div>';
        } else if (!matches.length) {
          box.innerHTML = '<div class="typeahead-item muted">No teams match</div>';
        } else {
          box.innerHTML = matches.map(t =>
            `<div class="typeahead-item" data-tid="${t.id}" data-lid="${t.league_id}"><span class="ta-name">${esc(t.name)}</span><span class="ta-league">${esc(t.league_name)}</span></div>`
          ).join('');
        }
        box.style.display = 'block';
      });

      box.addEventListener('click', e => {
        const item = e.target.closest('.typeahead-item[data-tid]');
        if (!item) return;
        box.style.display = 'none';
        input.value = '';
        pickSearchedTeam(item.dataset.tid, item.dataset.lid);
      });

      input.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
          const first = box.querySelector('.typeahead-item[data-tid]');
          if (first) {
            box.style.display = 'none';
            input.value = '';
            pickSearchedTeam(first.dataset.tid, first.dataset.lid);
          }
        } else if (e.key === 'Escape') {
          box.style.display = 'none';
          input.blur();
        }
      });

      document.addEventListener('click', e => {
        if (!e.target.closest('.team-search')) box.style.display = 'none';
      });
    }

    // ---- Interaction polish: skeletons, fade-in, count-ups, pull-to-refresh, button press ----

    // Shimmering placeholder blocks (styled via .skeleton / .skeleton-card in CSS)
    function skeletonHtml(cards=3) {
      let html = '<div class="skeleton">';
      for (let i = 0; i < cards; i++) html += '<div class="skeleton-card"></div>';
      return html + '</div>';
    }

    // Swap #main content with a fade-in transition, then run number count-ups.
    function setMainHtml(html) {
      $main.classList.remove('fade-in');
      $main.innerHTML = html;
      void $main.offsetWidth; // force reflow so the CSS animation restarts
      $main.classList.add('fade-in');
      animateNumbers($main);
    }

    // Count-up animation for purely numeric values (skips "6-6-0", "W3", etc.)
    function animateNumbers(root) {
      root.querySelectorAll('.stat-box .num, .game-card .score').forEach(el => {
        if (el.dataset.counted) return;
        const m = el.textContent.trim().match(/^([+-]?)(\d+)$/);
        if (!m) return; // non-numeric: leave untouched
        el.dataset.counted = '1';
        const sign = m[1], target = parseInt(m[2], 10), dur = 400;
        const t0 = performance.now();
        (function frame(t) {
          const p = Math.min((t - t0) / dur, 1);
          const eased = 1 - Math.pow(1 - p, 3); // ease-out cubic
          el.textContent = sign + Math.round(target * eased);
          if (p < 1) requestAnimationFrame(frame);
        })(t0);
      });
    }

    // Button press micro-interaction (.btn-press toggle, not just CSS :active)
    document.addEventListener('pointerdown', e => {
      const btn = e.target.closest && e.target.closest('button');
      if (btn) btn.classList.add('btn-press');
    });
    ['pointerup', 'pointercancel'].forEach(evt =>
      document.addEventListener(evt, () => {
        document.querySelectorAll('.btn-press').forEach(b => b.classList.remove('btn-press'));
      })
    );

    // Pull-to-refresh on mobile: drag down from top of #main while scrolled to top
    const PTR_THRESHOLD = 70;
    let ptrStartY = null, ptrDelta = 0, ptrBusy = false;
    const ptrHint = document.createElement('div');
    ptrHint.className = 'ptr-hint';
    ptrHint.style.cssText = 'position:fixed;top:8px;left:50%;transform:translateX(-50%);z-index:99;display:none;align-items:center;justify-content:center;padding:8px 14px;border-radius:999px;background:var(--card,rgba(0,0,0,.55));pointer-events:none;transition:opacity .15s;opacity:0';
    ptrHint.appendChild(Object.assign(document.createElement('span'), { className: 'spinner' }));
    document.body.appendChild(ptrHint);

    function ptrShow(delta) {
      ptrHint.style.display = 'flex';
      ptrHint.style.opacity = delta >= PTR_THRESHOLD ? '1' : String(Math.min(delta / PTR_THRESHOLD, 1) * 0.7);
    }
    function ptrHide() {
      ptrHint.style.opacity = '0';
      setTimeout(() => { if (ptrStartY === null && !ptrBusy) ptrHint.style.display = 'none'; }, 180);
    }

    $main.addEventListener('touchstart', e => {
      if (e.touches.length !== 1 || ptrBusy) return;
      if ($main.scrollTop > 0 || window.scrollY > 0) return;
      ptrStartY = e.touches[0].clientY;
      ptrDelta = 0;
    }, { passive: true });

    $main.addEventListener('touchmove', e => {
      if (ptrStartY === null) return;
      ptrDelta = e.touches[0].clientY - ptrStartY;
      if (ptrDelta > 10 && $main.scrollTop <= 0 && window.scrollY <= 0) {
        ptrShow(ptrDelta);
      } else if (ptrDelta <= 0) {
        ptrStartY = null;
        ptrHide();
      }
    }, { passive: true });

    $main.addEventListener('touchend', () => {
      if (ptrStartY === null) return;
      const delta = ptrDelta;
      ptrStartY = null;
      ptrDelta = 0;
      if (delta >= PTR_THRESHOLD && !ptrBusy) {
        ptrBusy = true;
        ptrHint.style.opacity = '1';
        Promise.resolve(refreshAll()).finally(() => { ptrBusy = false; ptrHide(); });
      } else {
        ptrHide();
      }
    }, { passive: true });

    async function api(path, refresh=false) {
      const cacheKey = (refresh ? '!' : '') + path;
      if (!refresh && state.cache[cacheKey]) return state.cache[cacheKey];
      try {
        const res = await fetch(path);
        const data = await res.json();
        if (res.ok) state.cache[cacheKey] = data;
        return data;
      } catch (e) {
        return { error: 'Network error. Try Refresh.' };
      }
    }

    async function refreshAll() {
      $refresh.disabled = true;
      $refresh.textContent = '';
      $refresh.appendChild(Object.assign(document.createElement('span'), { className: 'spinner' }));
      await fetch('/api/refresh', { method: 'POST' });
      state.cache = {};
      state._sessions = null;
      state.allTeams = [];
      await loadActiveTab(true);
      $refresh.innerHTML = 'Refresh';
      $refresh.disabled = false;
      const t = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
      showToast(`Updated ${t}`);
    }

    function setTab(tab) {
      state.tab = tab;
      navLinks.forEach(a => a.classList.toggle('active', a.dataset.tab === tab));
      loadActiveTab();
    }

    async function loadActiveTab(refresh=false) {
      $main.innerHTML = skeletonHtml(4);
      try {
        if (state.tab === 'today') await renderToday(refresh);
        if (state.tab === 'league') await renderLeague(refresh);
        if (state.tab === 'team') await renderTeam(refresh);
        if (state.tab === 'players') await renderPlayers(refresh);
        if (state.tab === 'analytics') await renderAnalytics(refresh);
      } catch (e) {
        $main.innerHTML = `<div class="error">Error loading tab: ${e.message}</div>`;
      }
    }

    function gameHtml(g, showScore=false) {
      const hasScore = g.home_final !== undefined && g.home_final !== null && (g.home_score !== undefined ? g.home_score || g.away_score : g.home_final);
      const home = g.home || g.home_name;
      const away = g.away || g.away_name;
      const homeId = g.home_id;
      const awayId = g.away_id;
      const score = g.home_score !== undefined ? `${g.home_score} - ${g.away_score}` : `${g.home_final} - ${g.away_final}`;
      const played = g.played || (g.home_final !== undefined);
      const now = new Date();
      // Very rough "live" guess: if today and time within the last 3h
      const timeStr = (g.time || '').replace(/\s+/g, '');
      let live = false;
      if (played && !g.home_score && !g.away_score && timeStr) {
        const [h, m] = timeStr.match(/(\d+):(\d+)/)?.slice(1) || [];
        const ampm = timeStr.toLowerCase().includes('pm');
        if (h) {
          let hh = parseInt(h);
          if (ampm && hh !== 12) hh += 12;
          const gameTime = new Date();
          gameTime.setHours(hh, parseInt(m) || 0, 0);
          live = Math.abs(now - gameTime) < 3 * 60 * 60 * 1000;
        }
      }
      return `
        <div class="game-card" data-game='${JSON.stringify({homeId, awayId}).replace(/'/g, "&#39;")}'>
          <div class="meta">
            <span>${esc(g.date || 'Today')} ${fmtTime(g.time)} ${g.facility ? '· ' + esc(g.facility) : ''}</span>
            ${(played || (g.home_score !== undefined && g.home_score !== null)) ? '<span class="score">' + score + '</span>' : (live ? '<span class="live">Live</span>' : '')}
          </div>
          <div class="matchup">
            <div class="team link" data-team="${homeId || ''}" onclick="selectTeam('${homeId || ''}')">${esc(home)}</div>
            <span class="vs">vs</span>
            <div class="team link" data-team="${awayId || ''}" onclick="selectTeam('${awayId || ''}')">${esc(away)}</div>
          </div>
        </div>
      `;
    }

    function todayRowHtml(g) {
      const rink = (g.facility || '').replace(/^Chiller\s+/i, '');
      // A 0-0 line is the site's default for unplayed games, so it doesn't count as a score
      const hasScore = g.played && (g.home_score || g.away_score);

      // Game started but no final posted yet -> treat as live (within a 3h window)
      let live = false;
      if (!hasScore && g.time) {
        const m = g.time.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
        if (m) {
          let hh = parseInt(m[1], 10) % 12;
          if (m[3].toUpperCase() === 'PM') hh += 12;
          const start = new Date();
          start.setHours(hh, parseInt(m[2], 10), 0, 0);
          const now = new Date();
          live = now >= start && now < new Date(start.getTime() + 3 * 60 * 60 * 1000);
        }
      }

      const scoreHtml = hasScore
        ? `<span class="t-score">${g.home_score}\u2013${g.away_score}</span>`
        : (live ? '<span class="t-score live-badge">LIVE</span>' : '');

      return `<div class="today-row">
        <span class="t-time">${fmtTime(g.time)}</span>
        <span class="t-match"><span class="link" onclick="selectTeam('${g.home_id || ''}')">${esc(g.home)}</span><span class="t-vs">vs</span><span class="link" onclick="selectTeam('${g.away_id || ''}')">${esc(g.away)}</span></span>
        ${scoreHtml}
        <span class="t-rink">${esc(rink)}</span>
      </div>`;
    }

    async function renderToday(refresh) {
      const data = await api('/api/today', refresh);
      if (data.error) { $main.innerHTML = `<div class="error">${data.error}</div>`; return; }
      state.leagues = data.leagues;

      let html = '';
      if (state.teamId) {
        html += '<div class="card hero-card" id="myTeamHero"><div class="empty">Loading your team\u2026</div></div>';
      } else {
        html += '<div class="card hero-card hero-cta"><div class="hero-cta-text">Set your team to see next game, last result, and record here</div>'
          + '<button class="small" onclick="setTab(\'team\')">Pick My Team</button></div>';
      }

      html += '<div class="card today-card"><h2>Today\'s Games</h2>';
      if (!data.today.length) {
        html += '<div class="empty">No games posted yet.</div>';
      } else {
        html += '<div class="today-list">' + data.today.map(todayRowHtml).join('') + '</div>';
      }
      html += '</div>';

      html += '<div class="card"><h3>Leagues</h3>' + pickerHtml() +
        '<div class="picker-hint">Pick a day, then a league</div></div>';
      setMainHtml(html);

      if (state.teamId) loadMyTeamHero(state.teamId, refresh);
    }

    async function loadMyTeamHero(teamId, refresh=false) {
      const el = document.getElementById('myTeamHero');
      if (!el) return;
      const data = await api(`/api/team/${teamId}`, refresh);
      if (data.error) { el.remove(); return; }

      const over = data.overview, form = data.form || {};
      const standings = data.standings || [];
      const rank = standings.findIndex(s => s.team_id === teamId) + 1;
      const total = standings.length;

      let inner = `<div class="hero-top"><span class="hero-team link" onclick="setTab('team')">${esc(over.team_name)}</span>`;
      if (form.played) inner += `<span class="hero-record">${form.record}${form.streak ? ' · ' + form.streak : ''}</span>`;
      if (rank) inner += `<span class="hero-rank">${rank}${rank === 1 ? 'st' : rank === 2 ? 'nd' : rank === 3 ? 'rd' : 'th'} of ${total}</span>`;
      inner += '</div>';

      if (over.recent_result) {
        const r = over.recent_result;
        const isHome = r.home_id === teamId;
        const us = isHome ? r.home_final : r.away_final;
        const them = isHome ? r.away_final : r.home_final;
        const res = us > them ? 'w' : (us < them ? 'l' : 't');
        inner += `<div class="hero-line"><span class="hero-label">Last</span><span class="form-chip ${res}">${res.toUpperCase()}</span> <b>${us}\u2013${them}</b> ${isHome ? 'vs' : '@'} ${esc(isHome ? r.away : r.home)}</div>`;
      }
      if (over.next_game) {
        const ng = over.next_game;
        inner += `<div class="hero-line"><span class="hero-label">Next</span> <b>${esc(ng.date || 'TBD')}</b> ${fmtTime(ng.time)} \u00b7 ${esc(ng.facility || 'TBD')} \u00b7 ${ng.home_away === 'Home' ? 'vs' : '@'} ${esc(ng.opponent)}</div>`;
      }
      el.innerHTML = inner;
    }

    async function renderLeague(refresh) {
      if (!state.leagues.length) {
        const home = await api('/api/today');
        state.leagues = home.leagues || [];
      }
      let html = '<div class="card">';
      html += '<h2>League / Scores</h2>';
      html += pickerHtml();
      html += '<div id="leagueContent"></div></div>';
      setMainHtml(html);

      if (state.leagueId) await loadLeagueContent(state.leagueId, refresh);
    }

    async function loadLeagueContent(leagueId, refresh=false) {
      const $content = $('#leagueContent');
      $content.innerHTML = skeletonHtml(3);
      const data = await api(`/api/league/${leagueId}`, refresh);
      if (data.error) { $content.innerHTML = `<div class="error">${data.error}</div>`; return; }

      // build team list from standings for the team tab
      state.teams = data.standings.map(s => ({ id: s.team_id, name: s.team })).filter(t => t.id);
      if (state.teamId) {
        const inLeague = state.teams.find(t => t.id === state.teamId);
        if (!inLeague) state.teamId = '';
      }

      // Reset sessions/calendar/compare state when the league changes
      if (state._sessions && state._sessions.leagueId !== leagueId) {
        state._sessions = null;
        state.sessionDate = '';
        state.calMonth = '';
        state.calDay = '';
      }
      if (state._cmpLeague !== leagueId) {
        state.cmpA = '';
        state.cmpB = '';
        state._cmpLeague = leagueId;
      }

      let html = `<h3 style="margin:18px 0 10px;color:var(--text)">${data.league_name} <span style="color:var(--muted);font-weight:400">${data.season}</span></h3>`;

      html += '<div class="pill-row">';
      const sections = [
        { key: 'Scores', label: 'Scores' },
        { key: 'Standings', label: 'Standings' },
        { key: 'Leaders', label: 'Leaders' },
        { key: 'Sessions', label: 'Game Nights' },
        { key: 'Calendar', label: 'Calendar' },
        { key: 'Compare', label: 'Compare' },
      ];
      const active = localStorage.getItem('cahl-league-section') || 'Scores';
      sections.forEach(s => html += `<span class="pill ${s.key===active?'active':''}" data-sec="${s.key}" tabindex="0" role="button">${s.label}</span>`);
      html += '</div>';

      html += '<div id="leagueSecScores" class="league-sec" style="display:'+(active==='Scores'?'block':'none')+'">';
      html += '<h3>Latest Scores</h3>';
      if (!data.recent.length) html += '<div class="empty">No recent scores yet.</div>';
      html += '<div class="games-grid">' + data.recent.map(g => gameHtml(g)).join('') + '</div>';
      html += '<h3 style="margin-top:18px">Upcoming</h3>';
      if (!data.upcoming.length) html += '<div class="empty">No upcoming games.</div>';
      html += '<div class="games-grid">' + data.upcoming.map(g => gameHtml(g)).join('') + '</div>';
      html += '</div>';

      html += '<div id="leagueSecStandings" class="league-sec" style="display:'+(active==='Standings'?'block':'none')+'">';
      html += '<table><thead><tr><th>Team</th><th class="num">GP</th><th class="num">W</th><th class="num">L</th><th class="num">OTL</th><th class="num">PTS</th><th class="num">GF</th><th class="num">GA</th></tr></thead><tbody>';
      html += data.standings.map(s => `
        <tr class="link" onclick="selectTeam('${s.team_id}')">
          <td><span class="link">${s.team}</span></td>
          <td class="num">${s.gp}</td><td class="num">${s.w}</td><td class="num">${s.l}</td><td class="num">${s.otl}</td>
          <td class="num">${s.pts}</td><td class="num">${s.gf}</td><td class="num">${s.ga}</td>
        </tr>`).join('');
      html += '</tbody></table></div>';

      html += '<div id="leagueSecLeaders" class="league-sec" style="display:'+(active==='Leaders'?'block':'none')+'">';
      html += '<h3>Points</h3><table><thead><tr><th>Player</th><th>Team</th><th class="num">Pts</th></tr></thead><tbody>';
      html += data.leaders.points.map(p => `<tr onclick="selectPlayer('${p.team_id}','${p.player_id}')" class="link"><td><span class="link">${p.name}</span></td><td>${p.team}</td><td class="num">${p.value}</td></tr>`).join('');
      html += '</tbody></table>';
      html += '<h3 style="margin-top:14px">Goals</h3><table><thead><tr><th>Player</th><th>Team</th><th class="num">G</th></tr></thead><tbody>';
      html += data.leaders.goals.map(p => `<tr onclick="selectPlayer('${p.team_id}','${p.player_id}')" class="link"><td><span class="link">${p.name}</span></td><td>${p.team}</td><td class="num">${p.value}</td></tr>`).join('');
      html += '</tbody></table>';
      html += '<h3 style="margin-top:14px">Assists</h3><table><thead><tr><th>Player</th><th>Team</th><th class="num">A</th></tr></thead><tbody>';
      html += data.leaders.assists.map(p => `<tr onclick="selectPlayer('${p.team_id}','${p.player_id}')" class="link"><td><span class="link">${p.name}</span></td><td>${p.team}</td><td class="num">${p.value}</td></tr>`).join('');
      html += '</tbody></table>';
      html += '</div>';

      // Sessions: every game night of the season, pick one to view all scores
      html += '<div id="leagueSecSessions" class="league-sec" style="display:'+(active==='Sessions'?'block':'none')+'">';
      html += '<div class="empty">All game nights for the season…</div>';
      html += '</div>';

      // Calendar: month grid of game nights with result markers
      html += '<div id="leagueSecCalendar" class="league-sec" style="display:'+(active==='Calendar'?'block':'none')+'">';
      html += '<div class="empty">Season calendar…</div>';
      html += '</div>';

      // Compare: team vs team head-to-head + tale of the tape
      html += '<div id="leagueSecCompare" class="league-sec" style="display:'+(active==='Compare'?'block':'none')+'">';
      html += '<div class="empty">Pick two teams to compare…</div>';
      html += '</div>';

      $content.innerHTML = html;
      animateNumbers($content);

      if (active === 'Sessions') loadLeagueSessions(leagueId);
      if (active === 'Calendar') loadLeagueCalendar(leagueId);
      if (active === 'Compare') loadLeagueCompare(leagueId);

      $('.pill-row')?.addEventListener('click', e => {
        if (e.target.classList.contains('pill') && e.target.dataset.sec) {
          const sec = e.target.dataset.sec;
          localStorage.setItem('cahl-league-section', sec);
          document.querySelectorAll('.pill[data-sec]').forEach(p => p.classList.toggle('active', p.dataset.sec === sec));
          document.querySelectorAll('.league-sec').forEach(s => s.style.display = s.id === 'leagueSec' + sec ? 'block' : 'none');
          if (sec === 'Sessions') loadLeagueSessions(leagueId);
          if (sec === 'Calendar') loadLeagueCalendar(leagueId);
          if (sec === 'Compare') loadLeagueCompare(leagueId);
        }
      });
    }

    async function ensureSessions(leagueId, force=false) {
      if (state._sessions && state._sessions.leagueId === leagueId && !force) return state._sessions;
      const data = await api(`/api/sessions/${leagueId}`, force);
      if (data.error) throw new Error(data.error);
      state._sessions = { leagueId, sessions: data.sessions, season: data.season };
      return state._sessions;
    }

    async function loadLeagueSessions(leagueId, force=false) {
      const $sec = $('#leagueSecSessions');
      if (!$sec) return;
      if (state._sessions && state._sessions.leagueId === leagueId && !force) {
        renderSessionsSection();
        return;
      }
      $sec.innerHTML = skeletonHtml(3);
      try {
        const pack = await ensureSessions(leagueId, force);
        if (!state.sessionDate) {
          // Default to the most recent night with final scores, else the last night
          const played = pack.sessions.filter(s => s.games.some(g => g.played));
          const fallback = played.length ? played[played.length - 1] : pack.sessions[pack.sessions.length - 1];
          state.sessionDate = fallback ? fallback.date : '';
        }
        renderSessionsSection();
      } catch (e) {
        $sec.innerHTML = `<div class="error">${e.message}</div>`;
      }
    }

    function renderSessionsSection() {
      const $sec = $('#leagueSecSessions');
      const pack = state._sessions;
      if (!$sec || !pack) return;
      const sessions = pack.sessions || [];
      if (!sessions.length) { $sec.innerHTML = '<div class="empty">No games found.</div>'; return; }

      const sel = sessions.some(s => s.date === state.sessionDate)
        ? state.sessionDate
        : sessions[sessions.length - 1].date;
      state.sessionDate = sel;

      // Date pills, most recent night first
      let html = '<div class="picker-days session-dates">';
      [...sessions].reverse().forEach(s => {
        const finals = s.games.filter(g => g.played).length;
        html += `<span class="pill date-pill ${s.date === sel ? 'active' : ''}" data-session="${s.date}" tabindex="0" role="button">${esc(s.date)}<span class="pill-count">${finals}/${s.games.length}</span></span>`;
      });
      html += '</div>';

      const cur = sessions.find(s => s.date === sel);
      const finals = cur.games.filter(g => g.played).length;
      html += `<div class="picker-hint">${cur.games.length} games · ${finals} final</div>`;
      html += '<div class="games-grid">' + cur.games.map(g => gameHtml(g)).join('') + '</div>';
      $sec.innerHTML = html;
      animateNumbers($sec);
    }

    // ---- Season calendar (month grid over the sessions data) ----
    const MONTH_NAMES = ['January','February','March','April','May','June','July','August','September','October','November','December'];

    function parseGameDate(d) {
      // "May 13" -> Date; infer the year, roll back if it lands far in the future
      const now = new Date();
      let dt = new Date(`${d} ${now.getFullYear()}`);
      if (isNaN(dt)) return null;
      if ((dt - now) / 86400000 > 200) dt = new Date(`${d} ${now.getFullYear() - 1}`);
      return dt;
    }

    function dateKey(dt) {
      return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
    }

    async function loadLeagueCalendar(leagueId, force=false) {
      const $sec = $('#leagueSecCalendar');
      if (!$sec) return;
      $sec.innerHTML = skeletonHtml(3);
      try {
        await ensureSessions(leagueId, force);
        if (!state.calMonth) {
          // Default to the month containing the most recent played night, else current month
          const played = state._sessions.sessions.filter(s => s.games.some(g => g.played));
          const ref = played.length ? played[played.length - 1] : state._sessions.sessions[state._sessions.sessions.length - 1];
          const dt = ref ? parseGameDate(ref.date) : null;
          const base = dt || new Date();
          state.calMonth = `${base.getFullYear()}-${String(base.getMonth() + 1).padStart(2, '0')}`;
        }
        renderCalendarSection();
      } catch (e) {
        $sec.innerHTML = `<div class="error">${e.message}</div>`;
      }
    }

    function renderCalendarSection() {
      const $sec = $('#leagueSecCalendar');
      const pack = state._sessions;
      if (!$sec || !pack) return;

      // Map dateKey -> { dateLabel, games }
      const byDay = {};
      pack.sessions.forEach(s => {
        const dt = parseGameDate(s.date);
        if (dt) byDay[dateKey(dt)] = s;
      });

      const [yy, mm] = state.calMonth.split('-').map(Number);
      const first = new Date(yy, mm - 1, 1);
      const daysInMonth = new Date(yy, mm, 0).getDate();
      const startDow = first.getDay(); // 0 = Sunday
      const todayKey = dateKey(new Date());

      let html = '<div class="cal-nav">'
        + '<button class="ghost small" data-cal-prev aria-label="Previous month">\u2039</button>'
        + `<span class="cal-title">${MONTH_NAMES[mm - 1]} ${yy}</span>`
        + '<span class="cal-nav-right">'
        + '<button class="ghost small" data-cal-today>Today</button>'
        + '<button class="ghost small" data-cal-next aria-label="Next month">\u203a</button>'
        + '</span>'
        + '</div>';

      html += '<div class="cal-grid">';
      ['S','M','T','W','T','F','S'].forEach(d => { html += `<span class="cal-dow">${d}</span>`; });
      for (let i = 0; i < startDow; i++) html += '<span class="cal-cell empty-cell"></span>';

      for (let day = 1; day <= daysInMonth; day++) {
        const key = `${yy}-${String(mm).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const sess = byDay[key];
        let cellClass = 'cal-cell';
        if (key === todayKey) cellClass += ' today';
        let dots = '';
        if (sess) {
          cellClass += ' has-games';
          dots = '<span class="cal-dots">' + sess.games.map(g => {
            let cls = 'cal-dot';
            if (g.played && state.teamId && (g.home_id === state.teamId || g.away_id === state.teamId)) {
              const us = g.home_id === state.teamId ? g.home_score : g.away_score;
              const them = g.home_id === state.teamId ? g.away_score : g.home_score;
              cls += us > them ? ' w' : (us < them ? ' l' : ' t');
            } else if (g.played) {
              cls += ' played';
            } else {
              cls += ' upcoming';
            }
            return `<span class="${cls}"></span>`;
          }).join('') + '</span>';
        }
        html += `<span class="${cellClass}" ${sess ? `data-cal-day="${key}" tabindex="0" role="button" aria-label="${sess.date}: ${sess.games.length} games"` : ''}><span class="cal-num">${day}</span>${dots}</span>`;
      }
      html += '</div>';

      // Selected day's games
      const selKey = state.calDay && byDay[state.calDay] ? state.calDay : null;
      if (selKey) {
        const sess = byDay[selKey];
        const finals = sess.games.filter(g => g.played).length;
        html += `<div class="picker-hint" style="margin-top:12px">${sess.date} \u00b7 ${sess.games.length} games \u00b7 ${finals} final</div>`;
        html += '<div class="games-grid" style="margin-top:8px">' + sess.games.map(g => gameHtml(g)).join('') + '</div>';
      } else {
        html += '<div class="picker-hint" style="margin-top:12px">Tap a day with dots to see that night\u2019s scores. Dots are green/red for your team\u2019s W/L when a team is selected.</div>';
      }

      $sec.innerHTML = html;
      animateNumbers($sec);
    }

    // ---- Team vs Team comparison ----
    async function loadLeagueCompare(leagueId) {
      const $sec = $('#leagueSecCompare');
      if (!$sec) return;

      if (!state.cmpA && state.teamId && state.teams.find(t => t.id === state.teamId)) state.cmpA = state.teamId;
      if (!state.cmpA && state.teams.length) state.cmpA = state.teams[0].id;
      if (!state.cmpB || state.cmpB === state.cmpA) {
        const other = state.teams.find(t => t.id !== state.cmpA);
        state.cmpB = other ? other.id : '';
      }

      let html = '<div class="cmp-picker">';
      html += `<select id="cmpA" aria-label="Team A">${state.teams.map(t => `<option value="${t.id}" ${t.id===state.cmpA?'selected':''}>${esc(t.name)}</option>`).join('')}</select>`;
      html += '<span class="t-vs">vs</span>';
      html += `<select id="cmpB" aria-label="Team B">${state.teams.map(t => `<option value="${t.id}" ${t.id===state.cmpB?'selected':''}>${esc(t.name)}</option>`).join('')}</select>`;
      html += '<button class="ghost small" id="cmpSwap" title="Swap teams" aria-label="Swap teams">\u21c4</button>';
      html += '</div><div id="cmpContent"></div>';
      $sec.innerHTML = html;

      $('#cmpA').onchange = e => { state.cmpA = e.target.value; renderComparison(); };
      $('#cmpB').onchange = e => { state.cmpB = e.target.value; renderComparison(); };
      $('#cmpSwap').onclick = () => { const t = state.cmpA; state.cmpA = state.cmpB; state.cmpB = t; loadLeagueCompare(leagueId); };

      await renderComparison();
    }

    function winProb(aS, bS) {
      // Fun logistic blend of points% and per-game goal diff
      const pa = (aS.pts || 0) / Math.max((aS.gp || 0) * 2, 1);
      const pb = (bS.pts || 0) / Math.max((bS.gp || 0) * 2, 1);
      const ga = ((aS.gf || 0) - (aS.ga || 0)) / Math.max(aS.gp || 1, 1);
      const gb = ((bS.gf || 0) - (bS.ga || 0)) / Math.max(bS.gp || 1, 1);
      const x = (pa - pb) * 2.2 + (ga - gb) * 0.35;
      return 1 / (1 + Math.exp(-x));
    }

    async function renderComparison() {
      const el = $('#cmpContent');
      if (!el) return;
      if (!state.cmpA || !state.cmpB || state.cmpA === state.cmpB) {
        el.innerHTML = '<div class="empty">Pick two different teams to compare.</div>';
        return;
      }
      el.innerHTML = skeletonHtml(3);
      const [a, b] = await Promise.all([api(`/api/team/${state.cmpA}`), api(`/api/team/${state.cmpB}`)]);
      if (a.error || b.error) { el.innerHTML = '<div class="error">Failed to load one of the teams.</div>'; return; }

      const aName = a.overview.team_name, bName = b.overview.team_name;
      const aS = a.standings.find(s => s.team_id === state.cmpA) || {};
      const bS = b.standings.find(s => s.team_id === state.cmpB) || {};
      const aRank = a.standings.findIndex(s => s.team_id === state.cmpA) + 1;
      const bRank = b.standings.findIndex(s => s.team_id === state.cmpB) + 1;
      const aForm = a.form || {}, bForm = b.form || {};

      // Head-to-head from A's schedule (meetings appear on both schedules)
      const todayK = dateKey(new Date());
      const meetings = a.schedule.filter(g => g.home_id === state.cmpB || g.away_id === state.cmpB);
      const past = meetings.filter(g => { const dt = parseGameDate(g.date); return dt && dateKey(dt) <= todayK && g.played; });
      const upcoming = meetings.filter(g => { const dt = parseGameDate(g.date); return dt && dateKey(dt) > todayK; });

      let aw = 0, bw = 0, ties = 0;
      past.forEach(g => {
        const us = g.home_id === state.cmpA ? g.home_score : g.away_score;
        const them = g.home_id === state.cmpA ? g.away_score : g.home_score;
        if (us > them) aw++; else if (us < them) bw++; else ties++;
      });

      let html = `<div class="cmp-title"><span class="cmp-team-a link" onclick="selectTeam('${state.cmpA}')">${esc(aName)}</span><span class="t-vs">vs</span><span class="cmp-team-b link" onclick="selectTeam('${state.cmpB}')">${esc(bName)}</span></div>`;

      // Head-to-head card
      html += '<div class="card cmp-card"><h3>Head to Head</h3>';
      if (past.length) {
        html += `<div class="cmp-h2h-record">${aw}\u2013${bw}${ties ? '\u2013' + ties : ''} <span class="picker-hint" style="display:inline;margin:0">this season</span></div>`;
        html += past.map(g => {
          const us = g.home_id === state.cmpA ? g.home_score : g.away_score;
          const them = g.home_id === state.cmpA ? g.away_score : g.home_score;
          const res = us > them ? 'w' : (us < them ? 'l' : 't');
          return `<div class="cmp-h2h-item"><span class="form-chip ${res}">${res.toUpperCase()}</span><span class="cmp-h2h-score">${us}\u2013${them}</span><span class="cmp-h2h-date">${esc(g.date)}${g.score_sheet ? ` <a class="link" href="${g.score_sheet}" target="_blank" rel="noopener" title="Score sheet">\u2197</a>` : ''}</span></div>`;
        }).join('');
      } else {
        html += '<div class="empty">No meetings yet this season.</div>';
      }
      if (upcoming.length) {
        const g = upcoming[0];
        html += `<div class="picker-hint" style="margin-top:8px">Next meeting: <b>${esc(g.date)}</b> ${fmtTime(g.time)} \u00b7 ${esc(g.facility || '')}</div>`;
      }
      html += '</div>';

      // Tale of the tape
      const rows = [
        { label: 'Rank', a: aRank ? `${aRank}${aRank===1?'st':aRank===2?'nd':aRank===3?'rd':'th'}` : '-', b: bRank ? `${bRank}${bRank===1?'st':bRank===2?'nd':bRank===3?'rd':'th'}` : '-', av: -aRank, bv: -bRank, better: 'high' },
        { label: 'Points', a: aS.pts ?? '-', b: bS.pts ?? '-', av: aS.pts ?? 0, bv: bS.pts ?? 0, better: 'high' },
        { label: 'Record', a: aForm.record || '-', b: bForm.record || '-', av: null, bv: null, better: null },
        { label: 'Pts %', a: aForm.played ? Math.round((aForm.pts_pct ?? aForm.win_pct) * 100) + '%' : '-', b: bForm.played ? Math.round((bForm.pts_pct ?? bForm.win_pct) * 100) + '%' : '-', av: aForm.pts_pct ?? aForm.win_pct ?? 0, bv: bForm.pts_pct ?? bForm.win_pct ?? 0, better: 'high' },
        { label: 'Goals For', a: aS.gf ?? '-', b: bS.gf ?? '-', av: aS.gf ?? 0, bv: bS.gf ?? 0, better: 'high' },
        { label: 'Goals Against', a: aS.ga ?? '-', b: bS.ga ?? '-', av: aS.ga ?? 0, bv: bS.ga ?? 0, better: 'low' },
        { label: 'Goal Diff', a: (aForm.goal_diff > 0 ? '+' : '') + (aForm.goal_diff ?? 0), b: (bForm.goal_diff > 0 ? '+' : '') + (bForm.goal_diff ?? 0), av: aForm.goal_diff ?? 0, bv: bForm.goal_diff ?? 0, better: 'high' },
        { label: 'Home', a: aForm.home_record || '-', b: bForm.home_record || '-', av: null, bv: null, better: null },
        { label: 'Away', a: aForm.away_record || '-', b: bForm.away_record || '-', av: null, bv: null, better: null },
        { label: 'Streak', a: aForm.streak || '-', b: bForm.streak || '-', av: null, bv: null, better: null },
      ];
      html += '<div class="card cmp-card"><h3>Tale of the Tape</h3><table class="tot"><thead><tr><th></th><th class="num cmp-team-a">' + esc(aName) + '</th><th class="num cmp-team-b">' + esc(bName) + '</th></tr></thead><tbody>';
      rows.forEach(r => {
        let aCls = '', bCls = '';
        if (r.better && r.av !== null && r.bv !== null && r.av !== r.bv) {
          const aWins = r.better === 'high' ? r.av > r.bv : r.av < r.bv;
          if (aWins) aCls = ' class="tot-win num"'; else bCls = ' class="tot-win num"';
        }
        html += `<tr><td>${r.label}</td><td class="num${aCls ? ' tot-win' : ''}">${r.a}</td><td class="num${bCls ? ' tot-win' : ''}">${r.b}</td></tr>`;
      });
      html += '</tbody></table></div>';

      // Fancied bar
      const p = winProb(aS, bS);
      const pctA = Math.round(p * 100), pctB = 100 - pctA;
      html += `<div class="card cmp-card"><h3>Fancied (for fun)</h3>
        <div class="prob-labels"><span class="cmp-team-a">${esc(aName)} ${pctA}%</span><span class="cmp-team-b">${pctB}% ${esc(bName)}</span></div>
        <div class="prob-bar"><div class="prob-a" style="width:${pctA}%"></div><div class="prob-b" style="width:${pctB}%"></div></div>
        <div class="picker-hint">Based on points % and goal differential — not science.</div>
      </div>`;

      // Top players + goalies side by side
      html += '<div class="cmp-grid">';
      html += '<div class="card cmp-card"><h3>Top Scorers \u00b7 ' + esc(aName) + '</h3><table><tbody>' +
        (a.overview.team_leaders.points || []).slice(0, 3).map(p => `<tr><td>${esc(p.name)}</td><td class="num">${p.points} pts</td></tr>`).join('') + '</tbody></table></div>';
      html += '<div class="card cmp-card"><h3>Top Scorers \u00b7 ' + esc(bName) + '</h3><table><tbody>' +
        (b.overview.team_leaders.points || []).slice(0, 3).map(p => `<tr><td>${esc(p.name)}</td><td class="num">${p.points} pts</td></tr>`).join('') + '</tbody></table></div>';
      const ga = (a.roster.goalies || [])[0], gb = (b.roster.goalies || [])[0];
      if (ga || gb) {
        html += '<div class="card cmp-card"><h3>Goalie \u00b7 ' + esc(aName) + '</h3>' +
          (ga ? `<table><tbody><tr><td>${esc(ga.name)}</td><td class="num">${ga.w}-${ga.l}-${ga.otl}</td><td class="num">${typeof ga.gaa === 'number' ? ga.gaa.toFixed(1) : ga.gaa} GAA</td></tr></tbody></table>` : '<div class="empty">No goalie stats</div>') + '</div>';
        html += '<div class="card cmp-card"><h3>Goalie \u00b7 ' + esc(bName) + '</h3>' +
          (gb ? `<table><tbody><tr><td>${esc(gb.name)}</td><td class="num">${gb.w}-${gb.l}-${gb.otl}</td><td class="num">${typeof gb.gaa === 'number' ? gb.gaa.toFixed(1) : gb.gaa} GAA</td></tr></tbody></table>` : '<div class="empty">No goalie stats</div>') + '</div>';
      }
      html += '</div>';

      el.innerHTML = html;
      animateNumbers(el);
    }

    async function renderTeam(refresh) {
      if (!state.leagues.length) {
        const home = await api('/api/today');
        state.leagues = home.leagues || [];
      }

      let html = '<div class="card"><h2>My Team</h2>' + teamSearchHtml();

      if (state.leagueId) {
        if (!state.teams.length) {
          const data = await api(`/api/league/${state.leagueId}`);
          state.teams = data.standings.map(s => ({ id: s.team_id, name: s.team })).filter(t => t.id);
        }
        html += changeLeagueHtml();
        html += '<select id="teamSelect"><option value="">Choose your team</option>';
        state.teams.forEach(t => html += `<option value="${t.id}" ${t.id === state.teamId ? 'selected' : ''}>${t.name}</option>`);
        html += '</select>';
        html += '<div id="teamContent"></div></div>';
        setMainHtml(html);
        bindTeamSearch();
        $('#teamSelect').onchange = async (e) => {
          state.teamId = e.target.value;
          localStorage.setItem('cahl-team', state.teamId);
          await loadTeamContent(state.teamId);
        };
        if (state.teamId) await loadTeamContent(state.teamId, refresh);
      } else if (state.teamId) {
        // Team tapped from a game card but league unknown — show the team, offer picker to switch
        html += '<div id="teamContent"></div>';
        html += '<div class="picker-hint" style="margin-top:16px">Pick your league to switch teams:</div>' + pickerHtml() + '</div>';
        setMainHtml(html);
        bindTeamSearch();
        await loadTeamContent(state.teamId, refresh);
      } else {
        html += '<div class="picker-hint" style="margin:-4px 0 10px">Pick a day, then your league</div>' + pickerHtml();
        html += '<div id="teamContent"></div></div>';
        setMainHtml(html);
        bindTeamSearch();
      }
    }

    async function loadTeamContent(teamId, refresh=false) {
      const $content = $('#teamContent');
      $content.innerHTML = skeletonHtml(3);
      const data = await api(`/api/team/${teamId}`, refresh);
      if (data.error) { $content.innerHTML = `<div class="error">${data.error}</div>`; return; }

      const over = data.overview;
      const standings = data.standings || [];
      const rank = standings.findIndex(s => s.team_id === teamId) + 1;
      const rankSuffix = rank === 1 ? 'st' : rank === 2 ? 'nd' : rank === 3 ? 'rd' : 'th';
      const icalUrl = `https://www.chillerstats.com/team/calendar_export.cfm?TeamID=${teamId}`;

      let html = `<div class="team-head">
        <h3 style="color:var(--text);margin:0">${esc(over.team_name)}</h3>
        <div class="team-head-actions">
          ${rank ? `<span class="hero-rank">${rank}${rankSuffix} of ${standings.length}</span>` : ''}
          <a class="ghost small btn-link" href="${icalUrl}" target="_blank" rel="noopener" title="Subscribe to this team's schedule in your calendar">iCal</a>
          <button class="ghost small" onclick="shareTeamResult('${teamId}')" title="Copy last result to share">Share</button>
        </div>
      </div>`;

      // Season record / historical wins (derived from full schedule)
      const form = data.form || {};
      if (form.played) {
        const s = form.streak || '';
        const streakClass = s.startsWith('W') ? 'win' : (s.startsWith('L') ? 'loss' : (s.startsWith('O') ? 'otl' : 'tie'));
        html += `<div class="record-row">
          <div class="stat-box"><div class="num">${form.record}</div><div class="label">Record</div></div>
          <div class="stat-box"><div class="num">${form.points ?? '-'}</div><div class="label">Points</div></div>
          <div class="stat-box"><div class="num">${form.home_record}</div><div class="label">Home</div></div>
          <div class="stat-box"><div class="num">${form.away_record}</div><div class="label">Away</div></div>
          <div class="stat-box"><div class="num">${form.goal_diff > 0 ? '+' + form.goal_diff : form.goal_diff}</div><div class="label">Goal Diff</div></div>
          <div class="stat-box"><div class="num"><span class="streak-badge ${streakClass}">${form.streak || '—'}</span></div><div class="label">Streak</div></div>
        </div>`;

        html += '<div class="form-chips-label">Last 5</div><div class="form-chips">' +
          (form.form || []).map(r => `<span class="form-chip ${r.toLowerCase()}">${r}</span>`).join('') +
          '</div>';

        html += '<div class="form-chips-label">Season Timeline</div><div class="timeline">' +
          (form.timeline || []).map(t =>
            `<span class="tl-game ${t.result.toLowerCase()}" title="${esc(t.date)} ${t.location === 'H' ? 'vs' : '@'} ${esc(t.opponent)} (${t.score})">${t.result}</span>`
          ).join('') +
          '</div>';
      }

      if (over.next_game) {
        const ng = over.next_game;
        html += `<div class="game-card"><div class="meta">Next Game ${ng.home_away}</div><div class="matchup"><div class="team">${esc(over.team_name)}</div><span class="vs">vs</span><div class="team">${esc(ng.opponent)}</div></div><div class="meta">${esc(ng.date || 'TBD')} · ${fmtTime(ng.time)} · ${esc(ng.facility || 'TBD')}</div></div>`;
      }

      if (over.recent_result) {
        const r = over.recent_result;
        html += `<div class="game-card"><div class="meta">Recent Result</div><div class="matchup"><div class="team">${esc(r.home)}</div><span class="score">${r.home_final}-${r.away_final}</span><div class="team">${esc(r.away)}</div></div></div>`;
      }

      html += '<h3 style="margin-top:18px">Team Leaders</h3><div class="stat-grid">';
      const leaderKeys = ['points','goals','assists','pim'];
      const leaderLabels = {points:'Points', goals:'Goals', assists:'Assists', pim:'PIM'};
      leaderKeys.forEach(k => {
        const top = over.team_leaders[k][0];
        html += `<div class="stat-box"><div class="num">${top ? (top.points || top.goals || top.assists || top.pim || 0) : '-'}</div><div class="label">${leaderLabels[k]} ${top ? '· ' + esc(top.name) : ''}</div></div>`;
      });
      html += '</div>';

      html += '<h3 style="margin-top:18px">Standings</h3>';
      html += '<table><thead><tr><th>Team</th><th class="num">GP</th><th class="num">W</th><th class="num">L</th><th class="num">OTL</th><th class="num">PTS</th><th class="num">GF</th><th class="num">GA</th></tr></thead><tbody>';
      html += data.standings.map(s => `
        <tr ${s.team_id === teamId ? 'style="color:var(--accent);font-weight:700"' : ''}>
          <td>${esc(s.team)}</td><td class="num">${s.gp}</td><td class="num">${s.w}</td><td class="num">${s.l}</td><td class="num">${s.otl}</td>
          <td class="num">${s.pts}</td><td class="num">${s.gf}</td><td class="num">${s.ga}</td>
        </tr>`).join('');
      html += '</tbody></table>';

      html += '<h3 style="margin-top:18px">Schedule</h3>';
      html += '<table><thead><tr><th>Date</th><th>Time</th><th>Facility</th><th>Opponent</th><th class="num">Score</th><th class="num">Sheet</th></tr></thead><tbody>';
      html += data.schedule.map(g => {
        const isHome = g.home_id === teamId;
        const opp = isHome ? g.away : g.home;
        const oppId = isHome ? g.away_id : g.home_id;
        const score = g.played ? `${g.home_score}-${g.away_score}` : '';
        const sheet = g.score_sheet ? `<a class="link" href="${g.score_sheet}" target="_blank" rel="noopener" title="View official score sheet">\u2197</a>` : '';
        return `<tr><td>${esc(g.date)}</td><td>${fmtTime(g.time)}</td><td>${esc(g.facility)}</td><td class="link" onclick="selectTeam('${oppId || ''}')">${isHome ? 'vs ' : '@ '}${esc(opp)}</td><td class="num">${score}</td><td class="num">${sheet}</td></tr>`;
      }).join('');
      html += '</tbody></table>';

      // Full roster: position-grouped sections + goalies
      const roster = data.roster || { sections: [], goalies: [] };
      const totalPlayers = roster.sections.reduce((n, s) => n + s.players.length, 0) + roster.goalies.length;
      html += `<h3 style="margin-top:18px">Full Roster${totalPlayers ? ` <span style="color:var(--muted);font-weight:600">${totalPlayers}</span>` : ''}</h3>`;

      const skaterHead = '<table><thead><tr><th>#</th><th>Player</th><th>Pos</th><th class="num">GP</th><th class="num">G</th><th class="num">A</th><th class="num">Pts</th><th class="num">P/GP</th><th class="num">PIM</th></tr></thead><tbody>';
      roster.sections.forEach(sec => {
        html += `<div class="form-chips-label">${esc(sec.label)}</div>`;
        html += skaterHead + sec.players.slice().sort((a, b) => b.pts - a.pts).map(p => `
          <tr class="link" onclick="selectPlayerToken('${p.token || ''}')">
            <td>${esc(p.jersey || '-')}</td><td><span class="link">${esc(p.name)}</span></td><td>${esc(p.position || '-')}</td>
            <td class="num">${p.gp}</td><td class="num">${p.g}</td><td class="num">${p.a}</td><td class="num">${p.pts}</td>
            <td class="num">${p.gp ? (p.pts / p.gp).toFixed(2) : '-'}</td><td class="num">${p.pim}</td>
          </tr>`).join('') + '</tbody></table>';
      });

      if (roster.goalies.length) {
        html += '<div class="form-chips-label">Goalies</div>';
        html += '<table><thead><tr><th>#</th><th>Goalie</th><th class="num">GP</th><th class="num">W</th><th class="num">L</th><th class="num">OTL</th><th class="num">GA</th><th class="num">GAA</th></tr></thead><tbody>';
        html += roster.goalies.map(p => `
          <tr class="link" onclick="selectPlayerToken('${p.token || ''}')">
            <td>${esc(p.jersey || '-')}</td><td><span class="link">${esc(p.name)}</span></td>
            <td class="num">${p.gp}</td><td class="num">${p.w}</td><td class="num">${p.l}</td><td class="num">${p.otl}</td>
            <td class="num">${p.ga}</td><td class="num">${typeof p.gaa === 'number' ? p.gaa.toFixed(1) : p.gaa}</td>
          </tr>`).join('');
        html += '</tbody></table>';
      }

      $content.innerHTML = html;
      animateNumbers($content);
    }

    async function renderPlayers(refresh) {
      if (!state.leagues.length) {
        const home = await api('/api/today');
        state.leagues = home.leagues || [];
      }

      let html = '<div class="card">';
      if (state.playersLeague) {
        html += `<h2>Player Leaders · ${currentPlayersLeagueName()}</h2>`;
      } else {
        html += '<h2>CAHL Player Leaders</h2>';
      }
      html += playersPickerHtml();

      if (state.playersLeague) {
        const data = await api(`/api/league/${state.playersLeague}`, refresh);
        if (data.error) { setMainHtml(html + `<div class="error">${data.error}</div></div>`); return; }
        html += leaderSection('Pts', data.leaders.points, 'value');
        html += leaderSection('G', data.leaders.goals, 'value');
        html += leaderSection('A', data.leaders.assists, 'value');
        html += leaderSection('PIM', data.leaders.pim, 'value');
        html += '</div>';
        setMainHtml(html);
        return;
      }

      const data = await api('/api/leaders', refresh);
      if (data.error) { setMainHtml(html + `<div class="error">${data.error}</div></div>`); return; }
      html += leaderSection('Pts', data.points, 'points');
      html += leaderSection('G', data.goals, 'goals');
      html += leaderSection('A', data.assists, 'assists');
      html += '</div>';
      setMainHtml(html);
    }

    async function renderPlayerProfile(teamId, playerId, token) {
      $main.innerHTML = skeletonHtml(3);
      const path = token ? `/api/player-token/${encodeURIComponent(token)}` : `/api/player/${teamId}/${playerId}`;
      const data = await api(path);
      if (data.error) { $main.innerHTML = `<div class="error">${data.error}</div>`; return; }

      let html = `<div class="card"><h2>${data.name}</h2>`;
      if (data.history.length) {
        const totals = data.history.reduce((acc, h) => {
          acc.gp += h.gp; acc.g += h.g; acc.a += h.a; acc.pts += h.pts; acc.pim += h.pim;
          return acc;
        }, { gp: 0, g: 0, a: 0, pts: 0, pim: 0 });
        html += '<h3>Career Totals</h3><div class="stat-grid">' +
          `<div class="stat-box"><div class="num">${totals.gp}</div><div class="label">Games</div></div>` +
          `<div class="stat-box"><div class="num">${totals.g}</div><div class="label">Goals</div></div>` +
          `<div class="stat-box"><div class="num">${totals.a}</div><div class="label">Assists</div></div>` +
          `<div class="stat-box"><div class="num">${totals.pts}</div><div class="label">Points</div></div>` +
          `<div class="stat-box"><div class="num">${totals.pim}</div><div class="label">PIM</div></div>` +
          `<div class="stat-box"><div class="num">${data.history.length}</div><div class="label">Seasons</div></div>` +
          '</div><h3 style="margin-top:18px">Season by Season</h3>';
      }
      html += '<table><thead><tr><th>Season</th><th>League</th><th>Team</th><th class="num">GP</th><th class="num">G</th><th class="num">A</th><th class="num">Pts</th><th class="num">PIM</th></tr></thead><tbody>';
      html += data.history.map(h => `
        <tr><td>${h.season}</td><td>${h.league}</td><td>${h.team}</td>
        <td class="num">${h.gp}</td><td class="num">${h.g}</td><td class="num">${h.a}</td><td class="num">${h.pts}</td><td class="num">${h.pim}</td></tr>`).join('');
      html += '</tbody></table></div>';
      const backTab = state.profileReturn || 'players';
      const backLabels = { today: 'Today', league: 'League', team: 'Team', players: 'Leaders', analytics: 'Analytics' };
      html += `<button class="ghost" onclick="setTab('${backTab}')">\u2190 Back to ${backLabels[backTab] || 'Leaders'}</button>`;
      setMainHtml(html);
    }

    async function renderAnalytics(refresh) {
      if (!state.leagues.length) {
        const home = await api('/api/today');
        state.leagues = home.leagues || [];
      }

      if (!state.leagueId) {
        let html = '<div class="card"><h2>Analytics</h2>';
        html += '<div class="picker-hint" style="margin:-4px 0 10px">Pick a day, then a league</div>' + pickerHtml() + '</div>';
        setMainHtml(html);
        return;
      }

      const data = await api(`/api/league/${state.leagueId}`, refresh);
      await loadAnalyticsContent(data);
    }

    async function loadAnalyticsContent(data) {
      if (!data || data.error) { $main.innerHTML = `<div class="error">${(data||{}).error || 'No data'}</div>`; return; }

      let html = `<div class="card"><h2>Analytics · ${data.league_name}</h2>`;
      html += changeLeagueHtml();

      // Points leaders mini chart
      const maxPts = Math.max(...data.standings.map(s => s.pts), 1);
      html += '<h3>Standings by Points</h3>';
      html += data.standings.map(s => `
        <div style="margin-bottom:8px" onclick="selectTeam('${s.team_id}')">
          <div style="display:flex;justify-content:space-between;font-size:13px"><span class="link">${s.team}</span><span>${s.pts} pts</span></div>
          <div class="bar"><div class="fill gf" style="width:${(s.pts / maxPts * 100).toFixed(1)}%"></div></div>
        </div>`).join('');

      // Goals for vs against
      const maxG = Math.max(...data.standings.map(s => Math.max(s.gf, s.ga)), 1);
      html += '<h3 style="margin-top:18px">Goals For vs Against</h3>';
      html += data.standings.slice(0, 8).map(s => `
        <div style="margin-bottom:10px" onclick="selectTeam('${s.team_id}')">
          <div style="display:flex;justify-content:space-between;font-size:13px"><span class="link">${s.team}</span><span><span style="color:var(--accent-2)">GF ${s.gf}</span> / <span style="color:var(--danger)">GA ${s.ga}</span></span></div>
          <div class="bar" title="GF green, GA red"><div class="fill gf" style="width:${(s.gf / (s.gf + s.ga || 1) * 100).toFixed(1)}%"></div><div class="fill ga" style="width:${(s.ga / (s.gf + s.ga || 1) * 100).toFixed(1)}%"></div></div>
        </div>`).join('');

      // Top scorers
      html += '<h3 style="margin-top:18px">Top Scorers</h3><table><thead><tr><th>Player</th><th>Team</th><th class="num">Pts</th></tr></thead><tbody>';
      html += data.leaders.points.map(p => `<tr class="link" onclick="selectPlayer('${p.team_id}','${p.player_id}')"><td><span class="link">${p.name}</span></td><td>${p.team}</td><td class="num">${p.value}</td></tr>`).join('');
      html += '</tbody></table></div>';

      setMainHtml(html);
    }

    // Toast + screen-reader announcements
    function announce(message) {
      const announcer = document.getElementById('a11y-announcer');
      if (announcer) {
        announcer.textContent = message;
        setTimeout(() => { announcer.textContent = ''; }, 1000);
      }
    }

    let toastTimer = null;
    function showToast(message) {
      let toast = document.getElementById('toast');
      if (!toast) return;
      toast.textContent = message;
      toast.classList.add('show');
      announce(message);
      if (toastTimer) clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
    }

    // Public helpers for inline event handlers
    window.setTab = setTab;
    window.selectTeam = (teamId) => {
      if (!teamId) return;
      state.teamId = teamId;
      localStorage.setItem('cahl-team', teamId);
      setTab('team');
    };
    window.selectPlayer = (teamId, playerId) => {
      if (!teamId || !playerId) return;
      state.profileReturn = state.tab;
      renderPlayerProfile(teamId, playerId);
    };

    window.selectPlayerToken = (token) => {
      if (!token) return;
      state.profileReturn = state.tab;
      renderPlayerProfile(null, null, token);
    };

    // Share the selected team's last result to the clipboard
    window.shareTeamResult = async (teamId) => {
      const data = await api(`/api/team/${teamId}`);
      if (data.error) { showToast('Could not load team'); return; }
      const over = data.overview, r = over.recent_result, form = data.form || {};
      if (!r) { showToast('No recent result to share'); return; }
      const isHome = r.home_id === teamId;
      const us = isHome ? r.home_final : r.away_final;
      const them = isHome ? r.away_final : r.home_final;
      const res = us > them ? 'W' : (us < them ? 'L' : 'T');
      const text = `${over.team_name} ${res} ${us}\u2013${them} ${isHome ? 'vs' : '@'} ${isHome ? r.away : r.home}` +
        (form.played ? ` \u00b7 Season: ${form.record}` : '');
      try {
        await navigator.clipboard.writeText(text);
        showToast('Result copied \u2014 paste it anywhere');
      } catch (e) {
        showToast(text);
      }
    };

    // Navigation
    navLinks.forEach(a => a.addEventListener('click', e => {
      e.preventDefault();
      setTab(a.dataset.tab);
    }));

    // Brand takes you home (Today) and back to the top
    document.getElementById('brandHome').addEventListener('click', e => {
      e.preventDefault();
      setTab('today');
      $main.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Keyboard operability for pill/cell controls (Enter/Space activates)
    $main.addEventListener('keydown', e => {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      const target = e.target.closest('[data-day], [data-lid], [data-sec], [data-session], [data-cal-day], [data-pl-all], [data-pl-day], [data-pl-lid], [data-change-league], [data-cal-today], [data-cal-prev], [data-cal-next]');
      if (target) {
        e.preventDefault();
        target.click();
      }
    });

    // Delegated league-picker + change-league clicks
    $main.addEventListener('click', async (e) => {
      // Players-tab division filter (separate state from main league picker)
      const plAll = e.target.closest('[data-pl-all]');
      if (plAll) {
        state.playersLeague = '';
        state.playersDay = '';
        localStorage.removeItem('cahl-players-league');
        await renderPlayers();
        return;
      }
      const plDay = e.target.closest('[data-pl-day]');
      if (plDay) {
        const day = plDay.dataset.plDay;
        state.playersDay = day;
        // Immediately filter to that day's first division so content always matches the picker
        const groups = leagueGroups();
        const first = (groups[day] || [])[0];
        if (first) {
          state.playersLeague = first.id;
          localStorage.setItem('cahl-players-league', first.id);
        }
        await renderPlayers();
        return;
      }
      const plLid = e.target.closest('[data-pl-lid]');
      if (plLid) {
        state.playersLeague = plLid.dataset.plLid;
        localStorage.setItem('cahl-players-league', state.playersLeague);
        const l = state.leagues.find(x => x.id === state.playersLeague);
        if (l) state.playersDay = leagueDay(l.name);
        await renderPlayers();
        return;
      }

      // Sessions date pills
      const sessEl = e.target.closest('[data-session]');
      if (sessEl) {
        state.sessionDate = sessEl.dataset.session;
        renderSessionsSection();
        return;
      }

      // Calendar controls
      const calToday = e.target.closest('[data-cal-today]');
      if (calToday) {
        const now = new Date();
        state.calMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        state.calDay = dateKey(now);
        renderCalendarSection();
        return;
      }
      const calPrev = e.target.closest('[data-cal-prev]');
      const calNext = e.target.closest('[data-cal-next]');
      if (calPrev || calNext) {
        const [yy, mm] = state.calMonth.split('-').map(Number);
        const dt = new Date(yy, mm - 1 + (calNext ? 1 : -1), 1);
        state.calMonth = `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`;
        state.calDay = '';
        renderCalendarSection();
        return;
      }
      const calDay = e.target.closest('[data-cal-day]');
      if (calDay) {
        state.calDay = calDay.dataset.calDay;
        renderCalendarSection();
        return;
      }

      const chg = e.target.closest('[data-change-league]');
      if (chg) {
        state.leagueId = '';
        localStorage.removeItem('cahl-league');
        await loadActiveTab();
        return;
      }
      const dayEl = e.target.closest('.day-pill');
      if (dayEl) {
        state.leagueDay = dayEl.dataset.day;
        localStorage.setItem('cahl-league-day', state.leagueDay);
        await loadActiveTab();
        return;
      }
      const lidEl = e.target.closest('.league-pill');
      if (lidEl) {
        await chooseLeague(lidEl.dataset.lid);
      }
    });

    $refresh.addEventListener('click', refreshAll);

    $auto.addEventListener('change', () => {
      state.auto = $auto.checked;
      localStorage.setItem('cahl-auto', state.auto ? '1' : '');
      if (autoTimer) clearInterval(autoTimer);
      if (state.auto) {
        autoTimer = setInterval(() => loadActiveTab(true), 60000);
      }
    });

    // Init
    (() => {
      state.auto = !!localStorage.getItem('cahl-auto');
      $auto.checked = state.auto;
      if (state.auto) autoTimer = setInterval(() => loadActiveTab(true), 60000);
      setTab(state.tab);
    })();
