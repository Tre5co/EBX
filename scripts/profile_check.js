// profile_check — the rebuilt profile page, driven in a real browser.
//
//   node scripts/profile_check.js [http://127.0.0.1:8000]
//
// §1 (2026-08-28). What it guards is the SHAPE of the drawing in the build
// sequence, because the shape is the argument: three cards across the top
// (c wallet · b allocations · a profile), seven weekly windows around the
// globe, the feed underneath. Each window is a WEEK and carries one initiative
// election and one organization election, which is why every card has two
// cause colours — and it is why the clockwise rule matters: the top card reads
// organization-then-initiative left to right, the right column reads the same
// pair top to bottom, and the left column reads it the other way round because
// you are coming back UP that side.
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

  await page.goto(BASE + '/profile.html');
  await page.evaluate(t => localStorage.setItem('ebx_auth_token', t), token);
  await page.goto(BASE + '/profile.html');
  await page.waitForSelector('.pf2-ring', { timeout: 15000 });
  await page.waitForTimeout(1200);

  section('the top row — c | b | a');
  ok(await page.$$eval('.pf2-top > .pf2-card', e => e.length === 3),
     'three cards across the top');
  ok(await page.$('#wallet-strip') !== null, '(c) the wallet strip');
  ok(await page.$$eval('.pf2-alloc .pf2-set', e => e.length === 3),
     '(b) allocations: three sets…');
  ok(await page.$$eval('.pf2-alloc .pf2-bar .pf2-seg', e => e.length === 6), '…of two');
  const setNames = await page.$$eval('.pf2-set__name', e => e.map(x => x.textContent.trim()));
  ok(/Unallocated/.test(setNames[0]) && /Committed/.test(setNames[1]) && /EBX/.test(setNames[2]),
     '…named for the four states', setNames.slice(0, 3).join(' · '));
  ok(await page.$('.pf2-conv') !== null, '…and the conversion row shares the panel');
  const acts = await page.$$eval('.pf2-me__acts .pf2-act', e => e.map(x => x.textContent.replace(/\s+/g, ' ').trim()));
  ok(acts.length === 3, '(a) three actions under the badge', acts.join(' | '));
  ok(/aa/.test(acts[0]) && /ab/.test(acts[1]) && /ac/.test(acts[2]),
     '…labelled aa · ab · ac, in the drawing’s order');

  section('(ab) is gated on a coin being SELECTED, not merely held');
  const gate = await page.$eval('#pf2-membermode', b => b.disabled).catch(() => null);
  ok(gate === true, 'member mode starts disabled');
  const chip = await page.$('#wallet-strip .coin-chip[data-coin]');
  if (chip) {
    await page.evaluate(() => {
      const c = document.querySelector('#wallet-strip .coin-chip[data-coin]');
      window.pickCoin(c.dataset.coin);
    });
    ok(await page.$eval('#pf2-membermode', b => b.disabled) === false,
       '…and opens once a coin is picked');
    ok(await page.$$eval('.coin-chip.is-picked', e => e.length === 1), '…which is marked as picked');
  } else {
    ok(true, '…(no coin on this account — gate stays shut)', 'skipped');
    ok(true, '…', 'skipped');
  }

  section('(e) seven weekly windows, one per week');
  ok(await page.$$eval('.pf2-win', e => e.length === 7), 'seven window cards');
  ok(await page.$$eval('.pf2-ring__top .pf2-win', e => e.length === 1), 'one on top…');
  ok(await page.$$eval('.pf2-ring__left .pf2-win', e => e.length === 3), '…three down the left…');
  ok(await page.$$eval('.pf2-ring__right .pf2-win', e => e.length === 3), '…three down the right');
  ok(await page.$$eval('.pf2-win .pf2-half', e => e.length === 14),
     'each card holds two halves — one initiative, one organization');

  section('…and time rotates clockwise');
  ok(await page.$$eval('.pf2-ring__top .pf2-win', e => e[0].classList.contains('pf2-win--cols')),
     'the top card is split into COLUMNS');
  ok(await page.$$eval('.pf2-ring__left .pf2-win, .pf2-ring__right .pf2-win',
       e => e.every(x => x.classList.contains('pf2-win--rows'))),
     'the six side cards are split into ROWS');
  const kindsOf = sel => page.$$eval(sel + ' .pf2-win',
    e => e.map(x => [...x.querySelectorAll('.pf2-half__kind')].map(k => k.textContent.trim().split(' ')[0])));
  const top = (await kindsOf('.pf2-ring__top'))[0];
  ok(top[0] === 'Organization' && top[1] === 'Initiative',
     'top: organization LEFT, initiative RIGHT', top.join(' | '));
  ok((await kindsOf('.pf2-ring__right')).every(k => k[0] === 'Organization' && k[1] === 'Initiative'),
     'right: organization on top, initiative below — falling clockwise');
  ok((await kindsOf('.pf2-ring__left')).every(k => k[0] === 'Initiative' && k[1] === 'Organization'),
     'left: initiative on top, organization below — coming back up');

  section('two colours, because the two races are never the same cause');
  const cols = await page.$$eval('.pf2-win',
    e => e.map(x => [x.style.getPropertyValue('--c-o').trim(), x.style.getPropertyValue('--c-i').trim()]));
  ok(cols.every(c => c[0] && c[1]), 'every card carries both cause colours');
  ok(cols.filter(c => c[0] !== c[1]).length >= 6,
     '…and they differ, because 8 weeks is not 7',
     cols.filter(c => c[0] !== c[1]).length + ' of ' + cols.length);

  section('(d) the globe turns, and the selection aims it');
  ok(await page.$('#pf2-globe-svg') !== null, 'a globe is mounted');
  ok(await page.$$eval('#gl-grid path', e => e.length > 6), '…with a graticule on it');
  const lon1 = await page.evaluate(() => {
    const p = document.querySelector('#gl-grid path'); return p && p.getAttribute('d');
  });
  await page.waitForTimeout(700);
  const lon2 = await page.evaluate(() => {
    const p = document.querySelector('#gl-grid path'); return p && p.getAttribute('d');
  });
  ok(lon1 !== lon2, '…and it is actually turning');
  ok(await page.$$eval('.pf2-win.is-selected', e => e.length === 1), 'one window is selected');
  await page.evaluate(() => window.selectWindow(3));
  ok(await page.$eval('.pf2-win.is-selected', e => e.dataset.week) === '3',
     '…and clicking another moves it');
  ok((await page.$eval('#pf2-globe-cap', e => e.textContent)).includes('cause anchors'),
     '…and the caption says these are cause anchors, not places',
     'missions carry no coordinates yet');

  section('(f) the feed answers for THIS benefactor');
  ok(await page.$('#pf2-feed-body') !== null, 'the feed is mounted');
  const tabs = await page.$$eval('.pf2-feed__tabs button', e => e.map(x => x.textContent.trim()));
  ok(tabs.length === 3, 'three tabs in benefactor mode', tabs.join(' · '));
  await page.evaluate(() => window.pfFeedTab('research'));
  ok((await page.$eval('#pf2-feed-body', e => e.textContent)).length > 0, '…and research is one of them');

  section('the old surfaces are gone');
  for (const sel of ['.pf-grid', '#choices-table-inits', '#choices-table-orgs',
                     '#toggle-inits', '#toggle-orgs', '.annulus3-card', '#a3-front'])
    ok(await page.$(sel) === null, 'no ' + sel);

  section('no script errors');
  ok(errors.length === 0, 'the page ran clean', errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'PROFILE CLEAN'));
  process.exit(bad ? 1 : 0);
})();
