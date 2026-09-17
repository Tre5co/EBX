/* ebx_page.js — the small things every page was writing for itself.
 * ===========================================================================
 * Build-seq §6 (2026-09-08): "Some items in main.html should be moved to a
 * resources/ .js module."
 *
 * WHAT BELONGS HERE, and what does not.
 *
 * This module is for helpers that are (a) pure, (b) not about one page's
 * state, and (c) written more than once. `main.html` defined the SAME html
 * escaper six times in one file; that is the shape of thing this file exists
 * to end. Anything that reads page state — the ballot, the annulus, the
 * tables — stays where it is, because moving it would only move the coupling.
 *
 * It was kept apart from `ebx_shared.js` while that file was compiled from a
 * TypeScript source that had drifted behind it. That source was retired on
 * 2026-09-16 — `ebx_shared.js` is plain, hand-edited JavaScript now — so this
 * can be folded in, or left alone, which is also fine.
 *
 * Global: `EBXPage`. No dependency on `EBX`, on load order, or on the DOM.
 */
(function (root) {
  'use strict';

  // ── text ─────────────────────────────────────────────────────────────────
  // The one escaper. Every value that reaches innerHTML from user or API data
  // goes through this: initiative titles, organization names (an org can be
  // nominated by anyone), cause names.
  function esc(v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // ── dates ────────────────────────────────────────────────────────────────
  // NOTE: these FORMAT dates. They do not compute them. Every mission date in
  // the system comes from `EBX.Cycle.missionDates`, which is the single owner
  // of the cycle arithmetic and stays in `ebx_shared.js`; a second module that
  // could answer "when is the organization election" is exactly the drift this
  // codebase has already been bitten by.
  function fmtFullDate(d) {
    return new Date(d).toLocaleDateString('en-US',
      { month: 'short', day: 'numeric', year: 'numeric' });
  }
  function fmtShortDate(d) {
    return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
  // Whole days from now until `d`, floored at 0 — a countdown never reads
  // negative, it reads "today".
  //
  // MIDNIGHT TO MIDNIGHT, and that is load-bearing. main.html measured this
  // with `ceil((date - now) / day)` until 2026-08-10, which adds a day for the
  // half-day remainder: the card read "51 d left" beside "Sep 29" on Aug 10,
  // which is 50 days. Two numbers on one card must not disagree, so both ends
  // are floored to local midnight and the count ALWAYS equals the printed date
  // minus today.
  function daysLeft(d) {
    if (!d) return 0;
    var t = new Date(d); t.setHours(0, 0, 0, 0);
    var n = new Date();  n.setHours(0, 0, 0, 0);
    return Math.max(0, Math.round((t.getTime() - n.getTime()) / 86400000));
  }

  // ── numbers ──────────────────────────────────────────────────────────────
  function num1(n) {
    return Number(n || 0).toLocaleString(undefined, { maximumFractionDigits: 1 });
  }
  function num0(n) {
    return Math.round(Number(n) || 0).toLocaleString();
  }

  // ── the watchlist ────────────────────────────────────────────────────────
  // Two lists, initiatives and organizations, in localStorage. Initiative
  // watches also sync to the account so a bookmark follows the benefactor
  // across devices; organization watches are local-only until there is an
  // endpoint for them.
  //
  // Every read is wrapped: a browser in private mode, or with site data
  // blocked, throws on `localStorage` rather than returning null, and a page
  // must not go blank because someone bookmarked an initiative.
  var WATCH_KEY = { tiv: 'ebx_watched_initiatives', org: 'ebx_watched_orgs' };

  function _key(kind) { return WATCH_KEY[kind === 'org' ? 'org' : 'tiv']; }

  function getWatched(kind) {
    try { return JSON.parse(root.localStorage.getItem(_key(kind)) || '[]') || []; }
    catch (e) { return []; }
  }
  function setWatched(kind, ids) {
    try { root.localStorage.setItem(_key(kind), JSON.stringify(ids || [])); }
    catch (e) {}
  }
  function isWatched(kind, id) { return getWatched(kind).indexOf(id) >= 0; }

  // Flip one id and report the new state, so a caller can sync it without
  // reading the list back.
  function toggleWatched(kind, id) {
    var ids = getWatched(kind);
    var i = ids.indexOf(id);
    var nowWatched = i < 0;
    if (nowWatched) ids.push(id); else ids.splice(i, 1);
    setWatched(kind, ids);
    return nowWatched;
  }

  root.EBXPage = {
    esc: esc,
    fmtFullDate: fmtFullDate,
    fmtShortDate: fmtShortDate,
    daysLeft: daysLeft,
    num0: num0,
    num1: num1,
    getWatched: getWatched,
    setWatched: setWatched,
    isWatched: isWatched,
    toggleWatched: toggleWatched,
  };
})(window);
