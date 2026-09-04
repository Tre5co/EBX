// landing_check — drives index.html (structure.md §1a–§1e) in jsdom against the
// live API and asserts the things render_check cannot: that the toggles TOGGLE,
// that the runway arithmetic on the page is the arithmetic /stats returned, and
// that nothing §1f took off the page has crept back on.
//
//   node scripts/landing_check.js [http://127.0.0.1:8000]
const { JSDOM, VirtualConsole } = require('jsdom');

const BASE = process.argv[2] || 'http://127.0.0.1:8000';
let bad = 0, n = 0;

function ok(cond, what, detail) {
  n++;
  if (!cond) bad++;
  console.log('  ' + (cond ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : ''));
}

(async () => {
  const stats = await fetch(BASE + '/stats').then(r => r.json());
  console.log('=== GET /stats\n  ' + JSON.stringify(stats));

  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errors.push(String(e.message || e).slice(0, 200)));
  vc.on('error', (...a) => errors.push('console.error: ' + a.join(' ').slice(0, 180)));
  const dom = await JSDOM.fromURL(BASE + '/index.html', {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse(win) {
      win.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
      win.matchMedia = win.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
    },
  });
  await new Promise(r => setTimeout(r, 4000));
  const d = dom.window.document;
  const txt = el => (el ? el.textContent.replace(/\s+/g, ' ').trim() : '');

  console.log('\n=== §1a–§1b');
  const real = errors.filter(e => !/Not implemented|getContext|SVGElement|fonts\.googleapis/i.test(e));
  ok(!real.length, 'no script errors', real.join(' | '));
  ok(d.querySelectorAll('.ld-lede span').length === 2, 'the two lede lines');
  ok(/Earthbux News/.test(txt(d.querySelector('.ld-wordmark'))), 'wordmark');
  ok(txt(d.querySelector('.ld-sub')) === 'you donate, we follow', 'tagline');
  ok(d.querySelectorAll('#ld-cta .ld-cta__btn').length === 2, 'log in + vote now');
  ok(/publicity to charity/i.test(txt(d.querySelector('.ld-couplet'))), '§1b couplet, in §1b');

  console.log('\n=== §1c — the two elections');
  const rows = [...d.querySelectorAll('.ld-elect__row')];
  ok(rows.length === 2, 'exactly 2 elections', 'got ' + rows.length);
  ok(/Mission Election/.test(txt(rows[0])) && /Week 0/.test(txt(rows[0])), 'ME · week 0');
  ok(/Organization Election/.test(txt(rows[1])) && /Week 7/.test(txt(rows[1])), 'OE · week 7');
  ok(rows[0].querySelector('a').getAttribute('href') === 'main.html', 'ME links the ME');
  ok(rows[1].querySelector('a').getAttribute('href') === 'main.html?state=oe', 'OE links the OE');
  ok(d.querySelectorAll('#ld-dime-viz svg').length === 10, 'ten dimes');

  console.log('\n=== §1c — the runway is /stats, not a guess');
  const weeks = Number(txt(d.querySelector('.ld-runway__weeks')));
  const active = Number(txt(d.querySelector('#ld-active-users b')));
  const note = txt(d.querySelector('.ld-runway__note'));
  ok(weeks === stats.runway_weeks, 'weeks match /stats', weeks + ' vs ' + stats.runway_weeks);
  ok(active === stats.active_members, '#Activeusers displayed', active + ' vs ' + stats.active_members);
  ok(note.includes('$' + stats.committed_usd.toFixed(2)), 'committed $ in the divisor line');
  ok(note.includes('$' + stats.weekly_cost_usd.toFixed(2)), 'weekly cost in the divisor line');
  // §3 (2026-08-28): the grant is TOKENS. It was written as EBX before EBX
  // became a state rather than a unit — a granted token has not been minted
  // and may never be, so it cannot be EBX.
  ok(/10 tokens per week/.test(note), 'the grant sentence §1c asks for');
  const lit = d.querySelectorAll('.ld-runway__bar.on').length;
  ok(lit === Math.min(12, stats.runway_weeks), 'bars lit = weeks (cap 12)', String(lit));

  console.log('\n=== §1d — three categories, and the toggles toggle');
  const cats = [...d.querySelectorAll('#ld-forum .ld-forum__cat')];
  ok(cats.length === 3, '3 categories', 'got ' + cats.length);
  ok(/Reviews/.test(txt(cats[0])) && !cats[0].querySelector('.ld-tt'), 'Reviews — no toggle');
  for (const [i, want] of [[1, ['Context', 'Investigation', 'Analysis']],
                           [2, ['Service', 'Supply', 'Support']]]) {
    const names = [...cats[i].querySelectorAll('.ld-tt__btn')].map(b => txt(b));
    ok(JSON.stringify(names) === JSON.stringify(want), txt(cats[i].querySelector('.ld-forum__name')) +
       ' types', names.join(' · '));
  }
  ok(!/Evaluation/.test(txt(cats[1])), 'research does NOT name Evaluation (it is a review type)');

  for (const i of [1, 2]) {
    const cat = () => [...d.querySelectorAll('#ld-forum .ld-forum__cat')][i];
    const before = txt(cat().querySelector('.ld-tt__what'));
    const label = txt([...cat().querySelectorAll('.ld-tt__btn')][2]);
    [...cat().querySelectorAll('.ld-tt__btn')][2].dispatchEvent(
      new dom.window.MouseEvent('click', { bubbles: true }));
    const after = txt(cat().querySelector('.ld-tt__what'));
    const on = txt(cat().querySelector('.ld-tt__btn.on'));
    ok(after !== before && after.length > 20, 'clicking ' + label + ' swaps the description');
    ok(on === label, 'and marks ' + label + ' selected', 'on=' + on);
  }
  // the other category must not have moved
  const stillOn = [...d.querySelectorAll('#ld-forum .ld-tt__btn.on')].map(b => txt(b));
  ok(stillOn.length === 2, 'one selected type per toggling category', stillOn.join(' · '));

  console.log('\n=== §1e — the cost scale');
  const steps = [...d.querySelectorAll('.ld-step')];
  ok(steps.length === 5, '5 steps', 'got ' + steps.length);
  ok(steps.map(s => txt(s.querySelector('.ld-step__name'))).join(' ') ===
     'Dormant Watching Reporting Auditing Arbitrating', 'named lowest→highest cost');
  ok(txt(steps[0]).includes('1/16') && txt(steps[4]).includes('5/16'), 'Dormant 1/16 … Arbitrating 5/16');
  ok(txt(d.querySelector('.ld-scale__split')).includes('1/16'), 'split bar starts at 1/16');
  steps[4].dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  ok(txt(d.querySelector('.ld-scale__split')).includes('5/16'), 'clicking Arbitrating moves the split');
  ok(txt(d.querySelector('.ld-scale__split')).includes('11/16'), 'and the mission keeps 11/16');
  // §1c's runway must NOT follow the scale any more
  ok(Number(txt(d.querySelector('.ld-runway__weeks'))) === stats.runway_weeks,
     'runway is unchanged by the scale (they are decoupled)');

  console.log('\n=== §1f — off the page');
  for (const sel of ['.ld-sys__row', '.ld-fine__item', '#cause-change', '#ld-causes', '.ld-key'])
    ok(!d.querySelector(sel), sel + ' is gone');
  const body = txt(d.body);
  for (const phrase of ['fine print', 'credit coin', 'slated to last'])
    ok(!new RegExp(phrase, 'i').test(body), '"' + phrase + '" is not on the page');

  dom.window.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'LANDING CLEAN'));
  process.exit(bad ? 1 : 0);
})();
