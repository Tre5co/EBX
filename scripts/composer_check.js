// composer_check — the mission story's budget panel, report, report thread and
// composer, in a real browser.
//
//   node scripts/composer_check.js [http://127.0.0.1:8000]
//
// Review 2 (2026-09-25, INSTRUCTIONS "P1. Mission"): budgeting and research are
// separate. Budget items live in the panel beside the progress log, with the
// "suggest a budget item" buttons at its foot. Under them, the mission REPORT is
// the page's main display — the leading post of each category: a mission
// statement, a plan, Background · Vetting · Analysis (Organization until P2, 2026-09-25). Clicking it opens
// the thread, where research posts are read, rated, replied to and written.
// Posting goes through POST /posts, so its rules still apply: the account first
// commits a stake in this week's initiative election (the membership the gate
// asks for; P3 lifts the gates). Replaces posts_box_check.js.
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
  await page.waitForSelector('#mb-report .mb-report__sec', { timeout: 20000 });
  await page.waitForTimeout(500);

  section('the story: a budget panel, then the report');
  ok(JSON.stringify(await page.$$eval('#mb-budget-add .mb-budget__btn b', els => els.map(e => e.textContent))) === '["Service","Supply","Support"]',
     'the budget panel ends in Suggest: Service · Supply · Support');
  const heads = await page.$$eval('#mb-report .mb-report__sec h4', els => els.map(e => e.childNodes[0].textContent.trim()));
  ok(JSON.stringify(heads) === '["Mission statement","Plan","Background","Vetting","Analysis"]',
     'the report: mission statement · plan · background · organization · analysis', heads.join(' · '));
  ok((await page.$$('#mp-cattabs, #mb-post, #mp-disc, #pb, #ps-ring')).length === 0,
     'no posts toggle, no old dialogue, no discussion box, no post-support ring');

  section('budget: a costed supply item, from the panel');
  await page.click('.mb-budget__btn[data-budget="supply"]'); await page.waitForTimeout(300);
  ok((await page.$$('#mxc-item, #mxc-supplier, #mxc-cost')).length === 3, 'supply asks for an item, a supplier and a cost');
  await page.fill('#mxc-in-title', 'Air-quality sensors'); await page.fill('#mxc-in-body', 'Forty sensors.');
  await page.fill('#mxc-item', '40 air-quality sensors'); await page.fill('#mxc-supplier', 'Acme'); await page.fill('#mxc-cost', '4000');
  await page.click('#mxc-send'); await page.waitForTimeout(1300);
  ok(/Posted/.test(await page.textContent('#mxc-msg')), 'it posts', await page.textContent('#mxc-msg'));
  await page.waitForTimeout(900);
  ok(/Air-quality sensors/.test(await page.textContent('#mp-posts')), 'it is in the budget panel');
  ok(/Air-quality sensors/.test(await page.textContent('#mb-report')), '…and in the report’s plan');

  section('the report opens its thread');
  await page.click('#mb-report'); await page.waitForTimeout(700);
  const box = await page.$eval('#mxt-bg .mxc', e => { const r = e.getBoundingClientRect(); return { w: r.width, h: r.height }; });
  ok(!(await page.$eval('#mxt-bg', e => e.hidden)) && box.w > 700, 'a full-screen thread', box.w + '×' + box.h);
  ok(JSON.stringify(await page.$$eval('#mxt-tabs .mxc__type', els => els.map(e => e.childNodes[0].textContent.trim()))) ===
     '["Background","Vetting","Analysis"]', 'three sections — "investigation" reads Vetting (P2)');
  await page.click('#mxt-write'); await page.waitForTimeout(400);
  ok(await page.$eval('#mxc-types .mxc__type.on', e => e.textContent) === 'Background', '"Write yours" opens the composer on the section');
  await page.fill('#mxc-in-title', 'What the survey measured');
  await page.fill('#mxc-in-body', 'A background post from composer_check.');
  await page.click('#mxc-send'); await page.waitForTimeout(1500);
  ok(/Posted/.test(await page.textContent('#mxc-msg')), 'it posts');
  await page.waitForTimeout(900);
  ok(/What the survey measured/.test(await page.textContent('#mxt-body')), 'the thread shows it');
  ok(/What the survey measured/.test(await page.textContent('#mb-report')), 'and the report leads with it');

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
  await page.waitForTimeout(700);
  await page.click('#mxt-body [data-tshow]'); await page.waitForTimeout(900);
  ok(/A reply from composer_check/.test(await page.textContent('#mxt-body')), 'and the thread shows it under the post');

  section('no script errors');
  ok(errors.length === 0, 'none', errors.slice(0, 3).join(' || '));
  await browser.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'COMPOSER CLEAN'));
  process.exit(bad ? 1 : 0);
})();
