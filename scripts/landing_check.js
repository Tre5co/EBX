// landing_check — drives index.html in jsdom against a live API.
//
//   node scripts/landing_check.js [http://127.0.0.1:8000]
//
// Rewritten 2026-09-16 (build-seq §2 Landing) for the page as it now stands:
// the `jax notes 2.md` Landing drawing (rebuilt 2026-09-15) with the §2 edits —
// "How it Works" over the four steps, the dates week 0 · week 8 · week 15 ·
// week 15 on, the two halves below the steps, and the research band ABOVE the
// budget band, each heading over its own trio. The 2026-08-18 version asserted
// §1a–§1f blocks the 09-15 rebuild removed, and had been failing since.
const { JSDOM, VirtualConsole } = require('jsdom');

const BASE = process.argv[2] || 'http://127.0.0.1:8000';
let bad = 0, n = 0;
function ok(cond, what, detail) {
  n++; if (!cond) bad++;
  console.log('  ' + (cond ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : ''));
}

(async () => {
  const stats = await fetch(BASE + '/stats').then(r => r.json());
  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errors.push(String(e.message || e).slice(0, 200)));
  const dom = await JSDOM.fromURL(BASE + '/index.html', {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(win) {
      win.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
      win.matchMedia = win.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
    },
  });
  await new Promise(r => setTimeout(r, 3500));
  const d = dom.window.document;
  const txt = el => (el ? el.textContent.replace(/\s+/g, ' ').trim() : '');

  console.log('\n=== hero');
  const real = errors.filter(e => !/Not implemented|getContext|SVGElement|fonts\.googleapis|cloudflareinsights/i.test(e));
  ok(!real.length, 'no script errors', real.join(' | '));
  ok(/Earthbux News/.test(txt(d.querySelector('.ld-wordmark'))), 'wordmark');
  ok(txt(d.querySelector('.ld-sub')) === 'you donate, we follow', 'tagline');
  ok(d.querySelectorAll('#ld-cta .ld-cta__btn').length === 2, 'two calls to action');

  console.log('\n=== How it Works — the four steps');
  const how = d.querySelector('.ld-how');
  ok(txt(how) === 'How it Works', '"How it Works" heads the steps');
  const steps = [...d.querySelectorAll('.ld-steps .ld-step')];
  ok(steps.length === 4, 'four steps', 'got ' + steps.length);
  const want = [
    ['01 · Week 0', 'You elect the initiative', /funding what you want the mission to be/i, 'main.html'],
    ['02 · Week 8', 'You elect who runs it', /After the mission is decided, your tokens can be put towards its philanthropy/i, 'main.html?state=oe'],
    ['03 · Week 15', 'Receive your Earthbucks', /orients the organization and its benefactors \(you\)/i, 'mission.html'],
    ['04 · Week 15 on', 'Follow along and trade', /Hold on, or exchange for a different mission/i, 'cause.html'],
  ];
  want.forEach(([nTxt, title, what, href], i) => {
    const s = steps[i]; if (!s) return;
    ok(txt(s.querySelector('.ld-step__n')) === nTxt, 'step ' + (i + 1) + ' is dated ' + nTxt, txt(s.querySelector('.ld-step__n')));
    ok(txt(s.querySelector('.ld-step__title')) === title, '…titled "' + title + '"');
    ok(what.test(txt(s.querySelector('.ld-step__what'))), '…with the new wording');
    ok(s.getAttribute('href') === href, '…and links to ' + href, s.getAttribute('href'));
  });

  console.log('\n=== the two halves sit BELOW the steps, smaller');
  const heads = d.querySelector('.ld-heads');
  const stepsList = d.querySelector('.ld-steps');
  ok(heads && stepsList && (stepsList.compareDocumentPosition(heads) & dom.window.Node.DOCUMENT_POSITION_FOLLOWING),
     'Maximizing Donor Control / Publicizing Charitable Impact follow the steps');
  ok(/Maximizing Donor Control/.test(txt(heads)) && /Publicizing Charitable Impact/.test(txt(heads)), '…both named');

  console.log('\n=== research band first, budget band second');
  const bands = [...d.querySelectorAll('.ld-band')];
  ok(bands.length === 2, 'two bands');
  ok(/Research the mission to win Rewards/.test(txt(bands[0] && bands[0].querySelector('.ld-band__h'))), 'band 1 heading');
  ok(txt(bands[0]).includes('Situation') && txt(bands[0]).includes('Investigation') && txt(bands[0]).includes('Analysis'),
     '…over Situation · Investigation · Analysis');
  ok(/A public forum budgets the missions/.test(txt(bands[1] && bands[1].querySelector('.ld-band__h'))), 'band 2 heading');
  ok(txt(bands[1]).includes('Service') && txt(bands[1]).includes('Supply') && txt(bands[1]).includes('Support'),
     '…over Service · Supply · Support');
  ok(bands[1] && bands[1].querySelector('a[href="cause.html"]'), '"public forum" still links to the feed');

  console.log('\n=== the grant and the runway');
  ok(d.querySelectorAll('#ld-dime-viz svg').length === 10, 'ten dimes');
  ok(Number(txt(d.querySelector('.ld-runway__weeks'))) === stats.runway_weeks, 'runway weeks match /stats');
  ok(Number(txt(d.querySelector('#ld-active-users b'))) === stats.active_members, 'active members match /stats');

  console.log('\n=== analytics (build-seq §1)');
  const beacon = d.querySelector('script[src*="static.cloudflareinsights.com/beacon.min.js"]');
  ok(!!beacon, 'the Cloudflare Web Analytics beacon is on the page');
  ok(beacon && /7e5bc527fed34f5c8b6f10611c680086/.test(beacon.getAttribute('data-cf-beacon') || ''), '…with the site token');

  dom.window.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'LANDING CLEAN'));
  process.exit(bad ? 1 : 0);
})();
