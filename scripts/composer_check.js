// composer_check — the mission story's budget panel, report, report thread and
// composer, in a real browser.
//
//   node scripts/composer_check.js [http://127.0.0.1:8000]
//
// Review 2 (2026-09-25, INSTRUCTIONS "P1. Mission"): budgeting and research are
// separate. P1 mission edits (2026-09-28): the budget panel moved INTO the
// report (once the initiative is elected), and the report sits straight under
// the ballot, which carries a post button. The mission REPORT is
// the page's main display — the leading post of each category: a mission
// statement, a plan, Background · Vetting · Analysis (Organization until P2, 2026-09-25). Clicking it opens
// the thread, where research posts are read, rated, replied to and written.
// Posting goes through POST /posts, so its rules still apply: the account first
// commits a stake in this week's initiative election (the membership the gate
// asks for; P3 lifts the gates). Replaces posts_box_check.js.
//
// 10/9 Reshuffle (2026-10-09): the report, its thread and its reply composer
// moved to NEWS (cause.html?mission=<id>, `EBX.MissionReport` in
// resources/js/ebx_report.js) — "When News is filtered to a mission, that
// mission's report sits above its posts." The mission page keeps a pointer to
// it (#mb-news), and `MB.compose('research')` goes there.
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
const J = (u, o) => fetch(BASE + u, o).then(r => r.json());

(async () => {
  const EMAIL = `composer-${Date.now()}@composer-check.example.com`;
  await fetch(BASE + '/auth/signup', { method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: EMAIL, handle: 'cmp' + (Date.now() % 100000), password: 'composer-pw-123' }) });
  const token = (await J('/auth/login', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: EMAIL, password: 'composer-pw-123' }) })).access_token;
  const auth = { Authorization: 'Bearer ' + token };
  const slate = await J('/causes/slate');
  const cause = (await J('/causes')).find(c => c.index === slate.active_index);
  const mission = (await J('/missions?cause_id=' + cause.id))
    .filter(m => !m.winning_tiv_id && ['pre', 'initiative'].includes(m.current_phase))
    .sort((a, b) => a.cycle_num - b.cycle_num)[0];
  const inits = await J('/initiatives?mission_id=' + mission.id);
  await fetch(BASE + '/wallet', { headers: auth });
  await fetch(BASE + '/missions/' + mission.id + '/p1/votes', { method: 'PUT',
    headers: Object.assign({ 'content-type': 'application/json' }, auth),
    body: JSON.stringify({ mission_id: mission.id, shares: { [inits[0].id]: 100 }, ebx: 5 }) });
  await fetch(BASE + '/missions/' + mission.id + '/p1/commit', { method: 'POST', headers: auth });

  const browser = await chromium.launch({ executablePath: chromeExe() });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message).slice(0, 200)));
  await page.addInitScript(t => localStorage.setItem('ebx_auth_token', t), token);
  await page.goto(BASE + '/m/' + mission.id, { waitUntil: 'networkidle' });
  await page.waitForSelector('#mx-pre:not([hidden])', { timeout: 20000 });
  await page.waitForTimeout(800);

  // Mission pass (2026-10-01): "Before the report appears, show posts below the
  // table … For initiative election, show posts targeting any initiative."
  section('before the initiative is elected: posts, not the report (mission pass 2026-10-01)');
  ok(await page.$eval('#mb-news', e => e.hidden), 'the way to the report waits for the initiative election');
  ok(/initiatives running in/i.test(await page.textContent('#mx-pre-title')), 'the posts on its initiatives stand in for it',
     (await page.textContent('#mx-pre-title')).trim());
  ok((await page.$$('#mp-cattabs, #mb-post, #mp-disc, #pb, #ps-ring, #mp-log, #mb-budget-add')).length === 0,
     'no posts toggle, no old dialogue, no discussion box, no post-support ring, no log card, no budget panel');
  // "+ post" ends every ballot; what it opens is still the phase's type.
  const pb = await page.$eval('.el3__col.on .bb .bb__post', e => ({ t: e.textContent.trim(), title: e.title }));
  ok(pb.t === '+ post' && /Post a Background/.test(pb.title), 'the initiative ballot\'s bar ends in "+ post" (a Background)', pb.t + ' / ' + pb.title);
  await Promise.all([page.waitForURL(/post\.html/, { timeout: 15000 }), page.click('.el3__col.on .bb .bb__post')]);
  const u1 = new URL(page.url());
  ok(u1.searchParams.get('type') === 'background' && u1.searchParams.get('cause') === mission.cause_id,
     '…which opens post.html on Background, the cause preselected', u1.search);

  section('the report, once the initiative is elected — in News, above the mission\'s posts; the budget buttons in the plan');
  const elected = (await J('/missions')).find(m => m.winning_tiv_id);
  if (elected) {
    await page.goto(BASE + '/m/' + elected.id, { waitUntil: 'networkidle' });
    await page.waitForSelector('#mb-news:not([hidden])', { timeout: 20000 });
    const href = await page.$eval('#mb-news', e => e.getAttribute('href'));
    ok(href === 'cause.html?mission=' + encodeURIComponent(elected.id) + '#mr', 'the mission page points to its report in News', href);
    await page.goto(BASE + '/cause.html?mission=' + encodeURIComponent(elected.id) + '#mr', { waitUntil: 'networkidle' });
    await page.waitForSelector('#mr .mb-report__sec', { timeout: 20000 });
    await page.waitForTimeout(500);
    ok(await page.evaluate(() => { const r = document.getElementById('mr'), l = document.getElementById('fd-list');
      return !!(r && l && (r.compareDocumentPosition(l) & Node.DOCUMENT_POSITION_FOLLOWING)); }), 'News shows the report above the mission\'s posts');
    const heads = await page.$$eval('#mr .mb-report__sec h4', els => els.map(e => e.childNodes[0].textContent.trim()));
    ok(JSON.stringify(heads) === '["Mission statement","Plan","Background","Investigation","Analysis"]',
       'mission statement · plan · background · investigation · analysis', heads.join(' · '));
    ok(JSON.stringify(await page.$$eval('#mr .mb-report__top .mb-budget__add--plan .mb-budget__btn b', els => els.map(e => e.textContent))) === '["Service","Supply","Support"]',
       'Suggest: Service · Supply · Support sits in the plan');
    ok(!/Budget items are how this mission gets planned/.test(await page.textContent('#mr')), '…and the budget description is gone (it lives on the post page)');
    await Promise.all([page.waitForURL(/post\.html/, { timeout: 15000 }), page.click('#mr .mb-budget__btn[data-budget="supply"]')]);
    await page.waitForSelector('#pc-item', { timeout: 10000 });
    ok(new URL(page.url()).searchParams.get('initiative') === elected.winning_tiv_id, 'the button opens post.html on Supply, the initiative preselected');
    ok((await page.$$('#pc-item, #pc-supplier, #pc-cost')).length === 3, 'supply asks for an item, a supplier and a cost');
  } else ok(false, 'no mission with an elected initiative to test against');
  await page.goto(BASE + '/m/' + mission.id, { waitUntil: 'networkidle' });
  await page.waitForSelector('#mx-pre:not([hidden])', { timeout: 20000 });
  await page.waitForTimeout(500);

  section('the mission\'s thread (behind the report, in News; the mission page\'s MB.compose goes there)');
  await Promise.all([page.waitForURL(/cause\.html\?mission=/, { timeout: 15000 }), page.evaluate(() => window.MB.compose('research'))]);
  ok(new URL(page.url()).searchParams.get('mission') === mission.id, 'MB.compose(\'research\') opens News on this mission', page.url().replace(BASE, ''));
  await page.waitForSelector('#mr .mb-report__head', { timeout: 20000 });
  await page.waitForTimeout(500);
  await page.click('#mr .mb-report__head'); await page.waitForTimeout(700);
  const box = await page.$eval('#mxt-bg .mxc', e => { const r = e.getBoundingClientRect(); return { w: r.width, h: r.height }; });
  ok(!(await page.$eval('#mxt-bg', e => e.hidden)) && box.w > 700, 'a full-screen thread', box.w + '×' + box.h);
  ok(JSON.stringify(await page.$$eval('#mxt-tabs .mxc__type', els => els.map(e => e.childNodes[0].textContent.trim()))) ===
     '["Background","Investigation","Analysis"]', 'three sections before the initiative is elected — Investigation (P3); Budget joins after');
  await Promise.all([page.waitForURL(/post\.html/, { timeout: 15000 }), page.click('#mxt-write')]);
  await page.waitForSelector('#pc-cause', { timeout: 10000 });
  ok(await page.$eval('#pc-types .pc-pill[aria-pressed="true"]', e => e.textContent) === 'Background', '"Write yours" opens post.html on the section');
  await page.fill('#pc-title', 'What the survey measured');
  await page.fill('#pc-body', 'A background post from composer_check.');
  await page.click('#pc-send'); await page.waitForTimeout(1500);
  ok(/Posted/.test(await page.textContent('#pc-msg')), 'it posts', (await page.textContent('#pc-msg')).slice(0, 160));
  const posted = await page.evaluate(() => window.PostPage.last);
  await page.goto(BASE + '/cause.html?mission=' + encodeURIComponent((posted && posted.mission_id) || mission.id), { waitUntil: 'networkidle' });
  await page.waitForSelector('#mr .mb-report__head', { timeout: 20000 });
  await page.waitForTimeout(800);
  await page.evaluate(() => EBX.MissionReport.openThread()); await page.waitForTimeout(900);
  ok(/What the survey measured/.test(await page.textContent('#mxt-body')), 'the thread of the mission it landed in shows it');

  section('rate it, reply to it');
  const before = await page.$eval('#mxt-body .mb-rate [data-val="helpful"]', e => e.textContent.trim());
  await page.click('#mxt-body .mb-rate [data-val="helpful"]'); await page.waitForTimeout(1200);
  const after = await page.$eval('#mxt-body .mb-rate [data-val="helpful"]', e => e.textContent.trim());
  ok(before !== after, 'a helpful rating counts', before + ' → ' + after);
  await page.click('#mxt-body [data-treply]'); await page.waitForTimeout(400);
  ok(!(await page.$eval('#mxc-reply', e => e.hidden)), 'Reply names the post');
  await page.fill('#mxc-in-body', 'A reply from composer_check.');
  await page.click('#mxc-send'); await page.waitForTimeout(1500);
  ok(/Posted/.test(await page.textContent('#mxc-msg')), 'the reply posts');
  // 10/9 Reshuffle: a reply opens its post's replies by itself (ebx_report.js)
  await page.waitForTimeout(1200);
  let thr = await page.textContent('#mxt-body');
  if (!/A reply from composer_check/.test(thr)) { await page.click('#mxt-body [data-tshow]'); await page.waitForTimeout(900); thr = await page.textContent('#mxt-body'); }
  ok(/A reply from composer_check/.test(thr), 'and the thread shows it under the post');

  section('no script errors');
  ok(errors.length === 0, 'none', errors.slice(0, 3).join(' || '));
  await browser.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'COMPOSER CLEAN'));
  process.exit(bad ? 1 : 0);
})();
