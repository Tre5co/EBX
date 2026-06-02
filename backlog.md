# Backlog

## Automated debug run — 2026-06-01

---

### ✅ FIXED — `/auth/me` 500 (profile page not accessible)

**Root cause:** `BenefactorAccount.watched_initiative_ids` is stored as `Text | NULL` in SQLite. Existing accounts have `NULL` there. Pydantic v2 reads the raw ORM value and fails with:
```
ResponseValidationError: watched_initiative_ids — Input should be a valid list, input: None
```

**Fix applied** in `backend/app/schemas.py` — added a `field_validator` on `BenefactorRead.watched_initiative_ids` that coerces `None → []` and a JSON string → parsed list. Safe, no DB migration needed.

Restart uvicorn and profile.html should load immediately.

---

### ⚠️ NEEDS JAX — cause.html is truncated

**Root cause:** `cause.html` ends abruptly at line 1518, mid-sentence inside the `commitVote` async function:
```js
    async function commitVote(causeId) {
      const shares = loadShares(causeId);
      const sum = Object.values(          ← FILE ENDS HERE
```

The async IIFE that wraps the whole script is never closed (`})()` is missing), so the browser hits a syntax error and **none of the JavaScript runs**. The phase recaps show static placeholder text, the annulus is never mounted for the selected cause, and votes can't be submitted.

**What's missing at minimum:**
- The closing body of `commitVote` (probably a fetch to `/votes/commit`)
- The page initialization block that:
  - looks up the cause from `causeId`
  - calls `EBX.Annulus.mount('#cause-annulus-mount')`
  - calls `renderPhaseRecaps(cause)` to bootstrap the 4 phase-recap blocks
  - possibly sets `--cause-color` on the root
- The closing `})();` of the IIFE
- The `</script>` tag

**My recommendation:** Check git history for the last complete version of `cause.html`. The initialization block is likely ~20-30 lines and would have been written right after the function definitions. If you can share it (or the last git commit message before it got truncated), I can reconstruct and wire it in.

---

### Pruning candidates (carry-over from STRUCTURE.md)

Still open per build-seq 6. Hold until list is longer.

---

### backlog.md note

`backlog.md` did not exist when this run started — created fresh. If you had a prior backlog file elsewhere, let me know and I'll merge.
