// wheel_check — `EBX.Wheel` (landing variant, on a bare mount), in jsdom, against FIXTURES.
//
//   node scripts/wheel_check.js            # from the repo root; no server
//
// Written 2026-09-20 (build-seq §1). Rewritten for P2 · Home (2026-09-25):
// the two phase rows, the live top card, the time span; the bands left Home. `landing_check.js` drives the real page
// against a live API and is the fuller test; this one needs neither, so it can
// be run while the backend is down — which is when the layout usually breaks.
// It stubs `fetch` with seven causes, two missions, three initiatives and a
// slate, loads ebx_shared.js and ebx_wheel.js by hand (jsdom will not resolve
// the page's own <script src> from disk), mounts the wheel, and asserts the
// §1 spec: five panels, the a/b/c/d top card, the side card inside it, the
// rotating annulus with no marker/tips/labels, the two-line card head, my-vote
// highlighting, the Background rename, the mission-page links and the news
// band. It then clicks a card and all five steps to prove the repaint path.
// Requires `npm i jsdom` (dev only — nothing on the page uses it).
const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const R = f => path.join(ROOT, f);

const CAUSES = ['atmosphere','oceans','land','forests','wildlife','human-rights','human-progress']
  .map((id, i) => ({ id, index: i, name: id.replace(/-/g,' '), color: ['#e8a84c','#4aa3c7','#b08d57','#4e7a4e','#c77d9e','#8fce9d','#d98b5f'][i], emoji: '🌱' }));
const MISSIONS = [
  { id:'m1', cause_id:'atmosphere', cycle_num:0, winning_tiv_id:'t1', winning_org_id:'o1', started_at:'2026-06-01T12:00:00', status:'active', credit_value:1.2 },
  { id:'m2', cause_id:'oceans', cycle_num:1, winning_tiv_id:'t2', winning_org_id:null, started_at:'2026-07-20T12:00:00', status:'org_vote' },
];
const TIVS = [
  { id:'t1', cause_id:'atmosphere', mission_id:'m1', title:'Methane Leak Detection Grid', emoji:'🛰️', status:'won', ebx_committed: 120 },
  { id:'t2', cause_id:'oceans', mission_id:'m2', title:'Reef Nursery Expansion', emoji:'🪸', status:'org_vote', ebx_committed: 80 },
  { id:'t3', cause_id:'oceans', mission_id:'m2', title:'Trawler Buyback', emoji:'⚓', status:'suggested', ebx_committed: 40 },
];
const ORGS = [{ id:'o1', name:'Clean Air Trust' }, { id:'o2', name:'Blue Coast Fund' }];
const SLATE = { slots: CAUSES.map((c,i)=>({ slot:'s'+i, cause_id:c.id, weeks_out: 7+i, votable: i<3, confirmed: i===0, challenger_id: i===1?'land':null, streak: i===1?2:0, weeks_required:7 })) };
const ROUTES = {
  '/causes': CAUSES, '/missions': MISSIONS, '/initiatives': TIVS, '/organizations': ORGS,
  '/causes/slate': SLATE, '/candidacies': [{ mission_id:'m2', org_id:'o2' }],
  '/stats': { active_members: 4, committed_usd: 120, weekly_cost_usd: 4, runway_weeks: 30 },
  '/feed': [],
};
function route(u) {
  const p = String(u).replace(/^https?:\/\/[^/]+/, '').split('?')[0];
  if (ROUTES[p]) return ROUTES[p];
  if (/\/p2\/tally$/.test(p)) return { mission_id:'m2', pool_ebx: 120, total_ebx:120, entries:[{ org_id:'o2', net_votes: 9 }], voter_count: 3 };
  if (/^\/causes\/ballot\//.test(p)) return { entries: [{ cause_id:'atmosphere', votes: 3 }] };
  if (/\/claims$/.test(p)) return [];
  return null;
}
(async () => {
  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errors.push(String(e.message || e).slice(0, 300)));
  vc.on('error', (...a) => errors.push('console.error: ' + a.join(' ').slice(0, 300)));
  // 2026-09-30 (P2 · Home mods): no page mounts the landing variant any more —
  // Home's wheel became the five steps (ebx_steps.js) and the mission hub. This
  // check keeps the variant honest on a bare mount until it is deleted
  // (INSTRUCTIONS › REMOVAL REGISTER › Added 2026-09-30 §B).
  const html = '<!DOCTYPE html><html><head></head><body><div id="ebx-wheel"></div></body></html>';
  const dom = new JSDOM(html, {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    url: 'http://localhost/index.html',
    beforeParse(win) {
      win.fetch = async (u) => {
        const body = route(u);
        return { ok: body !== null, status: body === null ? 404 : 200, json: async () => body };
      };
      win.matchMedia = () => ({ matches: false, addListener(){}, removeListener(){} });
      win.requestAnimationFrame = () => 0;
      win.IntersectionObserver = class { observe(){} disconnect(){} };
    },
  });
  // the page's own <script src> tags don't resolve from disk in this harness
  const win = dom.window;
  for (const f of ['resources/js/ebx_shared.js', 'resources/js/ebx_wheel.js']) {
    win.eval(fs.readFileSync(R(f), 'utf8'));
  }
  win.eval("EBX.Wheel.mount('#ebx-wheel')");
  await new Promise(r => setTimeout(r, 900));
  const d = win.document, txt = s => { const e = d.querySelector(s); return e ? e.textContent.replace(/\s+/g,' ').trim() : ''; };
  let bad = 0, n = 0;
  const ok = (c, what, detail) => { n++; if (!c) bad++; console.log('  ' + (c?'ok  ':'FAIL') + '  ' + what + (detail?'  '+detail:'')); };

  console.log('\n=== runtime');
  const real = errors.filter(e => !/Not implemented|getContext|SVGElement|fonts\.googleapis|cloudflareinsights|Could not load/i.test(e));
  ok(!real.length, 'no script errors', real.join(' | '));

  // P2 · Home (2026-09-25): two rows of phases over a top card of live facts.
  console.log('\n=== the two phase rows + top card (P2)');
  ok(d.querySelectorAll('.lw-step').length === 5, 'five phase toggles ("What\'s new")');
  ok(d.querySelectorAll('.lw-phase').length === 5, 'five phase cards');
  const rows = [...d.querySelectorAll('.lw-row')];
  ok(rows.length === 2, 'two rows');
  ok(/Deciding the mission/.test(rows[0] && rows[0].textContent) && rows[0].querySelectorAll('.lw-phase').length === 3, 'row 1: deciding the mission — three elections');
  ok(/Planning, feedback and accountability/.test(rows[1] && rows[1].textContent) && rows[1].querySelectorAll('.lw-phase').length === 2, 'row 2: planning — framing and exchange');
  ['Cause Election', 'Initiative Election', 'Organization Election', 'Mission Framing', 'Exchange'].forEach((t, i) =>
    ok(txt('.lw-phase:nth-child(1)') !== null && [...d.querySelectorAll('.lw-phase__t')][i].textContent === t, 'phase ' + (i + 1) + ' is "' + t + '"'));
  ok(d.querySelectorAll('.lw-row .lw-arrow').length === 3, 'arrows run left to right between phases');
  ok([...d.querySelectorAll('.lw-phase__vote')].every(a => /^mission\.html\?state=/.test(a.getAttribute('href'))), 'every Vote link goes to the mission page');
  ok(d.querySelectorAll('.lw-phase.on').length === 1, 'exactly one phase is selected');
  ok(!!d.querySelector('#lw-topcard .lw-pointer'), 'the top card has a pointer to the selected phase');
  ok(!/Process|Reason/.test(txt('#lw-topcard')), 'the descriptions are gone from the top card');
  ok(/Initiative Election/.test(txt('.lw-top__kicker')), 'the top card names the selected phase', txt('.lw-top__kicker'));
  ok(d.querySelectorAll('.lw-live .lw-live__row').length >= 2, 'the live facts are painted (F5)');
  ok(!!d.querySelector('.lw-top__live .lw-card--active'), 'the side card is inside the top card (spec e)');
  ok(txt('#lw-span').length > 0, 'the time span under the annulus is painted', txt('#lw-span'));

  console.log('\n=== the annulus');
  ok(d.querySelectorAll('.lw-sector').length === 7, 'seven sectors');
  ok(!d.querySelector('.lw-now'), 'now marker removed');
  ok(!d.querySelector('.lw-ringlabel'), 'sector labels removed');
  ok(d.querySelectorAll('.lw-sector--on').length === 1, 'exactly one lit sector');
  const ring = d.querySelector('#lw-ringlayer').innerHTML;
  ok(/fill-opacity="0.05"|fill-opacity="0.14"/.test(ring), 'rays are drawn');

  console.log('\n=== the side cards');
  const cards = d.querySelectorAll('#lw-left .lw-card, #lw-right .lw-card');
  ok(cards.length === 6, 'six side cards', String(cards.length));
  ok(!!d.querySelector('.lw-card__name'), 'title is its own line above the dates');
  ok(!d.querySelector('.lw-card__title'), 'the old one-line head is gone');
  const colors = new Set([...cards].map(c => c.getAttribute('style')));
  ok(colors.size > 1, 'each card carries its own cause colour');

  // P2: the explainer bands moved to about.html (D7).
  console.log('\n=== the bands left Home');
  ok(!d.querySelector('.ld-band') && !/bring you the news/i.test(d.body.textContent), 'no explainer bands on Home');
  ok(fs.existsSync(R('about.html')) && /Vetting/.test(fs.readFileSync(R('about.html'), 'utf8')) &&
     /bring you the news/.test(fs.readFileSync(R('about.html'), 'utf8')), 'about.html carries them, with Vetting');

  // the top sector must be the focused one: its path must contain the top point
  console.log('\n=== geometry');
  // the lit sector must STRADDLE 12 o'clock: it starts left of centre, ends
  // right of centre, and both ends are in the top half.
  const on = d.querySelector('.lw-sector--on').getAttribute('d');
  const a = on.match(/M([\d.]+),([\d.]+) A[\d.]+,[\d.]+ 0 0,1 ([\d.]+),([\d.]+)/).slice(1).map(Number);
  ok(a[0] < 210 && a[2] > 210 && a[1] < 210 && a[3] < 210, 'the lit sector straddles the top', a.join(','));
  // and every other sector must be somewhere else
  const all = [...d.querySelectorAll('.lw-sector')].map(p => p.getAttribute('d').slice(0, 14));
  ok(new Set(all).size === 7, 'the seven sectors are at seven angles');

  console.log('\n=== interaction');
  const before = errors.length;
  const rightCard = d.querySelector('#lw-right .lw-card');
  const wantCause = rightCard.getAttribute('data-cause');
  rightCard.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  await new Promise(r => setTimeout(r, 50));
  ok(errors.length === before, 'focusing a side card does not throw', errors.slice(before).join(' | '));
  ok(d.querySelector('.lw-sector--on').getAttribute('data-cause') === wantCause,
     'the ring re-rotates to the newly focused cause');
  ok(d.querySelectorAll('#lw-left .lw-card, #lw-right .lw-card').length === 6, 'still six side cards');
  for (const k of ['cause', 'org', 'frame', 'ex', 'tiv']) {
    const b = d.querySelector('.lw-step[data-step="' + k + '"]');
    b.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
    await new Promise(r => setTimeout(r, 30));
  }
  ok(errors.length === before, 'every step paints without throwing', errors.slice(before).join(' | '));
  ok(!!d.querySelector('.lw-top__live .lw-card--active'), 'the active card survives a step change');
  d.querySelector('.lw-step[data-step="cause"]').dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  await new Promise(r => setTimeout(r, 30));
  ok(/\w{3} \d+ – \w{3} \d+/.test(txt('#lw-span')), 'the span reads a date range (cause decisions)', txt('#lw-span'));
  const fr = d.querySelector('.lw-phase[data-step="frame"]');
  fr.querySelector('.lw-phase__p').dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  await new Promise(r => setTimeout(r, 30));
  ok(fr.classList.contains('on') && /Mission Framing/.test(txt('.lw-top__kicker')), 'clicking a phase card selects it');

  console.log('\n' + (bad ? 'FAILED ' + bad + '/' + n : 'all ' + n + ' checks passed'));
  process.exit(bad ? 1 : 0);
})();
