// Reproduce the user's exact Team-tab state: Swamp Donkeys + Monday D - West A,
// as restored from localStorage by a real visitor, then drive every interaction
// the Team tab offers and report any error with its real stack.
const { JSDOM } = require('jsdom');
const fs = require('fs');

const TEAM_ID = '6CD1F6FF76593E86C947DFD96D8BB549A6A078CFEE2DB2F51CC33813514850CBDB97A46B7DBA2D14065018887FD3AE604D66A29910BE8ED42E310B9DC63D6E05';
const LEAGUE_ID = 'CE2379A893C6FA3D47A5259689FF69C65506D5D56FAC94C855726C1A61EC240DF5202489C6EDA1B645A5200654CBC684D952A90E576926D13CBB469E6B4CF049';

async function main() {
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
  window.addEventListener('error', (e) => errors.push((e.error && e.error.stack) || e.message));
  // capture unhandled rejections too
  window.addEventListener('unhandledrejection', (e) => errors.push('UNHANDLED: ' + String(e.reason && e.reason.stack || e.reason)));

  window.localStorage.setItem('cahl-league', LEAGUE_ID);
  window.localStorage.setItem('cahl-team', TEAM_ID);
  window.eval(appJs);
  await new Promise(r => setTimeout(r, 300));

  const step = async (name, ms, fn) => {
    try {
      if (fn) fn();
      await new Promise(r => setTimeout(r, ms));
      const main = window.document.getElementById('main');
      const content = window.document.getElementById('teamContent');
      const txt = ((content && content.textContent) || main.textContent || '').replace(/\s+/g, ' ').trim();
      console.log(`[${errors.length ? 'ERR ' : 'ok  '}] ${name} -> ${txt.slice(0, 110)}`);
    } catch (e) {
      console.log(`[THRW] ${name} -> ${String(e.stack || e).split('\n').slice(0, 3).join(' | ')}`);
    }
  };

  await step('boot+team tab (saved state)', 4500, () => window.eval("setTab('team')"));
  await step('refresh team tab', 4500, () => window.eval("loadActiveTab(true)"));
  await step('teamSelect change to another team', 4500, () => {
    const sel = window.document.getElementById('teamSelect');
    if (sel && sel.options.length > 2) { sel.value = sel.options[1].value; sel.dispatchEvent(new window.Event('change')); }
  });
  await step('choose league again', 4500, () => window.eval(`chooseLeague('${LEAGUE_ID}')`));
  await step('selectTeam deep link', 3000, () => window.eval(`selectTeam('${TEAM_ID}')`));

  console.log('\n--- errors captured:', errors.length);
  errors.slice(0, 3).forEach((e, i) => console.log(`\n[${i + 1}]\n${String(e).split('\n').slice(0, 12).join('\n')}`));
  process.exit(0);
}
main().catch(e => { console.error('HARNESS:', e); process.exit(1); });
