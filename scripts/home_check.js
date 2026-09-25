// home_check — P2 · Home (2026-09-25): the Network row and the feed, in jsdom,
// against FIXTURES (no server).
//
//   node scripts/home_check.js            # from the repo root; needs `npm i jsdom`
//
// Pins what P2 put on Home below the annulus: THE NETWORK as one row
// (News · Research · Budgeting) that is also the feed's filter; the feed is
// ALL posts by default; research posts carry their B · V · A tag; Home's only
// other filters are a cause and "mine" (D6); and everything past that — a
// thread, a reply, search, a second filter — is a link into News
// (cause.html?thread= / ?q= / ?cat= / ?cause=). It also checks that News
// reads those parameters.
const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const R = f => path.join(ROOT, f);

const now = Date.now(), day = 864e5, iso = t => new Date(t).toISOString();
const CAUSES = ['atmosphere','oceans','land','forests','wildlife','human-rights','human-progress']
  .map((id, i) => ({ id, index: i, name: id.replace(/-/g,' '), color: '#4aa3c7', emoji: '🌱' }));
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
const ROUTES = { '/causes': CAUSES, '/missions': [], '/initiatives': [], '/organizations': [],
  '/causes/slate': { slots: [] }, '/candidacies': [], '/posts': POSTS };
const route = u => { const p = String(u).replace(/^https?:\/\/[^/]+/, '').split('?')[0]; return p in ROUTES ? ROUTES[p] : null; };

(async () => {
  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errors.push(String(e.message || e).slice(0, 300)));
  const dom = new JSDOM(fs.readFileSync(R('index.html'), 'utf8'), {
    runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc, url: 'http://localhost/index.html',
    beforeParse(win) {
      win.fetch = async u => { const b = route(u); return { ok: b !== null, status: b === null ? 404 : 200, json: async () => b }; };
      win.matchMedia = () => ({ matches: false, addListener(){}, removeListener(){} });
      win.requestAnimationFrame = () => 0;
      win.IntersectionObserver = class { observe(){} disconnect(){} };
    },
  });
  const win = dom.window, d = win.document;
  win.eval(fs.readFileSync(R('resources/js/ebx_shared.js'), 'utf8'));
  await win.HomeFeed.reload();
  await new Promise(r => setTimeout(r, 100));
  const txt = e => (e ? e.textContent.replace(/\s+/g, ' ').trim() : '');
  const click = el => el.dispatchEvent(new win.MouseEvent('click', { bubbles: true }));
  let bad = 0, n = 0;
  const ok = (c, what, detail) => { n++; if (!c) bad++; console.log('  ' + (c ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : '')); };
  const cards = () => [...d.querySelectorAll('#hf-list .hp')];

  console.log('\n=== runtime');
  const real = errors.filter(e => !/Not implemented|getContext|SVGElement|cloudflareinsights|Could not load/i.test(e));
  ok(!real.length, 'no script errors', real.join(' | '));

  console.log('\n=== the Network row');
  const tiles = [...d.querySelectorAll('#hn-row .hn__tile')];
  ok(tiles.length === 3, 'one row of three');
  ok(['News', 'Research', 'Budgeting'].every((t, i) => txt(tiles[i] && tiles[i].querySelector('.hn__name')) === t), 'News · Research · Budgeting, in that order');
  ok(['funded', 'wins rewards', 'drives the mission'].every((t, i) => txt(tiles[i].querySelector('.hn__tag')) === t), 'funded · wins rewards · drives the mission');
  ok(/2 this week/.test(txt(tiles[1])), 'counts this week\'s posts', txt(tiles[1].querySelector('.hn__n')));
  ok(tiles.every(t => t.getAttribute('aria-pressed') === 'false'), 'nothing pressed by default');

  console.log('\n=== the feed — all posts by default');
  ok(cards().length === POSTS.length, 'every root post is shown', String(cards().length));
  ok(/all posts/i.test(txt(d.getElementById('hf-state'))), 'the state line says all posts');
  const tag = id => txt(d.querySelector('.hp[data-post="' + id + '"] .hp__bia'));
  ok(tag('r1') === 'B' && tag('r2') === 'V' && tag('r3') === 'A', 'research tagged B · V · A');
  ok(/Vetting/.test(txt(d.querySelector('.hp[data-post="r2"]'))), 'the investigation type reads Vetting');
  ok(/example\.org/.test(txt(d.querySelector('.hp[data-post="r2"] .hp__src'))), 'a pulled-in news link shows its source');

  console.log('\n=== the filter split (D6)');
  click(tiles[1]);
  ok(cards().length === 3 && cards().every(c => c.classList.contains('hp--research')), 'Research tile filters to research');
  ok(d.querySelector('#hn-row .hn__tile--research').getAttribute('aria-pressed') === 'true', '…and shows pressed');
  click(d.querySelector('.hf-chip[data-cause="land"]'));
  ok(cards().length === 2, 'a cause narrows it further', String(cards().length));
  ok(d.getElementById('hf-more-news').getAttribute('href') === 'cause.html?cat=mission_support&cause=land', 'more filters → News with both carried');
  click(d.querySelector('#hn-row .hn__tile--research'));
  ok(cards().length === 2 && !d.querySelector('.hn__tile[aria-pressed="true"]'), 'pressing the tile again clears it');
  click(d.querySelector('.hf-chip[data-cause=""]'));
  ok(cards().length === POSTS.length, 'All causes restores the full feed');
  const mine = d.querySelector('.hf-chip[data-mine="1"]');
  ok(mine && mine.disabled, '"Mine" needs a sign-in');
  win.HomeFeed.state.me = 7; win.HomeFeed.state.mine = true; click(d.querySelector('.hf-chip[data-cause=""]'));
  ok(cards().length === 1 && cards()[0].dataset.post === 'b1', '"Mine" shows only my posts');
  win.HomeFeed.state.mine = false; click(d.querySelector('.hf-chip[data-cause=""]'));
  ok(d.querySelectorAll('.hn select, .hn input[type=date]').length === 0, 'no second-axis filters on Home');

  console.log('\n=== what goes to News');
  ok(cards().every(c => /^cause\.html\?(.*&)?thread=/.test(c.getAttribute('href'))), 'every post opens its thread in News');
  const f = d.getElementById('hf-search');
  ok(f && f.getAttribute('action') === 'cause.html' && f.querySelector('input[name=q]'), 'search submits to News (?q=)');
  ok(!d.querySelector('#hf-list textarea, #hf-list [data-send]'), 'no reply box on Home — replying is in News');
  const news = fs.readFileSync(R('cause.html'), 'utf8');
  ok(/function readHandoff\(\)/.test(news) && /P\.get\('q'\)/.test(news) && /P\.get\('cat'\)/.test(news) &&
     /P\.get\('cause'\)/.test(news) && /P\.get\('thread'\)/.test(news), 'News reads ?q ?cat ?cause ?thread');

  console.log('\n' + (bad ? 'FAILED ' + bad + '/' + n : 'all ' + n + ' checks passed'));
  process.exit(bad ? 1 : 0);
})();
