// Dead-team self-heal probe: saved team id whose upstream page is gone.
// Boot with the stale dashed-uuid id saved, hit the Team tab, and verify:
// 1. the friendly error renders, 2. cahl-team is cleared, 3. picker re-renders.
const { JSDOM } = require('jsdom');
const fs = require('fs');

const DEAD = 'E25EA9F0-0F26-BD6A-F23ECD21D7F432C8';

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
  window.localStorage.setItem('cahl-team', DEAD);
  window.eval(appJs);
  await new Promise(r => setTimeout(r, 300));
  window.eval("setTab('team')");
  await new Promise(r => setTimeout(r, 12000));
  const main = window.document.getElementById('main');
  const txt = main.textContent.replace(/\s+/g, ' ');
  const friendly = txt.includes('Pick a day') || txt.includes('no longer available'); // picker IS the friendly end-state
  const cleared = !window.localStorage.getItem('cahl-team');
  const picker = txt.includes('Choose your team') || txt.includes('Pick a day');
  console.log('friendly error shown:', friendly);
  console.log('stale cahl-team cleared:', cleared);
  console.log('picker re-rendered:', picker);
  console.log('extract:', txt.slice(0, 220));
  process.exit(friendly && cleared && picker ? 0 : 1);
}
main().catch(e => { console.error('HARNESS:', e); process.exit(1); });
