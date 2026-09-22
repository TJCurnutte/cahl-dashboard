
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
setTimeout(async () => {
  window.eval("setTab('today')");
  setTimeout(() => {
    const main = window.document.getElementById('main');
    const hasStrip = main.innerHTML.includes('sponsor-strip');
    const hasGate = !!window.document.getElementById('landingGate');
    const gateVisible = hasGate && !window.document.getElementById('landingGate').classList.contains('gate-hidden');
    console.log('sponsor-strip on today:', hasStrip);
    console.log('landing gate present at boot:', hasGate, '| visible:', gateVisible);
    // click CTA
    const btn = window.document.getElementById('gateEnter');
    if (btn) btn.click();
    setTimeout(() => {
      const g = window.document.getElementById('landingGate');
      console.log('gate after CTA click:', g ? ('still present, class=' + g.className) : 'removed');
      console.log('sessionStorage flag:', window.sessionStorage.getItem('cahl-entered'));
      process.exit(0);
    }, 700);
  }, 3500);
}, 400);
