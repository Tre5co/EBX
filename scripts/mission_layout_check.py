"""mission_layout_check — the mission page after build-seq P1, THE MERGE (2026-09-24).

    python3 scripts/mission_layout_check.py     # from the repo root; no server

Grown from `election_layout_check.py` (16 assertions, 2026-09-20), which read
main.html. main.html is a redirect now and the Elect page lives in
mission.html, so this reads mission.html and keeps every assertion that still
describes something on the page — the five ballots and their topbars, the
cause toggle's place and marks, the rename — and adds the merge:

  · main.html forwards, keeping its query; the nav is Home · Missions · News ·
    Inbox · Profile, with Inbox drawn but not live
  · the annulus is ONE component (EBX.Wheel) in its mission variant, with the
    toggler on its left and the overview on its right; the 5-phase toggle and
    the 7 cause toggles sit below it; the cause toggles carry their dates
  · every mission has a stable URL: /m and /m/<slug> are served, the page has
    <base href="/">, EBX.Slug builds the slug from the initiative title (D1)
  · the annulus leftovers are gone: renderPie, _buildPieSVG, updateCenter,
    the renderOne side cards, the dead .hero__* CSS, and all 13 dangling ids
    (F2) — the page reaches for no id it does not have
  · D5: six weeks in a row, everywhere

Review 2026-09-24 (INSTRUCTIONS "P1. Mission"), also pinned here:
  · the head reads "<Cause>: <Phase>"; the cause toggle sits above the phase
    toggle; the ballot tabs are folded into the phase toggle (D14) — one stage
  · the phase toggle keeps the mission (recap / not yet), the cause toggle
    keeps the phase, the navigator lists the toggled cause only
  · no allocations panel, no post-support ring, no discussion box, no "Show
    all Initiatives" / "Show active missions", no link to the page you are on
  · the posting dialogue at the foot of the story + the full-screen composer
  · D13 stored slugs with history · D15 six weekly elections, no aggregate
"""
import re, sys, os
R = lambda *p: os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', *p)
rd = lambda *p: open(R(*p), encoding='utf-8').read()
s = rd('mission.html')
main = rd('main.html')
shared = rd('resources', 'js', 'ebx_shared.js')
wheel = rd('resources', 'js', 'ebx_wheel.js')
css = rd('resources', 'css', 'ebx_frontend.css')
server = rd('backend', 'app', 'main.py')
crud = rd('backend', 'app', 'crud.py')
index = rd('index.html')
bad = 0; n = 0
def ok(c, what, detail=''):
    global bad, n
    n += 1
    if not c: bad += 1
    print('  %s  %s%s' % ('ok  ' if c else 'FAIL', what, ('  ' + detail) if detail else ''))

print('\n=== main.html is a redirect, the nav has five tabs')
ok(len(main.splitlines()) < 30 and "location.replace('mission.html' + location.search + location.hash)" in main,
   'main.html forwards to mission.html and keeps the query and hash')
nav = re.search(r'var NAV_TABS = \[(.*?)\];', shared, re.S).group(1)
labels = re.findall(r'label: "([^"]+)"', nav)
ok(labels == ['Home', 'Missions', 'News', 'Inbox', 'Profile'], 'Home · Missions · News · Inbox · Profile', ' · '.join(labels))
ok('href: null' in nav and 'ebx-nav__tab--soon' in shared and 'ebx-nav__tab--soon' in css, 'Inbox is drawn, not linked (a stub until P4)')
ok('"Elect"' not in nav, 'no Elect tab')

print('\n=== the ballots (kept from election_layout_check)')
ok(s.count('class="el3__tab"') == 5 and '.mx-stage .el3__tab { display: none; }' in s,
   'the five ballot tabs are still in the markup, folded into the phase toggle (D14)')
ok(len(re.findall(r'id="el3-top-(ce|me|oe|fr|ex)"', s)) == 5, 'five topbars in the markup')
ok('function renderBallotHeads' in s, 'the topbar renderer exists')
ok(s.count('renderBallotHeads()') >= 2, 'it is called from render() and setElectionCol()')
ok('_pickedMission' in s[s.index('function renderBallotHeads'):s.index('window.renderBallotHeads')],
   'the OE topbar names the pinned race first')
ok(s.count('id="cause-tabs"') == 1, 'only one cause toggle')
ok("cause-tab--me" in s and "cause-tab--oe" in s, 'the ME and OE causes are marked')
ok('cause-tab__date' in s, 'the cause toggles carry their next ballot date')
ok('situation' not in s.lower() or 'background · investigation' in s, 'no "situation" label left on this page')
ok('id="votebar-mount"' in s and 'id="init-table-body"' in s and 'id="fx-view"' in s,
   'the ballots, the table and the framing/exchange view moved in')

print('\n=== the annulus row, and the order of the page')
i_row = s.index('id="mx-row"'); i_ph = s.index('id="mx-phases"'); i_tabs = s.index('id="cause-tabs"')
i_el3 = s.index('id="el3"'); i_tbl = s.index('id="init-table-body"')
i_mb = s.index('id="mb"'); i_stage = s.index('id="mx-stage"'); i_recap = s.index('id="mx-recap"')
i_post = s.index('id="mx-postbar"'); i_report = s.index('id="mb-report"')
ok(i_tabs < i_row < i_stage < i_ph < i_post < i_recap < i_el3 < i_tbl < i_mb < i_report,
   '7 causes → the row → the stage (the phase log | post button, recap, ballot, TABLE) → the report (P1 edits 2026-09-28)')
ok(s.index('id="mx-stage"') < i_tbl < s.index('<section class="mb"'), 'the table sits inside the ballot panel (review 2)')
row = s[i_row:i_stage]
ok(row.index('id="mx-toggler"') < row.index('id="mx-wheel"') < row.index('id="mx-overview"'),
   'toggler left, wheel centre, overview right')
ok('id="mx-pager"' not in s and row.index('id="mx-search"') < row.index('id="mx-cards"') and 'Mission Navigator' in row
   and '.mx-cards--scroll' in s, 'the Mission Navigator: titled, search on top, one scrolling list, no pager (P1 edits 2026-09-28)')
ok("W().mount('#mx-wheel', { variant: 'mission'" in s, 'the wheel is EBX.Wheel in its mission variant')
ok("variant === 'mission'" in wheel and 'function show(' in wheel and 'onFocus' in wheel and 'function pinFor(' in wheel,
   'ebx_wheel.js has the variant, show(), the sector hand-off and the pinned race')
ok("'.lw {" not in index and '.lw-wheel' in css and '.lw--mission' in css, 'the wheel’s CSS is shared, not copied')
ok('ebx-top-card-mount' not in s.split('<script')[0], 'the two top cards are gone from the markup')
mx = s[s.index('function paintOverview'):s.index('async function loadOverview')]
for k in ['Phase', 'Cause', 'Initiative', 'Organization', 'Guaranteed', 'Committed', 'EBX value', 'EBX spent', 'Members']:
    ok("row('%s'" % k in mx, 'overview row: ' + k)
mx_real = mx[mx.index('const win = tivById'):]
ov = [(mx if k in ('Phase', 'Cause') else mx_real).index("row('%s'" % k) + (0 if k in ('Phase', 'Cause') else 10**6) for k in ['Phase', 'Cause', 'Initiative', 'Organization', 'Guaranteed', 'Committed', 'EBX value', 'EBX spent', 'Members']]
ok(ov == sorted(ov), '…in D3’s order')
ok('"/{mission_id}/overview"' in rd('backend', 'app', 'routers', 'missions.py') and 'def mission_overview' in rd('backend', 'app', 'wallet.py'),
   'the pools come from one read-only endpoint over the token model')

print('\n=== D1 — every mission has a URL')
ok('<base href="/" />' in s, '<base href="/"> so /m/<slug> resolves the page’s assets')
ok('@app.get("/m", include_in_schema=False)' in server and '@app.get("/m/{slug}", include_in_schema=False)' in server,
   'the server hands mission.html to /m and /m/<slug>')
ok('var Slug =' in shared and 'Slug,' in shared and 'function slugify' in shared, 'EBX.Slug exists and is exported')
ok(r'/^[a-z]{3}\d+$/.test(s)' in shared, 'a slug can never look like a mission id')
ok('history.pushState' in s and "addEventListener('popstate'" in s, 'toggling pushes history; Back works')
ok("mission.html?state=" in wheel and "main.html?state=" not in wheel, 'the landing wheel links the mission page directly')

print('\n=== D2 · D4 — the toggler, and what a cause toggle does')
ok("[windowFor(cid), newestIn('tiv', cid), newestIn('org', cid)]" in s, 'page one: the newest in CE, ME and OE — of the toggled cause (D16)')
ok('function goCause' in s and "missionFor(S.step, cid)" in s[s.index('function goCause'):s.index('function goCause') + 300]
   and "if (step === 'tiv') return W().meMission(cid);" in s,
   'a cause toggle (or sector) goes to that cause’s mission in the phase shown — its current initiative election on phase 2 (D4)')
ok("window.selectCause = function" in s and "window.selectMission = function" in s,
   'the cause tabs and the race rows both move the whole page')

print('\n=== the annulus leftovers are gone (F2)')
for fn in ['function renderPie', 'function _buildPieSVG', 'function updateCenter', 'const renderOne',
           'function _bindCardFilterClicks', 'renderControlBlock(active']:
    ok(fn not in s, 'no ' + fn)
style = re.sub(r'/\*.*?\*/', '', s[s.index('<style>'):s.index('</style>')], flags=re.S)   # rules, not comments
for cls in ['hero__layout', 'hero__side', 'hero__center', 'hero__annulus-wrap', 'hero__pie', 'hero__statetoggle',
            'st-side', 'st-now', 'ebx-center', 'hero__topgrid']:
    ok(not re.search(r'\.' + cls + r'(?![\w-])', style), 'no .' + cls + ' CSS')
missing = {i for i in set(re.findall(r"getElementById\(['\"]([a-zA-Z0-9\-_]+)['\"]\)", s))
           if ('id="%s"' % i) not in s and ("id=\"' + " not in i)}
ok(not missing, 'every getElementById target exists (was 13 dangling)', ', '.join(sorted(missing)))
ok("onclick=\"setOeScope(window._oeScope()" in s, 'F12: "Show all races" calls the accessor, not the let')

print('\n=== D5 — six weeks in a row, everywhere')
ok('CAUSE_STREAK_WEEKS = 6' in crud and 'CAUSE_ROTATION = 7' in crud, 'backend: streak 6, rotation 7 — two numbers')
ok('const CAUSE_STREAK_WEEKS = 6;' in s and 'const CAUSE_ROTATION = 7;' in s, 'page: the same two numbers')
ok('weeks_required || 7' not in wheel, 'the wheel’s fallback says 6')
ok(not re.search(r'(seven|7) (consecutive )?weeks in a row|seven consecutive', s + wheel + rd('README.md') + rd('docs', 'mission_model.md'), re.I),
   'no "seven weeks in a row" left in the page, the wheel, the README or mission_model')

print('\n=== review 2026-09-24')
mx = s[s.index('// ══ MX'):]
ok("h1.textContent = named || STEP_TITLE[S.step];" in mx and "tiv: 'Initiative Election'" in mx
   and "S.step !== 'cause' && S.step !== 'tiv'" in mx,
   'the title above the annulus: the phase for the cause and initiative elections, the mission title after (P1 edits 2026-09-28)')
wc = s[s.index('<div class="mx-wheelcell">'):s.index('<aside class="mx-side mx-panel" aria-label="Mission overview">')]
ok(wc.index('id="mx-title"') < wc.index('id="mx-wheel"') and '.lw--mission .lw-cap { display: none; }' in s,
   '…above the wheel, and the caption under the wheel is gone')
ok("got('Initiative'" in mx and "now('Electing the organization'" in mx, '…naming what exists and what is being elected')
ok("go({ mission: S.mission, tiv: S.tiv, cause: S.cause, step: st }" in mx, 'a phase click keeps the mission')
ok("go({ mission: missionFor(S.step, cid), cause: cid, step: S.step }" in mx, 'a cause click keeps the phase')
ok('function paintRecap' in mx and "when: 'past'" in mx and "when: 'future'" in mx,
   'a past phase shows a recap, a future one says not yet')
ok('info.short' in mx[mx.index('function paintPhases'):mx.index('function paintRecap')],
   '…and each phase tab carries its recap line and date even when closed')
ok("causeMissions(cid)" in mx[mx.index('function navList()'):mx.index('function cardHTML')], 'the navigator lists the toggled cause only')
ok('PER_PAGE' not in mx and 'S.page' not in mx, 'no pages left to turn')
ok("'cause-tab--me'" not in s and 'cause-tab__mark">' not in s and 'window._causeTabDate' in s,
   'one glow on the cause toggle — no ME/OE marks — and the selected phase’s date on each tab')
code = re.sub(r'<!--.*?-->', '', re.sub(r'/\*.*?\*/', '', s, flags=re.S), flags=re.S)
code = '\n'.join(l for l in code.split('\n') if not l.strip().startswith('//'))
for gone in ['id="alloc-mount"', 'id="oe-actions-mount"', 'id="show-all-inits"', 'id="show-cause-missions"',
             'id="ps-ring"', 'id="mp-disc"', 'ebx_postsbox.js', 'Open the mission page',
             'make your case', 'View Organizations']:
    ok(gone not in code, 'gone: ' + gone)
ok(not re.search(r"href=\"mission\.html\?mission=' \+", s), 'no link to mission.html?mission= — the page you are on')
for k in ["'context', 'Background'", "'investigation', 'Vetting'", "'analysis', 'Analysis'",
          "'service', 'Service'", "'supply', 'Supply'", "'support', 'Support'"]:
    ok(k in s, 'composer type ' + k.split(',')[1].strip())
ok('id="mxc-bg"' in s and 'Make the image or video the post' in s and "C.cat === 'review'" in s,
   'the full-screen composer: media drawn (P3), review is a reply to anything')
print('\n=== review 2 (2026-09-25)')
ok('function paintHow' not in mx and 'id="mx-how"' not in s and 'href="about.html#ab-phases"' in s,
   'P1 edits (2026-09-28): Process / Reason left for the About page; the log links there')
ok('function budgetHTML' in s and 'data-budget="service"' in s and 'function renderBudget' in s
   and 'id="mb-budget-add"' not in s and "if (!mission || !mission.winning_tiv_id) return '';" in s,
   'P1 edits: budget posting + explanation live in the report, once the initiative is elected')
for k in ['Mission statement', 'Plan']:
    ok("<h4>" + k + "</h4>" in s, 'the report has: ' + k)
ok("['investigation', 'Vetting'" in s and "['context', 'Background'" in s and "['analysis', 'Analysis'" in s,
   '…and Background · Organization · Analysis, each its leading post')
ok('id="mxt-bg"' in s and "report.addEventListener('click', e =>" in s and 'openThread();' in s and '/react' in s,
   'clicking the report opens its thread: read, rate (POST /posts/{id}/react), reply, write')
ok('id="mp-cattabs"' not in s and 'id="mb-post"' not in s, 'budgeting and research are no longer two toggles of one list')

print('\n=== P1 mission edits (2026-09-28)')
ok('mx-phase--row' in mx and 'eventsFor: mid =>' in s and 'id="mp-log"' not in s,
   'the progress log IS the phase toggle — one row per phase: title and date (mission pass 2026-10-01)')
ok('.mx-stage { display: grid; grid-template-columns: 236px minmax(0, 1fr)' in s, '…with the ballot to its right')
for st, t in [('cause', 'context'), ('tiv', 'context'), ('org', 'investigation'), ('frame', 'analysis')]:
    ok("%s: { cat: 'mission_support', type: '%s'" % ('cause' if st == 'cause' else st, t) in mx or
       ("%s:   { cat: 'mission_support', type: '%s'" % (st, t)) in mx or ("%s: { cat: 'mission_support', type: '%s'" % (st, t)) in mx,
       'the %s ballot has a post button: %s' % (st, t))
ok("ex:    { cat: 'budgeting'" in mx, 'the exchange ballot has a post button: a budget item')
ok('function lostTiv' in mx and 'Initiative election · closed' in mx and 'data-step="tiv"' in mx,
   'an initiative that lost gets a page with its ballot locked and a link to the next election')
ok("(col === 'me' && (_mainMode !== 'tiv' || _tableTab !== 'me'))" in s, 'bug: leaving the cause tab puts the table back on initiatives')
ok("const causeOf = causeF || ((typeof window.voteCauseId === 'function')" in s, 'bug: the initiative table is always one cause\u2019s')
ok("_th('cause', 'Cause', 'Sort by cause')" not in s and 'init-table__cause" style' not in s, 'the initiative table has no Cause column')
wal = rd('backend', 'app', 'wallet.py')
ok('def _voted_in_me(' in wal and 'or _voted_in_me(db, ben_id, m.id)' in wal and wal.count('_voted_in_me(db, ben_id, mission_id)') == 2,
   'bug: voting in a mission\u2019s initiative election opens its organization election in any week (ruling 16)')

print('\n=== D13 · D15')
ok(os.path.exists(R('backend', 'alembic', 'versions', 'c9e4a7d2b6f1_sep24_initiative_slugs.py'))
   and 'class InitiativeSlug' in rd('backend', 'app', 'models.py'), 'initiative_slugs: the table and its migration')
ok('def ensure_slug(' in crud and 'def rename_tiv(' in crud and '"/slugs"' in rd('backend', 'app', 'routers', 'initiatives.py'),
   'a rename keeps the old slug; GET /initiatives/slugs lists them all')
ok('async function load()' in shared and 'await EBX.Slug.load()' in s, 'the page reads the stored slugs before it resolves the URL')
ok('for k in range(CAUSE_STREAK_WEEKS):' in crud and 'CAUSE_LOOKBACK_WEEKS' not in crud,
   'D15: six weekly elections, no aggregate column')

print('\n=== Mission pass (2026-10-01) — Jax\'s P1 list')
shared_js = rd('resources', 'js', 'ebx_shared.js')
pcfg = rd('backend', 'app', 'post_config.py')
tivr = rd('backend', 'app', 'routers', 'initiatives.py')
walr = rd('backend', 'app', 'routers', 'wallet.py')
ok('Suggest a mission statement' in shared_js and 'async _statement(tivId, text)' in shared_js
   and '"mission_statement",' in pcfg and 'MISSION_STATEMENT_MAX = 280' in pcfg,
   'proposing an initiative: a title and an optional mission statement — a general post tagged mission_statement (≤280)')
ok("mx-phase--row" in mx and "mx-phase__ev" not in mx[mx.index('function paintPhases'):mx.index('function paintRecap')],
   'the progress log is one row per phase — title and date, nothing else')
ok('ce-bars--slate' in s and "filter(x => x.slot >= CAUSE_FIRST_OPEN)" in s and 'ce-bars__row--lit' in s
   and 'ce-bars__row--dim' in s and 'ce-bars__row--here' in s,
   'the cause panel: six-segment bars for each of the seven open windows — lit with a challenger, dim without, this page marked')
ok("bars + votes + pager + dist + barHTML" in s and '+ Nominate a cause' in s,
   '…then keep / replace, then the click-through with "Nominate a cause" on its right')
ok(">+ post</button>" in s and "POST[o.step] + ' &rarr;</button>'" not in s, 'every ballot ends in "+ post", not "Post a <type>"')
ok('tiv_is_elected' in tivr and 'only the initiative\'s proposer can rename it' in tivr
   and 'data.proposer_ben_id = user.id' in tivr and 'window._tivRenameSave' in s,
   'the proposer renames an initiative until it is elected (PUT /initiatives/{id}/title)')
ok('suggestOnly' in shared_js and "+ Suggest an organization" in s and 'window._nominateExisting' in s,
   'an organization can be suggested for an initiative before it wins; its race lists the suggestion to nominate')
ok('rowConvert' not in s and '⇄ Convert' not in s, 'no Convert in the initiative election')
ok('function _meExpansionHTML' in s and 'Selected Initiative' not in s[s.index('function _meExpansionHTML'):s.index('function _meExpansionHTML') + 6000]
   and 'data-prev-tiv' in s and 'vb-x__slider' in s,
   'the initiative expansion is small: a slider row, a post preview, its page, suggest an org, + post')
ok('function _oeExpansionHTML' in s and "o.myOrg || o.leadId" in s,
   'the organization expansion: the picked organization, else my vote, else the leader')
ok("el3__top-tiv" in s and "Finalized on" in s and "'Cause for the window that runs" not in s,
   'the header line reads "Finalized on x"; organization · framing · exchange add the initiative on the right')
ok('vb-stake--ro' in s and "'Donate more' : 'Donate'" in s and 'id="vb-amt-\' + mid' not in s,
   '"My stake" is a figure, not a box; with no stake the button just says Donate')
ok('/row/{mission_id}' in walr and 'window._fetchOeRow' in s and 'derived = crud.p2_ebx_by_ben(db, mission_id)' in wal,
   'withdraw: the stake is read the way the page reads it, even outside the eight rows (the "no slate" bug)')
ok('id="mx-pre"' in s and 'function paintPrePosts' in s, 'before the report: the posts on the causes / the initiatives below the table')
ok('mb-budget__add--plan' in s and 'Budget items are how this mission gets planned' not in s,
   'the budget suggestions sit in the plan; the budget description is gone')
ok('/initiatives/descriptions-to-posts' in rd('backend', 'app', 'routers', 'admin.py') and 'def tiv_descriptions_to_posts' in crud,
   'initiative descriptions become Mission statements or Justifications (staff endpoint, dry run by default)')

print('\n' + ('FAILED %d/%d' % (bad, n) if bad else 'all %d checks passed' % n))

sys.exit(1 if bad else 0)
