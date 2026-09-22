
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
  const checks = {
    'landing present': !!d.getElementById('landingGate'),
    'nav links (About/Features/Sponsor)': d.querySelectorAll('.lp-links a').length === 3,
    'hero CTA': !!d.getElementById('gateEnterCta'),
    'footer CTA': !!d.getElementById('gateEnterFoot'),
    'feature cards x4': d.querySelectorAll('.lp-feature').length === 4,
    'about section': !!d.getElementById('lp-about'),
    'sponsor card + lockup img': !!d.querySelector('.lp-sponsor-card img[src*="upright-lockup"]'),
    'sponsor link noopener': (d.querySelector('.lp-sponsor-card') || {}).target === '_blank',
    'footer fine print + chillerstats link': !!d.querySelector('.lp-fine a[href*="chillerstats"]'),
    'no emoji icons': !d.body.innerHTML.match(/[\u{1F3C5}\u{1F4CA}\u{2B50}\u{1F4CD}]/u),
  };
  let ok = true;
  for (const [k, v] of Object.entries(checks)) { console.log((v ? 'PASS' : 'FAIL'), k); if (!v) ok = false; }
  // click hero CTA -> gate dismisses
  d.getElementById('gateEnterCta').click();
  setTimeout(() => {
    const gone = !d.getElementById('landingGate') || d.getElementById('landingGate').classList.contains('gate-hidden');
    console.log(gone ? 'PASS' : 'FAIL', 'hero CTA dismisses gate');
    console.log('sessionStorage:', window.sessionStorage.getItem('cahl-entered'));
    process.exit(ok && gone ? 0 : 1);
  }, 700);
}, 400);
