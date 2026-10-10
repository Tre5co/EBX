// oe_check — the organization election on the merged mission page, in a real
// browser.
//
//   node scripts/oe_check.js [http://127.0.0.1:8000]
//
// REWRITTEN 2026-09-24 (build-seq P1, OPEN DEFECTS F4). The previous version
// drove main.html's OE table as a fixed queue of eight sliders — the layout of
// 2026-08-20. Three things replaced it and the old check failed on all three:
//   · 2026-09-08  the OE table is ONE race's organizations; the queue of open
//                 races is behind "Show all races"
//   · 2026-09-17  a race is open only to the people who backed its initiative
//                 election (plus this week's race, open to everyone), with the
//                 My-votes ladder instead of an amount slider
//   · 2026-09-24  the Elect page merged into the mission page: a race IS a
//                 mission, and picking one moves the whole page to it
// What it guards now: the race the page is about is the race the ballot, its
// topbar, the head and the overview all name; the queue of races opens and
// each row is a door to its mission; a benefactor outside a race is told why
// instead of being handed a dead control; and the voting surface counts tokens.
// A full commit round-trip needs a benefactor with an initiative-election stake
// that has CLOSED, which a fresh account cannot have — that belongs to a bot-
// seeded database (INSTRUCTIONS backlog), not to this check.
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
const EMAIL = `oe-check-${Date.now()}@oe-check.example.com`;
let bad = 0, n = 0;
function ok(cond, what, detail) {
  n++; if (!cond) bad++;
  console.log('  ' + (cond ? 'ok  ' : 'FAIL') + '  ' + what + (detail ? '  ' + detail : ''));
}
const section = t => console.log('\n=== ' + t);

(async () => {
  let r = await fetch(BASE + '/auth/signup', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: EMAIL, handle: 'oecheck' + (Date.now() % 100000), password: 'oe-check-pw-123' }),
  });
  if (!r.ok) { console.log('FAIL  could not sign up: ' + (await r.text()).slice(0, 200)); process.exit(1); }
  r = await fetch(BASE + '/auth/login', {
    method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: EMAIL, password: 'oe-check-pw-123' }),
  });
  const token = (await r.json()).access_token;

  // The open races, from the API, oldest first — the order they close in.
  const missions = await (await fetch(BASE + '/missions')).json();
  const open = missions.filter(m => m.winning_tiv_id && !m.winning_org_id)
    .sort((a, b) => new Date(a.started_at) - new Date(b.started_at));
  const inits = await (await fetch(BASE + '/initiatives')).json();
  const tivTitle = id => (inits.find(i => i.id === id) || {}).title || id;
  if (open.length < 2) { console.log('FAIL  this database has fewer than two open organization elections'); process.exit(1); }

  const browser = await chromium.launch({ executablePath: chromeExe() });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1100 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message).slice(0, 200)));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.googleapis|gstatic|favicon|TUNNEL|cloudflareinsights/i.test(m.text()))
    errors.push('console: ' + m.text().slice(0, 160)); });
  await page.addInitScript(t => localStorage.setItem('ebx_auth_token', t), token);

  section('a race is a mission: one address, one race on every surface');
  // the newest open race that has a candidate, so the refusal below has a button to test
  const cands = await (await fetch(BASE + '/candidacies')).json();
  // …and that /wallet/rows carries (it caps at eight, and the first is this
  // week's, open to everyone — OPEN DEFECTS F11/F13).
  const wrows = (await (await fetch(BASE + '/wallet/rows')).json()).map(x => x.mission_id);
  const withCands = open.filter(m => cands.some(c => c.mission_id === m.id) &&
    wrows.indexOf(m.id) > 0);
  const race = withCands[withCands.length - 1] || open[open.length - 1];
  const title = tivTitle(race.winning_tiv_id);
  await page.goto(BASE + '/mission.html?mission=' + race.id, { waitUntil: 'networkidle' });
  await page.waitForSelector('#el3-oe.on .votebar', { timeout: 20000 });
  await page.waitForTimeout(1200);
  const st = await page.evaluate(() => ({
    path: location.pathname, head: document.getElementById('mx-title').textContent,
    sub: document.getElementById('mx-sub').textContent,
    phase: (document.querySelector('.mx-phase.on') || {}).dataset?.step,
    bar: (document.getElementById('el3-top-oe') || {}).textContent || '',
    ballot: (document.querySelector('#el3-oe-body .votebar__title') || {}).textContent || '',
    ov: document.getElementById('mx-overview').innerText,
  }));
  ok(/^\/m\/[a-z0-9-]+$/.test(st.path) && !/^\/m\/[a-z]{3}\d+$/.test(st.path),
     'the old ?mission= link settles on the initiative-title address (D1)', st.path);
  // P1 edits (2026-09-28): the phase names the title above the annulus for the
  // cause and initiative elections only; after that it is the mission's own —
  // its initiative — and the line under it says what is being elected.
  ok(st.head === title, 'the title above the annulus is the mission\'s: its initiative (P1 edits 2026-09-28)', st.head);
  ok(/Electing the organization/.test(st.sub), '…and the line under it says the organization is being elected', st.sub);
  ok(st.phase === 'org', 'the phase toggle is on 3 · Organization election');
  ok(st.bar.indexOf(title) >= 0, 'the ballot topbar names THIS race, not the one closing soonest', st.bar.slice(0, 80));
  // Unified elections (2026-09-29): the header line names the race; the ballot no longer repeats the title.
  ok(!/ORGANIZATION ELECTION:/i.test(st.ballot), '…and the ballot does not repeat it (the redundant title is gone)', st.ballot.slice(0, 90));
  ok(/Organization election/i.test(st.ov) && /Election open/i.test(st.ov), 'the overview says the organization is being elected');
  ok(/Guaranteed/i.test(st.ov) && /Committed/i.test(st.ov), '…and carries both pools (D3)');
  const ovApi = await (await fetch(BASE + '/missions/' + race.id + '/overview')).json();
  const tally = await (await fetch(BASE + '/missions/' + race.id + '/p2/tally')).json();
  ok(Math.round(ovApi.committed_ct / 100) === Math.round(Number(tally.pool_ebx) || 0),
     'the committed pool and the ballot’s race pool are one number', ovApi.committed_ct / 100 + ' vs ' + tally.pool_ebx);
  ok(ovApi.guaranteed_ct <= ovApi.committed_ct, '…and the guaranteed part never exceeds it');

  section('"Show all races" opens the queue (F12: the button threw)');
  await page.click('#show-all-races');
  await page.waitForTimeout(900);
  ok(await page.evaluate(() => window._oeScope() === 'all'), 'the table is in its all-races scope');
  const rows = await page.$$eval('#init-table-body tr.init-table__row[data-mission]',
    trs => trs.map(tr => ({ mission: tr.dataset.mission, date: tr.querySelector('.init-table__date')?.textContent.trim() })));
  ok(rows.length >= 2, 'one row per open race', rows.length + ' rows');
  const dates = rows.map(x => new Date(x.date).getTime()).filter(x => !isNaN(x));
  ok(dates.length === rows.length && dates.every((d, i) => i === 0 || d >= dates[i - 1]),
     'in the order they close');
  ok(await page.$eval('#show-all-races', b => /Back to this race/.test(b.textContent)), 'the button offers the way back');

  section('a race row moves the whole page to that mission');
  const other = rows.find(x => x.mission !== race.id);
  await page.click(`tr[data-mission="${other.mission}"] .init-table__name`);
  await page.waitForTimeout(1400);
  const moved = await page.evaluate(() => ({
    path: location.pathname, head: document.getElementById('mx-title').textContent,
    picked: window._pickedMission && window._pickedMission(),
    state: window.MX && MX.state.mission && MX.state.mission.id,
  }));
  const om = missions.find(m => m.id === other.mission);
  ok(moved.state === other.mission && moved.picked === other.mission,
     'the page and the ballot both follow the row', moved.state + ' / ' + moved.picked);
  ok(moved.head.indexOf(tivTitle(om.winning_tiv_id)) >= 0, 'the head names its initiative', moved.head);
  ok(moved.path !== st.path, '…at its own address', moved.path);
  ok((await page.$$('#init-table-body .init-detail-row')).length === 0, 'nothing unfolds under the row');
  await page.goBack(); await page.waitForTimeout(1400);
  ok(await page.evaluate(() => MX.state.mission && MX.state.mission.id) === race.id, 'Back returns to the first race');

  section('outside a race, the ballot says why rather than offering a dead control');
  const picks = await page.$$eval('#el3-oe-body .vb-org__pick',
    els => els.map(e => ({ off: e.disabled, why: e.title })));
  if (picks.length) {
    ok(picks.every(p => !p.off || /\S/.test(p.why || '')),
       'every pick button is live, or says who the race is open to',
       picks.map(p => (p.off ? 'closed: ' : 'open') + (p.why || '')).join(' | ').slice(0, 120));
    ok(picks.some(p => p.off), 'a fresh account is refused in a race it did not back (this one is not this week\u2019s)',
       race.id);
  } else {
    ok(true, '(no candidates in this race — nothing to refuse)');
  }

  section('the voting surface counts tokens');
  const ebxOnBallot = await page.$$eval('#el3 *, #init-table-body *', els =>
    els.filter(e => e.children.length === 0 && /\bEBX\b/.test(e.textContent)).map(e => e.textContent.trim()).slice(0, 5));
  ok(ebxOnBallot.length === 0, 'no "EBX" inside the ballots or the table', ebxOnBallot.join(' | '));

  section('no script errors');
  ok(errors.length === 0, 'none', errors.slice(0, 4).join(' || '));

  await browser.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'OE CHECK CLEAN'));
  process.exit(bad ? 1 : 0);
})();
