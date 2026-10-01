// home_check — Home (index.html), in jsdom, against FIXTURES (no server).
//
//   node scripts/home_check.js            # from the repo root; needs `npm i jsdom`
//
// Rewritten 2026-09-30 for P2 · Home mods. Pins, top to bottom:
//   · THE HERO, left-aligned, with THE FIVE STEPS to its right (ebx_steps.js):
//     five pages Cause → Initiative → Organization → Network → Reporting, one
//     message each and no other text, arrows both ways, a dot per step, and
//     every scene drawable at any second without throwing;
//   · THE MISSION HUB: seven rows, the cause election first, then the missions
//     newest first; each mission's stage read from its dates; "Week x" on every
//     post-ME mission; this week's decisions glow; ‹ › « » and collapse;
//   · THE NETWORK + THE FEED with no toggles on Home — tiles and posts link into
//     News (cause.html?cat= / ?thread=), which reads those parameters;
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
const ROUTES = { '/causes': CAUSES, '/missions': MISSIONS, '/initiatives': TIVS, '/organizations': ORGS,
  '/causes/slate': SLATE, '/candidacies': [{ mission_id: 'oce2', org_id: 'o2' }], '/posts': POSTS, '/initiatives/slugs': [] };
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
  for (const f of ['resources/js/ebx_shared.js', 'resources/js/ebx_wheel.js', 'resources/js/ebx_steps.js']) win.eval(fs.readFileSync(R(f), 'utf8'));
  await win.EBX.loadCauses();
  win.EBX.Steps.mount('#ebx-steps', { onChange: win.HomeFlow.paint });   // as the page does
  await win.HomeFeed.reload();
  await win.HomeHub.reload();
  await new Promise(r => setTimeout(r, 150));
  const txt = e => (e ? e.textContent.replace(/\s+/g, ' ').trim() : '');
  const click = el => el.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  let bad = 0, n = 0;
  const ok = (c, what, detail) => { n++; if (!c) bad++; console.log('  ' + (c ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : '')); };

  console.log('\n=== runtime');
  const real = () => errors.filter(e => !/Not implemented|getContext|SVGElement|cloudflareinsights|Could not load/i.test(e));
  ok(!real().length, 'no script errors', real().join(' | '));

  console.log('\n=== the hero, left · the five steps, right');
  const hx = d.querySelector('.hx');
  ok(hx && hx.children[0].classList.contains('ld-a') && hx.querySelector('.hx__vis > #ebx-steps'), 'hero first, steps to its right');
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
  ok(names === 'Cause · Initiative · Organization · Network · Reporting', 'the order', names);
  let threw = '';
  for (let i = 0; i < 5; i++) for (const t of [0, 1.5, 4, 7.5, 9.9]) { try { win.EBX.Steps._at(i, t); } catch (e) { threw += i + '@' + t + ' ' + e.message + '; '; } }
  ok(!threw, 'every scene draws at any second', threw);
  const msgs = [];
  for (let i = 0; i < 5; i++) { win.EBX.Steps._at(i, 0); msgs.push(txt(S.querySelector('.sx__msg'))); }
  ok(msgs.join('|') === MSG.join('|'), 'one message per page, in order');
  win.EBX.Steps._at(4, 0);
  click(S.querySelector('.sx__arrow--next'));
  await new Promise(r => setTimeout(r, 400));
  ok(S.querySelector('.sx__scene.on') === S.querySelectorAll('.sx__scene')[0] && txt(S.querySelector('.sx__msg')) === MSG[0], '→ from Reporting wraps to Cause');
  click(S.querySelector('.sx__arrow--prev'));
  ok(S.querySelector('.sx__scene.on') === S.querySelectorAll('.sx__scene')[4], '← from Cause goes to Reporting');
  click(S.querySelectorAll('.sx__dot')[2]);
  ok(S.querySelector('.sx__scene.on') === S.querySelectorAll('.sx__scene')[2], 'a dot jumps to its page');
  ok(Object.keys(win.EBX.Steps.PANOS).length === 7, 'a vista for each of the seven causes');

  console.log('\n=== the mission hub');
  const hub = d.getElementById('mh');
  // Home pass (2026-10-01): collapsed by default — this week's two elections
  ok(d.getElementById('mh-body').hidden && !d.getElementById('mh-week').hidden, 'collapsed by default: the grid hidden, this week\'s elections shown');
  ok(txt(d.getElementById('mh-toggle')) === 'Show all missions', '"Show all missions"', txt(d.getElementById('mh-toggle')));
  ok(txt(d.getElementById('mh-sub')) === 'This week\u2019s elections', 'the head says "This week\u2019s elections" collapsed', txt(d.getElementById('mh-sub')));
  ok([...d.querySelectorAll('#mh-week .mw')].every(w => !w.querySelector('.mw__lead') || /Leading/.test(txt(w.querySelector('.mw__lab')))), '…its leaders labelled Leading');
  const wk = [...d.querySelectorAll('#mh-week .mw')];
  ok(wk.length === 2 && wk[0].classList.contains('mw--me') && wk[1].classList.contains('mw--oe'),
     'two cards: the initiative election, then the organization election', wk.map(w => w.className).join(' | '));
  ok(wk.every(w => w.querySelectorAll('.mw__lead li').length <= 3) && wk.some(w => w.querySelectorAll('.mw__lead li').length >= 1),
     '…each with its top three at most', wk.map(w => w.querySelectorAll('.mw__lead li').length).join(','));
  click(d.getElementById('mh-toggle'));
  ok(!d.getElementById('mh-body').hidden && d.getElementById('mh-week').hidden && txt(d.getElementById('mh-toggle')) === 'Collapse missions',
     '"Show all missions" opens the grid; the button says "Collapse missions"');
  ok(txt(d.getElementById('mh-sub')) === 'All missions', '…and the head says "All missions"');
  ok(/Leading/.test(win.HomeHub.state.rows.flatMap(r => r.cells.map(c => c.html)).filter(h => /mc--me/.test(h)).join('')),
     'an initiative-election card says Leading');
  const heads = [...hub.querySelectorAll('.mh__rowhead')];
  ok(heads.length === 7, 'seven rows, one per cause');
  // the whole grid, whatever the width: open every column
  win.HomeHub.state.vis = 99;
  const row = cid => win.HomeHub.state.rows.find(r => r.c.id === cid).cells.map(c => c.html);
  const oce = row('oceans');
  ok(/mc--ce/.test(oce[0]) && /mission\.html\?slot=7/.test(oce[0]), 'column 0 is the cause election, linked to its window');
  const ids = oce.slice(1).map(h => (h.match(/data-mission="([^"]+)"/) || [])[1]);
  ok(ids.join(',') === 'oce4,oce3,oce2,oce1,oce0', 'then its missions, newest first', ids.join(','));
  const kind = h => (h.match(/class="mc mc--([a-z-]+)/) || [])[1];
  ok(oce.slice(1).map(kind).join(',') === 'me,no-tiv,oe,fr,ex', 'each mission\'s stage from its dates', oce.slice(1).map(kind).join(','));
  ok(!/Week \d/.test(oce[1]), 'no "Week x" before the initiative election closes');
  ok(/Week 2</.test(oce[3]) && /Week 10</.test(oce[4]) && /Week 20</.test(oce[5]), '"Week x" on every post-ME mission');
  ok(/Coral Restoration Alliance/.test(oce[1]) && /Leading · 75% · 2 initiatives/.test(oce[1]), 'an initiative election shows its leader');
  ok(/leading: Reef Keepers/.test(oce[3]) && /Blue Coast Fund/.test(oce[4]), 'later stages show the organization');
  ok(/mc--now/.test(oce[0]) && /mc--now/.test(row('land')[1]), 'this week\'s decisions glow (a cause election, a closing initiative election)');
  ok(!/mc--now/.test(oce[1]) && !/mc--now/.test(oce[5]), '…and nothing else does');
  ok(/forests challenging · 2\/6/.test(row('land')[0]), 'a challenger shows its streak');
  // paging: three columns at a time
  const S2 = win.HomeHub.state;
  Object.defineProperty(d.getElementById('mh-body'), 'clientWidth', { configurable: true, get: () => 128 + 3 * 206 });
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
  const wks = win.HomeHub.state.rows.map(r => win.HomeHub.weekOf(r.c));
  ok(wks.join(',') === '6,5,4,3,2,1,0', 'rows run week 6 at the top to week 0 at the bottom', wks.join(','));
  ok(win.HomeHub.state.rows.every(r => !/ holds</.test(r.cells[0].html)), 'a cause election says "<cause> <number>", not "holds"');
  ok(/>oceans \d+</i.test(oce[0]), '…e.g. ' + (oce[0].match(/mc__t">([^<]+)/) || [])[1]);
  click(d.getElementById('mh-toggle'));
  ok(d.getElementById('mh-body').hidden && d.getElementById('mh-toggle').getAttribute('aria-expanded') === 'false', 'collapses');
  ok([...d.querySelectorAll('#mh-nav [data-mh]')].every(b => b.hidden), '…and the paging buttons go with the grid');
  click(d.getElementById('mh-toggle'));
  ok(!d.getElementById('mh-body').hidden, '…and opens again');

  console.log('\n=== Home pass (2026-10-01) — the hero, the steps list, the four doors');
  ok(!d.querySelector('.ld-claim') && !/Social Network for Charities/i.test(txt(d.querySelector('.hx'))), '"The social network for charities" is gone');
  ok(!/Vote now/.test(txt(d.querySelector('.hx'))), 'no "Vote now"');
  const flow = [...d.querySelectorAll('#ld-flow .ld-flow__i')].map(txt);
  ok(flow.join(' · ') === 'Cause · Initiative · Organization · Network · Reporting' && d.querySelectorAll('#ld-flow .ld-flow__arr').length === 4,
     'beside the visual: the five steps stacked, arrows down', flow.join(' · '));
  win.EBX.Steps._at(3, 0);
  ok(d.querySelectorAll('#ld-flow .ld-flow__i.on').length === 1 && txt(d.querySelector('#ld-flow .ld-flow__i.on')) === 'Network',
     '…the step being shown glows');
  click(d.querySelector('#ld-flow [data-flow="1"]'));
  ok(txt(d.querySelector('#ebx-steps .sx__msg')) === MSG[1], '…and clicking one shows its page');
  const doors = [...d.querySelectorAll('#hk .hk__card')];
  ok(doors.length === 4 && hx.compareDocumentPosition(d.getElementById('hk')) & 4 && d.getElementById('hk').compareDocumentPosition(hub) & 4,
     'four doors between the hero and the mission hub');
  const hrefs = doors.map(c => [...c.querySelectorAll('a')].map(a => a.getAttribute('href')).join(' '));
  ok(/mission\.html/.test(hrefs[0]) && /about\.html/.test(hrefs[1]) && /cause\.html/.test(hrefs[2]) && /profile\.html/.test(hrefs[3]) && /register/.test(hrefs[3]),
     'Decide what gets funded → Missions · Who are we? → About · Go to the discussion → News · sign in / profile + For charities', hrefs.join(' | '));
  ok(/\$1/.test(txt(doors[0])) && /charity agrees/.test(txt(doors[0])), 'the two key decisions, as written');
  ok(!d.querySelector('.hk__n') && /can be as impactful/.test(txt(doors[1])), 'not numbered; "can be as impactful" (no "just")');

  console.log('\n=== the Network + the feed — no toggles on Home');
  // tweaks (2026-10-01): "News research and budgeting tabs … should be gone."
  ok(!d.getElementById('hn-row') && !d.querySelector('.hn__tile'), 'no News · Research · Budgeting tiles');
  ok(/grid-template-columns:\s*minmax\(0, 1fr\);/.test(d.querySelector('style').textContent.match(/\.hf__list\s*\{[^}]*\}/)[0]), 'one column of posts');
  ok(/journalists, scientists and auditors/.test(fs.readFileSync(R('about.html'), 'utf8')) && /id="ab-net"/.test(fs.readFileSync(R('about.html'), 'utf8')),
     'their descriptions are on About');
  // Posting pass (2026-10-01): the shared card, EBX.Post.collapsed
  const cards = () => [...d.querySelectorAll('#hf-list .ep--card')];
  ok(cards().length === POSTS.length, 'the feed is every root post, as the shared card', String(cards().length));
  const card1 = cards()[0];
  ok(card1 && card1.querySelector('.ep__main .ep__title') && card1.querySelector('.ep__side .ep__who') && card1.querySelector('.ep__side .ep__kind') &&
     card1.querySelector('.ep__votes') && /Discussion/.test(txt(card1.querySelector('.ep__disc'))),
     'title left · account-date and type right · votes and Discussion → along the foot');
  const kindOf = id => txt(d.querySelector('.ep--card[data-post="' + id + '"] .ep__kind'));
  ok(/Background/i.test(kindOf('r1')) && /Investigation/i.test(kindOf('r2')) && /Analysis/i.test(kindOf('r3')), 'research says its type', [kindOf('r1'), kindOf('r2'), kindOf('r3')].join(' | '));
  ok(/example\.org/.test(txt(d.querySelector('.ep--card[data-post="r2"] .ep__src'))), 'a pulled-in news link shows its source');
  ok(!/\.hp--(news|research|budgeting)\b|border-left:\s*3px/.test(d.getElementById('ebx-post-css').textContent), 'no colour coding on the cards');
  ok(cards().every(c => c.querySelector('[data-ep-vote="helpful"]')), 'every card can be voted on from Home');
  ok(!d.querySelector('.hn .hf-chip, .hn input, .hn select, .hn form, .hn [aria-pressed]:not(.ep__v)'), 'no filter, search or toggle on Home');
  ok(cards().every(c => /^cause\.html\?thread=/.test(c.querySelector('.ep__disc').getAttribute('href'))), 'Discussion → opens its thread in News');
  ok(/post\.html/.test((d.getElementById('hn-post') || {}).href || ''), "Home's + opens the composer (P3)");
  const news = fs.readFileSync(R('cause.html'), 'utf8');
  ok(/function readHandoff\(\)/.test(news) && /P\.get\('cat'\)/.test(news) && /P\.get\('thread'\)/.test(news), 'News reads ?cat ?thread');

  console.log('\n=== the phase lines moved to the ballots');
  const mp = fs.readFileSync(R('mission.html'), 'utf8');
  ok(['ce', 'me', 'oe', 'fr', 'ex'].every(k => mp.includes('id="el3-blurb-' + k + '"')), 'each ballot panel has its line');
  ok(/W\.PHASE\[_PH\[k\]\]/.test(mp) && Object.keys(win.EBX.Wheel.PHASE).length === 5, '…read from EBX.Wheel.PHASE (one source)');

  ok(!real().length, 'still no script errors', real().join(' | '));
  console.log('\n' + (bad ? 'FAILED ' + bad + '/' + n : 'all ' + n + ' checks passed'));
  process.exit(bad ? 1 : 0);
})();
