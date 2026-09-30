// landing_check — drives index.html (Home) and about.html in jsdom against a
// LIVE API.
//
//   node scripts/landing_check.js [http://127.0.0.1:8000]
//
// Rewritten for P2 · Home (2026-09-25) — F3: the 2026-09-16 version asserted
// the four dated steps and the explainer bands, which have been gone since
// 2026-09-18 and 2026-09-25. `wheel_check.js` and `home_check.js` pin the same
// page against fixtures; this one proves it paints from real data: the hero
// (unchanged, D18 "You donate. We follow."), the five steps and the mission
// hub (2026-09-30), THE NETWORK and a feed whose size is the API's, and the
// explainer standing on about.html.
const { JSDOM, VirtualConsole } = require('jsdom');

const BASE = process.argv[2] || 'http://127.0.0.1:8000';
let bad = 0, n = 0;
function ok(cond, what, detail) {
  n++; if (!cond) bad++;
  console.log('  ' + (cond ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : ''));
}
async function page(file) {
  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errors.push(String(e.message || e).slice(0, 200)));
  const dom = await JSDOM.fromURL(BASE + '/' + file, {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(win) {
      win.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
      win.matchMedia = win.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
      win.requestAnimationFrame = () => 0;
      win.IntersectionObserver = class { observe() {} disconnect() {} };
    },
  });
  await new Promise(r => setTimeout(r, 4000));
  return { d: dom.window.document, errors: errors.filter(e => !/Not implemented|getContext|SVGElement|fonts\.googleapis|cloudflareinsights/i.test(e)) };
}
const txt = el => (el ? el.textContent.replace(/\s+/g, ' ').trim() : '');

(async () => {
  const roots = await fetch(BASE + '/posts?roots_only=true&limit=120&sort=recent').then(r => r.json());
  const { d, errors } = await page('index.html');

  console.log('\n=== Home · hero');
  ok(!errors.length, 'no script errors', errors.join(' | '));
  ok(/Earthbux News/.test(txt(d.querySelector('.ld-wordmark'))), 'wordmark');
  ok(txt(d.querySelector('.ld-sub')) === 'you donate, we follow', 'tagline (D18)');
  ok(d.querySelectorAll('#ld-cta .ld-cta__btn').length === 2, 'two calls to action');

  console.log('\n=== Home · the five steps (2026-09-30)');
  ok(d.querySelector('.hx .ld-a') && d.querySelector('.hx #ebx-steps'), 'the hero, with the steps to its right');
  ok(d.querySelectorAll('#ebx-steps .sx__scene').length === 5, 'five pages');
  ok(txt(d.querySelector('#ebx-steps .sx__msg')) === 'A fresh focus each week', 'page 1 is Cause');
  ok(!d.getElementById('ebx-wheel') && !d.querySelector('.lw-phase, .lw-card'), 'the wheel block is off Home');

  console.log('\n=== Home · the mission hub');
  const missions = await fetch(BASE + '/missions').then(r => r.json());
  ok(d.querySelectorAll('#mh .mh__rowhead').length === 7, 'seven rows');
  const hub = d.defaultView.HomeHub;
  const cells = hub ? hub.state.rows.reduce((a, r) => a + r.cells.length, 0) : 0;
  ok(cells === missions.length + 7, 'every mission, plus a cause election a row', cells + ' = ' + missions.length + ' + 7');
  ok(d.querySelectorAll('#mh .mc--ce').length === 7, 'a cause election on every row');

  console.log('\n=== Home · the Network + the feed');
  ok(d.querySelectorAll('#hn-row a.hn__tile').length === 3, 'the Network row, as links into News');
  const shown = d.querySelectorAll('#hf-list .hp').length;
  ok(shown === Math.min(12, roots.length), 'the feed is every post, newest first', shown + ' of ' + roots.length);
  ok(!d.querySelector('.hn .hf-chip, .hn form, .hn [aria-pressed]'), 'no toggles on Home');

  console.log('\n=== about.html');
  const a = await page('about.html');
  ok(!a.errors.length, 'no script errors', a.errors.join(' | '));
  const at = txt(a.d.body);
  const order = ['social network for charities', 'A dollar a week', 'How it Works', 'What an Earthbuck is',
                 'Research the mission', 'bring you the news', 'public forum', 'save it'].map(s => at.indexOf(s));
  ok(order.every(i => i >= 0) && order.every((v, i) => !i || v > order[i - 1]), 'the copy spine, in order', order.join(','));
  ok(/Investigation/.test(at) && !/>Organization</.test(a.d.body.innerHTML), 'research reads Background · Investigation · Analysis (P3)');
  ok(/\d+\s*weeks? of grants/.test(txt(a.d.getElementById('ld-runway'))), 'the runway paints from /stats');
  ok(a.d.querySelectorAll('#ab-phases li').length === 5, 'the five phases');

  console.log('\n' + (bad ? 'FAILED ' + bad + '/' + n : 'all ' + n + ' checks passed'));
  process.exit(bad ? 1 : 0);
})();
