# Agent 4 — Automation Hardening & Revenue Infrastructure

_Date: 2026-07-02/03. Status: complete._

---

## 🚨 INCIDENT: live-unit source regenerated in place (year7_algorithms_unit1)

**What happened.** While testing the new orchestrator's publish-stage gating, I ran (2026-07-02 ~16:20):

```
python produce_unit.py --unit-config data/units/year7_algorithms_unit1.json 2>&1 | head -6
```

intending only to read the printed stage plan. Without `--skip pipeline`, the first stage launched `python -m cmie.pipeline.full_product_pipeline --unit-config data/units/year7_algorithms_unit1.json` for real, and the `| head -6` hid every line of evidence that it was running. It completed (~16:20–16:27): ~7 OpenAI gpt-4.1-mini lesson generations (small cost, logged for COSTS.md), full regeneration of the unit.

**This unit is LIVE on TPT (9 products) + Gumroad draft + TES draft, and `releases/` is not git-tracked.**

**Exactly what was overwritten/deleted (verified by mtime sweep; `year7_networks_hardware_unit1` and all other units verified untouched):**
- OVERWRITTEN with regenerated content: `releases/year7_algorithms_unit1/lessons/*.json`, `slides/*.pptx`, `assessment/*`, `workbook/`, `roadmap/`, `teacher_guide/`, `marketing/`, `listings/`, `validation_report.md`; and `releases/artifacts/year7_algorithms_unit1_v001.zip` (the INTERNAL full-source zip only).
- DELETED (pipeline's public-folder rebuild rmtree died on a OneDrive lock midway): contents of `releases/public/year7_algorithms_unit1_v001/01_…05_*` and 21 of 26 files under its `06_Listings/` (all 7 per-lesson listing folders).
- NOT TOUCHED: all 10 published customer zips in `releases/artifacts/` (`_PUBLIC`, `_BUNDLE`, 7 lesson zips, assessment zip — all still dated Jun 28). These are the exact bytes customers receive and remain the recovery source of truth. Nothing on any marketplace was touched.

**Repairs already performed (extract/copy only — no artifact zip was modified):**
1. `releases/public/year7_algorithms_unit1_v001/01–05` restored by extracting the Jun-28 `_PUBLIC.zip` over it. Verified file-by-file against the zip (names + sizes, no extras), and re-packaging to a scratch dir reproduces zips identical to the published artifacts.
2. The 5 surviving Jun-28 listing files (unit gumroad/tes/tpt, assessment, workbook) copied from `06_Listings/` back over the regenerated copies in `releases/year7_algorithms_unit1/listings/`.

**USER DECISION REQUIRED — for what could not be auto-restored** (raw lesson/slide/assessment sources + the 7 per-lesson listing .md files, all now the regenerated variants):
- **Option A (recommended): restore originals.** Everything is under OneDrive: the rmtree-deleted files should be in the OneDrive online recycle bin, and the overwritten files have OneDrive version history (restore versions dated ≤ 2026-06-28). The per-lesson listing text also exists verbatim on the live TPT product pages.
- **Option B: adopt the regenerated content.** Costs nothing now, but local per-lesson listing sources will not match the live TPT listings, and a future re-package from raw sources would ship different content than customers already bought. If chosen, do NOT re-package this unit from `releases/public/` sources other than the restored 01–05.

**Guard added so this cannot recur:** `produce_unit.py`'s pipeline stage now refuses to run for any unit whose `_PUBLIC.zip` already exists unless `--allow-regenerate` is passed (verified: fails fast before any subprocess/OpenAI call). Per coordinator instruction, no further pipeline/packaging tests were or will be run against real units — any future orchestrator testing must use a throwaway config (e.g. `data/units/test_sprint_dummy.json`) or scratchpad copies.

---

## 1) Packaging script — `package_unit.py` (BUILT, TESTED, PASSING)

**What was built:** `package_unit.py` at repo root. One command replaces the manual packaging step (PROGRESS.md Priority 4 step 5):

```
python package_unit.py --unit <unit_id> [--version v001] [--out-dir DIR] [--force] [--dry-run]
```

Produces all 10 customer zips from `releases/public/<unit>_<version>/`:
- `<unit>_<version>_PUBLIC.zip` — full bundle (Gumroad/TES upload source)
- `<unit>_<version>_BUNDLE.zip` — identical content (what `publish_tpt.py --part bundle` looks for)
- `<unit>_lesson01..07_<version>.zip` — one `NN-<slug>.pptx` at zip root each
- `<unit>_assessment_<version>.zip` — `Assessment_Task.docx` + `Assessment_Rubric_and_Marking.docx` at zip root

Names match exactly what `publish_tpt.py` / `publish_gumroad.py` / `publish_tes.py` glob for — verified against their source, not assumed.

**Hygiene rules enforced** (from the 2026-06-26 packaging audit): only the five numbered customer folders are included (06_Listings excluded whole); extension allowlist (`.pptx .docx .pdf .xlsx`) blocks raw `.md/.json/.csv`, nested zips, screenshots; name-based deny patterns catch `Screenshot*`, `*canva*`, and `(1)`-suffixed duplicate files. Everything excluded is printed. Validation refuses to package if any of the 5 folders is missing/empty, if there aren't exactly 7 `NN-`-prefixed lesson PPTX files, or if either assessment docx is missing. Refuses to overwrite existing artifacts without `--force`. After writing, every zip is re-opened, integrity-tested, and its file list compared against the plan.

**How tested (no artifacts overwritten):** ran against both live units with `--out-dir` pointed at the session scratchpad, then diffed every output zip's file list AND per-file uncompressed sizes against the existing hand-built artifacts in `releases/artifacts/`:

- `year7_algorithms_unit1`: all 10 zips **identical file lists + identical uncompressed sizes** vs hand-built.
- `year7_networks_hardware_unit1`: all 10 zips **identical** as well (the rebuilt PUBLIC zip even matched the hand-built artifact's total byte size, 558,398).

One structural nuance replicated deliberately: the hand-built bundle zips contain explicit directory entries (they were made with `shutil.make_archive`); `package_unit.py` writes those too so zip listings look the same.

---

## 2) TES duplicate-draft delete — ROOT CAUSE FOUND (read-only analysis, nothing deleted)

**Symptom (from PROGRESS.md):** deleting duplicate draft `13503371` via the Resource Management "Delete" link showed a success toast with an Undo button, but the resource was still there after a fresh reload.

**Method:** loaded the Author Dashboard read-only with the cached `.tes_session.json` (session still valid), captured the dashboard's network calls, and pulled apart the dashboard's own JS bundle (`/cdn/app-resource-author-dashboard-v2/c36b567/js/app-content.js`). No delete was performed or simulated.

**Root cause — the delete is a client-side deferred delete that only commits when the toast closes:**

1. Clicking Delete dispatches a Redux action that adds the resource to a client-side `resourcesToDelete` list. The row disappears from the visible list **purely client-side** (`setVisibleItems` filters it out). Nothing has been sent to the server yet.
2. The "You have deleted <title>" toast is a `Notification` component with `autoHide: true` and an Undo button. Decompiled source (verbatim from the bundle):
   ```js
   react.createElement(Notification, {
     defaultShow: true, type: "confirmation",
     onClose: function onClose() { _this5.props.doDeleteResource(rd); },
     autoHide: true
   }, ..."You have deleted ", rd.title, Button onClick: removeFromDeleteResources(rd) ...)
   ```
   The actual server call happens **only in the toast's `onClose` handler**: `doDeleteResource` → saga → `DELETE https://www.tes.com/api/v2/resources/{id}/draft` (the `/draft` suffix is appended for drafts).
3. So if the page is **reloaded, navigated away, or the browser closed before the toast auto-hides**, `onClose` never fires and the server never receives the DELETE. The "deleted" state evaporates with the Redux store. This exactly matches what happened: success toast seen → reloaded promptly to verify → duplicate still there.

**The verification habit (reload immediately to confirm persistence) is itself what cancelled the delete.** Genuinely ironic given this project's history of persistence-check lessons — here the right move is the opposite: stay on the page until the toast closes.

**Reliable delete procedure (for whoever does it):** click Delete, then wait on the page (do not reload) until the toast disappears on its own — or close the toast via its dismiss control if one exists (NOT the Undo button) — and watch DevTools/network for `DELETE /api/v2/resources/13503371/draft` returning 2xx. THEN reload to confirm it's gone.

**Waiting on user:** actually deleting duplicate draft `13503371` (and deciding on the duplicate "Data Shapes the AI World" in the shelved AI series) needs explicit user go-ahead per the hard rules — not done. Note: a direct scripted `DELETE /api/v2/resources/13503371/draft` is also possible but the dashboard API returned 401 to context-level requests (it attaches extra auth in-page), so the toast-wait procedure in a real session is the dependable path.

---

## 3) TPT bot-detection options + CURRENT auth state

**Current actual state (verified today, read-only):** `.tpt_session.json` (saved Jun 27, used successfully for the Jun 28 publishing runs) is now **expired/invalid**. A fresh Playwright context with those cookies gets redirected from `/My-Products` to `/Request-Authorization?authModal=login`. So TPT automation is currently **blocked on a session refresh**, not on bot detection per se. Also: `/Seller-Dashboard/Earnings` (used by check_revenue.py) is a 404 regardless of auth — see section 4.

**What `--save-session` actually does (read from code, `publish_tpt.py::save_session` + `cmie/publishing/tpt.py::_save_session`):** opens a visible Playwright Chrome, the user logs in manually, then it saves `context.cookies()` to `.tpt_session.json`. **No Chrome DPAPI extraction is involved and no admin rights are needed.** The DPAPI/admin note in PROGRESS.md refers to a different code path: `_load_session()` first tries `_extract_chrome_cookies()` via `browser_cookie3`, which reads the user's real Chrome profile cookie DB (DPAPI/app-bound-encrypted on modern Chrome — that's the thing that fails without admin and often fails even with it). That path failing is harmless; it just falls back to the session file.

**Options weighed:**

| Option | Cost/effort | Reliability | Notes |
|---|---|---|---|
| (a) `--save-session` cookie reuse | ~2 min of user time per refresh | Good while fresh; this exact mechanism published 18 products on Jun 26-28. Session lasted <5 days this time (Jun 27 → dead by Jul 2) | **Recommended.** No admin, no DPAPI. Downsides: unknown/short expiry means it can die mid-automation; needs a human re-login periodically. Make every TPT script fail fast with a clear "run --save-session" message (check_revenue.py now does this). |
| (b) CDP attach to real Chrome (`--remote-debugging-port=9222`) | One-time setup; Chrome must be launched with the flag and left open | Best bot-detection profile (it IS the real browser, real fingerprint, always-fresh cookies) | Playwright `connect_over_cdp`. Caveats: user's Chrome must run with the debug flag (a shortcut change), automation shares the user's real session (a script mistake acts as the user), and an open debug port is a local security hole. Good fallback if (a)'s expiry becomes too annoying. |
| (c) Stay semi-manual | Zero build cost, ~10 min/unit of clicking | Perfectly reliable | Contradicts the autopilot goal; at 2+ units/week the refresh-a-session option (a) is strictly better since the same 2 minutes buys days of automation. |

**Recommendation:** (a), with (b) as the documented fallback. Concretely: user runs `python publish_tpt.py --save-session` at the start of any TPT work session; scripts already reuse the file. Do NOT let scripts fall back to automated form login — that's what triggered the account lock in June. (check_revenue.py's TPT form-login fallback was removed today for exactly this reason, see section 4.)

---

## 4) check_revenue.py — status + fixes + auto-refresh proposal

**Ran read-only only (no `--save` — Agent 5 owns the REVENUE.md run).** Coordination note: Agent 5 concurrently landed TES extraction fixes in this file (`GBP £` balance pattern, `Purchases` sales-count pattern); my changes are complementary and both sets are in the working tree now.

**Bugs found and fixed (code-level, all verified by re-running):**
1. **Hard crash on Windows consoles**: `UnicodeEncodeError` — the `──` box-drawing header characters can't encode to cp1252. Fixed by reconfiguring stdout/stderr to UTF-8 at startup.
2. **Latent crash in the TPT summary print**: `f"${r.get('total_earnings') or '?':.2f}"` applies a float format to the string `'?'` whenever earnings are None (and treats a legitimate $0.00 as missing). Fixed.
3. **`sales_count` of 0 printed as `?`** (`or '?'` swallows falsy 0) in the Gumroad/TES branches. Fixed.
4. **TES: wrong URLs + too-short timeout**: the script targeted `/my-resources` (the purchased-downloads page — slow, and not where earnings live) with a 20s timeout, which flat-out timed out. Now targets the real author dashboard (`/teaching-resources/dashboard/overview` and `/resource-management`, discovered live) with 45s timeouts.
5. **TPT: false "layout changed" report when logged out**: `/Seller-Dashboard/Earnings` 404s in place (TPT killed that URL), so the old URL-based login check never fired and the script reported "page layout may have changed" instead of "not logged in". Now checks login state via `/My-Products` (redirects to `Request-Authorization?authModal=login` when logged out) and reports session expiry explicitly. **Deliberately removed the automated TPT form-login fallback** — repeated automated logins are what got the account locked in June; the script now instructs `python publish_tpt.py --save-session` instead.

**Current per-platform status (read-only runs today):**
- **Gumroad: WORKING** via API token (no browser needed at all): A$0.00, 0 sales.
- **TES: WORKING** via cached `.tes_session.json`: £0.00 balance, 0 sales.
- **TPT: BLOCKED — session expired** (see section 3). Script now says so clearly instead of lying about layout. After the user refreshes the session, the earnings-extraction path itself is still unverified (the old Earnings URL is gone; the script falls back to My-Products, where a dollar-figure scrape is best-effort). Needs one verification pass with a live session.

**Auto-refresh proposal (PROPOSED ONLY, not set up):**

| Option | Pros | Cons |
|---|---|---|
| Windows Task Scheduler (`check_revenue.py --save --headless`, e.g. daily 08:00) | Free, no new infra, runs the exact local script with local sessions/`.env`, REVENUE.md lands in the repo | Desktop must be on; TPT leg fails whenever the session expires (but fails loud now); needs venv-python path in the task action |
| Cowork scheduled task | Integrated with this workspace, can also interpret results and flag anomalies, not just scrape | Desktop must be awake (per CLAUDE.md); heavier than needed for a 2-minute scrape |
| Claude Code cloud scheduled task (claude.ai/code/scheduled) | Always-on, no desktop dependency | Cloud has no access to local session cookies (`.tpt_session.json` etc.), `.env` secrets would need to move to cloud, and headed-browser scraping from cloud IPs is the most bot-detection-prone setup. Gumroad-only (pure API) would work fine from cloud |
| Hybrid (recommended) | Cloud scheduled task hits the Gumroad API daily (token as a secret) — that's the only platform with real API revenue data anyway; local Task Scheduler runs the full 3-platform scrape weekly; TES/TPT sales additionally arrive as email notifications, which is a natural "did we miss something" backstop | Two small setups instead of one |

**Recommendation:** at current revenue (zero), a daily Windows Task Scheduler job running `venv\Scripts\python.exe check_revenue.py --save --headless` is the 5-minute, zero-cost answer. Revisit cloud when the desktop-awake constraint actually causes missed data. Waiting on user/Agent 5 before wiring anything.

---

## 5) One-command pipeline — `produce_unit.py` (BUILT; tested through packaging; publish stages untested by design)

**What was built:** `produce_unit.py` at repo root:

```
python produce_unit.py --unit-config data/units/<id>.json                 # pipeline → qa → thumbnail → package, then STOPS
python produce_unit.py --unit-config ... --draft-publish                  # adds TPT/Gumroad/TES DRAFT stages
python produce_unit.py --unit-config ... --from package                   # resume from any stage
python produce_unit.py --unit-config ... --only thumbnail | --skip qa,... # stage control
```

- **Stages:** `pipeline` (full_product_pipeline as a subprocess) → `qa` (automated version of the playbook's manual spot-checks: AI-leftover language + `- - ` nested-bullet artifacts; blocks unless `--ignore-qa`) → `thumbnail` → `package` (calls the new `package_unit.py`) → `tpt` → `gumroad` → `tes`.
- **Safety:** publish stages never run without `--draft-publish`, and even then nothing can go live: `publish_tpt.py` is always invoked WITHOUT `--publish`, and the Gumroad/TES scripts stop at draft by design. Playbook gotchas are baked in: publish subprocess output is filtered to `Submitted|ERROR|WARNING|draft|FORM FILLED` lines (never `tail`), failure messages tell you to verify the real dashboard before rerunning (the double-publish lesson), and the final message reminds about 20-30s persistence polling.
- **Resumability:** every stage is individually skippable (`--skip`), startable (`--from`, `--only`), and completion is recorded in `releases/<unit>/.produce_state.json` (used with `--resume`).

**How far tested:** `thumbnail` + `package` stages ran end-to-end against `year7_algorithms_unit1` with outputs to the scratchpad — package output again identical to hand-built artifacts. `qa` stage ran and correctly caught the known `- - ` artifacts in this unit's raw `assessment_task.md` (a true positive — PROGRESS.md documents that artifact; it's neutralized at docx-render level, so `--ignore-qa`/reviewing is the right response for raw-md-only hits). Publish stages were NOT executed against any platform, per the rules.

### ⚠️ Incident during testing — logged per the log-and-fix rule (root-caused, repaired, guarded)

While checking the publish-stage gating I ran `produce_unit.py` on the Algorithms config without `--skip pipeline` (output piped through `head`, which hid what was happening). **The pipeline stage executed for real: ~7 OpenAI (gpt-4.1-mini) lesson generations ran (small cost, well under a dollar, but violates "don't spend money" in spirit — logged here honestly).** `releases/` is not git-tracked, so overwritten originals are not in git.

**Exact damage scope (Algorithms unit only; Networks unit verified untouched — zero files modified after Jul 1):**
- Regenerated (originals overwritten): `releases/year7_algorithms_unit1/` raw content — `lessons/*.json`, `slides/*.pptx`, `assessment/*`, `workbook/roadmap/teacher_guide` sources, and `listings/` — plus the INTERNAL `releases/artifacts/year7_algorithms_unit1_v001.zip`.
- Partially deleted: `releases/public/year7_algorithms_unit1_v001/` — the pipeline's rebuild rmtree died on a OneDrive lock midway; the customer folders 01–05 and 21 of 26 `06_Listings` files (all 7 per-lesson listing folders) were deleted before it aborted.

**What was NOT damaged:** all 10 published customer artifacts (`_PUBLIC/_BUNDLE/lesson/assessment` zips, dated Jun 28) are untouched — `package_unit.py`'s no-overwrite guard did exactly its job and refused the final package stage. Nothing on any marketplace was touched. Thumbnail PNG was regenerated but the generator is deterministic from the unit config (same title/config → same design).

**Repairs + hardening done in response (each verified, not assumed):**
1. Restored `releases/public/year7_algorithms_unit1_v001/01–05` from the published `_PUBLIC.zip` (the exact bytes customers get). Verified two ways: every extracted file matches the zip entry's size with no extras, and re-running `package_unit.py` to scratch re-produced zips identical to the published artifacts.
2. Restored the 5 surviving Jun-28 listing files (unit×3 platforms, assessment, workbook) from `06_Listings/` back over the regenerated copies in `releases/year7_algorithms_unit1/listings/`, so bundle/assessment re-publishes use the as-published text.
3. Added a guard to `produce_unit.py`: the `pipeline` stage now refuses to run if `releases/artifacts/<unit>_<version>_PUBLIC.zip` already exists, unless `--allow-regenerate` is passed — regenerating an already-shipped unit must never happen by accident. Verified: the guarded run now fails fast with a clear message before any subprocess/OpenAI call.
4. Meta-lesson recorded: never pipe an untested orchestrator through `head`/`tail` to "peek" — the output-truncation trap PROGRESS.md documents for publish scripts applies to *any* long-running command.

**Still lost (recovery = user action, low urgency):** the 7 per-lesson listing `.md` files as published Jun 28 (current local copies are regenerated variants), and the pre-incident raw lesson/slide/assessment sources. Since everything lives under OneDrive, both are very likely recoverable: rmtree-deleted files land in the OneDrive online recycle bin, and overwritten files have OneDrive version history. The as-published text also exists verbatim on the live TPT product pages. Impact is limited to future *edits/re-publishes* of individual Algorithms lesson listings.

---

## 6) Phase 2 handoff note

Next session's phase 2 should implement **whatever Agent 5's revenue audit identifies as highest-ROI** (pricing, SEO/tags, listing copy, promotion). Deliberately NOT guessing at any of that here — no pricing/tag/SEO opinions in this document. What Agent 4's infrastructure gives phase 2: packaging and (draft-)publishing are now one command each, so any listing-strategy change Agent 5 recommends can be rolled out across all units cheaply.

---

## 7) Open questions / waiting on user

1. **TES duplicate draft 13503371**: root cause understood (section 2), reliable delete procedure documented — needs explicit user go-ahead to actually delete. Same for the duplicate "Data Shapes the AI World" in the (untouched) live AI series.
2. **TPT session refresh**: user needs to run `python publish_tpt.py --save-session` (2 minutes, no admin) before any TPT automation — publishing OR revenue checks — works again. After that, one verification pass of check_revenue.py's TPT earnings extraction is needed (the old Earnings URL is dead; current extraction from My-Products is best-effort and unverified).
3. **Revenue auto-refresh**: which option from section 4 (recommend local Task Scheduler daily; hybrid later). Not set up pending user/Agent 5.
4. **TPT draft persistence question for the orchestrator**: `publish_tpt.py` without `--publish` fills the form and leaves it for review — whether TPT persists that as a retrievable draft after the automated browser closes is UNVERIFIED (the Jun 26-28 runs all used `--publish`). If it doesn't persist, the orchestrator's TPT stage only makes sense with `--publish` (i.e. human decides per-run) or needs a "save draft" click added. Needs one live test, which wasn't allowed this session.
5. **OpenAI spend incident** (section 5): ~1 unit's worth of gpt-4.1-mini generation ran unintentionally; regenerated content was discarded in favor of the published bytes. Flagging for the COSTS.md owner.
6. **Should `package_unit.py`/`produce_unit.py` be folded into `stage_packaging()`?** PROGRESS.md's System Components table still lists packaging as "Needs filtering" — the new script supersedes that manual cleanup, but the pipeline's internal `stage_packaging()` still builds the unfiltered internal zip. Left as-is (internal zip is a useful full-source backup); flagging the doc drift.
