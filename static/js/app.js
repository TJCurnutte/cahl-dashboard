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
      leaders: null,
      cache: {}
    };

    const TABS = ['today','league','team','players','analytics'];
    let autoTimer = null;

    function $(sel){ return document.querySelector(sel); }
    function fmtTime(t){ return t || 'TBD'; }

    // Desktop vs mobile context: body.is-desktop mirrors the 900px CSS breakpoint
    const desktopMQ = window.matchMedia('(min-width: 900px)');
    function syncViewportClass() {
      document.body.classList.toggle('is-desktop', desktopMQ.matches);
      document.body.classList.toggle('is-mobile', !desktopMQ.matches);
    }
    syncViewportClass();
    desktopMQ.addEventListener('change', syncViewportClass);

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
      s = s.replace(/^NTPRD Chiller\s+/i, '');
      s = s.replace(/^(Sunday|Monday|Tuesday|Tue|Wednesday|Thursday|Thur|Friday)\s*-?\s*/i, '');
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
        html += `<span class="pill day-pill ${d === day ? 'active' : ''}" data-day="${d}">${d}<span class="pill-count">${groups[d].length}</span></span>`;
      });
      html += '</div>';
      if (day && groups[day].length) {
        html += '<div class="picker-leagues">';
        groups[day].forEach(l => {
          html += `<span class="pill league-pill ${l.id === state.leagueId ? 'active' : ''}" data-lid="${l.id}">${shortLeagueName(l.name)}</span>`;
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
      html += `<span class="pill day-pill ${!state.playersLeague ? 'active' : ''}" data-pl-all="1">All CAHL</span>`;
      DAY_ORDER.forEach(d => {
        if (!groups[d].length) return;
        html += `<span class="pill day-pill ${d === activeDay && state.playersLeague ? 'active' : ''}" data-pl-day="${d}">${d}<span class="pill-count">${groups[d].length}</span></span>`;
      });
      html += '</div>';
      if (activeDay && groups[activeDay] && groups[activeDay].length) {
        html += '<div class="picker-leagues">';
        groups[activeDay].forEach(l => {
          html += `<span class="pill league-pill ${l.id === state.playersLeague ? 'active' : ''}" data-pl-lid="${l.id}">${shortLeagueName(l.name)}</span>`;
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
        `<tr class="link" onclick="selectPlayer('${p.team_id || ''}','${p.player_id || ''}')"><td class="num">${p.rank || ''}</td><td><span class="link">${p.name}</span></td><td>${p.team}</td><td class="num">${p[valKey] ?? p.value ?? 0}</td></tr>`
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
            `<div class="typeahead-item" data-tid="${t.id}" data-lid="${t.league_id}"><span class="ta-name">${t.name}</span><span class="ta-league">${t.league_name}</span></div>`
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
            <span>${g.date || 'Today'} ${fmtTime(g.time)} ${g.facility ? '· ' + g.facility : ''}</span>
            ${(played || (g.home_score !== undefined && g.home_score !== null)) ? '<span class="score">' + score + '</span>' : (live ? '<span class="live">Live</span>' : '')}
          </div>
          <div class="matchup">
            <div class="team link" data-team="${homeId || ''}" onclick="selectTeam('${homeId || ''}')">${home}</div>
            <span class="vs">vs</span>
            <div class="team link" data-team="${awayId || ''}" onclick="selectTeam('${awayId || ''}')">${away}</div>
          </div>
        </div>
      `;
    }

    function todayRowHtml(g) {
      const rink = (g.facility || '').replace(/^Chiller\s+/i, '');
      return `<div class="today-row">
        <span class="t-time">${fmtTime(g.time)}</span>
        <span class="t-match"><span class="link" onclick="selectTeam('${g.home_id || ''}')">${g.home}</span><span class="t-vs">vs</span><span class="link" onclick="selectTeam('${g.away_id || ''}')">${g.away}</span></span>
        <span class="t-rink">${rink}</span>
      </div>`;
    }

    async function renderToday(refresh) {
      const data = await api('/api/today', refresh);
      if (data.error) { $main.innerHTML = `<div class="error">${data.error}</div>`; return; }
      state.leagues = data.leagues;

      let html = '<div class="card today-card"><h2>Today\'s Games</h2>';
      if (!data.today.length) {
        html += '<div class="empty">No games posted yet.</div>';
      } else {
        html += '<div class="today-list">' + data.today.map(todayRowHtml).join('') + '</div>';
      }
      html += '</div>';

      html += '<div class="card"><h3>Leagues</h3>' + pickerHtml() +
        '<div class="picker-hint">Pick a day, then a league</div></div>';
      setMainHtml(html);
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

      // Reset sessions cache when the league changes
      if (state._sessions && state._sessions.leagueId !== leagueId) {
        state._sessions = null;
        state.sessionDate = '';
      }

      let html = `<h3 style="margin:18px 0 10px;color:var(--text)">${data.league_name} <span style="color:var(--muted);font-weight:400">${data.season}</span></h3>`;

      html += '<div class="pill-row">';
      const sections = ['Scores', 'Standings', 'Leaders', 'Sessions'];
      const active = localStorage.getItem('cahl-league-section') || 'Scores';
      sections.forEach(s => html += `<span class="pill ${s===active?'active':''}" data-sec="${s}">${s}</span>`);
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

      $content.innerHTML = html;
      animateNumbers($content);

      if (active === 'Sessions') loadLeagueSessions(leagueId);

      $('.pill-row')?.addEventListener('click', e => {
        if (e.target.classList.contains('pill') && e.target.dataset.sec) {
          const sec = e.target.dataset.sec;
          localStorage.setItem('cahl-league-section', sec);
          document.querySelectorAll('.pill[data-sec]').forEach(p => p.classList.toggle('active', p.dataset.sec === sec));
          document.querySelectorAll('.league-sec').forEach(s => s.style.display = s.id === 'leagueSec' + sec ? 'block' : 'none');
          if (sec === 'Sessions') loadLeagueSessions(leagueId);
        }
      });
    }

    async function loadLeagueSessions(leagueId, force=false) {
      const $sec = $('#leagueSecSessions');
      if (!$sec) return;
      if (state._sessions && state._sessions.leagueId === leagueId && !force) {
        renderSessionsSection();
        return;
      }
      $sec.innerHTML = skeletonHtml(3);
      const data = await api(`/api/sessions/${leagueId}`, force);
      if (data.error) { $sec.innerHTML = `<div class="error">${data.error}</div>`; return; }
      state._sessions = { leagueId, sessions: data.sessions, season: data.season };
      if (!state.sessionDate) {
        // Default to the most recent night with final scores, else the last night
        const played = data.sessions.filter(s => s.games.some(g => g.played));
        const fallback = played.length ? played[played.length - 1] : data.sessions[data.sessions.length - 1];
        state.sessionDate = fallback ? fallback.date : '';
      }
      renderSessionsSection();
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
        html += `<span class="pill date-pill ${s.date === sel ? 'active' : ''}" data-session="${s.date}">${s.date}<span class="pill-count">${finals}/${s.games.length}</span></span>`;
      });
      html += '</div>';

      const cur = sessions.find(s => s.date === sel);
      const finals = cur.games.filter(g => g.played).length;
      html += `<div class="picker-hint">${cur.games.length} games · ${finals} final</div>`;
      html += '<div class="games-grid">' + cur.games.map(g => gameHtml(g)).join('') + '</div>';
      $sec.innerHTML = html;
      animateNumbers($sec);
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
      let html = `<h3 style="color:var(--text);margin-bottom:12px">${over.team_name}</h3>`;

      // Season record / historical wins (derived from full schedule)
      const form = data.form || {};
      if (form.played) {
        const streakClass = form.streak && form.streak.startsWith('W') ? 'win' : (form.streak && form.streak.startsWith('L') ? 'loss' : 'tie');
        html += `<div class="record-row">
          <div class="stat-box"><div class="num">${form.record}</div><div class="label">Record</div></div>
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
            `<span class="tl-game ${t.result.toLowerCase()}" title="${t.date} ${t.location === 'H' ? 'vs' : '@'} ${t.opponent} (${t.score})">${t.result}</span>`
          ).join('') +
          '</div>';
      }

      if (over.next_game) {
        const ng = over.next_game;
        html += `<div class="game-card"><div class="meta">Next Game ${ng.home_away}</div><div class="matchup"><div class="team">${over.team_name}</div><span class="vs">vs</span><div class="team">${ng.opponent}</div></div><div class="meta">${ng.date || 'TBD'} · ${fmtTime(ng.time)} · ${ng.facility || 'TBD'}</div></div>`;
      }

      if (over.recent_result) {
        const r = over.recent_result;
        html += `<div class="game-card"><div class="meta">Recent Result</div><div class="matchup"><div class="team">${r.home}</div><span class="score">${r.home_final}-${r.away_final}</span><div class="team">${r.away}</div></div></div>`;
      }

      html += '<h3 style="margin-top:18px">Team Leaders</h3><div class="stat-grid">';
      const leaderKeys = ['points','goals','assists','pim'];
      const leaderLabels = {points:'Points', goals:'Goals', assists:'Assists', pim:'PIM'};
      leaderKeys.forEach(k => {
        const top = over.team_leaders[k][0];
        html += `<div class="stat-box"><div class="num">${top ? (top.points || top.goals || top.assists || top.pim || 0) : '-'}</div><div class="label">${leaderLabels[k]} ${top ? '· ' + top.name : ''}</div></div>`;
      });
      html += '</div>';

      html += '<h3 style="margin-top:18px">Standings</h3>';
      html += '<table><thead><tr><th>Team</th><th class="num">GP</th><th class="num">W</th><th class="num">L</th><th class="num">OTL</th><th class="num">PTS</th><th class="num">GF</th><th class="num">GA</th></tr></thead><tbody>';
      html += data.standings.map(s => `
        <tr ${s.team_id === teamId ? 'style="color:var(--accent);font-weight:700"' : ''}>
          <td>${s.team}</td><td class="num">${s.gp}</td><td class="num">${s.w}</td><td class="num">${s.l}</td><td class="num">${s.otl}</td>
          <td class="num">${s.pts}</td><td class="num">${s.gf}</td><td class="num">${s.ga}</td>
        </tr>`).join('');
      html += '</tbody></table>';

      html += '<h3 style="margin-top:18px">Schedule</h3>';
      html += '<table><thead><tr><th>Date</th><th>Time</th><th>Facility</th><th>Opponent</th><th class="num">Score</th></tr></thead><tbody>';
      html += data.schedule.map(g => {
        const isHome = g.home_id === teamId;
        const opp = isHome ? g.away : g.home;
        const oppId = isHome ? g.away_id : g.home_id;
        const score = g.played ? `${g.home_score}-${g.away_score}` : '';
        return `<tr><td>${g.date}</td><td>${fmtTime(g.time)}</td><td>${g.facility}</td><td class="link" onclick="selectTeam('${oppId || ''}')">${isHome ? 'vs ' : '@ '}${opp}</td><td class="num">${score}</td></tr>`;
      }).join('');
      html += '</tbody></table>';

      html += '<h3 style="margin-top:18px">Player Stats</h3>';
      html += '<table><thead><tr><th>#</th><th>Player</th><th class="num">GP</th><th class="num">G</th><th class="num">A</th><th class="num">Pts</th><th class="num">PIM</th></tr></thead><tbody>';
      html += data.stats.sort((a,b) => b.pts - a.pts).map(p => `
        <tr class="link" onclick="selectPlayerToken('${p.token || ''}')">
          <td>${p.jersey || '-'}</td><td><span class="link">${p.name}</span></td>
          <td class="num">${p.gp}</td><td class="num">${p.g}</td><td class="num">${p.a}</td><td class="num">${p.pts}</td><td class="num">${p.pim}</td>
        </tr>`).join('');
      html += '</tbody></table>';

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
      html += '<button class="ghost" onclick="setTab(\'players\')">Back to Leaders</button>';
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
      renderPlayerProfile(teamId, playerId);
    };

    window.selectPlayerToken = (token) => {
      if (!token) return;
      renderPlayerProfile(null, null, token);
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

    // Delegated league-picker + change-league clicks
    $main.addEventListener('click', async (e) => {
      // Players-tab division filter (separate state from main league picker)
      const plAll = e.target.closest('[data-pl-all]');
      if (plAll) {
        state.playersLeague = '';
        localStorage.removeItem('cahl-players-league');
        await renderPlayers();
        return;
      }
      const plDay = e.target.closest('[data-pl-day]');
      if (plDay) {
        state.playersDay = plDay.dataset.plDay;
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
