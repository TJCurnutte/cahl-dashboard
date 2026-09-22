// Chrome-free repro harness: run the deployed app.js inside jsdom and drive
// the Team tab through every state a real visitor can hit, catching the
// "Maximum call stack size exceeded" reported on the Team tab.
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

const APP = 'https://cahl.neural-forge.io';

function makeDom(html) {
  const dom = new JSDOM(html, {
    url: APP + '/',
    runScripts: 'outside-only',
    pretendToBeVisual: true,
  });
  const { window } = dom;
  // minimal rAF shim (jsdom has none without pretendToBeVisual frames)
  window.requestAnimationFrame = (cb) => setTimeout(() => cb(window.performance.now()), 16);
  // matchMedia shim (jsdom lacks it)
  window.matchMedia = (q) => ({ matches: false, media: q, addEventListener: () => {}, removeEventListener: () => {}, addListener: () => {}, removeListener: () => {} });
  return dom;
}

async function main() {
  const indexHtml = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
  const appJs = fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8');
  const dom = makeDom(indexHtml);
  const { window } = dom;
  const { document } = window;

  // fetch stub backed by real prod API (network calls only, no browser)
  const realFetch = (p) => fetch(APP + p, { cache: 'no-store' }).then(r => r.json());
  window.fetch = (p) => {
    const url = String(p);
    return realFetch(url.startsWith('http') ? url.replace(APP, '') : url);
  };

  // swallow and record errors instead of killing the process
  const errors = [];
  window.addEventListener('error', (e) => errors.push(String(e.error && e.error.stack || e.message)));

  window.eval(appJs);

  // give init a tick
  await new Promise(r => setTimeout(r, 300));

  const results = [];
  const step = (name, fn) => Promise.resolve().then(fn)
    .then(() => results.push([name, 'ok']))
    .catch(e => results.push([name, 'THREW: ' + (e && e.stack ? e.stack.split('\n').slice(0, 4).join(' | ') : e)]));

  // 1. Today tab
  await step('today tab', async () => {
    window.eval("setTab('today')");
    await new Promise(r => setTimeout(r, 400));
  });

  // 2. Team tab cold (no league, no team) — the picker branch
  await step('team tab cold', async () => {
    window.eval("setTab('team')");
    await new Promise(r => setTimeout(r, 400));
  });

  // 3. Team tab with league+team restored from localStorage (the hero branch)
  await step('team tab with league+team', async () => {
    const today = await realFetch('/api/today');
    const leagues = today.leagues || [];
    const fri = leagues.find(l => /Friday/i.test(l.name)) || leagues[0];
    const lg = await realFetch('/api/league/' + fri.id);
    const t0 = (lg.standings || [])[0];
    if (t0) {
      window.localStorage.setItem('cahl-league', fri.id);
      window.localStorage.setItem('cahl-team', t0.team_id);
      // re-init the app with restored state: re-eval a fresh copy
      window.eval(appJs);
      window.eval("setTab('team')");
      await new Promise(r => setTimeout(r, 3000));
    }
  });

  // 4. Re-render again with same state (double-render race class)
  await step('team tab double render', async () => {
    window.eval("loadActiveTab(true)");
    await new Promise(r => setTimeout(r, 2500));
  });

  // 5. hashchange routing into #team
  await step('hash route to team', async () => {
    window.location.hash = 'team';
    window.dispatchEvent(new window.HashChangeEvent('hashchange'));
    await new Promise(r => setTimeout(r, 1500));
  });

  // 6. League change while on team tab
  await step('chooseLeague on team tab', async () => {
    const today = await realFetch('/api/today');
    const leagues = today.leagues || [];
    const other = leagues.find(l => !/Friday/i.test(l.name));
    if (other) {
      window.eval(`chooseLeague('${other.id}')`);
      await new Promise(r => setTimeout(r, 3000));
    }
  });

  // 7. selectTeam from a game card (deep-link path)
  await step('selectTeam deep link', async () => {
    window.eval("selectTeam('')");
    await new Promise(r => setTimeout(r, 1500));
  });

  for (const [name, res] of results) console.log(`${res === 'ok' ? 'PASS' : 'FAIL'}  ${name}${res === 'ok' ? '' : '  ->  ' + res}`);
  if (errors.length) {
    console.log('\nwindow errors:');
    errors.forEach(e => console.log('  ' + e.split('\n').slice(0, 6).join('\n  ')));
  } else {
    console.log('\nno window.onerror events');
  }
  const main = document.getElementById('main');
  console.log('\nfinal #main first 300 chars:', main ? main.innerHTML.slice(0, 300).replace(/\s+/g, ' ') : '(none)');
}

main().catch(e => { console.error('HARNESS ERROR:', e); process.exit(1); });

// appended: full-tab regression sweep
(async () => {
  const { JSDOM } = require('jsdom');
  const fs = require('fs');
  const indexHtml = fs.readFileSync(__dirname + '/index.html', 'utf8');
  const appJs = fs.readFileSync(__dirname + '/app.js', 'utf8');
  const dom = new JSDOM(indexHtml, { url: 'https://cahl.neural-forge.io/', runScripts: 'outside-only', pretendToBeVisual: true });
  const { window } = dom;
  window.requestAnimationFrame = (cb) => setTimeout(() => cb(window.performance.now()), 16);
  window.matchMedia = (q) => ({ matches: false, media: q, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} });
  window.fetch = async (p) => {
    const r = await fetch('https://cahl.neural-forge.io' + String(p), { cache: 'no-store' });
    let j = null; try { j = await r.json(); } catch (e) { j = { error: 'HTTP ' + r.status }; }
    return { ok: r.ok, status: r.status, json: async () => j };
  };
  const errors = [];
  window.addEventListener('error', (e) => errors.push(String(e.error && e.error.message || e.message)));
  window.eval(appJs);
  await new Promise(r => setTimeout(r, 400));
  for (const tab of ['today', 'league', 'team', 'players', 'analytics']) {
    window.eval(`setTab('${tab}')`);
    await new Promise(r => setTimeout(r, 3500));
    const main = window.document.getElementById('main');
    const hasError = /class="error"/.test(main.innerHTML);
    console.log(`${hasError ? 'ERR ' : 'OK  '} ${tab}: ${main.innerHTML.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 90)}`);
  }
  if (errors.length) console.log('window errors:', errors.join(' | '));
  process.exit(0);
})();
