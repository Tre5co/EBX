// home_check — Home (index.html), in jsdom, against FIXTURES (no server).
//
//   node scripts/home_check.js            # from the repo root; needs `npm i jsdom`
//
// Rewritten 2026-09-30 for P2 · Home mods; reshaped 2026-10-09 for the 10/9
// Reshuffle. Pins, top to bottom:
//   · THE HERO, left-aligned, with THE FIVE STEPS beside it (ebx_steps.js):
//     five pages Cause → Initiative → Organization → Network → Feedback, one
//     message each and no other text, arrows both ways, a dot per step, and
//     every scene drawable at any second without throwing — the stacked list
//     standing LEFT of the visual;
//   · THE FOUR DOORS in Jax's copy of 2026-10-09;
//   · THE WEEKLY REPORT (GET /inbox/weekly/report): three updates above the
//     timeline, three below, each card hanging from its dot; the cause
//     elections and the exchange at the foot — and no hub, no feed on Home;
//   · THE MISSION HUB, now EBX.Hub (resources/js/ebx_hub.js, on Missions and,
//     reading your own choices, on Profile) — mounted here on a bare element
//     against the same fixtures: seven rows, the cause election first, then
//     the missions newest first; each mission's stage read from its dates;
//     this week's decisions glow; ‹ › « » and collapse;
//   · the phase blurbs now standing in the mission page's ballot panels.
const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const R = f => path.join(ROOT, f);

const now = Date.now(), day = 864e5, WK = 7 * day, iso = t => new Date(t).toISOString();
// the mission clock's weekly boundary (ebx_shared.js cycleStart)
const CS = new Date('2026-04-28T12:00:00').getTime();
const weekEnd = CS + (Math.floor((now - CS) / WK) + 1) * WK;
const CAUSES = ['atmosphere', 'oceans', 'land', 'forests', 'wildlife', 'human-rights', 'human-progress']
  .map((id, i) => ({ id, index: i, name: id.replace(/-/g, ' '), color: '#4aa3c7', emoji: '🌱' }));
// started_at = T − 7 weeks (EBX.Cycle.missionDates)
const M = (id, cause, n, T, tiv, org) => ({ id, cause_id: cause, cycle_num: n, started_at: iso(T - 7 * WK),
  winning_tiv_id: tiv || null, winning_org_id: org || null, current_phase: 'initiative', credit_value: 1.25 });
const MISSIONS = [
  M('oce4', 'oceans', 4, now + 5 * WK),                 // initiative election
  M('oce3', 'oceans', 3, now - 1 * WK),                 // closed with no initiative
  M('oce2', 'oceans', 2, now - 2 * WK - day, 't2'),     // organization election, week 2
  M('oce1', 'oceans', 1, now - 10 * WK - day, 't1', 'o1'), // framing, week 10
  M('oce0', 'oceans', 0, now - 20 * WK - day, 't0', 'o1'), // exchange, week 20
  M('lan2', 'land', 2, weekEnd),                         // initiative election closing this week → glows
];
const TIVS = [
  { id: 't0', cause_id: 'oceans', mission_id: 'oce0', title: 'Garbage Patch Analysis', ebx_committed: 90 },
  { id: 't1', cause_id: 'oceans', mission_id: 'oce1', title: 'Coastal Water Monitoring', ebx_committed: 70 },
  { id: 't2', cause_id: 'oceans', mission_id: 'oce2', title: 'Deep Sea Protection Zones', ebx_committed: 60 },
  { id: 't4a', cause_id: 'oceans', mission_id: 'oce4', title: 'Coral Restoration Alliance', ebx_committed: 30 },
  { id: 't4b', cause_id: 'oceans', mission_id: 'oce4', title: 'Kelp Forest Recovery', ebx_committed: 10 },
];
const ORGS = [{ id: 'o1', name: 'Blue Coast Fund' }, { id: 'o2', name: 'Reef Keepers' }];
const SLATE = { first_open_slot: 7, slots: CAUSES.map((c, i) => ({ slot: 7 + ((i - 1 + 7) % 7), weeks_out: 7 + ((i - 1 + 7) % 7),
  incumbent_id: c.id, challenger_id: c.id === 'land' ? 'forests' : null, streak: c.id === 'land' ? 2 : 0, weeks_required: 6, votable: true })) };
const P = (id, category, type, cause, extra) => Object.assign({ id, category, type, cause_id: cause, mission_id: null,
  title: id, body: 'body of ' + id, author_type: 'ben', ben_author_id: 2, helpful_count: 1, harmful_count: 0,
  created_at: iso(now - day) }, extra || {});
const POSTS = [
  P('n1', 'editorial', null, 'oceans', { author_type: 'earthbux', ben_author_id: null }),
  P('r1', 'mission_support', 'context', 'oceans'),
  P('r2', 'mission_support', 'investigation', 'land', { body: 'see https://www.example.org/report for the audit' }),
  P('r3', 'mission_support', 'analysis', 'land', { created_at: iso(now - 20 * day) }),
  P('b1', 'budgeting', 'service', 'atmosphere', { est_cost_usd: 160, ben_author_id: 7 }),
  P('v1', 'review', 'case', 'forests'),
];
// THE WEEKLY REPORT, as backend/app/report.py shapes it (10/9 Reshuffle)
const CX = id => { const c = CAUSES.find(x => x.id === id); return { id: c.id, name: c.name, color: c.color, index: c.index }; };
const U = (role, side, cause, age, id, n, extra) => Object.assign({ role, side, cause: CX(cause), age, missing: false, mission_id: id,
  label: cause + ' ' + n, number: n, kicker: role.replace(/_/g, ' '), title: 'Mission ' + id, line: 'line of ' + id,
  leaders: [], leaders_kind: null, org: null, stats: { members: 2, committed_ct: 2500, budget_items: 1, initiatives: 3 } }, extra || {});
const REPORT = { week: 23, title: 'October 6 – 13: Land', cause: CX('land'), last_cause: CX('oceans'), next_cause: CX('forests'),
  // deliberately out of age order: the page sorts each row by age, so card i hangs from dot i
  above: [U('budget_day', 'above', 'land', 14, 'lan0', 1, { org: { id: 'o1', name: 'Blue Coast Fund' } }),
          U('new', 'above', 'land', 0, 'lan2', 3, { leaders_kind: 'organizations' }),
          U('oe_final', 'above', 'land', 7, 'lan1', 2, { leaders_kind: 'organizations', leaders: [{ name: 'Reef Keepers', votes: 4 }] })],
  below: [U('current_me', 'below', 'forests', -1, 'for2', 3, { leaders_kind: 'initiatives', leaders: [{ name: 'Rewilding', share: 75 }] }),
          U('left_prep', 'below', 'oceans', 15, 'oce0', 1, { org: { id: 'o1', name: 'Blue Coast Fund' } }),
          U('entered_prep', 'below', 'oceans', 8, 'oce1', 2)],
  timeline: { from: -2, to: 16, phases: [{ key: 'me', label: 'Initiative election', from: -7, to: 0 }, { key: 'oe', label: 'Organization election', from: 0, to: 8 },
    { key: 'prep', label: 'Prep', from: 8, to: 15 }, { key: 'ex', label: 'Exchange', from: 15, to: 16 }],
    marks: [{ at: 0, label: 'Initiative elected' }, { at: 8, label: 'Organization elected' }, { at: 15, label: 'Budget day' }], dots: [] },
  cause_elections: { secured: [{ window: 'Oceans 4', closes: iso(now + 6 * WK), incumbent: CX('oceans'), holder: CX('oceans'), outcome: 'secured' }],
    won: [], leading: [{ window: 'Land 4', challenger: CX('forests'), incumbent: CX('land'), streak: 2, required: 6 }] },
  exchange: { movers: [{ mission_id: 'oce0', label: 'oceans 1', cause: CX('oceans'), title: 'Garbage Patch Analysis', org: 'Blue Coast Fund', ebx_held_ct: 1072, change_ct: 0, members: 3 }],
    in_exchange: 1, note: 'Ranked by EBX held.' } };
const ROUTES = { '/causes': CAUSES, '/missions': MISSIONS, '/initiatives': TIVS, '/organizations': ORGS,
  '/causes/slate': SLATE, '/candidacies': [{ mission_id: 'oce2', org_id: 'o2' }], '/posts': POSTS, '/initiatives/slugs': [],
  '/inbox/weekly/report': REPORT };
const route = u => {
  const p = String(u).replace(/^https?:\/\/[^/]+/, '').split('?')[0];
  if (p in ROUTES) return ROUTES[p];
  if (/\/p2\/tally$/.test(p)) return { entries: [{ org_id: 'o2', net_votes: 4 }] };
  if (/\/claims$/.test(p)) return [];
  if (/^\/causes\/ballot\//.test(p)) return { columns: [] };
  return null;
};

(async () => {
  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errors.push(String(e.message || e).slice(0, 300)));
  const dom = new JSDOM(fs.readFileSync(R('index.html'), 'utf8'), {
    runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc, url: 'http://localhost/index.html',
    beforeParse(win) {
      win.fetch = async u => { const b = route(u); return { ok: b !== null, status: b === null ? 404 : 200, json: async () => b }; };
      win.matchMedia = () => ({ matches: false, addListener() {}, removeListener() {} });
      win.requestAnimationFrame = () => 0;
      win.cancelAnimationFrame = () => {};
      win.IntersectionObserver = class { observe() {} disconnect() {} };
    },
  });
  const win = dom.window, d = win.document;
  // the page's own <script src> tags don't resolve from disk in this harness
  for (const f of ['resources/js/ebx_shared.js', 'resources/js/ebx_wheel.js', 'resources/js/ebx_steps.js', 'resources/js/ebx_hub.js']) win.eval(fs.readFileSync(R(f), 'utf8'));
  await win.EBX.loadCauses();
  win.EBX.Steps.mount('#ebx-steps', { onChange: win.HomeFlow.paint });   // as the page does
  await win.HomeReport.reload();
  // the hub left Home for Missions (10/9 Reshuffle): mount EBX.Hub on a bare
  // element, as mission.html does, and drive it against the same fixtures
  const hubEl = d.createElement('section'); hubEl.id = 'mh-bare'; d.body.appendChild(hubEl);
  const HomeHub = win.EBX.Hub.mount(hubEl, { mode: 'leaders' });
  await HomeHub.reload();
  await new Promise(r => setTimeout(r, 150));
  const H = k => hubEl.querySelector('[data-hub="' + k + '"]');
  const txt = e => (e ? e.textContent.replace(/\s+/g, ' ').trim() : '');
  const click = el => el.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  let bad = 0, n = 0;
  const ok = (c, what, detail) => { n++; if (!c) bad++; console.log('  ' + (c ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : '')); };

  console.log('\n=== runtime');
  const real = () => errors.filter(e => !/Not implemented|getContext|SVGElement|cloudflareinsights|Could not load/i.test(e));
  ok(!real().length, 'no script errors', real().join(' | '));

  console.log('\n=== the hero, left · the five steps, right');
  const hx = d.querySelector('.hx');
  ok(hx && hx.children[0].classList.contains('ld-a') && hx.querySelector('.hx__vis > #ebx-steps'), 'hero first, the steps beside it');
  ok(txt(d.querySelector('.ld-sub')) === 'you donate, we follow', 'the hero\'s words');
  ok(!/Decide what gets funded|My profile/.test(txt(d.getElementById('ld-cta'))), 'no "Decide what gets funded" or "My profile" in the hero (tweaks 2026-10-01)');
  ok(/text-align:\s*left/.test(d.querySelector('style').textContent.match(/\.ld-a\s*\{[^}]*\}/)[0]), 'the hero is left-aligned');
  ok(!d.getElementById('ebx-wheel') && !d.querySelector('.lw-phase, .lw-card, #lw-topcard'), 'the phase rows, top card, annulus and side cards are off Home');
  const S = d.getElementById('ebx-steps');
  ok(S.querySelectorAll('.sx__scene').length === 5, 'five pages');
  const MSG = ['A fresh focus each week', 'Broad causes → narrow missions', 'Identify those worthy of the job',
    'Collaborate and create a plan', 'Regular updates and built in control'];
  ok(txt(S.querySelector('.sx__msg')) === MSG[0], 'page 1 is Cause', txt(S.querySelector('.sx__msg')));
  ok(S.querySelectorAll('.sx__scene.on').length === 1, 'one page showing');
  ok(!!S.querySelector('.sx__arrow--prev') && !!S.querySelector('.sx__arrow--next'), 'arrows left and right');
  ok(S.querySelectorAll('.sx__dot').length === 5, 'a dot per step');
  ok(S.querySelectorAll('text').length === 0 && txt(S) === MSG[0], 'the message is the only text');
  const names = win.EBX.Steps.STEPS.map(s => s.name).join(' · ');
  ok(names === 'Cause · Initiative · Organization · Network · Feedback', 'the order — step 5 is Feedback (10/9 Reshuffle)', names);
  let threw = '';
  for (let i = 0; i < 5; i++) for (const t of [0, 1.5, 4, 7.5, 9.9]) { try { win.EBX.Steps._at(i, t); } catch (e) { threw += i + '@' + t + ' ' + e.message + '; '; } }
  ok(!threw, 'every scene draws at any second', threw);
  const msgs = [];
  for (let i = 0; i < 5; i++) { win.EBX.Steps._at(i, 0); msgs.push(txt(S.querySelector('.sx__msg'))); }
  ok(msgs.join('|') === MSG.join('|'), 'one message per page, in order');
  win.EBX.Steps._at(4, 0);
  click(S.querySelector('.sx__arrow--next'));
  await new Promise(r => setTimeout(r, 400));
  ok(S.querySelector('.sx__scene.on') === S.querySelectorAll('.sx__scene')[0] && txt(S.querySelector('.sx__msg')) === MSG[0], '→ from Feedback wraps to Cause');
  click(S.querySelector('.sx__arrow--prev'));
  ok(S.querySelector('.sx__scene.on') === S.querySelectorAll('.sx__scene')[4], '← from Cause goes to Feedback');
  click(S.querySelectorAll('.sx__dot')[2]);
  ok(S.querySelector('.sx__scene.on') === S.querySelectorAll('.sx__scene')[2], 'a dot jumps to its page');
  ok(Object.keys(win.EBX.Steps.PANOS).length === 7, 'a vista for each of the seven causes');

  console.log('\n=== the mission hub — EBX.Hub, on Missions since the 10/9 Reshuffle');
  const hub = hubEl;
  ok(!d.getElementById('mh') && !d.getElementById('mh-body'), 'Home itself has no hub any more');
  // Home pass (2026-10-01): collapsed by default — this week's two elections
  ok(H('body').hidden && !H('week').hidden, 'collapsed by default: the grid hidden, this week\'s elections shown');
  ok(txt(H('toggle')) === 'Show all missions', '"Show all missions"', txt(H('toggle')));
  // P2 · Home (2026-10-05): "This Week's Decisions"; standing column heads; the
  // cards titled "Leading initiative/organization: x", runners-up below.
  ok(txt(H('title')) === 'This Week\u2019s Decisions', 'the head says "This Week\u2019s Decisions" collapsed', txt(H('title')));
  ok([...H('week').querySelectorAll('.mh__wh')].map(txt).join(' | ') === 'Initiative Election | Organization Election', 'column heads: Initiative Election · Organization Election');
  ok([...H('week').querySelectorAll('.mw')].every(w => /^Leading (initiative|organization)/.test(txt(w.querySelector('.mw__t'))) && !/election/i.test(txt(w.querySelector('.mw__k')))),
     '…cards titled "Leading initiative/organization", no phase label inside');
  ok([...H('week').querySelectorAll('.mw .mw__t small')].every(x => /tokens|vote/.test(txt(x))), '…with the commit or vote count');
  const wk = [...H('week').querySelectorAll('.mw')];
  ok(wk.length === 2 && wk[0].classList.contains('mw--me') && wk[1].classList.contains('mw--oe'),
     'two cards: the initiative election, then the organization election', wk.map(w => w.className).join(' | '));
  const shown = w => (w.querySelector('.mw__t small') ? 1 : 0) + w.querySelectorAll('.mw__lead li').length;
  ok(wk.every(w => shown(w) <= 3) && wk.some(w => shown(w) >= 1),
     '…each with its top three at most (the leader in the title, the runners-up below)', wk.map(shown).join(','));
  click(H('toggle'));
  ok(!H('body').hidden && H('week').hidden && txt(H('toggle')) === 'Collapse missions',
     '"Show all missions" opens the grid; the button says "Collapse missions"');
  ok(txt(H('title')) === 'All missions', '…and the head says "All missions"');
  ok(/Leading/.test(HomeHub.state.rows.flatMap(r => r.cells.map(c => c.html)).filter(h => /mc--me/.test(h)).join('')),
     'an initiative-election card says Leading');
  ok(!hub.querySelector('.mh__rowhead, .mh__colhead') && HomeHub.state.rows.length === 7, 'seven rows, one per cause, with no row or column labels');
  // the whole grid, whatever the width: open every column
  HomeHub.state.vis = 99;
  const row = cid => HomeHub.state.rows.find(r => r.c.id === cid).cells.map(c => c.html);
  const oce = row('oceans');
  ok(/mc--ce/.test(oce[0]) && /mission\.html\?slot=7/.test(oce[0]), 'column 0 is the cause election, linked to its window');
  const ids = oce.slice(1).map(h => (h.match(/data-mission="([^"]+)"/) || [])[1]);
  ok(ids.join(',') === 'oce4,oce3,oce2,oce1,oce0', 'then its missions, newest first', ids.join(','));
  const kind = h => (h.match(/class="mc mc--([a-z-]+)/) || [])[1];
  ok(oce.slice(1).map(kind).join(',') === 'me,no-tiv,oe,fr,ex', 'each mission\'s stage from its dates', oce.slice(1).map(kind).join(','));
  ok(oce.every(h => !/Week \d/.test(h)), 'no "Week x" anywhere (2026-10-05)');
  ok(/mc__k">Initiative election · closes /.test(oce[1]) && /mc__k">Organization election · closes /.test(oce[3]), 'the top row is "phase · closes x"');
  ok(oce.slice(1).every(h => /mc__f"><span><b>oceans<\/b> · started /.test(h)), 'the bottom row is "cause · started x"');
  ok(/Leading: Coral Restoration Alliance · 75% · 2 initiatives/.test(oce[1]), 'an initiative election says "Leading: <initiative>"');
  ok(/Leading: Reef Keepers|2 nominated|1 nominated/.test(oce[3]) && /Blue Coast Fund/.test(oce[4]), 'later stages show the organization');
  ok(/mc--now/.test(oce[0]) && /mc--now/.test(row('land')[1]), 'this week\'s decisions glow (a cause election, a closing initiative election)');
  ok(!/mc--now/.test(oce[1]) && !/mc--now/.test(oce[5]), '…and nothing else does');
  ok(/forests challenging · 2\/6/.test(row('land')[0]), 'a challenger shows its streak');
  // paging: three columns at a time
  const S2 = HomeHub.state;
  Object.defineProperty(H('body'), 'clientWidth', { configurable: true, get: () => 3 * 196 });
  S2.off = 0; click(d.querySelector('[data-mh="1"]'));
  ok(S2.vis === 3 && S2.off === 1, '› moves one column', S2.vis + '/' + S2.off);
  click(d.querySelector('[data-mh="page"]'));
  ok(S2.off === S2.cols - S2.vis, '» moves a page (and stops at the end)', S2.off + ' of ' + S2.cols);
  ok(d.querySelector('[data-mh="1"]').disabled, '› is off at the end');
  click(d.querySelector('[data-mh="-page"]'));
  ok(S2.off === 0 && d.querySelector('[data-mh="-1"]').disabled, '« back to the start');
  ok(hub.querySelectorAll('.mh__grid .mc').length === 7 * 3 - hub.querySelectorAll('.mc--empty').length, 'a card or an empty cell in every visible slot');
  // "The current cause with a mission in week 0 should be the bottom row …
  // week 6 the top row."
  const wks = HomeHub.state.rows.map(r => HomeHub.weekOf(r.c));
  ok(wks.join(',') === '6,5,4,3,2,1,0', 'rows run week 6 at the top to week 0 at the bottom', wks.join(','));
  ok(HomeHub.state.rows.every(r => !/ holds</.test(r.cells[0].html)), 'a cause election says "<cause> <number>", not "holds"');
  ok(/>oceans \d+</i.test(oce[0]), '…e.g. ' + (oce[0].match(/mc__t">([^<]+)/) || [])[1]);
  click(H('toggle'));
  ok(H('body').hidden && H('toggle').getAttribute('aria-expanded') === 'false', 'collapses');
  ok([...H('nav').querySelectorAll('[data-mh]')].every(b => b.hidden), '…and the paging buttons go with the grid');
  click(H('toggle'));
  ok(!H('body').hidden, '…and opens again');

  console.log('\n=== Home pass (2026-10-01) — the hero, the steps list, the four doors');
  ok(!d.querySelector('.ld-claim') && !/Social Network for Charities/i.test(txt(d.querySelector('.hx'))), '"The social network for charities" is gone');
  ok(!/Vote now/.test(txt(d.querySelector('.hx'))), 'no "Vote now"');
  const flow = [...d.querySelectorAll('#ld-flow .ld-flow__i')].map(txt);
  ok(flow.join(' · ') === '1. Cause · 2. Initiative · 3. Organization · 4. Network · 5. Feedback' && d.querySelectorAll('#ld-flow .ld-flow__arr').length === 4,
     'beside the visual: the five steps stacked, arrows down', flow.join(' · '));
  ok(d.getElementById('ld-flow').parentNode === S.parentNode && !!(d.getElementById('ld-flow').compareDocumentPosition(S) & 4)
     && /grid-template-columns:\s*auto minmax\(0, 1fr\)/.test(d.querySelector('style').textContent.match(/\.hx__vis\s*\{[^}]*\}/)[0]),
     '…to the LEFT of the visual (10/9 Reshuffle)');
  win.EBX.Steps._at(3, 0);
  ok(d.querySelectorAll('#ld-flow .ld-flow__i.on').length === 1 && txt(d.querySelector('#ld-flow .ld-flow__i.on')) === '4. Network',
     '…the step being shown glows');
  click(d.querySelector('#ld-flow [data-flow="1"]'));
  ok(txt(d.querySelector('#ebx-steps .sx__msg')) === MSG[1], '…and clicking one shows its page');
  const doors = [...d.querySelectorAll('#hk .hk__card')];
  ok(doors.length === 4 && hx.compareDocumentPosition(d.getElementById('hk')) & 4 && d.getElementById('hk').compareDocumentPosition(d.getElementById('wr')) & 4,
     'four doors between the hero and the weekly report');
  const hrefs = doors.map(c => [...c.querySelectorAll('a')].map(a => a.getAttribute('href')).join(' '));
  ok(/mission\.html/.test(hrefs[0]) && /about\.html/.test(hrefs[1]) && /cause\.html/.test(hrefs[2]) && /profile\.html/.test(hrefs[3]) && /\/org/.test(hrefs[3]),
     'Decide what gets funded → Missions · Who are we? → About · Go to the discussion → News · sign in / profile + For charities', hrefs.join(' | '));
  ok(/We give everyone \$1 to vote with in every initiative election/.test(txt(doors[0])) && /charities compete for the chance to lead the mission/.test(txt(doors[0])),
     'the two key decisions, as Jax wrote them (2026-10-09, edit 1)');
  ok(d.querySelectorAll('#hk ol.hk__list > li').length === 2 && /as important as financial donations/.test(txt(doors[1]))
     && /follow the will of the people/.test(txt(doors[1])), 'numbered 1 and 2; "Every voice matters"');
  ok(/Feedback and accountability/.test(txt(doors[2])) && /progress is public, week by week/.test(txt(doors[2])) && /move your donation to a different mission/.test(txt(doors[2])),
     '"Feedback and accountability", with edits 2 and 3');

  console.log('\n=== the weekly report (10/9 Reshuffle) — and no feed on Home');
  ok(!d.getElementById('hf-list') && !d.querySelector('.hn') && !d.getElementById('hn-post'), 'the feed is News\' now: no feed, no Network row on Home');
  ok(txt(d.getElementById('wr-title')) === REPORT.title, 'headed with the week and its cause', txt(d.getElementById('wr-title')));
  const above = [...d.querySelectorAll('#wr-above .wu')], below = [...d.querySelectorAll('#wr-below .wu')];
  ok(above.length === 3 && below.length === 3, 'three updates above the timeline, three below');
  ok(above.map(c => c.id).join(',') === 'wu-new,wu-oe_final,wu-budget_day' && below.map(c => c.id).join(',') === 'wu-current_me,wu-entered_prep,wu-left_prep',
     '…each row in timeline order, so card i hangs from dot i', above.map(c => c.id).concat(below.map(c => c.id)).join(','));
  const dots = [...d.querySelectorAll('#wr-tl .tl__dot')];
  ok(dots.length === 6 && dots.every(x => /^\d$/.test(txt(x))), 'six dots on the timeline, each labelled with its mission\'s number', dots.map(txt).join(''));
  const xs = side => [...d.querySelectorAll('#wr-tl .tl__dot--' + side)].map(x => parseFloat(x.style.left));
  ok(xs('above').every((x, i, a) => !i || a[i - 1] < x) && xs('below').every((x, i, a) => !i || a[i - 1] < x), '…placed by weeks since the initiative was elected');
  ok(d.querySelectorAll('#wr-tl .tl__ph').length === 4 && /Prep/.test(txt(d.getElementById('wr-tl'))) && !/Framing/.test(txt(d.getElementById('wr-tl'))),
     'the phases run initiative election → organization election → prep → exchange (Framing reads Prep)');
  ok(above.concat(below).every(c => c.querySelector('.wu__go a[href^="cause.html?mission="]')), 'every card links to its mission\'s news');
  ok(/Vote with your 10 tokens/.test(txt(d.getElementById('wu-current_me'))), 'this week\'s initiative election asks for the ten granted tokens');
  ok(/Forests/i.test(txt(d.getElementById('wr-ce'))) && /Oceans 4/.test(txt(d.getElementById('wr-ce'))), 'the cause elections: who leads, who secured a window');
  ok(d.querySelectorAll('#wr-ex .wx tbody tr').length === 1 && /\+0/.test(txt(d.querySelector('#wr-ex .wx tbody tr'))), 'the exchange\'s top movers, +0 until trading');
  // The shared card the feed drew here (posting pass, 2026-10-01) is News' now
  // (and the profile's): EBX.Post.collapsed, drawn on a bare element against
  // the same fixture posts.
  ok(/Journalists/.test(fs.readFileSync(R('about.html'), 'utf8')) && /id="news"/.test(fs.readFileSync(R('about.html'), 'utf8')),
     'the newsroom\'s description is on About (Our goals › the newsroom)');
  const bare = d.createElement('div'); d.body.appendChild(bare);
  bare.innerHTML = POSTS.filter(p => !p.parent_id).map(p => win.EBX.Post.collapsed(p)).join('');
  win.EBX.Post.bindVotes(bare);
  const cards = () => [...bare.querySelectorAll('.ep--card')];
  ok(cards().length === POSTS.length, 'the shared card draws every root post', String(cards().length));
  const card1 = cards()[0];
  // posting edits (2026-10-02): top bar (target · next decision · cause) /
  // title · source · date · tag / contents …show more / votes · comments · reply
  ok(card1 && card1.querySelector('.ep__bar .ep__bar-t') && card1.querySelector('.ep__bar .ep__bar-c') &&
     card1.querySelector('.ep__head .ep__title') && card1.querySelector('.ep__head .ep__by') && card1.querySelector('.ep__head .ep__kind') &&
     card1.querySelector('.ep__more') && card1.querySelector('.ep__foot2 .ep__votes') && card1.querySelector('[data-ep-reply]'),
     'top bar · title, source, date, tag · show more · votes, comments, reply');
  const kindOf = id => txt(bare.querySelector('.ep--card[data-post="' + id + '"] .ep__kind'));
  ok(/Background/i.test(kindOf('r1')) && /Investigation/i.test(kindOf('r2')) && /Analysis/i.test(kindOf('r3')), 'research says its type', [kindOf('r1'), kindOf('r2'), kindOf('r3')].join(' | '));
  ok(/example\.org/.test(txt(bare.querySelector('.ep--card[data-post="r2"] .ep__src'))), 'a pulled-in news link shows its source');
  ok(!/\.hp--(news|research|budgeting)\b|border-left:\s*3px/.test((d.getElementById('ebx-post-css') || { textContent: '' }).textContent), 'no colour coding on the cards');
  ok(cards().every(c => c.querySelector('[data-ep-vote="helpful"]')), 'every card can be voted on');
  ok(cards().every(c => c.querySelector('[data-ep-extra]') && c.querySelector('[data-ep-extra]').hidden), 'every card starts collapsed, expandable in place');
  const news = fs.readFileSync(R('cause.html'), 'utf8');
  ok(/function readHandoff\(\)/.test(news) && /P\.get\('cat'\)/.test(news) && /P\.get\('thread'\)/.test(news) && /P\.get\('mission'\)/.test(news),
     'News reads ?cat ?thread ?mission');

  console.log('\n=== the phase lines moved to the ballots');
  const mp = fs.readFileSync(R('mission.html'), 'utf8');
  ok(['ce', 'me', 'oe', 'fr', 'ex'].every(k => mp.includes('id="el3-blurb-' + k + '"')), 'each ballot panel has its line');
  ok(/W\.PHASE\[_PH\[k\]\]/.test(mp) && Object.keys(win.EBX.Wheel.PHASE).length === 5, '…read from EBX.Wheel.PHASE (one source)');

  ok(!real().length, 'still no script errors', real().join(' | '));
  console.log('\n' + (bad ? 'FAILED ' + bad + '/' + n : 'all ' + n + ' checks passed'));
  process.exit(bad ? 1 : 0);
})();
