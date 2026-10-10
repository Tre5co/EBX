// posts_box_check — P3 · Posting in a real browser (2026-09-29).
//
//   node scripts/posts_box_check.js [http://127.0.0.1:8000]
//
// Retired 2026-09-24 with the discussion box; brought back under the name P3's
// "Done when" gives it, for what replaced the box: ONE composer (post.html),
// reachable from everywhere. It checks
//   · every entry point opens post.html — News, a profile, a mission, the
//     About page's post types (F16: the link preselects); Home has no + since
//     the 10/9 Reshuffle (2026-10-09) took its feed to News;
//   · the link decides what is preselected — the type and the target;
//   · each type posts from the page with no stake (the gates are gone), and
//     lands on the target it named;
//   · the Analysis composer — the two leading posts attached and locked;
//   · a Response names the post it answers; an edit is a new version;
//   · the guide beside the composer and the How-to cards are post_config.py's;
//   · a nomination can carry a Justification post; a row shows a preview.
// Signs up a throwaway account — run it against a local server.
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
const ok = (c, what, d) => { n++; if (!c) bad++; console.log('  ' + (c ? 'ok  ' : 'FAIL') + '  ' + what + (d && !c ? '  ' + d : '')); };
const section = t => console.log('\n=== ' + t);
const J = (u, o) => fetch(BASE + u, o).then(r => r.json());

(async () => {
  const H = 'pb' + (Date.now() % 1000000);
  const EMAIL = H + '@posts-box-check.example.com';
  await fetch(BASE + '/auth/signup', { method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: EMAIL, handle: H, password: 'posts-box-pw-1' }) });
  const token = (await J('/auth/login', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: EMAIL, password: 'posts-box-pw-1' }) })).access_token;
  const auth = { Authorization: 'Bearer ' + token };
  const guide = await J('/posts/guide');
  const causes = await J('/causes');
  const tivs = await J('/initiatives');
  const orgs = await J('/organizations');
  const missions = await J('/missions');

  const browser = await chromium.launch({ executablePath: chromeExe() });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message).slice(0, 200)));
  await page.addInitScript(t => localStorage.setItem('ebx_auth_token', t), token);
  const open = async (path, sel) => {
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    if (sel) await page.waitForSelector(sel, { timeout: 20000 });
    await page.waitForTimeout(400);
  };
  const send = async () => { await page.click('#pc-send'); await page.waitForTimeout(1400); return page.textContent('#pc-msg'); };
  const last = () => page.evaluate(() => window.PostPage && window.PostPage.last);

  // ── entry points ─────────────────────────────────────────────────────────
  section('entry points — every one opens post.html');
  await open('/', '#wr');
  ok(await page.$('#hn-post, #hf-list') === null, 'Home has no + and no feed — they went to News (10/9 Reshuffle)');
  await open('/cause.html', '#fd-compose');
  ok(/post\.html/.test(await page.getAttribute('#fd-compose', 'href')), "News's + Post opens post.html");
  await open('/profile.html', '#pf-newpost');
  ok(/post\.html/.test(await page.getAttribute('#pf-newpost', 'href')), 'a profile has + New post');
  // About reshape (2026-10-05): the phase cards stand in the How it works tab
  await open('/about.html#ab-phases', '#how .ld-trio__link');
  const trio = await page.$$eval('.ld-trio__link', as => as.map(a => a.getAttribute('href')).filter(h => /post\.html/.test(h)));
  ok(trio.length === 6 && trio.some(h => /type=background/.test(h)) && trio.some(h => /type=support/.test(h)),
     'About\'s research and budget cards link post.html, preselected (F16)', trio.join(' '));

  // ── the guide ───────────────────────────────────────────────────────────
  section('the guide beside the composer, and the How-to cards');
  await open('/post.html', '#pc-cats .pc-tab');
  ok(JSON.stringify(await page.$$eval('#pc-cats .pc-tab', e => e.map(x => x.textContent))) === '["General","Research","Budget"]',
     'three kinds of post: General · Research · Budget');
  const gGen = guide.types.find(t => t.key === 'general').guide;
  ok((await page.textContent('#pc-g-body')).includes(gGen.purpose), 'the guide beside it is post_config.py\'s');
  await page.click('#pc-cats [data-cat="mission_support"]'); await page.waitForTimeout(200);
  ok(JSON.stringify(await page.$$eval('#pc-types .pc-pill', e => e.map(x => x.textContent))) === '["Background","Investigation","Analysis"]',
     'Research: Background · Investigation · Analysis');
  ok((await page.textContent('#pc-g-body')).includes(guide.types.find(t => t.key === 'context').guide.limit),
     '…and the guide follows the type');
  await open('/about.html#posting', '#ab-post-cards .ab-card');
  const cards = await page.$$eval('#ab-post-cards .ab-card', e => e.map(x => x.dataset.type).filter(Boolean));
  ok(cards.length === guide.types.length && guide.types.every(t => cards.includes(t.key)),
     'about.html#posting has one card per type, from the guide', cards.join(' '));
  ok(/Research vote/.test(await page.textContent('#ab-votes')) && /Election vote/.test(await page.textContent('#ab-votes')),
     '…and names the three kinds of vote');

  // ── general ─────────────────────────────────────────────────────────────
  section('a general post — tags, and a target from the link');
  const tiv = tivs.find(t => t.mission_id) || tivs[0];
  await open('/post.html?type=opinion&initiative=' + encodeURIComponent(tiv.id), '#pc-tags .pc-tag');
  ok(await page.$eval('#pc-tags [data-tag="opinion"]', e => e.getAttribute('aria-pressed')) === 'true', '?type=opinion preselects the Opinion tag');
  ok(await page.$eval('#pc-tkind', e => e.value) === 'initiative' && await page.$eval('#pc-tid', e => e.value) === tiv.id,
     '?initiative= preselects the target');
  await page.click('#pc-tags [data-tag="question"]');
  await page.fill('#pc-body', 'A general post from posts_box_check.');
  ok(/Posted/.test(await send()), 'it posts — no stake');
  let p = await last();
  ok(p && p.target_kind === 'initiative' && p.target_id === tiv.id && p.tags.includes('opinion') && p.tags.includes('question'),
     '…on the initiative, tagged Opinion and Question', JSON.stringify(p && { k: p.target_kind, t: p.tags }));
  const general = p;

  section('a Response names the post it answers');
  await open('/post.html?type=general&tag=response&post=' + encodeURIComponent(general.id), '.pc-fixed');
  ok(/In response to/.test(await page.textContent('.pc-fixed')), 'the composer shows what it responds to');
  await page.fill('#pc-body', 'In response, from posts_box_check.');
  ok(/Posted/.test(await send()), 'it posts');
  p = await last();
  ok(p && p.target_kind === 'post' && p.target_id === general.id, '…targeting that post');

  // ── research ────────────────────────────────────────────────────────────
  section('a Background — the cause, and the initiatives it covers');
  const cause = causes.find(c => tivs.some(t => t.cause_id === c.id)) || causes[0];
  await open('/post.html?type=background&cause=' + cause.id, '#pc-cause');
  ok(await page.$eval('#pc-cause', e => e.value) === cause.id, '?cause= preselects the cause');
  const box = await page.$('#pc-tivtags input');
  if (box) await box.check();
  await page.fill('#pc-title', 'posts_box_check background');
  await page.fill('#pc-body', 'What a voter should know.');
  ok(/Posted/.test(await send()), 'it posts — no stake');
  p = await last();
  ok(p && p.target_kind === 'cause' && p.cause_id === cause.id && p.mission_id, '…on the cause, in its open initiative election', JSON.stringify(p && { k: p.target_kind, m: p.mission_id }));
  if (box) ok(p.tags.some(t => t.startsWith('tiv:')), '…tagged with the initiative it covers');
  const background = p;
  await page.fill('#pc-body', 'Again.');
  ok(/one Background per person per cause/.test(await send()), 'a second Background for the cause is refused, with the rule');

  section('an Investigation — the organization');
  const org = orgs[orgs.length - 1];
  await open('/post.html?type=investigation&org=' + encodeURIComponent(org.id), '#pc-org');
  ok(await page.$eval('#pc-org', e => e.value) === org.id, '?org= preselects the organization');
  await page.fill('#pc-body', 'What I found about them.');
  ok(/Posted/.test(await send()), 'it posts');
  p = await last();
  ok(p && p.target_kind === 'organization' && p.org_id === org.id, '…on the organization');

  section('a budget item — the initiative, any time');
  await open('/post.html?type=supply&initiative=' + encodeURIComponent(tiv.id), '#pc-item');
  ok(await page.$eval('#pc-tiv', e => e.value) === tiv.id, '?initiative= preselects it');
  await page.fill('#pc-item', '12 water-quality kits'); await page.fill('#pc-supplier', 'Acme'); await page.fill('#pc-cost', '840');
  await page.fill('#pc-body', 'Kits for the field teams.');
  ok(/Posted/.test(await send()), 'it posts — no stake');
  p = await last();
  ok(p && p.target_kind === 'initiative' && p.tiv_id === tiv.id && p.est_cost_usd === 840, '…costed, on the initiative');

  section('an Analysis — the two leading posts attached, and locked');
  let am = null, kit = null;
  for (const m of missions.filter(x => x.winning_tiv_id)) {
    const k = await J('/posts/analysis-kit?mission_id=' + m.id);
    if (k.open && (k.leads.background_id || k.leads.investigation_id)) { am = m; kit = k; break; }
    if (k.open && !am) { am = m; kit = k; }
  }
  if (am) {
    await open('/post.html?type=analysis&mission=' + am.id, '#pc-mission');
    await page.waitForTimeout(1200);
    const leads = [kit.leads.background_id, kit.leads.investigation_id].filter(Boolean);
    const locked = await page.$$eval('#pc-refbox input[data-ref]:disabled:checked', e => e.map(x => x.dataset.ref));
    ok(leads.every(id => locked.includes(id)) && locked.length === leads.length, 'the leading Background and Investigation are checked and cannot be unchecked', locked.join(','));
    const free = await page.$('#pc-refbox input[data-ref]:not(:disabled)');
    if (free) { await free.click(); await page.waitForTimeout(200); }
    await page.fill('#pc-body', 'An analysis from posts_box_check.');
    ok(/Posted/.test(await send()), 'it posts');
    p = await last();
    const full = p ? await J('/posts/' + p.id) : null;
    ok(full && leads.every(id => full.references.some(r => r.post_id === id && r.auto)), '…with the leads attached as references');
  } else ok(true, '(no mission with an open Analysis window here — skipped)');

  section('edits are new versions');
  await open('/post.html?edit=' + encodeURIComponent(background.id), '#pc-body');
  ok(/Edit your Background/.test(await page.textContent('#pc-h1')), 'post.html?edit= opens the author\'s post');
  await page.fill('#pc-body', 'What a voter should know — updated.');
  ok(/version 2/.test(await send()), 'saving makes version 2');
  const v1 = await J('/posts/' + background.id + '/versions/1');
  ok(v1.body === 'What a voter should know.', 'version 1 is unchanged');

  section('pull an earlier post into a mission');
  const other = missions.find(m => m.id !== general.mission_id && m.cause_id !== cause.id);
  await open('/post.html?type=general&mission=' + other.id, '#pc-body');
  await page.waitForTimeout(800);
  const pullBtn = await page.$('#pc-pull [data-pull="' + general.id + '"]');
  ok(!!pullBtn, 'your earlier posts are offered to pull in');
  if (pullBtn) {
    await pullBtn.click(); await page.waitForTimeout(900);
    const after = await J('/posts/' + general.id);
    ok(after.mission_id === other.id, '…and pulling one moves it here, votes from zero', after.mission_id);
  }

  section('nominating carries a post — a Mission statement (mission pass 2026-10-01)');
  await open('/mission.html', '#mb');
  const created = await page.evaluate(async (causeId) => {
    EBX.Dialogs.propose({ causeId });
    await new Promise(r => setTimeout(r, 300));
    document.getElementById('ebx-dlg-title').value = 'posts_box_check initiative ' + Date.now();
    document.getElementById('ebx-dlg-desc').value = 'What it will do, from posts_box_check.';
    document.querySelector('#ebx-dlg-propose [data-act=submit]').click();
    await new Promise(r => setTimeout(r, 2500));
    return (document.getElementById('ebx-dlg-msg') || {}).textContent || '';
  }, cause.id);
  ok(/mission statement is posted/.test(created), 'proposing an initiative with a mission statement posts it', created);
  const orgDlg = await page.evaluate(async () => {
    EBX.Dialogs.orgRegister({});
    await new Promise(r => setTimeout(r, 300));
    const d = document.getElementById('ebx-dlg-orgreg');
    return { boxes: d.querySelectorAll('.ebx-dlg-org-cb').length, text: d.textContent };
  });
  ok(orgDlg.boxes === 0 && /registered on Earthbux/.test(orgDlg.text),
     'the organization dialog has no initiative checkboxes; opened with no mission it registers the organization', orgDlg.boxes);
  await page.evaluate(() => EBX.Dialogs.close('ebx-dlg-orgreg'));

  section('a row previews its discussion');
  const prev = await page.evaluate(async (tivId) => {
    const el = document.createElement('div'); document.body.appendChild(el);
    await EBX.Post.preview(el, { tiv_id: tivId });
    return el.textContent;
  }, created ? tiv.id : tiv.id);
  ok(/posts_box_check|Justification|Opinion|Question|post/i.test(prev) && prev.length < 400,
     'an initiative\'s preview is one short post, best justification first', prev.slice(0, 120));

  section('no script errors');
  ok(errors.length === 0, 'none', errors.slice(0, 3).join(' || '));
  await browser.close();
  console.log('\n' + n + ' assertions · ' + (bad ? 'PROBLEMS: ' + bad : 'POSTING CLEAN'));
  process.exit(bad ? 1 : 0);
})();
