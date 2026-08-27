// ce_check — the Cause Election tab, driven in a real browser.
//
//   node scripts/ce_check.js [http://127.0.0.1:8000]
//
// §1 (2026-08-21, build-seq §1 "CE Work"). What it guards is the shape of the
// decision, which is the part the old card got wrong: thirteen dated windows,
// six of them already confirmed by the existence of an election card, one open
// to a vote this week, and a ballot above the table rather than a ballot
// crammed into a corner of a card that also had to report the rotation.
const { chromium } = require('playwright');

const BASE = process.argv[2] || 'http://127.0.0.1:8000';
const EMAIL = `ce-check-${Date.now()}@ce-check.example.com`;
let bad = 0, n = 0;

function ok(cond, what, detail) {
  n++;
  if (!cond) bad++;
  console.log('  ' + (cond ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : ''));
}
const section = t => console.log('\n=== ' + t);

(async () => {
  let r = await fetch(BASE + '/auth/signup', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: EMAIL, handle: 'cecheck' + (Date.now() % 100000),
                           password: 'ce-check-pw-123' }),
  });
  if (!r.ok) { console.log('FAIL  could not sign up: ' + (await r.text()).slice(0, 200)); process.exit(1); }
  r = await fetch(BASE + '/auth/login', {
    method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: EMAIL, password: 'ce-check-pw-123' }),
  });
  const token = (await r.json()).access_token;

  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1100 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message).slice(0, 200)));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.googleapis|gstatic|favicon|TUNNEL/i.test(m.text()))
    errors.push('console: ' + m.text().slice(0, 160)); });
  const httpErrors = [];
  page.on('response', res => { if (res.status() >= 400 && !/fonts\.googleapis|gstatic/.test(res.url()))
    httpErrors.push(res.status() + ' ' + res.request().method() + ' ' + new URL(res.url()).pathname); });

  await page.addInitScript(t => localStorage.setItem('ebx_auth_token', t), token);

  section('the cause election is a PANEL above the election panel');
  // §1 (2026-08-27): "Replace the cause election as an area on top of the
  // election panel. It can persist across ME/OE." The ME right-hand card that
  // carried it is deleted, and with it the seven window toggles that used to
  // run across the top of it — "the cause toggle in the CE is no longer
  // necessary; it is toggled by the main page cause toggle".
  await page.goto(BASE + '/main.html', { waitUntil: 'networkidle' });
  await page.waitForSelector('#ce-panel-mount .ce-panel', { timeout: 15000 });
  await page.waitForTimeout(1500);
  ok(!(await page.$('.cause-election')), 'the cause-election CARD is gone from the hero');
  ok(!(await page.$('.ce-tabs--abbr')), '…and so are its seven window toggles');
  ok(!(await page.$('.ce-panel .cause-tab')), 'the panel carries no cause toggle of its own');
  // §1 (2026-08-27b): "Cause election box should be below the table." It spent
  // a day above the election panel; the two elections a benefactor votes in
  // this week come first, and the one that decides a cause seven weeks out
  // comes after them.
  ok(await page.evaluate(() => {
       const ce = document.querySelector('#ce-panel-mount');
       const tbl = document.querySelector('.init-table-wrap');
       const vb = document.querySelector('#votebar-mount');
       return !!(ce && tbl && vb) &&
         (tbl.compareDocumentPosition(ce) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0 &&
         (vb.compareDocumentPosition(ce) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0;
     }), 'it sits BELOW the table, after the election panel');
  ok((await page.$$('.ce-weeks .ce-week')).length === 7,
     'the streak is ONE column of seven lines');
  ok(!(await page.$('.cs-bars .cs-col')), '…and the seven-column staircase is gone');
  ok(await page.$eval('.ce-panel__b .rf-btn', e => /Show Cause Table/i.test(e.textContent)),
     'Show Cause Table is the way to the table');
  const ceBtns = await page.$$eval('.ce-panel .ce-row--acts .vb-btn',
    els => els.map(e => ({ t: e.textContent.replace(/\s+/g, ' ').trim(), off: e.disabled })));
  ok(ceBtns.length === 2 && /Commit/.test(ceBtns[0].t) && /Cancel/.test(ceBtns[1].t),
     'Commit and Cancel are both on it', ceBtns.map(b => b.t).join(' | '));
  ok(ceBtns.every(b => b.off), '…and both are dead until something is dialled');
  // It persists across the page states — that is the point of moving it here.
  const slotME = await page.$eval('.ce-panel', e => e.dataset.slot);
  await page.click('#st-oe');
  await page.waitForTimeout(1400);
  ok(!!(await page.$('#ce-panel-mount .ce-panel')), 'it is still there in the OE state');
  await page.click('#st-me');
  await page.waitForTimeout(1200);

  section('the page cause toggle chooses the window');
  // Every cause holds exactly one OPEN window — the active cause's is slot 7,
  // everybody else's is 8..13 — so the seven tabs and the seven replaceable
  // windows are the same seven things.
  const tabNames = await page.$$eval('.hero__causetabs .cause-tab',
    els => els.map(e => e.querySelector('.cause-tab__name')?.textContent.trim()));
  ok(tabNames.length === 7, 'seven cause tabs', tabNames.join(' · '));
  const seen = [];
  for (let i = 0; i < 7; i++) {
    await page.click('.hero__causetabs .cause-tab:nth-child(' + (i + 1) + ')');
    await page.waitForTimeout(700);
    const p = await page.$eval('.ce-panel', e => ({
      slot: Number(e.dataset.slot),
      cause: e.dataset.cause,
      sub: e.querySelector('.ce-panel__sub')?.textContent.replace(/\s+/g, ' ').trim() || '',
    }));
    seen.push(p);
    ok(p.sub.indexOf(tabNames[i]) >= 0,
       'tab ' + tabNames[i] + ' points the panel at its own window', p.sub.slice(0, 80));
  }
  const slots = seen.map(x => x.slot).sort((a, b) => a - b);
  ok(JSON.stringify(slots) === JSON.stringify([7, 8, 9, 10, 11, 12, 13]),
     'the seven tabs are the seven OPEN windows, 7 through 13', slots.join(','));
  const runDays = seen.map(x => new Date((x.sub.match(/runs (.+)$/) || [])[1] || '').getTime());
  ok(runDays.every(d => !isNaN(d)), 'each window prints the date it runs');
  ok(Math.min(...runDays) - Date.now() >= 35 * 864e5,
     '…and the nearest is at least six weeks out, because six windows are confirmed',
     Math.round((Math.min(...runDays) - Date.now()) / 864e5) + ' days');
  // The page opens on the cause whose election decides NEXT (the upcoming one
  // in ME, the active one in OE), and the panel follows that, not a default of
  // its own. Slot 7 — the active cause's own next appearance — is what the OE
  // state opens on.
  ok(Number(slotME) >= 7 && Number(slotME) <= 13,
     'the panel opens on the window of the cause the page opens on', slotME);
  // A fresh load of the OE state opens on the ACTIVE cause, whose window is
  // slot 7 — the nearest one still open. (The tab loop above left a selection
  // behind, and a selection deliberately survives the ME/OE switch.)
  await page.goto(BASE + '/main.html?state=oe', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2200);
  ok(await page.$eval('.ce-panel', e => e.dataset.slot) === '7',
     '…and a fresh OE load opens on slot 7, the nearest open window',
     await page.$eval('.ce-panel', e => e.dataset.slot));
  await page.goto(BASE + '/main.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  section('"Show Cause Table" toggles the TABLE and leaves the cards alone');
  const cardsBefore = await page.$$eval('.race-face', els => els.length);
  const meToggleBefore = await page.$eval('#st-me', e => e.classList.contains('on'));
  await page.click('.ce-panel__b .rf-btn');
  await page.waitForTimeout(1400);
  ok(await page.$$eval('.race-face', els => els.length) === cardsBefore,
     'the election cards are untouched', cardsBefore + ' cards');
  ok(await page.$eval('#st-me', e => e.classList.contains('on')) === meToggleBefore,
     '…and the ME/OE marker has not moved');
  ok(await page.$eval('#init-table-head', h => /Election date/.test(h.textContent)),
     'the table head is the cause table');
  // §2 (2026-08-21): the allocations panel is under the annulus now and
  // persists in every state, so it is present here rather than absent.
  ok(!!(await page.$('.alloc-section #alloc-mount .unalloc')),
     'the allocations panel is still on screen in this tab — parked at the bottom');
  ok(!!(await page.$('#ce-panel-mount .ce-panel')),
     '…and so is the CE panel, which is the point of it being a panel');

  section('thirteen windows: six confirmed, seven still open');
  const rows = await page.$$eval('#init-table-body tr.init-table__row',
    trs => trs.map(tr => ({
      slot: Number(tr.dataset.slot),
      name: tr.querySelector('.init-table__name span')?.textContent.trim(),
      tag: tr.querySelector('.cw-tag')?.textContent.trim(),
      date: tr.querySelector('.init-table__date')?.childNodes[0]?.textContent.trim(),
      open: tr.classList.contains('row-active-race'),
      cells: tr.children.length,
    })));
  ok(rows.length === 13, 'THIRTEEN rows', rows.length + ' rows');
  ok(rows.every(r => r.cells === 5), 'five columns, like the OE table');
  ok(rows.filter(r => r.tag === 'confirmed').length === 6,
     'six are confirmed — the six initiative elections that have cards',
     rows.filter(r => r.tag === 'confirmed').map(r => r.name).join(', '));
  ok(rows.slice(0, 6).every(r => r.tag === 'confirmed'),
     '…and they are the first six, because the queue is in date order');
  ok(rows.filter(r => r.tag !== 'confirmed').length === 7,
     'seven are not confirmed yet');
  ok(rows.filter(r => r.tag === 'open').length === 7,
     '…and all seven of them are OPEN — "all 7 ballots should be votable at once"',
     rows.filter(r => r.tag === 'open').map(r => r.name).join(', '));
  ok(!rows.some(r => /not yet open|horizon/i.test(r.tag || '')),
     'nothing says "not yet open" any more — the seven-slot ceiling is gone');
  ok(rows.filter(r => r.open).length === 1,
     'exactly one row is tinted: the NEAREST open window',
     rows.filter(r => r.open).map(r => r.name).join(', '));
  ok(rows[6] && rows[6].open, '…and it is the seventh', 
     rows[6] ? rows[6].name + ' · ' + rows[6].date : '');
  const days = rows.map(r => new Date(r.date).getTime());
  ok(days.every((d, i) => i === 0 || d > days[i - 1]),
     'each window runs a week after the one above it');
  ok(days.every(d => !isNaN(d)), 'every row carries a real date');
  ok(await page.$eval('.init-table-scroll', el => getComputedStyle(el).overflowY !== 'auto'),
     'no scrollbar — the table is sized to its rows');
  ok(await page.$eval('.init-toolbar--below', el => getComputedStyle(el).display === 'none'),
     'no search box and no Show all Initiatives button');

  section('a row does not expand; it points the TOGGLE');
  const before = await page.$$eval('#init-table-body tr', trs => trs.length);
  const row3cause = await page.$eval('tr[data-slot="3"] .init-table__name',
    e => e.textContent.replace(/\s+/g, ' ').trim());
  await page.click('tr[data-slot="3"] .init-table__name');
  await page.waitForTimeout(1100);
  ok((await page.$$('#init-table-body .init-detail-row')).length === 0,
     'clicking a window opens no detail panel');
  ok(await page.$$eval('#init-table-body tr', trs => trs.length) === before,
     'the table still has exactly the rows it had', String(before));
  // §1 (2026-08-27): a CONFIRMED window cannot be voted in at all, so the row
  // no longer points a locked ballot at it — it selects the cause that holds
  // it, and the panel shows that cause's own OPEN window.
  const after3 = await page.$eval('.ce-panel', e => ({ slot: Number(e.dataset.slot), c: e.dataset.cause }));
  ok(after3.slot >= 7, 'the panel lands on an OPEN window, never a confirmed one', String(after3.slot));
  ok(!(await page.$('.ce-locked')), '…so there is nothing locked to explain');
  ok(await page.$eval('.hero__causetabs .cause-tab.selected .cause-tab__name',
                      e => e.textContent.trim().length > 0),
     'and the cause toggle moved with it', row3cause.slice(0, 40));

  section('an open window takes a vote — and only from a NOMINATED cause');
  // §1 (2026-08-21): "A cause can not be replaced by a preexisting cause, only
  // by a new, user generated cause." The ballot used to list the six other
  // ACTIVE causes as challengers, which could only ever reorder the rotation.
  await page.click('tr[data-slot="13"] .init-table__name');
  await page.waitForTimeout(1200);
  ok(!(await page.$('.ce-locked')),
     'the FURTHEST window is open too, not just the nearest');
  const votes13 = await page.$$eval('.ce-panel .ce-row--votes .ce-vote',
    els => els.map(e => ({ t: e.textContent.replace(/\s+/g, ' ').trim(), off: e.disabled })));
  ok(votes13.length === 2, 'the ballot is keep-or-swap: two buttons', votes13.map(v => v.t).join(' | '));
  ok(/^Keep|Oceans|Land|Forests|Wildlife|Human|Atmosphere/.test(votes13[0].t),
     'the first is the incumbent', votes13[0].t);
  ok(!votes13[0].off, '…and it is live, because keeping is always a vote you can cast');
  const actives = ['Atmosphere', 'Oceans', 'Land', 'Forests', 'Wildlife', 'Human Rights', 'Human Progress'];
  ok(!actives.some(a => votes13[1].t.startsWith(a)),
     'the challenger slot never offers one of the seven active causes', votes13[1].t);
  // §1 (2026-08-21): a click-through pager, not a flat list.
  ok(!(await page.$('.ce-choices')), 'the all-at-once list of alternatives is gone');
  ok(!!(await page.$('.ce-panel .ce-row--sugg .ce-sugg')), '…replaced by a click-through pager');
  ok(!!(await page.$('.ce-panel .ce-row--acts .rf-btn')), 'the proposal row is here');
  ok(!(await page.$('#ce-suggest')),
     '…and it is no longer a name box wedged into a row');
  ok(await page.$eval('.ce-panel .ce-row--acts .rf-btn',
                      e => /Nominate a Cause/i.test(e.textContent)),
     '…it opens a dialog, like proposing an initiative',
     await page.$eval('.ce-panel .ce-row--acts .rf-btn', e => e.textContent.trim()));
  // §0 (2026-08-21): `--rf` is declared on `.race-face`, so an `.rf-btn` in this
  // dialog painted #0f1a14 text on no background. Same fault as the OE Commit.
  const ink = await page.$eval('.ce-panel .ce-row--acts .rf-btn', el => {
    const s = getComputedStyle(el); return { c: s.color, b: s.backgroundColor };
  });
  const lum = c => { const m = (c.match(/[\d.]+/g) || [0, 0, 0]).map(Number);
    return (0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]) / 255; };
  ok(Math.max(lum(ink.c), lum(ink.b)) > 0.25, '…and it is legible', JSON.stringify(ink));

  section('casting the vote for a nominated cause');
  // Nominate one through the API so the ballot has a challenger to page to.
  const CNAME = 'Check Cause ' + (Date.now() % 100000);
  const nom = await fetch(BASE + '/causes/suggest', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + token, 'content-type': 'application/json' },
    body: JSON.stringify({ name: CNAME, color: '#39c0c8', description: 'a check' }),
  });
  ok(nom.ok, 'a cause can be nominated', 'HTTP ' + nom.status);
  const nominated = await nom.json();

  await page.goto(BASE + '/main.html?state=ce', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2200);
  await page.click('tr[data-slot="7"] .init-table__name');
  await page.waitForTimeout(1400);
  // Page the challenger slot onto the cause just nominated.
  let found = false;
  for (let i = 0; i < 30; i++) {
    const t = await page.$eval('.ce-sugg', e => e.textContent.replace(/\s+/g, ' ').trim());
    if (t.includes(CNAME)) { found = true; break; }
    const next = await page.$('.ce-panel .ce-row--sugg .rf-btn:last-child');
    if (!next || await next.isDisabled()) break;
    await next.click();
    await page.waitForTimeout(400);
  }
  ok(found, 'the pager reaches the cause that was just nominated', CNAME);

  // §1 (2026-08-27) — **the vote is DIALLED, then committed.** Clicking a
  // choice used to POST it; the panel has a Commit and a Cancel now, so a
  // click marks a draft and nothing reaches the server until Commit.
  const votesOf = async () => Number(
    ((await page.$eval('.ce-panel .ce-row--head', e => e.textContent)).match(/This week\s*(\d+)/) || [])[1] || 0);
  const before7 = await page.$eval('.ce-panel .ce-row--head', e => e.textContent);
  const votesBefore = await votesOf();
  const mineBefore = await (await fetch(BASE + '/causes/vote/mine', {
    headers: { Authorization: 'Bearer ' + token } })).json();
  const challenger = (await page.$$('.ce-panel .ce-row--votes .ce-vote'))[1];
  await challenger.click();
  await page.waitForTimeout(900);
  ok(await page.$$eval('.ce-panel .ce-row--votes .ce-vote',
                       els => els.some(e => e.classList.contains('draft'))),
     'clicking a choice DIALS it, and says so');
  const midway = await (await fetch(BASE + '/causes/vote/mine', {
    headers: { Authorization: 'Bearer ' + token } })).json();
  ok(JSON.stringify(midway) === JSON.stringify(mineBefore),
     '…and nothing has reached the server yet', JSON.stringify(midway));
  const ceCommit = (await page.$$('.ce-panel .ce-row--acts .vb-btn'))[0];
  ok(!(await ceCommit.isDisabled()), 'Commit wakes up once something is dialled');
  await ceCommit.click();
  await page.waitForTimeout(2400);
  const mine = await (await fetch(BASE + '/causes/vote/mine', {
    headers: { Authorization: 'Bearer ' + token } })).json();
  ok(mine['7'] === nominated.id, 'the server recorded it in window 7', JSON.stringify(mine));
  ok(await page.$$eval('.ce-panel .ce-row--votes .ce-vote', els => els.some(e => e.classList.contains('on'))),
     '…and the button it was cast on is marked');
  const myRow = await page.$eval('tr[data-slot="7"] .init-table__stake',
    e => e.textContent.replace(/\s+/g, ' ').trim());
  ok(/voted/.test(myRow), 'the table row reports it in My vote', myRow);
  const head7 = await page.$eval('.ce-panel .ce-row--head', e => e.textContent.replace(/\s+/g, ' ').trim());
  ok((await votesOf()) === votesBefore + 1, 'and the panel counts one more than before',
     votesBefore + ' \u2192 ' + (await votesOf()));
  ok(/This week ?\d+ votes?/.test(head7), '…in words that agree with the number', head7.slice(-70));
  ok(before7 !== head7, '…which is a change from before the click');

  section('what the SERVER refuses, and what it now accepts');
  const post = (slot, cause_id) => fetch(BASE + '/causes/vote', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + token, 'content-type': 'application/json' },
    body: JSON.stringify({ slot, cause_id }),
  });
  // A confirmed window: its election card is already made.
  ok((await post(3, nominated.id)).status === 400,
     'a CONFIRMED window (3) is refused');
  // §1 (2026-08-21): all seven open windows, not just the nearest.
  ok((await post(13, nominated.id)).ok,
     'the FURTHEST open window (13) is accepted — all 7 ballots are votable at once');
  ok((await post(10, nominated.id)).ok, '…and so is one in the middle (10)');
  // §1 (2026-08-21): a preexisting cause cannot take a window.
  // §0c (2026-08-26): …and WHICH active cause is a challenger depends on the
  // week. This asked slot 11 to take `atmosphere` and expected a 400, but slot
  // s is held by the cause at (active + s) % 7, so once the rotation reached
  // Forests, atmosphere WAS slot 11's incumbent and the post was a KEEP — which
  // is allowed, and always was. The check now asks the slate who holds the
  // window and challenges it with somebody else.
  const slate = await (await fetch(BASE + '/causes/slate')).json();
  const inc11 = (slate.slots.find(x => x.slot === 11) || {}).incumbent_id;
  const activeCauses = await (await fetch(BASE + '/causes')).json();
  const rival = (activeCauses.find(c => c.id !== inc11 && c.index != null) || {}).id;
  const preexisting = await post(11, rival);
  ok(preexisting.status === 400,
     'an ACTIVE cause is refused as a challenger', rival + ' \u2192 HTTP ' + preexisting.status);
  ok(/proposed|nominate/i.test(JSON.stringify(await preexisting.json().catch(() => ({})))),
     '…and says why');
  // Keeping the incumbent is not a replacement, so it is still allowed.
  ok((await post(11, inc11)).ok, 'voting to KEEP the incumbent is still allowed', inc11);

  section('?state=ce lands here directly');
  await page.goto(BASE + '/main.html?state=ce', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2200);
  ok(await page.$$eval('#init-table-body tr.init-table__row', t => t.length) === 13,
     'the deep link opens the cause table', '');
  ok(await page.$eval('#init-table-head', h => /Election date/.test(h.textContent)),
     '…with the cause head on it');

  section('and back out again');
  // §1 (2026-08-27): the way back is the panel's own button, which flips to
  // "Hide Cause Table" while the table is showing — the toolbar under the cause
  // table is hidden, so nothing else returns you to the elections.
  ok(await page.$eval('.ce-panel__b .rf-btn', e => /Hide Cause Table/i.test(e.textContent)),
     'the button flips while the cause table is showing');
  await page.click('.ce-panel__b .rf-btn');
  await page.waitForTimeout(1400);
  ok(await page.$eval('#init-table-head', h => /Total tokens/.test(h.textContent)),
     'the back button returns the table to the initiative elections');

  section('no script errors');
  ok(errors.length === 0, 'the page ran clean', errors.slice(0, 3).join(' | '));
  ok(httpErrors.length === 0, 'and every request it made succeeded',
     httpErrors.slice(0, 4).join(' | '));

  await page.goto(BASE + '/main.html?state=ce', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1800);
  await page.screenshot({ path: '/tmp/ebx/ce_table.png', fullPage: true });
  await browser.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'CAUSE TABLE CLEAN'));
  process.exit(bad ? 1 : 0);
})();
