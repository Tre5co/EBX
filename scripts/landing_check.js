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
//
// 10/9 Reshuffle (2026-10-09): the steps stand LEFT of the visual, step 5 reads
// "Feedback"; the mission hub went to Missions and the feed to News; Home
// carries THE WEEKLY REPORT (GET /inbox/weekly/report) at all times.
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
  const { d, errors } = await page('index.html');

  console.log('\n=== Home · hero');
  ok(!errors.length, 'no script errors', errors.join(' | '));
  ok(/Earthbux News/.test(txt(d.querySelector('.ld-wordmark'))), 'wordmark');
  ok(txt(d.querySelector('.ld-sub')) === 'you donate, we follow', 'tagline (D18)');
  ok(!/Decide what gets funded|My profile/.test(d.getElementById('ld-cta').textContent), 'the hero carries no Decide / My profile links (tweaks 2026-10-01)');

  console.log('\n=== Home · the five steps (2026-09-30)');
  ok(d.querySelector('.hx .ld-a') && d.querySelector('.hx #ebx-steps') && d.querySelectorAll('#ld-flow .ld-flow__i').length === 5, 'the hero, with the steps and their list');
  const flow = d.getElementById('ld-flow'), vis = d.getElementById('ebx-steps');
  ok(flow && vis && flow.parentNode === vis.parentNode && !!(flow.compareDocumentPosition(vis) & d.defaultView.Node.DOCUMENT_POSITION_FOLLOWING),
     'the list stands LEFT of the visual (10/9 Reshuffle)');
  ok(txt(d.querySelectorAll('#ld-flow .ld-flow__i')[4]) === '5. Feedback', 'step 5 is Feedback, not Reporting', txt(d.querySelectorAll('#ld-flow .ld-flow__i')[4]));
  ok(d.querySelectorAll('#hk .hk__card').length === 4, 'the four doors');
  const hk = txt(d.getElementById('hk'));
  ok(/Two key decisions/.test(hk) && /We give everyone \$1 to vote with in every initiative election/.test(hk) && /Every voice matters/.test(hk)
     && /Feedback and accountability/.test(hk) && /week by week/.test(hk) && /move your donation to a different mission/.test(hk),
     'Jax\'s door copy of 2026-10-09, with the three edits');
  ok(d.querySelectorAll('#ebx-steps .sx__scene').length === 5, 'five pages');
  ok(txt(d.querySelector('#ebx-steps .sx__msg')) === 'A fresh focus each week', 'page 1 is Cause');
  ok(!d.getElementById('ebx-wheel') && !d.querySelector('.lw-phase, .lw-card'), 'the wheel block is off Home');

  console.log('\n=== Home · the weekly report (10/9 Reshuffle)');
  const rep = await fetch(BASE + '/inbox/weekly/report').then(r => r.json());
  ok(!d.getElementById('mh') && !d.getElementById('hf-list') && !d.querySelector('.hn'),
     'the mission hub went to Missions, the feed to News — no discussion on Home');
  ok(txt(d.getElementById('wr-title')) === rep.title && /^[A-Z][a-z]+ \d+ – (?:[A-Z][a-z]+ )?\d+: \S/.test(rep.title),
     'headed with the week and its cause', rep.title);
  ok(d.querySelectorAll('#wr-above .wu').length === 3 && d.querySelectorAll('#wr-below .wu').length === 3,
     'three updates above the timeline, three below', d.querySelectorAll('#wr-above .wu').length + ' + ' + d.querySelectorAll('#wr-below .wu').length);
  ok((rep.above || []).length === 3 && (rep.below || []).length === 3 && (rep.timeline.dots || []).length >= 1,
     '…as the endpoint has them, with the missions on the timeline', (rep.timeline.dots || []).length + ' dots');
  ok(d.querySelectorAll('#wr-tl .tl__dot, #wr-tl [data-dot]').length >= 1 || /circle/.test(d.getElementById('wr-tl').innerHTML),
     'the timeline draws its dots');
  ok(txt(d.getElementById('wr-ce')).length > 10 && txt(d.getElementById('wr-ex')).length > 10, 'at the bottom: the cause elections and the exchange');

  console.log('\n=== about.html (the About reshape, 2026-10-05)');
  const a = await page('about.html');
  ok(!a.errors.length, 'no script errors', a.errors.join(' | '));
  const ad = a.d, AW = ad.defaultView;
  ok(!ad.querySelector('.ld-wordmark') && !ad.querySelector('.ebx-nav'), 'no hero, no site nav');
  const tabs = [...ad.querySelectorAll('.ab-tab')].map(txt);
  ok(tabs.join(' | ') === '← Earthbux Home | Our story | Our goals | How it works | Our team', 'its own tabs', tabs.join(' | '));
  ok(/index\.html$/.test(ad.querySelector('.ab-tab--home').getAttribute('href')), '← Home goes home');
  const on = () => (ad.querySelector('.ab-panel.is-on') || {}).id;
  ok(on() === 'story', 'opens on Our story');
  for (const [hash, tab] of [['story', 'story'], ['goals', 'goals'], ['how', 'how'], ['team', 'team'],
       ['why', 'story'], ['grant', 'goals'], ['what', 'how'], ['earthbuck', 'how'], ['posting', 'how'], ['ab-phases', 'how']]) {
    AW.AboutTabs.show(hash);
    ok(on() === tab && txt(ad.getElementById(tab)).length > 200, '#' + hash + ' lands on ' + tab);
  }
  const at = txt(ad.body);
  ok(/Nobody follows the money/.test(at) && /What if giving were an election/.test(at) && /Attention moved to the feed/.test(at) && /save it/.test(at), 'Our story: the gap, the idea, the moment, the verse');
  ok(/Give donors control/.test(at) && /Hold charities accountable/.test(at) && /more optimistic/.test(at), 'Our goals: the three');
  ok(/\d+\s*weeks? of grants/.test(txt(ad.getElementById('ld-runway'))), 'the runway paints from /stats');
  ok(ad.querySelectorAll('#ab-phases .ab-phase').length === 5 && ad.querySelectorAll('#ab-phases .ab-net').length === 5, 'five phases, each with its network');
  const C = AW.EBX && AW.EBX.Wheel && AW.EBX.Wheel.COPY;
  const norm = h => { const t = ad.createElement('div'); t.innerHTML = h; return t.innerHTML; };
  ok(C && ['cause', 'tiv', 'org', 'frame', 'ex'].every(k => ['kicker', 'title', 'what', 'why'].every(f =>
       ad.querySelector('.ab-phase[data-phase="' + k + '"] [data-copy="' + f + '"]').innerHTML === norm(C[k][f]))),
     'the phase copy is the string Home reads (EBX.Wheel.COPY)');
  ok(/Investigation/.test(at) && /Service/.test(at) && /Analysis/.test(at), 'research and budgeting sit in their phases');
  ok(ad.querySelectorAll('#compare tbody tr').length >= 5 && ad.querySelector('#compare tr.is-us'), 'how we compare');
  ok(ad.querySelector('#team [data-ebx-contact="join"]') && ad.querySelector('#team [data-ebx-contact]:not([data-ebx-contact="join"])'), 'Our team: Join us + Contact us');

  console.log('\n' + (bad ? 'FAILED ' + bad + '/' + n : 'all ' + n + ' checks passed'));
  process.exit(bad ? 1 : 0);
})();
