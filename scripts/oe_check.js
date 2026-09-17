// oe_check — the rebuilt organization-election table, driven in a real browser.
//
//   node scripts/oe_check.js [http://127.0.0.1:8000]
//
// jsdom can render this table but it cannot drag a slider, and the whole point
// of the rebuild is that the commitment is a slider in the row. So this one
// drives Chromium: it signs an account in, opens main.html?state=oe, and moves
// the controls the way a benefactor would.
//
// What it is guarding is the conservation law. Eight sliders and one unallocated
// balance share a single pot; the failure mode is a drag that takes money the
// bar does not give back, which is the ratchet bug the carryover panel had.
const { chromium } = require('playwright');
const fs = require('fs');
// Resolve a Chromium binary: PW_CHROME env, else the preinstalled cloud paths,
// else Playwright's own download (works on a normal dev machine after
// `npx playwright install chromium`).
function chromeExe() {
  const cands = [process.env.PW_CHROME,
    '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    '/opt/pw-browsers/chromium/chrome-linux/chrome',
    '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'];
  for (const p of cands) { try { if (p && fs.statSync(p).isFile()) return p; } catch (e) {} }
  return undefined;   // let Playwright pick its own
}


const BASE = process.argv[2] || 'http://127.0.0.1:8000';
const EMAIL = `oe-check-${Date.now()}@oe-check.example.com`;
let bad = 0, n = 0;

function ok(cond, what, detail) {
  n++;
  if (!cond) bad++;
  console.log('  ' + (cond ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : ''));
}
const section = t => console.log('\n=== ' + t);

(async () => {
  // ── a throwaway account, made through the API the page uses ──
  let r = await fetch(BASE + '/auth/signup', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: EMAIL, handle: 'oecheck' + (Date.now() % 100000),
                           password: 'oe-check-pw-123' }),
  });
  if (!r.ok) { console.log('FAIL  could not sign up: ' + (await r.text()).slice(0, 200)); process.exit(1); }
  r = await fetch(BASE + '/auth/login', {
    method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: EMAIL, password: 'oe-check-pw-123' }),
  });
  const token = (await r.json()).access_token;

  const browser = await chromium.launch({ executablePath: chromeExe() });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1100 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message).slice(0, 200)));
  // The sandbox has no outbound network, so the Google-Fonts <link> and its
  // preconnect always fail here. That is the environment, not the page.
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.googleapis|gstatic|favicon|TUNNEL/i.test(m.text()))
    errors.push('console: ' + m.text().slice(0, 160)); });
  const httpErrors = [];
  page.on('response', res => { if (res.status() >= 400 && !/fonts\.googleapis|gstatic/.test(res.url()))
    httpErrors.push(res.status() + ' ' + res.request().method() + ' ' + new URL(res.url()).pathname); });

  await page.addInitScript(t => localStorage.setItem('ebx_auth_token', t), token);
  await page.goto(BASE + '/main.html?state=oe', { waitUntil: 'networkidle' });
  await page.waitForSelector('#init-table-body .init-table__row', { timeout: 15000 });
  await page.waitForTimeout(1200);

  const T = 100;   // centitokens per token

  section('the table is the open races, and only those');
  const rows = await page.$$eval('#init-table-body tr.init-table__row',
    trs => trs.map(tr => ({
      mission: tr.dataset.mission,
      name: tr.querySelector('.init-table__name span')?.textContent.trim(),
      date: tr.querySelector('.init-table__date')?.textContent.trim(),
      pool: tr.querySelector('.init-table__ebx')?.textContent.trim(),
      say: tr.querySelector('.stk__say')?.textContent.replace(/\s+/g, ' ').trim() || null,
      hasSlider: !!tr.querySelector('.stk__range'),
      cells: tr.children.length,
      active: tr.classList.contains('row-active-race'),
      voteCell: tr.querySelector('.col-vote')?.textContent.trim(),
    })));
  ok(rows.length === 8, 'EIGHT rows — the table is a fixed queue of deadlines',
     rows.length + ' rows');
  ok(rows.every(r => r.mission), 'every row is a mission');
  ok(!rows.some(r => /elected/i.test(r.voteCell || '')),
     'no decided race is in the table any more');
  const dates = rows.map(r => new Date(r.date).getTime());
  ok(dates.every((d, i) => i === 0 || d >= dates[i - 1]),
     'ordered by the date in the column');
  ok(rows.every(r => r.date && r.date !== '—'), 'every row shows its vote date');
  ok(await page.$eval('#init-table-head', h => /Vote date/.test(h.textContent)),
     '"Week 0" is gone from the head; "Vote date" replaces it');
  ok(!(await page.$eval('#init-table-head', h => /Week 0/.test(h.textContent))),
     '…and nothing still says Week 0');

  section('the date bug: the row and the dialog agree');
  // lan1 · Protect lake ecosystems read Aug 25 in the dialog and Oct 13 on the
  // card — the dialog was printing the SIBLING race's date (lan0's).
  const lake = rows.find(r => /lake/i.test(r.name || ''));
  if (lake) {
    ok(/Oct 13, 2026/.test(lake.date), 'lan1 · Protect lake ecosystems votes Oct 13', lake.date);
    // §1 (2026-08-20b): the Vote button is gone — the row IS the way in.
    await page.click(`tr[data-mission="${lake.mission}"] .init-table__name`);
    await page.waitForTimeout(900);
    const title = await page.$eval('.votebar__title', el => el.textContent.trim());
    ok(/Oct 13, 2026/.test(title), 'and the dialog above it says the same day', title);
    ok(!/Aug 25/.test(title), '…not Aug 25, which belongs to the other land race');
  } else {
    ok(true, '(no "Protect lake ecosystems" row in this database)');
  }

  section('§1: the commitment is READ-ONLY in the row');
  // The slider is gone and stays gone. It came off on 2026-08-20b because
  // committing was one way; the reason changed on 2026-08-27c — an allocation
  // IS revisable inside its own week — but the shape did not, because the row's
  // job is to report and the dialog's job is to decide. What the row says now is
  // which STATE the money is in: EBX, or still movable.
  ok(rows.every(r => !r.hasSlider), 'no row carries a slider');
  ok(rows.every(r => r.say === null || /committed to/.test(r.say)),
     'each says what it did: "x committed to <phl>"');
  ok(rows.every(r => r.cells === 5),
     'five columns — the Vote column is gone, the row itself is the way in',
     rows[0] ? rows[0].cells + ' cells' : '');
  const heads = await page.$$eval('#init-table-head th',
    els => els.map(e => e.textContent.replace(/[▲▼]/g, '').trim()));
  ok(!heads.includes('Vote'), '…and the head does not name it either', heads.join(' · '));
  ok(heads.includes('Vote date'), '…while the DEADLINE column keeps its name');
  ok(rows.filter(r => r.active).length === 1, 'exactly one row is marked this week\u2019s',
     rows.filter(r => r.active).map(r => r.name).join(', '));
  const activeRow = rows.find(r => r.active);

  section('§1 (2026-08-20b): no scrollbar, no filter, no search');
  ok(await page.$eval('.init-table-scroll',
                      el => el.classList.contains('init-table-scroll--fixed')),
     'the table is sized to its eight rows rather than capped and scrolled');
  ok(await page.$eval('.init-table-scroll',
                      el => getComputedStyle(el).overflowY !== 'auto'),
     '…so there is no scrollbar implying a ninth race below the fold');
  ok(await page.$eval('.init-toolbar--below', el => getComputedStyle(el).display === 'none'),
     'the search box and the cause filter are not on this table');
  const cardVotes = await page.$$eval('.rf-btn',
    els => els.filter(e => e.textContent.trim() === 'Vote').length);
  ok(cardVotes === 0, 'and no card carries a Vote button that would filter it',
     cardVotes + ' found');

  section('§1 (2026-08-20): an OE row does not expand');
  // "The OE table rows should not be expandable." Clicking one selects the race
  // and points the dialog at it; nothing unfolds underneath and pushes the other
  // seven races down the page.
  const clickRow = rows.find(r => !r.active) || rows[0];
  const before = await page.$$eval('#init-table-body tr', trs => trs.length);
  await page.click(`tr[data-mission="${clickRow.mission}"] .init-table__name`);
  await page.waitForTimeout(700);
  ok((await page.$$('#init-table-body .init-detail-row')).length === 0,
     'clicking a row opens no detail panel');
  ok(await page.$$eval('#init-table-body tr', trs => trs.length) === before,
     'the table still has exactly the rows it had', String(before));
  ok(await page.$eval(`tr[data-mission="${clickRow.mission}"]`,
                      el => el.classList.contains('row-selected')),
     '…but the row is selected, so the dialog and the row name the same race');
  await page.click(`tr[data-mission="${clickRow.mission}"] .init-table__name`);
  await page.waitForTimeout(500);
  ok((await page.$$('#init-table-body .init-detail-row')).length === 0,
     'and clicking it again does not expand it either');

  section('§2 (2026-08-21): the allocations panel, and where the links went');
  // "Move the 2 bottom (side) cards to the side so they create 2 columns of 3 …
  // and nestle the allocations panel in between them and up against the bottom
  // of the annulus. The allocations panel should persist in both the ME and OE
  // page state." So the OE action ROW is gone: its balance is a panel under the
  // wheel, and its three links moved into the election panel that is about the
  // race they describe.
  ok(!!(await page.$('#alloc-mount .unalloc')), 'the allocations panel is under the annulus');
  ok((await page.$$('#init-table-body .unalloc-row')).length === 0,
     '…and not a row inside the table');
  ok(await page.$eval('#oe-actions-mount', el => el.children.length === 0),
     '…and the old action row above the table is empty');
  // §2 (2026-08-27): "For now, move the allocations panel to the very bottom of
  // the page until its design is complete." It hugged the underside of the
  // annulus from 2026-08-21 until the ME/OE toggle took that place.
  const parked = await page.evaluate(() => {
    const a = document.getElementById('alloc-mount');
    const sec = document.querySelector('.alloc-section');
    const tbl = document.querySelector('.tiv-table-section');
    if (!a || !sec || !tbl) return 'missing';
    return sec.contains(a) &&
      (tbl.compareDocumentPosition(sec) & Node.DOCUMENT_POSITION_FOLLOWING) ? 'ok' : 'wrong';
  });
  ok(parked === 'ok', 'it is parked at the bottom of the page, below the table', String(parked));
  // §2 (2026-08-27): "Need a deselect or cancel button next to commit everywhere."
  ok(!!(await page.$('#oe-cancel')), '…with a Cancel beside its Commit');
  const cols = await page.evaluate(() => [
    document.querySelectorAll('#left-panel .race-face').length,
    document.querySelectorAll('#right-panel .race-face').length,
    document.querySelectorAll('.hero__bottomrow').length,
    document.querySelectorAll('.hero__edgebtn').length,
  ]);
  ok(cols[0] === 3 && cols[1] === 3, 'two columns of three cards', cols[0] + ' / ' + cols[1]);
  ok(cols[2] === 0 && cols[3] === 0, '…and the bottom row with Help and Commit is gone');

  section('§2: the election panel carries the links now');
  await page.click(`tr[data-mission="${activeRow.mission}"] .init-table__name`);
  await page.waitForTimeout(900);
  const foot = await page.$$eval('.votebar__foot .vb-btn', els => els.map(e => e.textContent.trim()));
  ok(foot.some(t => /Discuss/.test(t)), 'Discuss is in the election panel', foot.join(' · '));
  ok(foot.some(t => /Nominate \/ Register/.test(t)), '…with Nominate / Register an Organization');
  // "Instead of 'Mission page' it should say 'View Organizations'."
  ok(foot.some(t => /View Organizations/.test(t)), '…and View Organizations');
  ok(!foot.some(t => /Mission page/.test(t)), '…which replaced "Mission page"');
  // §2 (2026-09-08) — **REVERSED, on Jax's instruction:** "OE ballot card is
  // currently missing the commit button." The 2026-08-21 rule (Commit is
  // all-encompassing, so it lives with the balance) still holds for the button
  // in the allocations panel, which is still there and still asserted below —
  // but the ballot is where the decision is made, and it used to end in three
  // links with no way to act on them. Both buttons now exist and both call
  // `commitAll`, so there is one write path and two doors to it.
  ok(foot.some(t => /^Commit/.test(t)), '…and Commit, which is on the ballot again');
  ok(foot.some(t => /^Cancel$/.test(t)), '…with the Cancel that arms beside it');
  ok(!!(await page.$('.unalloc__commit #oe-commit')),
     'and Commit is ALSO in the allocations panel, beside the balance it spends');
  // §0 (2026-08-21): the filled Commit button resolved `--vb` to nothing when it
  // sat outside `.votebar` — near-black on near-black. Contrast, not presence.
  const commitInk = await page.$eval('#oe-commit', el => {
    const s = getComputedStyle(el);
    return { color: s.color, bg: s.backgroundColor, op: s.opacity };
  });
  const _lum = c => { const m = (c.match(/[\d.]+/g) || [0, 0, 0]).map(Number);
    return (0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]) / 255; };
  ok(Number(commitInk.op) * Math.max(_lum(commitInk.color), _lum(commitInk.bg)) > 0.2,
     'and it is legible against the panel it sits on', JSON.stringify(commitInk));

  section('§2: the ballot is the ranked top three');
  const picks = await page.$$eval('.vb-org', els => els.length);
  ok(picks > 0 && picks <= 4, 'at most three candidates (plus my own pick if it fell out)',
     picks + ' rows');

  section('§2: where the next token comes from');
  // "Option to add more vote (grant (if available), purchase, from another OE
  // (dropdown) + amount)."
  const srcs = await page.$$eval('.vb-amount__src option', els => els.map(e => e.textContent.trim()));
  ok(srcs.length >= 2, 'the source is a choice, not an assumption', srcs.join(' | '));
  ok(srcs.some(t => /Unallocated/.test(t)), '…the unallocated balance');
  ok(srcs.some(t => /Purchase/.test(t)), '…a purchase');

  section('§0 (2026-08-21): the voting area counts TOKENS, not EBX');
  // "Voting no longer happens in EBX. It happens in tokens. We need to remove
  // 'EBX' everywhere from the voting area."
  //
  // §0c (2026-08-28) — NARROWED to what the finalized model actually says.
  // This forbade the string EBX anywhere outside the topbar, which was right
  // while EBX was a rival NAME for the unit. Since 2026-08-27c it is a STATE:
  // "main.html says tokens on the voting surface because that is where tokens
  // are; EBX is correct wherever mission-tied, minted money is meant." Two
  // places on this page mean exactly that and must keep the word — the third
  // allocation set, which IS the minted bin, and the commit dialog's warn line,
  // which is the sentence explaining what the week roll does to what you are
  // about to commit. What must never say EBX is the part a benefactor types an
  // amount into or reads a pool from. So those two are excluded and the rest of
  // the page is still held to the rule.
  const stray = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('body *').forEach(el => {
      // Scripts and styles are not text a benefactor reads; the topbar mark and
      // the brand are the PRODUCT's name, which is still Earthbux — what had to
      // go is EBX as the unit a vote is counted in.
      if (/^(SCRIPT|STYLE|NOSCRIPT)$/.test(el.tagName)) return;
      if (el.closest('.ebx-topbar, .ebx-home-mark, .alloc-set, .vb-amount__warn')) return;
      for (const n of el.childNodes) {
        if (n.nodeType === 3 && /\bEBX\b/.test(n.textContent)) out.push(
          el.tagName + ': ' + n.textContent.trim().slice(0, 60));
      }
    });
    return out;
  });
  ok(stray.length === 0, 'not one visible "EBX" on the voting surface', stray.slice(0, 4).join(' | '));
  ok(await page.$eval('#init-table-head', h => /Total pool/.test(h.textContent)),
     '…and the table head counts a pool, not a currency');

  section('the allocations bar');
  // §2 (2026-08-21): "There are 2 sets of 2 allocation states — Unallocated
  // (granted or purchased), and Committed (to an initiative or an organization)."
  // §0c (2026-08-28) — THREE sets now, not two. The finalized model has four
  // states, not four half-states: `unallocated → committed → minted → donated`,
  // and `docs/structure.md` states the shape of the bar in one line — "One bar,
  // three sets of two". The third set is the minted bin (held · donated), which
  // did not exist when this assertion was written and which the page has been
  // drawing since 2026-08-27c. The check was rewritten that day but never RUN,
  // which is why it still asked for the old shape.
  const sets = await page.$$eval('.alloc-set .alloc-set__name', els => els.map(e => e.textContent.trim()));
  ok(sets.length === 3 && /Unallocated/i.test(sets[0]) && /Committed/i.test(sets[1]) && /EBX/i.test(sets[2]),
     'three sets: Unallocated · Committed · EBX', sets.join(' · '));
  const seg = await page.$$eval('.unalloc__seg:not(.unalloc__seg--none)',
    els => els.map(e => e.style.width));
  ok(seg.length === 6, 'six segments — three sets of two',
     seg.join(' / '));
  ok(parseFloat(seg[0]) === 100, 'a new account holds nothing but its grant', seg[0]);
  ok(await page.$eval('.unalloc__title', e => /Allocations/i.test(e.textContent)),
     'the panel is titled Allocations, not Unallocated');
  const total0 = await page.$eval('.unalloc__total', e => e.textContent.trim());
  ok(total0 === '10', 'the total is everything held \u2014 10 tokens', total0);
  // §0 (2026-08-21): "Allocations: 88 tokens - $8.80".
  ok(await page.$eval('.unalloc__usd', e => /^\$\d+\.\d\d$/.test(e.textContent.trim())),
     '…and what that cost, because voting is donating',
     await page.$eval('.unalloc__usd', e => e.textContent.trim()));
  const unalloc0 = await page.$$eval('.alloc-set__n', els => els.map(e => e.textContent.trim()));
  ok(unalloc0[0] === '10' && unalloc0[1] === '0',
     '10 unallocated, 0 committed', unalloc0.join(' / '));
  // §2 (2026-08-21): the explanation is gone.
  ok((await page.$$('.unalloc__note')).length === 0,
     'the paragraph explaining the allocations is gone');

  // The grant's CAUSE survives the cut where the commit-by date used to: it is a
  // fact about the tokens, and the only fact that still binds them.
  const key = await page.$$eval('.unalloc__key', els =>
    els.map(e => e.textContent.replace(/\s+/g, ' ').trim()).join(' | '));
  ok(/granted for /.test(key), 'granted tokens carry the CAUSE they were granted for', key);
  ok(!/by [A-Z][a-z]{2} \d/.test(key),
     '…and no commit-by date, because a granted token cannot expire or move');
  ok(/granted/.test(key) && /purchased/.test(key),
     '…and the unallocated set still names its two kinds');
  ok(/initiatives/.test(key) && /organizations/.test(key),
     '…while the committed set names its two');
  ok(/held/.test(key) && /donated/.test(key),
     '…and the third set is EBX: held, and donated');
  // The week change moved to the dialog, beside the act it governs.
  ok(await page.$eval('.vb-amount__warn', e => /week changes|EBX/i.test(e.textContent)),
     'and the dialog says what the week change will do to this amount');

  section('committing: an amount and a philanthropy, then one button');
  const mid = activeRow.mission;
  await page.click(`tr[data-mission="${mid}"] .init-table__name`);
  await page.waitForTimeout(800);
  const poolBefore = (await (await fetch(BASE + '/missions/' + mid + '/p2/tally')).json()).pool_ebx;
  const pick = await page.$('.vb-org__pick');
  if (pick) { await pick.click(); await page.waitForTimeout(600); }
  const amt = await page.$(`#vb-amt-${mid}`);
  ok(!!amt, 'the dialog carries an amount field for the picked race');
  ok(await page.$eval('.vb-amount__label', e => /This race holds/.test(e.textContent)),
     '…and it is labelled as a POSITION, not an addition');
  await amt.evaluate(el => {
    el.value = '3';
    el.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await page.waitForTimeout(600);
  // §2 (2026-08-21): the TOTAL does not move when an amount is dialled — the
  // boundary inside the bar does. Dialling is a preview of where the tokens go,
  // not a preview of destroying them, and a shrinking total said the latter.
  ok(await page.$$eval('.alloc-set__n', els => els[0].textContent.trim()) === '7',
     'dialling 3 tokens previews unallocated at 7 — the money has not moved yet');
  ok(await page.$$eval('.alloc-set__n', els => els[1].textContent.trim()) === '3',
     '…and previews committed at 3, because that is where they are headed');
  ok(await page.$eval('.unalloc__total', e => e.textContent.trim()) === '10',
     '…while the total still reads the 10 tokens they hold');
  // The segment is scaled within its own SET now (2 sets of 2), so 3 of 3
  // committed is the whole of that bar.
  ok(await page.$$eval('.unalloc__seg--org', els => parseFloat(els[0].style.width) === 100),
     '…and the organizations segment is the whole of the committed bar');
  ok(await page.$eval('.unalloc__pending', e => /3/.test(e.textContent)),
     '…and the bar says so in words');
  const commit = await page.$('#oe-commit');
  ok(commit && !(await commit.isDisabled()), 'the one Commit button is armed');
  ok(/Commit 3/.test(await commit.evaluate(el => el.textContent.trim())),
     '…and names the amount it is about to make irreversible');
  await commit.click();
  await page.waitForTimeout(2500);
  const server = await (await fetch(BASE + '/wallet', {
    headers: { Authorization: 'Bearer ' + token } })).json();
  ok(server.wallet.committed_ct === 300, 'the server holds 300 ct committed',
     server.wallet.committed_ct + ' ct');
  ok(server.wallet.free_ct === 700, '…and 700 ct unallocated', server.wallet.free_ct + ' ct');
  ok(server.wallet.free_ct + server.wallet.committed_ct === 10 * T,
     'conservation survives the round trip');
  ok(server.wallet.minted_ct === 0,
     '…and none of it is EBX yet: the week has not changed');
  ok(!('staked_ct' in server.wallet) && !('claimed_ct' in server.wallet),
     '`staked` is `committed`, and `claimed` went back to meaning an org claim');
  const srvRow = server.rows.find(r => r.mission_id === mid);
  ok(srvRow && srvRow.my_stake_ct === 300, 'on the race the dialog named');
  ok(srvRow && srvRow.my_org_id, '…standing behind the philanthropy picked with it');

  section('§0 (2026-08-21): the race pool MOVES when a vote is committed');
  // "The OE race pool is not updating when I commit votes." `p2_tally` measured
  // phase-2 weight with `p2_ebx_by_ben` — the money phase 1 left behind — and
  // knew nothing about `VoteP2.stake_ct`, which is what `POST /wallet/commit`
  // writes. The commit was real; the reported pool was stale.
  const tally = await (await fetch(BASE + '/missions/' + mid + '/p2/tally')).json();
  ok(Math.round((tally.pool_ebx - poolBefore) * 100) === 300,
     'the pool grew by exactly the 3 tokens committed',
     poolBefore + ' \u2192 ' + tally.pool_ebx);
  // Read the page fresh, so the comparison is against the same moment the
  // server was asked about rather than whatever the last repaint captured.
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.click(`tr[data-mission="${mid}"] .init-table__name`);
  await page.waitForTimeout(900);
  const nowTally = await (await fetch(BASE + '/missions/' + mid + '/p2/tally')).json();
  const dlgPool = await page.$eval('.votebar__chip', e => e.textContent.replace(/\s+/g, ' ').trim());
  ok(new RegExp('Race pool\\s*' + Math.round(nowTally.pool_ebx) + ' tokens').test(dlgPool),
     '…and the dialog says the same number the server does',
     dlgPool + ' vs ' + nowTally.pool_ebx);

  section('§0: an UNASSIGNED commitment is in the pool too, not nowhere');
  // `unassigned_ebx` was summed from the phase-1 carry, which for a stake
  // committed straight out of the allocations bar is zero — so those tokens
  // vanished from the pool entirely.
  const em2 = `oe-unassigned-${Date.now()}@oe-check.example.com`;
  await fetch(BASE + '/auth/signup', { method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: em2, handle: 'oeun' + (Date.now() % 100000),
                           password: 'oe-check-pw-123' }) });
  const t2 = (await (await fetch(BASE + '/auth/login', { method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: em2, password: 'oe-check-pw-123' }) })).json()).access_token;
  await fetch(BASE + '/wallet', { headers: { Authorization: 'Bearer ' + t2 } });
  const b2 = await (await fetch(BASE + '/missions/' + mid + '/p2/tally')).json();
  await fetch(BASE + '/wallet/commit', { method: 'POST',
    headers: { Authorization: 'Bearer ' + t2, 'content-type': 'application/json' },
    body: JSON.stringify({ mission_id: mid, target_ct: 250 }) });
  const a2 = await (await fetch(BASE + '/missions/' + mid + '/p2/tally')).json();
  ok(Math.round((a2.pool_ebx - b2.pool_ebx) * 100) === 250,
     'the pool grew by 2.5 tokens with no philanthropy named',
     b2.pool_ebx + ' \u2192 ' + a2.pool_ebx);
  ok(Math.round((a2.unassigned_ebx - b2.unassigned_ebx) * 100) === 250,
     '…and every one of them is reported as unassigned',
     b2.unassigned_ebx + ' \u2192 ' + a2.unassigned_ebx);

  section('and inside the week it CAN be taken back');
  // The exact inverse of what this section asserted from 2026-08-20b until
  // 2026-08-27c. Committing was one way then; the week change is the ratchet
  // now, so a draft made this week can be dialled back down and the balance
  // returns. What cannot be undone is a week roll — `wallet_check` guards that
  // half, where a row can be aged without waiting seven days.
  const undo = await fetch(BASE + '/wallet/commit', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + token, 'content-type': 'application/json' },
    body: JSON.stringify({ mission_id: mid, target_ct: 100 }),
  });
  ok(undo.status === 200, 'lowering this week\u2019s allocation is accepted', 'HTTP ' + undo.status);
  const back = await (await fetch(BASE + '/wallet', {
    headers: { Authorization: 'Bearer ' + token } })).json();
  ok(back.wallet.free_ct === 900, '…and the 2 tokens came back to unallocated',
     back.wallet.free_ct + ' ct');
  ok(back.wallet.free_ct + back.wallet.committed_ct === 10 * T,
     '…with nothing created or destroyed on the way');
  const neg = await fetch(BASE + '/wallet/commit', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + token, 'content-type': 'application/json' },
    body: JSON.stringify({ mission_id: mid, target_ct: -300 }),
  });
  ok(neg.status === 422, 'a NEGATIVE target is still refused by the schema',
     'HTTP ' + neg.status);
  await fetch(BASE + '/wallet/commit', { method: 'POST',
    headers: { Authorization: 'Bearer ' + token, 'content-type': 'application/json' },
    body: JSON.stringify({ mission_id: mid, target_ct: 300 }) });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  ok(await page.$$eval('.alloc-set__n', els => els[0].textContent.trim()) === '7',
     'the page comes back reading 7 unallocated, not 10');
  ok(await page.$eval('.unalloc__total', e => e.textContent.trim()) === '10',
     '…out of a total that is still 10, because nothing was destroyed');
  ok(await page.$$eval('.unalloc__seg--org', els => parseFloat(els[0].style.width) === 100),
     '…and the 3 now sit in the organizations segment for real');
  ok(await page.$eval(`#stk-val-${mid}`, e => e.textContent.trim()) === '3',
     '…with 3 committed on the row');

  section('the grant is not paid twice by a refresh');
  const after = await (await fetch(BASE + '/wallet', {
    headers: { Authorization: 'Bearer ' + token } })).json();
  ok(after.granted_this_week_ct === 0, 'reloading the page grants nothing further');
  ok(after.wallet.free_ct + after.wallet.committed_ct === 10 * T,
     'the balance is still exactly one week’s grant');

  section('no script errors');
  ok(errors.length === 0, 'the page ran clean', errors.slice(0, 3).join(' | '));
  ok(httpErrors.length === 0, 'and every request it made succeeded',
     httpErrors.slice(0, 4).join(' | '));

  await page.screenshot({ path: '/tmp/ebx/oe_table.png', fullPage: false });
  await browser.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'OE TABLE CLEAN'));
  process.exit(bad ? 1 : 0);
})();
