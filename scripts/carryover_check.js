// Drives the OE **vote rollover** on main.html in a headless DOM
// (build-seq §1, 2026-08-14). The previous pass would not touch the selection
// path "without a test that drives a real vote" — this is that test.
//
// What it asserts:
//   · the carryover panel paints inside the OE voting area for a picked mission
//   · the slider's range is [send floor, what is here + what can be reclaimed],
//     so after a roll there is still somewhere to drag BACK to
//   · the label names the elected initiative ("commit to …"), not "keep here"
//   · keep + roll always add up to the ORIGINAL commitment
//   · dragging wakes the area's single [Commit]
//   · a roll and a reclaim both round-trip through the API, and the org race's
//     EBX follows the slider in both directions
//
// Usage:  node scripts/carryover_check.js [BASE] [TOKEN] [MISSION]
// A TOKEN is a bearer token for a benefactor with a commitment in MISSION;
// mint one with backend/app/auth.create_access_token. Without it the script
// still checks the signed-out path (the panel must not paint at all).
const { JSDOM, VirtualConsole } = require('jsdom');

const BASE = process.argv[2] || 'http://127.0.0.1:8000';
const TOKEN = process.argv[3] || '';
const MISSION = process.argv[4] || 'lan0';

(async () => {
  const errs = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => {
    const m = String(e.message || e);
    if (!/fonts\.googleapis\.com/.test(m)) errs.push(m.slice(0, 240));
  });
  vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ').slice(0, 200)));

  const dom = await JSDOM.fromURL(BASE + '/main.html?state=oe', {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
      w.matchMedia = w.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
      w.alert = () => {};
      // Sign in before any script runs: EBX.Auth reads the token out of
      // localStorage on boot, so setting it afterwards is a page too late.
      if (TOKEN) try { w.localStorage.setItem('ebx_auth_token', TOKEN); } catch (e) {}
    },
  });
  await new Promise(r => setTimeout(r, 4500));
  const d = dom.window.document, W = dom.window;

  let bad = 0;
  const say = (label, ok, extra) => {
    console.log((ok ? '  ok    ' : '  FAIL  ') + label + (extra ? '  ' + extra : ''));
    if (!ok) bad++;
  };
  const panel = () => d.querySelector('#votebar-mount .carryover');
  const txt = s => { const e = d.querySelector(s); return e ? e.textContent.trim() : ''; };
  const api = async (path, opts) => {
    const r = await fetch(BASE + path, Object.assign({
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + TOKEN },
    }, opts || {}));
    return r.ok ? r.json() : { _status: r.status };
  };
  const settle = async () => { await new Promise(r => setTimeout(r, 1200)); };

  if (!TOKEN) {
    W.selectMission(MISSION);
    await settle();
    say('signed out — no carryover panel', !panel());
    say('no script errors', errs.length === 0, errs[0] || '');
    console.log('\n' + (errs.length ? 'PROBLEMS' : 'SIGNED-OUT PATH CLEAN'));
    process.exit(errs.length ? 1 : 0);
  }

  // ── the selection path ────────────────────────────────────────────────
  // The pass before this one would not touch row selection "without a test
  // that drives a real vote". These are that test.
  const missions = await (await fetch(BASE + '/missions')).json();
  const mission = missions.find(m => m.id === MISSION) || {};

  W.selectMission(MISSION);
  await settle();
  const row = () => d.querySelector('#init-table-body tr[data-mission="' + MISSION + '"]');
  const rowOpen = () => { const r = row(); return !!(r && r.nextElementSibling &&
    r.nextElementSibling.classList.contains('init-detail-row')); };
  say('picking a mission points the voting area at it', W._pickedMission() === MISSION);

  // The reported bug: pressing the race you are already in emptied the dialog.
  W.selectMission(MISSION);
  await settle();
  say('pressing the same mission again does NOT clear it',
      W._pickedMission() === MISSION, 'picked=' + W._pickedMission());
  // NB: `.votebar__empty` does double duty — "pick a mission" AND "no
  // organizations registered yet" — so the tell is the TITLE. The unpicked
  // state titles the kind of election; a picked one titles the race.
  say('and the voting area still names that race',
      !!d.querySelector('#votebar-mount .votebar') &&
      txt('#votebar-mount .votebar__title') !== 'Philanthropy Election',
      txt('#votebar-mount .votebar__title'));

  // An org card's Vote from the INITIATIVE side has to cross over to the org
  // side and open the race, not filter the initiative table and stop.
  W.setMainMode('tiv');
  await settle();
  W.voteOnCause(mission.cause_id, MISSION);
  await settle();
  say('an OE card Vote flips the page to the organization side',
      !!d.querySelector('#st-oe.on'));
  say('and lands on that mission', W._pickedMission() === MISSION);
  say('and opens its row in the table', rowOpen());

  // Start from a known position: everything committed here.
  const start = await api('/missions/' + MISSION + '/p1/carryover');
  await api('/missions/' + MISSION + '/p1/carryover',
            { method: 'PUT', body: JSON.stringify({ keep_ebx: start.original_ebx }) });

  W.selectMission(MISSION);
  await W.loadCarryover(MISSION);
  await settle();

  const st = await api('/missions/' + MISSION + '/p1/carryover');
  say('the panel paints in the voting area', !!panel());
  say('nothing is rolled to begin with', st.already_rolled_ebx === 0,
      st.total_ebx + ' EBX here');

  const slider = d.querySelector('#votebar-mount .cy-slider input[type=range]');
  say('the slider is there', !!slider);
  if (slider) {
    // The ends round INWARD, so every position the handle can take is one the
    // server will actually write.
    say('its floor is the send, and never below it',
        Number(slider.min) >= st.min_keep_ebx,
        'min=' + slider.min + ' send=' + st.sent_to_pool_ebx);
    say('its ceiling is what can be committed, and never above it',
        Number(slider.max) <= st.max_keep_ebx && Number(slider.max) === Math.floor(st.max_keep_ebx),
        'max=' + slider.max + ' max_keep=' + st.max_keep_ebx);
  }
  const keepLabel = txt('#votebar-mount .cy-split span');
  say('the label names the elected initiative, not a location',
      /^commit to /.test(keepLabel) && !/keep here/i.test(keepLabel), keepLabel);
  say('the send is described as counting toward the vote',
      /counts toward your commitment and vote weight/.test(panel().textContent));

  // ── drag it down, and the Commit button wakes up ──
  const half = Math.round(st.total_ebx / 2);
  W.dragCarry(MISSION, half);
  const btn = d.querySelector('#oe-commit');
  say('dragging wakes [Commit]', !!btn && !btn.disabled);
  const shown = n => Number((txt('#cy-' + n).match(/-?\d+/) || [0])[0]);
  say('keep + roll = the original commitment',
      shown('keep') + shown('roll') === Math.round(st.original_ebx),
      shown('keep') + ' + ' + shown('roll') + ' = ' + Math.round(st.original_ebx));

  // ── the roll, through the API the page uses ──
  const pool0 = (await api('/missions/' + MISSION + '/p2/tally')).pool_ebx;
  const rolled = await api('/missions/' + MISSION + '/p1/carryover',
                           { method: 'PUT', body: JSON.stringify({ keep_ebx: half }) });
  say('the roll goes through', rolled.rolled_ebx > 0,
      rolled.rolled_ebx + ' EBX to ' + rolled.next_mission_id);
  const mid1 = await api('/missions/' + MISSION + '/p1/carryover');
  say('what rolled can still come back', mid1.reclaimable_ebx > 0,
      mid1.reclaimable_ebx + ' EBX reclaimable');
  say('the ceiling did NOT collapse to what is left',
      Math.abs(mid1.max_keep_ebx - st.original_ebx) < 0.01,
      'max_keep=' + mid1.max_keep_ebx + ' original=' + st.original_ebx);
  const tally1 = await api('/missions/' + MISSION + '/p2/tally');
  // Measured as a DELTA against the pool before the roll — the race holds every
  // benefactor's EBX, not just this one's.
  say('the org race lost exactly what rolled',
      Math.abs((pool0 - tally1.pool_ebx) - rolled.rolled_ebx) < 0.01,
      'race pool ' + pool0 + ' → ' + tally1.pool_ebx + ', rolled ' + rolled.rolled_ebx);

  // the repainted slider has to offer the way back
  await W.loadCarryover(MISSION);
  await settle();
  const slider2 = d.querySelector('#votebar-mount .cy-slider input[type=range]');
  say('the slider is still live after a roll', !!slider2);
  say('and it can be dragged back up', !!slider2 &&
      Number(slider2.max) > Number(slider2.value),
      slider2 ? 'value=' + slider2.value + ' max=' + slider2.max : '');

  // ── the reclaim ──
  const back = await api('/missions/' + MISSION + '/p1/carryover',
                         { method: 'PUT', body: JSON.stringify({ keep_ebx: st.original_ebx }) });
  say('the reclaim goes through', back.reclaimed_ebx > 0, back.reclaimed_ebx + ' EBX back');
  const mid2 = await api('/missions/' + MISSION + '/p1/carryover');
  say('the commitment is whole again',
      Math.abs(mid2.total_ebx - st.original_ebx) < 0.01,
      mid2.total_ebx + ' vs ' + st.original_ebx);
  say('and nothing is left rolled', mid2.already_rolled_ebx === 0);
  const tally2 = await api('/missions/' + MISSION + '/p2/tally');
  say('the org race got its EBX back', Math.abs(tally2.pool_ebx - pool0) < 0.01,
      'race pool ' + tally2.pool_ebx + ' vs ' + pool0);

  // ── the floor holds ──
  const floored = await api('/missions/' + MISSION + '/p1/carryover',
                            { method: 'PUT', body: JSON.stringify({ keep_ebx: 0 }) });
  say('the send can never be rolled',
      Math.abs(floored.kept_ebx - st.sent_to_pool_ebx) < 0.01,
      'kept ' + floored.kept_ebx + ', send ' + st.sent_to_pool_ebx);
  await api('/missions/' + MISSION + '/p1/carryover',
            { method: 'PUT', body: JSON.stringify({ keep_ebx: st.original_ebx }) });

  say('no script errors', errs.length === 0, errs[0] || '');
  console.log('\n' + (bad || errs.length ? 'PROBLEMS: ' + (bad + errs.length) : 'ROLLOVER CLEAN'));
  process.exit(bad || errs.length ? 1 : 0);
})().catch(e => { console.error('could not run:', e.message); process.exit(1); });
