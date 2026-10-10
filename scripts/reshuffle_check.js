// reshuffle_check — the 10/9 Reshuffle (2026-10-09), end to end: the API and
// every page it touched, in a real browser.
//
//   node scripts/reshuffle_check.js [http://127.0.0.1:8000]
//
// INSTRUCTIONS › BUILD SEQUENCE › "10/9 - Reshuffle time", item by item:
//   · the nav: Home · Missions · News — Profile is the badge, Inbox an icon
//     beside it carrying the unread count;
//   · Home: the five steps LEFT of the visual, "Feedback" for "Reporting", the
//     doors in Jax's copy, and THE WEEKLY REPORT (GET /inbox/weekly/report) —
//     no hub, no feed;
//   · Missions: the missions hub on top (moved from Home); the report gone to
//     News, with a way there; Framing reads "Prep";
//   · News: the arch and the globe on top; everything, or one mission — its
//     report above its posts;
//   · Profile: the choices hub (your selections), two allocation bars; no arch;
//   · grants: exactly ten granted tokens in EVERY open initiative election
//     (ruling 19) — usable in any of them, not only the nearest;
//   · organization elections: one nominal vote for everyone in every open one;
//     tokens only for those who voted in its initiative election (ruling 20);
//   · the exchange's top movers, ranked by EBX held, with the week's change.
// Signs up throwaway accounts — run it against a local server.
const { chromium } = require('playwright');
const fs = require('fs');
function chromeExe() {
  const cands = [process.env.PW_CHROME, '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    '/opt/pw-browsers/chromium/chrome-linux/chrome'];
  for (const p of cands) { try { if (p && fs.statSync(p).isFile()) return p; } catch (e) {} }
  return undefined;
}
const BASE = process.argv[2] || 'http://127.0.0.1:8000';
let bad = 0, n = 0;
const ok = (c, what, d) => { n++; if (!c) bad++; console.log('  ' + (c ? 'ok  ' : 'FAIL') + '  ' + what + (d ? '  ' + d : '')); };
const section = t => console.log('\n=== ' + t);
const J = async (u, o) => { const r = await fetch(BASE + u, o); let b = null; try { b = await r.json(); } catch (e) {} return { status: r.status, ok: r.ok, body: b }; };
async function account(tag) {
  const h = tag + (Date.now() % 1000000) + Math.floor(Math.random() * 90 + 10);
  const email = h + '@reshuffle-check.example.com';
  await J('/auth/signup', { method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email, handle: h, password: 'reshuffle-pw-1' }) });
  const t = (await J('/auth/login', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password: 'reshuffle-pw-1' }) })).body.access_token;
  const H = { Authorization: 'Bearer ' + t, 'content-type': 'application/json' };
  return { handle: h, token: t, get: u => J(u, { headers: H }),
    put: (u, b) => J(u, { method: 'PUT', headers: H, body: JSON.stringify(b) }),
    post: (u, b) => J(u, { method: 'POST', headers: H, body: JSON.stringify(b || {}) }) };
}

(async () => {
  const tivs = (await J('/initiatives')).body || [];

  // ── grants: ten in every initiative election ───────────────────────────
  section('grants — exactly ten granted tokens in every open initiative election (ruling 19)');
  const a = await account('rsa');
  let w = (await a.get('/wallet')).body;
  const els = (w.grant && w.grant.elections) || [];
  ok(els.length >= 2, 'more than one initiative election is open', els.map(e => e.mission_id).join(' · '));
  ok(els.every(e => e.left_ct === 1000 && e.used_ct === 0), 'each carries ten granted tokens, untouched', els.map(e => e.left_ct / 100).join(','));
  ok(w.grant.left_ct === 1000 * els.length && w.rules.me_grant_ct === 1000, 'the grant is their sum, and the rule says ten', String(w.grant.left_ct / 100));
  ok((w.wallet.purchased_ct || 0) === 0 && (w.wallet.free_ct || 0) === 0, 'no weekly pile in the wallet — the grant is never cash');
  const lastEl = els[els.length - 1];
  const lastTiv = tivs.find(t => t.mission_id === lastEl.mission_id);
  if (lastTiv) {
    const r = await a.put('/missions/' + lastEl.mission_id + '/p1/votes', { mission_id: lastEl.mission_id, shares: { [lastTiv.id]: 1 }, ebx: 10 });
    ok(r.ok, 'the furthest initiative election takes its ten — not only the nearest (the 10/9 bug)', lastEl.mission_id + ' HTTP ' + r.status);
    w = (await a.get('/wallet')).body;
    const e2 = w.grant.elections.find(e => e.mission_id === lastEl.mission_id);
    ok(e2 && e2.used_ct === 1000 && e2.left_ct === 0, '…its ten are used', e2 && (e2.used_ct / 100 + ' used'));
    ok(w.grant.elections.filter(e => e.mission_id !== lastEl.mission_id).every(e => e.left_ct === 1000), '…and every other election still has its own ten');
    ok((w.wallet.purchased_ct || 0) === 0, '…and no purchased token was touched');
    const r2 = await a.put('/missions/' + lastEl.mission_id + '/p1/votes', { mission_id: lastEl.mission_id, shares: { [lastTiv.id]: 1 }, ebx: 25 });
    w = (await a.get('/wallet')).body;
    const e3 = w.grant.elections.find(e => e.mission_id === lastEl.mission_id);
    ok(r2.ok && e3.committed_ct === 1000, 'asking for 25 with no funds of your own commits the ten the grant gives', (e3.committed_ct / 100) + ' committed');
  } else ok(false, 'an initiative to vote for in ' + lastEl.mission_id);

  // ── organization elections: one vote for everyone, tokens for ME voters ──
  section('organization elections — one vote for everyone; tokens only for its initiative election\'s voters (ruling 20)');
  const rows = (w.rows || []).filter(x => x.phase === 'oe' || x.open !== false);
  ok(rows.length >= 1 && rows.every(x => x.can_take_part === true), 'every open organization election takes this account\'s vote', rows.length + ' rows');
  const cands = (await J('/candidacies')).body || [];
  // a race whose organization election is still open (the table also lists
  // stalled races whose date passed with no organization — OPEN DEFECTS F11)
  const race = rows.find(x => cands.some(c => c.mission_id === x.mission_id) && !x.can_commit && new Date(x.vote_date).getTime() > Date.now());
  if (race) {
    const org = cands.find(c => c.mission_id === race.mission_id).org_id;
    let r = await a.put('/wallet/org', { mission_id: race.mission_id, org_id: org });
    ok(r.ok, 'the nominal vote: an organization picked in ' + race.mission_id + ' without having voted in its initiative election', 'HTTP ' + r.status + ' ' + JSON.stringify(r.body).slice(0, 120));
    await a.post('/wallet/add-funds', { usd_cents: 300 });
    r = await a.post('/wallet/commit', { mission_id: race.mission_id, target_ct: 500, org_id: org });
    ok(r.status === 400 && /voted in this mission.s initiative election/.test((r.body || {}).detail || ''),
       'tokens there are refused: only its initiative election\'s voters can commit them', ((r.body || {}).detail || '').slice(0, 110));
    const pos = ((await a.get('/wallet/positions?include=' + race.mission_id)).body || []).find(p => p.mission_id === race.mission_id);
    ok(pos && pos.oe.can_vote === true && pos.oe.can_commit === false, '…and the coin says so: can vote, can\'t commit');
  } else ok(true, '(no open organization race with a candidate to vote in)');

  // ── the weekly report ────────────────────────────────────────────────────
  section('the weekly report — GET /inbox/weekly/report');
  const rep = (await J('/inbox/weekly/report')).body || {};
  ok(/^[A-Z][a-z]+ \d+ – (?:[A-Z][a-z]+ )?\d+: \S/.test(rep.title || ''), 'titled with the week and its cause', rep.title);
  ok((rep.above || []).length === 3 && (rep.below || []).length === 3, 'three updates above the timeline, three below');
  const roles = (rep.above || []).concat(rep.below || []).map(u => u.role).sort().join(',');
  ok(roles === 'budget_day,current_me,entered_prep,left_prep,new,oe_final', 'new · final OE week · budget day · this week\'s ME · entered prep · left prep', roles);
  ok((rep.above || []).every(u => u.missing || (rep.cause && u.cause.id === rep.cause.id)), 'the three above are this week\'s cause');
  const ph = ((rep.timeline || {}).phases || []).map(p => p.label);
  ok(ph.join(' · ') === 'Initiative election · Organization election · Prep · Exchange', 'the timeline runs from the initiative election to a week after budget day', ph.join(' · '));
  const mv = ((rep.exchange || {}).movers || []);
  ok(mv.every((m, i) => !i || mv[i - 1].ebx_held_ct >= m.ebx_held_ct) && mv.every(m => typeof m.change_ct === 'number'),
     'the exchange\'s top movers: ranked by EBX held, each with the week\'s change', mv.map(m => m.label + ' ' + m.ebx_held_ct / 100).join(' · '));
  ok(rep.cause_elections && Array.isArray(rep.cause_elections.secured) && Array.isArray(rep.cause_elections.won), 'the cause elections: won, secured');

  // ── the pages ────────────────────────────────────────────────────────────
  const browser = await chromium.launch({ executablePath: chromeExe() });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const errors = [];
  page.on('pageerror', e => errors.push(page.url().replace(BASE, '') + ': ' + String(e.message).slice(0, 160)));
  await page.addInitScript(t => localStorage.setItem('ebx_auth_token', t), a.token);
  const go = async (path, sel) => { await page.goto(BASE + path, { waitUntil: 'networkidle' }); if (sel) await page.waitForSelector(sel, { timeout: 20000 }); await page.waitForTimeout(600); };
  const T = async sel => ((await page.textContent(sel)) || '').replace(/\s+/g, ' ').trim();

  section('the nav — three tabs; Profile is the badge, Inbox an icon beside it');
  for (const p of ['/index.html', '/mission.html', '/cause.html', '/profile.html']) {
    await go(p, '.ebx-nav');
    const tabs = await page.$$eval('.ebx-nav__tab', e => e.map(x => x.textContent.trim()));
    const ic = await page.$('.ebx-badge-row .ebx-inbox-ic[href="inbox.html"] [data-ebx-inbox-badge]');
    ok(tabs.join(' · ') === 'Home · Missions · News' && !!ic, p + ': Home · Missions · News, and the inbox icon carries the count', tabs.join(' · '));
  }

  section('Home — the steps left of the visual, the doors, the weekly report');
  await go('/index.html', '#wr-above .wu');
  ok(await page.evaluate(() => { const f = document.getElementById('ld-flow').getBoundingClientRect(), v = document.getElementById('ebx-steps').getBoundingClientRect(); return f.right <= v.left + 1; }),
     'the five steps stand LEFT of the visual');
  ok((await T('#ld-flow [data-flow="4"]')) === '5. Feedback', '"Feedback" replaces "Reporting"');
  ok(/We give everyone \$1 to vote with in every initiative election/.test(await T('#hk')) && /week by week/.test(await T('#hk')), 'the doors, in Jax\'s copy');
  ok((await T('#wr-title')) === rep.title && (await page.$$('#wr-above .wu, #wr-below .wu')).length === 6, 'the weekly report, three and three');
  ok(await page.$('#mh, #hf-list, .hn') === null, 'no hub and no feed on Home');

  section('Missions — the hub on top, the report gone to News, "Prep"');
  await go('/mission.html', '#mx-hub .mw');
  ok(await page.evaluate(() => { const h = document.getElementById('mx-hub'), t = document.getElementById('cause-tabs'); return !!(h.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING); }),
     'the missions hub sits at the top of the page');
  ok(/This Week.s Decisions/.test(await T('#mx-hub .mh__title')) && (await page.$$('#mx-hub .mw')).length === 2, 'this week\'s two elections, with their leaders');
  ok(await page.$('#mb-report, #mxt-bg') === null && await page.$('#mb-news') !== null, 'no report on the mission page — a way to it in News');
  await go('/mission.html?state=fr&cause=forests', '#mx-phases');
  const phs = await page.$$eval('#mx-phases .mx-phase', e => e.map(x => x.textContent.replace(/\s+/g, ' ').trim()).join(' | '));
  ok(/Prep/.test(phs) && !/Fram/.test(phs), 'the phase toggle says Prep, not Framing', phs.slice(0, 160));
  ok(!/Framing|Frame Mission/.test(await page.evaluate(() => document.body.innerText)), 'and nothing on the page says Framing');

  section('News — the arch on top; everything, or one mission with its report');
  await go('/cause.html', '#nw-arch .ar-sec');
  ok(await page.$('#nw-arch .ar-arch') !== null && await page.$('#nw-arch [data-ar="globe"] .ar-land') !== null, 'the 3/7 annulus and the globe, at the top');
  ok((await page.$('#fd-mission[hidden]')) !== null && (await page.$('#mr[hidden]')) !== null, 'it opens on everything');
  const sec = await page.$('.ar-sec[data-rel="0"][data-m]');
  const sid = sec && await sec.getAttribute('data-m');
  if (sid) {
    await sec.click(); await page.waitForTimeout(1800);
    ok(new URL(page.url()).searchParams.get('mission') === sid && !(await page.$eval('#fd-mission', e => e.hidden)), 'a sector toggles the feed to its mission', sid);
    ok(await page.$('#mr .mb-report__title') !== null && await page.evaluate(() => !!(document.getElementById('mr').compareDocumentPosition(document.getElementById('fd-list')) & Node.DOCUMENT_POSITION_FOLLOWING)),
       '…its report above its posts');
    await page.click('#fd-mission [data-mclear]'); await page.waitForTimeout(1000);
    ok(await page.$eval('#mr', e => e.hidden) && !new URL(page.url()).searchParams.get('mission'), '"Show everything" turns it off');
  } else ok(false, 'a sector with a mission to toggle');

  section('Profile — the choices hub and two allocation bars; no arch');
  await go('/profile.html', '#pf-wallet');
  await page.waitForSelector('#pf-hub .mh__title', { timeout: 15000 }); await page.waitForTimeout(800);
  ok(await page.$('.ar-arch, #pf-arch, [data-ar="globe"]') === null, 'no globe, no annulus, no mission toggle');
  ok((await page.$$('#pf-wallet .pf-track')).length === 2 && /^Uncommitted/.test(await T('#pf-al-unc')) && /^Committed/.test(await T('#pf-al-com')),
     'two allocation bars: Uncommitted and Committed');
  ok(/^Your choices/.test(await T('#pf-hub .mh__title')) && await page.$('#pf-hub.mh--mine') !== null, 'the choices hub: the missions hub, with your selections');
  ok(await page.$('#pf-stats .pf-stat') !== null && await page.$('#pf-posts') !== null, 'stats and your posts');

  section('no script errors');
  ok(errors.length === 0, 'none', errors.slice(0, 3).join(' || '));
  await browser.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'RESHUFFLE CLEAN'));
  process.exit(bad ? 1 : 0);
})();
