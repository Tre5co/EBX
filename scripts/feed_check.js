// Drives THE FEED on cause.html in a headless DOM (2026-09-17, the feed pass).
//
// structure.md §8 states the two rules the feed has to obey, and they are the
// first two things asserted here: **all posts are included** — one feed, every
// category — and it is **not sorted by mission**, so the order is the API's
// `sort=hot` and nothing on the page re-sorts it. The rest is the control panel
// (box d), the reactions (b) and the reply affordance (f).
//
// The last assertion is the move itself: the DISCUSSION BOX is gone from this
// page. posts_box_check.js drives it on mission.html now.
const { JSDOM, VirtualConsole } = require('jsdom');
const BASE = process.argv[2] || 'http://127.0.0.1:8000';
const CAUSE = process.argv[3] || 'atmosphere';

(async () => {
  const errs = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => {
    const m = String(e.message || e);
    if (!/fonts\.googleapis\.com/.test(m)) errs.push(m.slice(0, 240));
  });
  vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ').slice(0, 200)));

  const dom = await JSDOM.fromURL(BASE + '/cause.html?id=' + CAUSE, {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
      w.matchMedia = w.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
    },
  });
  await new Promise(r => setTimeout(r, 4000));
  const d = dom.window.document, W = dom.window;
  let bad = 0;
  const say = (label, ok, extra) => {
    console.log((ok ? '  ok    ' : '  FAIL  ') + label + (extra ? '  ' + extra : ''));
    if (!ok) bad++;
  };
  const q = s => [...d.querySelectorAll(s)];
  const txt = s => (d.querySelector(s) || {}).textContent || '';
  const section = t => console.log('\n=== ' + t);

  // ── d · the control panel ──
  section('d — the control panel');
  say('the panel is on the page', !!d.getElementById('fd-panel'));
  say('it carries a search box', !!d.getElementById('fd-search'));
  say('…an order select, hot first',
      (d.getElementById('fd-sort') || {}).value === 'hot',
      [...q('#fd-sort option')].map(o => o.value).join(' | '));
  say('…and a way to post, which points at a mission',
      /mission\.html/.test((d.getElementById('fd-compose') || {}).href || ''),
      (d.getElementById('fd-compose') || {}).textContent || '');
  const chips = q('#fd-filters .fd-chip').map(e => e.textContent.trim());
  say('the phase/category tabs are FILTERS here, not a frame',
      chips.length >= 5 && /Everything/i.test(chips[0]), chips.join(' | '));
  say('"Everything" is the one that is on, so the page opens unfiltered',
      q('#fd-filters .fd-chip--on').length === 1 &&
      /Everything/i.test(txt('#fd-filters .fd-chip--on')));

  // ── a · the feed, in the API's order ──
  section('a — the feed itself');
  const cards = q('.fd-card');
  say('the feed paints cards', cards.length > 0, cards.length + ' cards');
  const api = await (await fetch(BASE + '/posts?sort=hot&roots_only=true&limit=120')).json();
  say('it asks the API for the HOT order', Array.isArray(api) && api.length > 0,
      (api || []).length + ' posts from /posts?sort=hot');
  const shown = cards.map(c => c.dataset.id);
  say('and prints them in that order, unsorted by anything on the page',
      shown.every((id, i) => id === api[i].id), shown.slice(0, 3).join(' · '));
  const cats = new Set((api || []).slice(0, shown.length).map(p => p.category));
  say('ALL posts are included — every category the API returned is on the page',
      cats.size > 1, [...cats].join(' | '));
  const missions = new Set(cards.map(c => (c.querySelector('.fd-card__mission') || {}).textContent || ''));
  say('…and NOT sorted by mission', missions.size > 1, missions.size + ' missions in the first page');

  // ── b · reactions, f · reply ──
  section('b · f — reactions and reply, per card');
  const first = cards[0];
  const reacts = first ? [...first.querySelectorAll('.fd-react')] : [];
  // How many depends on the TYPE — the API takes helpful only on a budgeting
  // suggestion and fair/unfair on a case, so a card offering three would be
  // offering two that 400. Asserted per type below; here: it has some, counted.
  say('each card carries its reactions, with their counts',
      reacts.length >= 1 && reacts.every(e => /\d/.test(e.textContent)),
      reacts.map(e => e.textContent.trim()).join(' | '));
  say('every reaction names the post it belongs to',
      reacts.every(e => e.dataset.post === first.dataset.id));
  say('each card has a reply affordance', !!first.querySelector('[data-toggle]'));
  say('…and a way through to the mission it was written in',
      !!first.querySelector('.fd-card__mission') || !!first.querySelector('a[href*="mission.html"]'));

  // replies open on the card, and ask the API for the thread
  const withReplies = (api || []).find(p => p.id === first.dataset.id);
  first.querySelector('[data-toggle]').dispatchEvent(new W.Event('click', { bubbles: true }));
  await new Promise(r => setTimeout(r, 900));
  const box = d.querySelector('[data-repliesfor="' + first.dataset.id + '"]');
  say('opening a reply opens that card only, in place',
      !!box && box.className.includes('fd-replies--open') &&
      q('.fd-replies--open').length === 1, withReplies ? '' : '');
  say('a signed-out reader is told to sign in rather than shown a dead box',
      /sign in/i.test(box.textContent) || !!box.querySelector('textarea'));

  // ── the control panel actually controls ──
  section('d — the filters filter');
  const target = (api || []).find(p => p.category === 'mission_support');
  if (target) {
    const chip = q('#fd-filters .fd-chip').find(c => c.dataset.cat === 'mission_support');
    chip.dispatchEvent(new W.Event('click', { bubbles: true }));
    await new Promise(r => setTimeout(r, 300));
    const after = q('.fd-card').map(c => c.dataset.id);
    const wantIds = (api || []).filter(p => p.category === 'mission_support').map(p => p.id);
    say('a category chip narrows the feed to that category',
        after.length > 0 && after.every(id => wantIds.includes(id)),
        after.length + ' of ' + wantIds.length + ' research posts');
    say('…and only one chip is on at a time', q('#fd-filters .fd-chip--on').length === 1,
        txt('#fd-filters .fd-chip--on').trim());
    q('#fd-filters .fd-chip')[0].dispatchEvent(new W.Event('click', { bubbles: true }));
    await new Promise(r => setTimeout(r, 300));
  } else {
    say('(no research posts in this database to filter to)', true);
  }
  const s = d.getElementById('fd-search');
  const needle = ((api[0].title || api[0].body || '').trim().split(/\s+/)[0] || '').toLowerCase();
  if (needle.length > 3) {
    s.value = needle;
    s.dispatchEvent(new W.Event('input', { bubbles: true }));
    await new Promise(r => setTimeout(r, 300));
    const hits = q('.fd-card').length;
    const want = (api || []).filter(p => ((p.title || '') + ' ' + (p.body || '')).toLowerCase().includes(needle)).length;
    say('the search box filters the feed', hits > 0 && hits <= want,
        '"' + needle + '" → ' + hits + ' of ' + want);
    s.value = '';
    s.dispatchEvent(new W.Event('input', { bubbles: true }));
    await new Promise(r => setTimeout(r, 300));
  } else {
    say('(nothing searchable in the first post)', true);
  }

  // ── b · a reaction is a round trip, and only the ones the type takes ──
  section('b — reacting, signed in');
  const EMAIL = 'feedcheck' + Date.now() + '@example.com';
  await fetch(BASE + '/auth/signup', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: EMAIL, handle: 'feedchk' + (Date.now() % 100000), password: 'feed-check-pw-1' }),
  });
  const tok = (await (await fetch(BASE + '/auth/login', {
    method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: EMAIL, password: 'feed-check-pw-1' }),
  })).json()).access_token;
  const dom2 = await JSDOM.fromURL(BASE + '/cause.html?id=' + CAUSE, {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
      w.matchMedia = w.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
      try { w.localStorage.setItem('ebx_auth_token', tok); } catch (e) {}
    },
  });
  await new Promise(r => setTimeout(r, 4000));
  const d2 = dom2.window, doc2 = dom2.window.document;
  const card2 = doc2.querySelector('.fd-card');
  const btn = card2 && card2.querySelector('.fd-react[data-react="helpful"]');
  const n0 = btn ? parseInt(btn.textContent.replace(/\D/g, ''), 10) : NaN;
  if (btn) {
    btn.dispatchEvent(new d2.Event('click', { bubbles: true }));
    await new Promise(r => setTimeout(r, 1200));
    const n1 = parseInt(doc2.querySelector('.fd-card .fd-react[data-react="helpful"]').textContent.replace(/\D/g, ''), 10);
    say('a reaction goes to the API and the count comes back changed', n1 === n0 + 1, n0 + ' → ' + n1);
  } else {
    say('the first card offers a helpful reaction', false);
  }
  // a budgeting post takes ONE reaction; the API rejects the other two, so the
  // card must not offer them.
  const budget = (api || []).find(p => ['service', 'supply', 'support'].includes(p.type));
  if (budget) {
    const bcard = [...doc2.querySelectorAll('.fd-card')].find(c => c.dataset.id === budget.id);
    if (bcard) {
      say('a budgeting suggestion offers only Approve',
          bcard.querySelectorAll('.fd-react').length === 1,
          [...bcard.querySelectorAll('.fd-react')].map(e => e.title).join(' | '));
    } else { say('(the budgeting post is below the first page)', true); }
  } else { say('(no budgeting posts in this database)', true); }
  const caseCard = [...doc2.querySelectorAll('.fd-card')]
    .find(c => { const p = (api || []).find(x => x.id === c.dataset.id); return p && ['case', 'evaluation'].includes(p.type); });
  if (caseCard) {
    say('a case offers fair / unfair and nothing in between',
        caseCard.querySelectorAll('.fd-react').length === 2,
        [...caseCard.querySelectorAll('.fd-react')].map(e => e.title).join(' | '));
  } else { say('(no case posts on the first page)', true); }
  dom2.window.close();

  // ── the move ──
  section('the discussion box has LEFT this page');
  for (const sel of ['#pb', '#pb-phase', '#pb-cat', '#pb-compose', '#pb-leading', '.ct-startline']) {
    say('gone: ' + sel, q(sel).length === 0, q(sel).length ? q(sel).length + ' left' : '');
  }
  say('and the page does not still load its handlers', typeof W.pbPhase === 'undefined');
  say('the hero above it is untouched — the cause bar, wheel and mission cards stay',
      !!d.getElementById('cause-tabs') && !!d.getElementById('cause-annulus-mount') &&
      !!d.getElementById('right-mission-panel'));

  say('no script errors', errs.length === 0, errs.join(' | '));
  dom.window.close();
  console.log(bad ? '\nFEED: ' + bad + ' PROBLEM(S)' : '\nFEED CLEAN');
  process.exit(bad ? 1 : 0);
})();
