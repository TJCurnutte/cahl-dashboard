
const { JSDOM } = require('jsdom');
const fs = require('fs');
const indexHtml = fs.readFileSync('qa/index.html', 'utf8');
const appJs = fs.readFileSync('qa/app.js', 'utf8');
const dom = new JSDOM(indexHtml, { url: 'https://cahl.neural-forge.io/', runScripts: 'outside-only', pretendToBeVisual: true });
const { window } = dom;
window.requestAnimationFrame = (cb) => setTimeout(() => cb(window.performance.now()), 16);
window.matchMedia = (q) => ({ matches: false, media: q, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} });
window.fetch = async (p) => {
  const r = await fetch('https://cahl.neural-forge.io' + String(p), { cache: 'no-store' });
  let j = null; try { j = await r.json(); } catch (e) { j = { error: 'HTTP ' + r.status }; }
  return { ok: r.ok, status: r.status, json: async () => j };
};
window.eval(appJs);
setTimeout(() => {
  const d = window.document;
  // enter the dashboard
  d.getElementById('gateEnterCta').click();
  setTimeout(() => {
    const gate = d.getElementById('landingGate');
    const gateHidden = !gate || gate.classList.contains('gate-hidden');
    console.log('gate dismissed after CTA:', gateHidden);
    // click the brand logo
    d.getElementById('brandHome').click();
    setTimeout(() => {
      const gate = d.getElementById('landingGate');
      const visible = gate && !gate.classList.contains('gate-hidden');
      const flagCleared = !window.sessionStorage.getItem('cahl-entered');
      console.log('landing visible after logo click:', visible);
      console.log('cahl-entered cleared:', flagCleared);
      process.exit(visible && flagCleared ? 0 : 1);
    }, 700);
  }, 700);
}, 400);
