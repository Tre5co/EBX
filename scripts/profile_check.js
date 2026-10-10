// profile_check — the profile page, driven in a real browser.
//
//   node scripts/profile_check.js [http://127.0.0.1:8000]
//
// REWRITTEN 2026-10-09 for the 10/9 Reshuffle (INSTRUCTIONS › BUILD SEQUENCE ›
// 10/9 - Reshuffle time): "Profile doesn't need the globe and mission toggle,
// just wallet, allocations, stats, choices-hub, and personal posts" · "There
// should be 2 main allocations bars - committed and uncommitted" · the missions
// hub on the profile "will show the selections of the user". The arch and the
// globe went to News (news: scripts/feed_check.js). Pinned here: you · the
// wallet's two bars on one scale (Uncommitted = granted + purchased, Committed
// = ME · OE · Prep) · the grant as ten tokens in EVERY open initiative election
// (ruling 19) · Add funds · the stats · the choices hub · your posts · phone width.
//
// (2026-10-07 header, kept for history:) the arch (top 3/7 of the annulus, one
// mission per sector, three layers = ME · OE · budget day), the globe, You |
// Wallet beside it, a panel per arch mission, the activity feed — and the
// wallet itself: the grant as its own entity, Add funds, the committed split.
const { chromium } = require('playwright');
const fs = require('fs');
function chromeExe() {
  const cands = [process.env.PW_CHROME,
    '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    '/opt/pw-browsers/chromium/chrome-linux/chrome',
    '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'];
  for (const p of cands) { try { if (p && fs.statSync(p).isFile()) return p; } catch (e) {} }
  return undefined;
}
const BASE = process.argv[2] || 'http://127.0.0.1:8000';
const EMAIL = `pf-check-${Date.now()}@pf-check.example.com`;
let bad = 0, n = 0;
function ok(cond, what, detail) {
  n++; if (!cond) bad++;
  console.log('  ' + (cond ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : ''));
}
const section = t => console.log('\n=== ' + t);

(async () => {
  const browser = await chromium.launch({ executablePath: chromeExe() });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message)));

  // A real account, so the page runs its signed-in path.
  const handle = 'pfchk' + (Date.now() % 100000);
  let r = await page.request.post(BASE + '/auth/signup',
    { data: { email: EMAIL, password: 'pw12345678', handle } });
  ok(r.ok(), 'a fresh benefactor account', 'HTTP ' + r.status());
  r = await page.request.post(BASE + '/auth/login',
    { form: { username: EMAIL, password: 'pw12345678' } });
  const token = (await r.json()).access_token;
  ok(!!token, 'and a session for it');

  // a vote in this week's first open initiative election, so the bars have
  // something on both sides: its ten granted tokens move to Committed
  const W0 = await (await page.request.get(BASE + '/wallet', { headers: { Authorization: 'Bearer ' + token } })).json();
  const els = (W0.grant && W0.grant.elections) || [];
  ok(els.length >= 1 && els.every(e => e.left_ct === 1000), 'the grant: ten tokens in every open initiative election (ruling 19)',
     els.length + ' open · ' + els.map(e => e.left_ct / 100).join(','));
  const tivs = await (await page.request.get(BASE + '/initiatives')).json();
  const first = els[0] && tivs.find(t => t.mission_id === els[0].mission_id);
  if (first) {
    r = await page.request.put(BASE + '/missions/' + els[0].mission_id + '/p1/votes',
      { headers: { Authorization: 'Bearer ' + token }, data: { mission_id: els[0].mission_id, shares: { [first.id]: 1 }, ebx: 10 } });
    ok(r.ok(), 'a vote in ' + els[0].mission_id + '\'s initiative election', 'HTTP ' + r.status());
  }

  await page.goto(BASE + '/profile.html');
  await page.evaluate(t => localStorage.setItem('ebx_auth_token', t), token);
  await page.goto(BASE + '/profile.html');
  await page.waitForSelector('#pf-wallet', { timeout: 15000 });
  await page.waitForTimeout(1500);
  const T = async sel => ((await page.textContent(sel)) || '').replace(/\s+/g, ' ').trim();

  section('the arch and the globe are News\' now');
  ok(await page.$('#pf-arch, .ar-arch, #pf-globe, .pf-weeknav, #pf-missions') === null, 'no arch, no globe, no week navigator, no mission panels');
  ok(await page.$('.ebx-nav__tab[href="profile.html"], .ebx-nav__tab[href="inbox.html"]') === null && await page.$('.ebx-badge-row .ebx-inbox-ic') !== null,
     'Profile and Inbox are not tabs: the badge and the inbox icon beside it');

  section('you');
  ok((await T('.pf-me__h')) === '@' + handle, 'the handle', await T('.pf-me__h'));
  await page.click('.pf-set summary');
  const set = await T('.pf-set__menu');
  ok(/Organization login/.test(set) && /Sign out/.test(set) && /Inbox/.test(set), 'settings: inbox, organization login, sign out', set.slice(0, 120));
  await page.keyboard.press('Escape');

  section('the wallet — two allocation bars');
  const unc = await T('#pf-al-unc'), com = await T('#pf-al-com');
  ok(/^Uncommitted/.test(unc) && /^Committed/.test(com), 'Uncommitted, then Committed');
  const grantLeft = (els.length - (first ? 1 : 0)) * 10;
  ok(new RegExp('Granted\\s*' + grantLeft + ' tk').test(unc), 'Granted: ten in each open initiative election, less the one used', 'expected ' + grantLeft + ' · ' + unc.slice(0, 120));
  ok(/each of the .*open initiative election/.test(unc), '…and it says so');
  ok(/Purchased\s*0 tk/.test(unc), 'Purchased: nothing yet');
  ok(!first || /Initiative elections\s*10 tk/.test(com), 'Committed: the ten granted tokens in the initiative election', com.slice(0, 160));
  ok(/Organization elections/.test(com) && /Prep/.test(com) && !/Framing/.test(com), '…by phase: initiative elections · organization elections · prep');
  const widths = await page.$$eval('.pf-fill', e => e.map(x => x.getBoundingClientRect().width));
  const tracks = await page.$$eval('.pf-track', e => e.map(x => x.getBoundingClientRect().width));
  ok(widths.length === 2 && Math.abs(Math.max(...widths) - tracks[0]) <= 2 && (!first || Math.abs(widths[1] / widths[0] - 10 / grantLeft) < 0.05),
     'one scale: the longer bar fills its track, the other is in proportion', widths.map(Math.round).join(' / ') + ' of ' + Math.round(tracks[0]));

  section('add funds');
  await page.click('#pf-wallet .pf-h [data-addfunds]');
  await page.waitForSelector('#ebw-bg');
  await page.click('#ebw-bg [data-c="500"]');
  await page.click('#ebw-bg [data-go]');
  await page.waitForTimeout(1800);
  ok(/Purchased\s*50 tk/.test(await T('#pf-al-unc')), '$5 lands as 50 purchased tokens, uncommitted', (await T('#pf-al-unc')).slice(0, 160));
  ok(await page.$('#pf-al-unc [data-withdraw]') !== null, '…and can be withdrawn');

  section('your numbers, your choices, your posts');
  ok(await page.$$eval('#pf-stats .pf-stat', e => e.length === 8), 'eight stats tiles');
  ok((await T('#pf-stats')).includes('Elections voted'), '…elections voted among them');
  await page.waitForSelector('#pf-hub .mh__title', { timeout: 10000 });
  ok(await page.$('#pf-hub.mh--mine') !== null && /^Your choices/.test(await T('#pf-hub .mh__title')), 'the choices hub: the missions hub, reading YOUR selections', await T('#pf-hub .mh__title'));
  if (first) {
    await page.waitForTimeout(800);
    const you = await page.$$eval('#pf-hub .mw__you, #pf-hub .mc--you', e => e.map(x => x.textContent.replace(/\s+/g, ' ').trim()));
    const mine = tivs.find(t => t.id === first.id);
    await page.click('#pf-hub [data-hub="toggle"]'); await page.waitForTimeout(500);
    const all = await T('#pf-hub [data-hub="body"]');
    ok(all.includes('You: ' + mine.title), 'your initiative vote is on its card', mine.title);
    ok(await page.$$eval('#pf-hub .mc--notyou', e => e.length > 0), '…and the missions you have not touched are dimmed');
  }
  ok(await page.$('#pf-posts .pf-btn--honey') !== null && /\+ New post/.test(await T('#pf-posts .pf-h')), 'your posts, with + New post');

  section('phone width');
  await page.setViewportSize({ width: 390, height: 860 });
  await page.waitForTimeout(800);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  ok(overflow <= 1, 'no sideways scroll at 390px', overflow + 'px');

  ok(errors.length === 0, 'no page errors', errors.join(' | ').slice(0, 200));
  console.log('\n' + n + ' assertions · ' + (bad ? bad + ' FAILED' : 'PROFILE CLEAN'));
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
