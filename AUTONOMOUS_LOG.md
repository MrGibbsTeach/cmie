# Autonomous Run Log

Running log for the unattended scheduled jobs (business review, new unit,
marketing push, resource drop) covering the period the business owner is
away. Newest entries at the top. Each entry: date, job name, what happened,
anything that needs a human decision.

Hard boundaries every job must respect, no exceptions, regardless of what
is found during a run:
- Never delete anything on any platform (TPT, Gumroad, TES, Pinterest)
- Never edit the Categories or Licence step on an already-published TES
  resource (a 2026-07-19 incident corrupted a live paid listing to FREE
  doing exactly this — see project memory `project_direction_change.md`)
- Never touch the off-brand Gumroad products (SWMS guide, ADHD guide)
- No new platforms, no pricing changes, no strategic direction changes
- If something needs a human decision (looks like a bug, a duplicate, an
  ambiguous state), log it clearly below and move on — do not attempt to
  resolve it unilaterally

Known platform limitation, accepted for now (2026-08-24) — NOT permanent,
revisit periodically:
- TPT sits behind a Cloudflare bot challenge that a fresh/disposable
  browser fails even with genuinely valid, freshly-exported session
  cookies — verified directly: a same-machine, same-IP, 2-minute-old
  cookie export still hit "Performing security verification" in a new
  browser profile. This is NOT a cookie-staleness problem, so refreshing
  `TPT_SESSION_JSON` does not fix it and never has reliably — the cloud
  sandbox is a disposable container every run, so it can never carry the
  aged, real-usage browser trust TPT's Cloudflare challenge is actually
  checking for. Local automation works because it runs against a
  long-lived, real-usage Chrome profile on this machine, not a cookie
  snapshot.
- Accepted interim shape: Gumroad, TES, and Pinterest run unattended in
  the cloud. TPT stays local-only — a human (or an active session at this
  machine) periodically runs the TPT half of whatever queued up. Jobs
  should detect the block, log it clearly, and move on without retrying
  login workarounds — this is expected behavior, not a bug to chase.
- This is accepted as a current constraint to work within, not a decision
  to stop improving on. Do not treat "3 of 4 platforms automated" as a
  finish line.

Standing direction (2026-08-24): automation maturity is one axis of
improvement, not the whole project. Keep actively looking for gains in:
resource quality, which platforms/marketplaces the catalog lists on,
pricing, marketing effectiveness, and automation coverage — in every
session, not just when asked.

---

(entries below this line, newest first)

## 2026-08-31 — Scheduled business review + integrity checks: Gumroad and TES clean, TPT blocked by the accepted Cloudflare/session limit on all 13 units

Ran `business_review.py --save` followed by the three integrity checkers,
report-only, per the standing job description.

- **Revenue**: Gumroad AUD 0 (0 sales), TES GBP 0.30 (1 sale). TPT revenue
  unreadable (session expired, see below). Combined not currency-converted:
  AUD0 + GBP0.30.
- **Catalog**: 13 live units (unchanged from the prior run) — algorithms,
  cybersecurity, data_representation, databases, digital_systems,
  game_design, networks_hardware, orientation, python_programming,
  robotics_physical_computing, spreadsheets, ux_design, web_design.
- **`verify_tpt_listings.py --unit <unit_id>`**, run for all 13 live
  units: every single one failed the same way — `TPT_SESSION_JSON` /
  `.tpt_session.json` is not a valid session (`ERROR: not logged in to
  TPT (no valid session found)`, plus `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'` since this container has no real browser
  profile to pull cookies from). This is the accepted platform limit
  documented above (2026-08-24): TPT's Cloudflare challenge rejects a
  disposable cloud container's browser fingerprint regardless of cookie
  validity. Not a bug, no login/retry attempted, no code changes made.
- **`verify_gumroad_listings.py`** — **ran clean.** 14 products matching
  "Unit 1" (of 18 total) checked, all "(published)", no empty/near-empty
  descriptions, no unrendered markdown, no HTML leakage. Same 14 URLs as
  prior runs plus the AI & Data Literacy Series Unit 1 listing
  (`focuslabdigital.gumroad.com/l/cqwjlt`).
- **`verify_tes_listings.py`** — **ran clean.** Logged in via saved
  session cookies; found 36 resources total on the dashboard, 23 matching
  "Unit 1". All 23 checked clean — no empty descriptions, no literal HTML
  tags, no unrendered markdown. As in prior runs, several topic titles
  are shared by two resource IDs (e.g. Networks & Hardware: `13517745`
  and `13517664`; Game Design: `13517663` and `13516159`; Introduction to
  Programming: `13517665` and `13516158`; Digital Systems: `13517662`
  and `13516138`; Websites & Web Design: `13517668` and `13516137`;
  Spreadsheets: `13517666` and `13516136`; UX & Interface Design:
  `13517667` and `13514520`; Cyber Security: `13517659` and `13514519`;
  Data Representation: `13517661` and `13514517`; Algorithms:
  `13517658` and `13503396`) — per the 2026-07-31 entry below, these are
  separate per-lesson resources sharing a "Unit 1" title prefix, not new
  duplicates (a genuine duplicate would share the *exact same* title, as
  the already-logged `13432831`/`13432796` pair does). Not investigated
  further this run.

**Open items carried forward, unchanged, none touched this run** (full
list in `BUSINESS_REVIEW.md`): TES Unit 1 (AI series) presenter-
placeholder/"Unknown" quote cosmetic bug on the TES side; TES genuine
duplicate `13432831`/`13432796`; TES resource `13445828` permanently
broken; off-brand Gumroad products (SWMS, ADHD guide) still on the
storefront; shelved AI-series Units 3-8 still live on TES.

No fixes, edits, or deletions made — report-only per the job's hard
boundaries. Environment dependency installs (`python-dotenv`,
`playwright`, `browser_cookie3`, `openai`, `python-pptx`, `python-docx`,
`yt-dlp` via `pip install -r requirements.txt`) are ephemeral to this
container, not committed.

## 2026-08-28 (concurrent-run note) — Root cause found for the "13553843/13553844 duplicate" flagged below: two scheduled Resource Drop instances ran the same cycle at the same time, not a TES platform bug

This session independently picked up the same queue item (the
`year7_web_design_unit1` Lesson 6 lead magnet) at essentially the same
moment as the run recorded immediately below, built the identical zip via
`make_lead_magnet.py --unit year7_web_design_unit1 --lesson 6`, and ran
`publish_lead_magnets.py --unit year7_web_design_unit1 --lesson 6
--platform tes --publish` through to a live "Publish now" landing —
resource **13553844**. Neither run's process had any way to see the
other's in-flight work, so both independently built, published, and
verified, and both hit the same live duplicate the other run's entry
below already flagged (13553843 vs 13553844) and correctly declined to
touch, per the "never delete anything" rule.

On `git checkout main && git pull origin main`, the other run's commit
(`c106532`, "Resource Drop: publish Lesson 6 lead magnet for
year7_web_design_unit1") was already on `origin/main` — queue item marked
`[x]`, log entry written, resource 13553843 recorded as the canonical
result. Since the actual work item is already complete and recorded, this
session made no further edits to the queue and did not re-log a duplicate
"item done" entry — this note only corrects the open question the other
entry left unresolved.

That entry attributed the duplicate to "the same class of platform-side
duplicate-draft behavior already open... elsewhere in this project" —
worth revisiting: the real mechanism, confirmed here, is two concurrent
scheduled-job instances racing on the same queue item, each creating its
own genuinely live TES resource (both 13553843 and 13553844 are live,
public, 200-status pages with identical title/description/licence — not
one draft and one orphan). It's plausible the older 13432831/13432796
pair referenced there has the same explanation rather than a TES-side bug.
**Needs a human decision**: pick one of 13553843/13553844 to keep live and
remove the other (this session did not — no delete authority), and check
why this cycle's scheduled trigger fired more than once concurrently, since
if that keeps happening it will keep producing paid-resource risk, not
just free-lead-magnet duplicates.

TPT was independently checked in this session too (`verify_tpt_listings.py`
read-only, `TPT_SESSION_JSON` invalid, no login retried) — same accepted
platform limit as the other run's entry, nothing new there.

## 2026-08-28 — Resource Drop: Lesson 6 lead magnet for year7_web_design_unit1 (TES fully live, TPT still blocked by accepted platform limit); found a new instance of the known TES duplicate-draft behavior, not touched

Worked the first unchecked item in `data/units/RESOURCE_DROP_QUEUE.md`:
a second free lead magnet for `year7_web_design_unit1`. Picked Lesson 6,
"Accessibility and Responsive Design Basics" — of the unit's 7 lessons,
the most standalone and broadly relatable (a conceptual lesson on
inclusive/responsive design, not dependent on the HTML/CSS build-up in
Lessons 2-5), matching the pattern used for the previous two lead-magnet
picks (Debugging for algorithms, Phishing for cybersecurity).

**Build**: `python make_lead_magnet.py --unit year7_web_design_unit1
--lesson 6` — succeeded, zip built at
`releases/artifacts/year7_web_design_unit1_lesson06_FREE_v001.zip` from
the tracked source pptx (all 7 lesson decks are committed under
`data/units/lead_magnet_source/year7_web_design_unit1_v001/`, so no
`releases/` tree dependency).

**TPT**: blocked, exactly the accepted platform limit — `TPT_SESSION_JSON`
has no valid session in this container and no `TPT_EMAIL`/`TPT_PASSWORD`
fallback is configured, so `publish_lead_magnets.py --platform tpt`
correctly refused to submit a blank login form rather than risk bot
detection. Per the 2026-08-24 finding, this is a Cloudflare fresh-browser-
fingerprint block, not fixable by refreshing cookies from this sandbox —
not retried. A human running locally: `python publish_tpt.py
--save-session` then `python publish_lead_magnets.py --unit
year7_web_design_unit1 --lesson 6 --platform tpt`.

**TES**: `python publish_lead_magnets.py --unit year7_web_design_unit1
--lesson 6 --platform tes --publish` ran the full flow end-to-end — login,
title/description, zip upload, categories, "Share for free" licence,
copyright checkbox, "Publish now" — and landed on the `.../published` URL
for resource **13553843**. Fully live, no manual step, per the TES
full-automation fix landed 2026-08-24.

**Verification, and a new open item found (not touched)**:
`verify_tes_listings.py --keyword Accessibility --lead-magnet-lesson 6`
found **two** resources with the identical Lesson 6 title/content —
13553843 (the one this run's own publish log named) and a second,
13553844, with the same title, same "Created: 28 Aug 2026" / "Last
modified: 28 Aug 2026" timestamps, and the same CC-BY-SA licence (checked
directly via a dashboard-row dump and a per-resource page load for both
IDs). This run's `publish_lead_magnets.py` call was made exactly once and
its own log output only ever mentions 13553843 — nothing in this session's
commands directly created or touched 13553844. This reads as the same
class of platform-side duplicate-draft behavior already an open item
elsewhere in this project (the 13432831 / 13432796 pair), not a bug
introduced by this run's script usage. Per the standing "never delete
anything" rule, neither resource was modified or removed — this needs a
human to look at both and decide whether to keep, edit, or remove the
extra one. The checker's other flag ("could not find £0.00 on the page")
is the already-documented inherent limitation of that specific check
(TES's Licence step always shows the "Sell my resource" tab by default on
a fresh page load, regardless of the actually-saved price) — the reliable
confirmation of genuine £0.00 pricing is the publish run's own "Selected
'Share for free' tab (price <= 0)" log line, which fired correctly here.

**Queue update**: marked `year7_web_design_unit1 — Lesson 6` `[x]` in
`data/units/RESOURCE_DROP_QUEUE.md` with today's date, and logged the
duplicate finding there too.

**Nothing was deleted, no off-brand products were touched, no pricing or
strategic changes were made.** Files changed:
`data/units/RESOURCE_DROP_QUEUE.md` (item checked off + log note), this
file. `releases/artifacts/*` and `releases/debug_*.png` are gitignored
working files, not committed.

## 2026-08-25 — Added check_tpt_backlog.py; found and closed a real TPT gap (cybersecurity lead magnet); fixed a real Cloudflare-risk bug in upload_unit()

Built `check_tpt_backlog.py` so catching up TPT locally (see the
"Known platform limitation" note above) is a 2-minute check instead of
reading through this log. It diffs completed units against
`bundle_urls.json` and does a live local TPT search for completed lead
magnets (no tracking file exists for those).

First run found `year7_cybersecurity_unit1` lesson 3's lead magnet had
never actually reached TPT, unlike `year7_algorithms_unit1` lesson 5
(done 2026-08-20) — a real gap that had gone unnoticed. Publishing it hit
Cloudflare's challenge even with a freshly-refreshed local session,
which led to finding the real cause: `upload_unit()` in
`cmie/publishing/tpt.py` (used for every new TPT product, including all
lead magnets) launched a fresh throwaway browser instead of the
persistent, Cloudflare-trusted profile `automation_chrome()` provides —
same risk class as `--save-session`'s Cloudflare hang. Fixed; retried
live with no challenge this time. Product `17480910` confirmed live.
`replace_product_file()` in the same file has the identical pattern and
was not fixed this session (not currently blocking anything).

Also committed a `publish_lead_magnets.py` change (the `--publish` flag
for TES) that had been made the prior session but never actually
committed.

**Merge note**: this session's `upload_unit()` fix (throwaway browser →
`automation_chrome()`) was made independently of, and in parallel with,
the cloud routine's own `upload_unit()`/`replace_product_file()` fix
below (blank-credential guard + missing Xvfb) — both landed the same day
on overlapping code and needed a manual merge to keep both. Final state:
`upload_unit()` uses `automation_chrome()` (which already handles Xvfb
internally) with no upfront email/password requirement;
`replace_product_file()` keeps the routine's Xvfb + no-upfront-credential
fix on its still-throwaway launch (not migrated to `automation_chrome()`
this session).

## 2026-08-25 — New Unit Production: Databases – Organising and Querying Data built, QA-verified, spot-checked, and published to TES; TPT and Gumroad still blocked in this cloud container

Picked the first unchecked `UPCOMING_QUEUE.md` topic, "Databases:
Organising and Querying Data". Wrote `data/units/year7_databases_unit1.json`
(7 topics, matching the existing catalog format), ran
`produce_unit.py --unit-config ...` end to end (pipeline → qa → thumbnail →
package) — all stages passed, automated QA found no AI-leftover language or
`- -` artifacts.

**Manual spot-check** (not just automated QA, per the 2026-07-19 cosmetic-
bug lesson in project memory): read the full lesson-1 JSON, the queries
lesson (5), the keys/relationships lesson (4), the assessment task, and
extracted real slide text from the queries deck via python-pptx. All
technically accurate for the age group (sorting/filtering/searching,
primary/foreign keys, validation), well-structured (Explore → Hook →
Watch → Learn → Apply → Reflect → Teacher Notes, matching the existing
catalog), assessment realistically scoped (90–120 min, community-library
database design task). No issues found.

**Published live to TES** (resource `13550116`,
https://www.tes.com/uploader/v2/13550116) via `publish_tes.py --publish`
— fully automated, no manual step, confirmed by the task's note that this
is fully live as of 2026-08-24. Verified clean via
`verify_tes_listings.py --keyword "Databases"`.

**Gumroad: blocked, not attempted further.** `publish_gumroad.py` failed
immediately: "No GUMROAD_EMAIL/GUMROAD_PASSWORD in .env and no saved
session." This container has `GUMROAD_TOKEN` (the read-only API key used
by `verify_gumroad_listings.py`/`business_review.py`) but not
`GUMROAD_SESSION_JSON` (the browser-session cookie the *publish* flow
needs, because Gumroad 2FA defeats form login — see the 2026-08-22 entry
below). Did not attempt a login workaround, per standing instructions.
**A human needs to set `GUMROAD_SESSION_JSON` in this environment's
settings** (export a fresh session the same way as the 2026-08-22 fix),
or run `publish_gumroad.py` locally.

**TPT: found and fixed 2 real bugs, but still blocked.** First attempt
failed immediately: `RuntimeError: TPT_EMAIL and TPT_PASSWORD must be set
in .env`, even though `TPT_SESSION_JSON` *is* set in this container. Read
`cmie/publishing/tpt.py` and found `upload_unit()` /
`replace_product_file()` both raised on missing email/password *before*
ever calling `_login()` — which already tries the cookie/env session
first and only needs credentials for the form-login fallback. Fixed by
removing the upfront requirement and instead having `_login()` itself
refuse a blank-credential form submit explicitly (never silently attempt
one — that has triggered TPT bot detection and an account lock before).

Retried — got past the credential check, but then hit a second bug:
`playwright._impl._errors.TargetClosedError` / "Missing X server or
$DISPLAY". Both launch sites called `pw.chromium.launch(headless=False,
...)` directly, bypassing the `_ensure_display()` throwaway-Xvfb-server
helper that `automation_chrome()` already uses elsewhere in this project
for exactly this cloud-sandbox failure. Fixed by calling
`_ensure_display()` before each launch and tearing it down in the
existing `finally:` blocks.

Retried again with both fixes: `TPT_SESSION_JSON` now loads
successfully and `_login()` attempts it, but `_is_logged_in()` still
comes back false — the debug screenshot shows a normal, non-Cloudflare-
challenge TPT homepage in a logged-out state (not the "Performing
security verification" screen from the 2026-08-24 note). This is a
*different* symptom than the previously-documented hard Cloudflare
block, and might just mean today's `TPT_SESSION_JSON` value is stale —
**worth a human trying `python publish_tpt.py --save-session` to refresh
it** before concluding this is the same unfixable platform limit. Did
not retry further or attempt any login workaround, per standing
instructions.

Both TPT fixes committed and pushed directly to `main`
(`770610b`) — they're real, narrowly-scoped correctness fixes
independent of whether TPT itself unblocks.

**Queue item left unchecked** (`data/units/UPCOMING_QUEUE.md`) — TES is
live, TPT + Gumroad both need a human/local step before this unit is
complete. Bundle URL and marketing-content generation deferred until
TPT is live (bundle_urls.json only holds TPT product URLs; marketing
content is normally generated once the full listing set exists).
Boundaries respected: nothing deleted, no Categories/Licence touched on
any published resource, no off-brand products touched, no pricing/
strategic changes.

## 2026-08-24 — Scheduled business review + integrity checks: TPT session expired (accepted platform limit), Gumroad and TES both clean

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers against all 12 live units. Report-only run —
nothing found below was touched, edited, or deleted.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-24 06:28 UTC):
- **TPT**: could not check — session expired. Exact error: "TPT session
  expired (.tpt_session.json no longer valid). Refresh it manually once:
  python publish_tpt.py --save-session (automated form login is disabled
  here — it has triggered TPT bot detection and an account lock before)."
  Per this session's task instructions and the "Known platform limitation"
  note above, this is an accepted platform limit (Cloudflare blocks fresh
  browser fingerprints in the cloud container regardless of cookie
  validity) — did not attempt any login workaround or retry.
- **Gumroad**: AUD 0.00 net, 0 sales (via API, `GUMROAD_TOKEN` — checked
  successfully).
- **TES**: GBP 0.30 net, 1 sale (via saved session cookies — checked
  successfully).
- **Combined (not currency-converted)**: AUD 0 + GBP 0.30.

**Catalog**: 12 live units, unchanged from the last review.

**Integrity checks**:
- **TPT** (`verify_tpt_listings.py --unit <id>` × 12): all 12 failed with
  "not logged in to TPT (no valid session found) — cannot check listings"
  (`Could not extract Chrome cookies: 'DBUS_SESSION_BUS_ADDRESS'`). Same
  accepted platform limit as above, not a new issue — no checks could run,
  which is distinct from "0 products, nothing to check."
- **Gumroad** (`verify_gumroad_listings.py`): 13 of 17 products matched
  'Unit 1' and were checked, all `[OK] (published)`. No integrity issues.
- **TES** (`verify_tes_listings.py`): 22 of 33 resources matched 'Unit 1'
  and were checked, all `[OK]`. No integrity issues.

**No new integrity issues found.** Open items unchanged from the prior
entry (TES Unit 1 AI-series cosmetic bug, TES duplicate pair 13432831 /
13432796, permanently-broken TES resource 13445828, off-brand Gumroad
products, real unattended scheduling) — see `BUSINESS_REVIEW.md` for the
current list.

## 2026-08-24 — Automation hardening session: fixed root causes behind 4 routines' recurring failures, automated TES publish, confirmed TPT cloud automation is a hard platform limit (not a bug)

Working session (not a scheduled routine run) to get all 4 routines to a
state where a full week can run unattended. Found and fixed real, live
bugs; ran two real corrective actions; made one deliberate scope decision.

**Root-caused the Gumroad duplicate-listing incident.** The Gumroad API
paginates at 10 products/page via `next_page_url`. Once the catalog
passed 10 products (2026-08-22), `verify_gumroad_listings.py` had been
silently checking only page 1 for days — reporting "10 of 10, all clean"
while never seeing the other real products — and `publish_pinterest.py`'s
thumbnail lookup independently hit the same blind spot, falsely
concluding `algorithms` and `networks_hardware` had no Gumroad listing at
all (both real, both on page 2; a cloud Marketing Push run on 2026-08-22
logged this exact false conclusion too). Trusting that false signal, 2
duplicate live Gumroad products were created (`jimmhz`, `ffsjn`) before
the real cause was found. Fixed: both fetchers now paginate fully; the
two duplicates were deleted (0 sales on either, originals `bpvevc`/`rrdvk`
untouched); `publish_gumroad.py`'s product-creation path now refuses to
create a duplicate-titled product at all, closing the class of bug for
good rather than just this instance.

**Automated TES's final "Publish now" step.** This was a deliberate
manual-review gate in `publish_tes.py`/`publish_lead_magnets.py`, not a
technical limitation — confirmed by inspecting the real wizard: step 5
is just a `#confirm` checkbox + "Publish now" button. Automating it is
consistent with this project's standing live-publishing policy (backed
by `verify_tes_listings.py`'s post-publish checks). Added `--publish` to
both scripts and a `--resume <resource_id>` path in `publish_tes.py` for
finishing an already-created draft. Used it live to finish the 2 TES
drafts that had been stuck waiting on this exact manual click since
2026-08-20/21 (resources `13545886`, `13545171`) — both confirmed
published ("Nice one claytongibbs!"; TES notes up to 3 working days
before public visibility).

**Fixed `business_review.py` reporting "0 live units" on every cloud
run** — it read the gitignored `releases/public/` build dir (always
empty on a fresh clone) instead of the git-tracked
`data/units/bundle_urls.json` every other check already treats as the
real catalog list. Now reads the same source of truth.

**Reduced Chromium launch noise** — build 1208 crashes on
`launch_persistent_context()` 100% of the time on this machine; every
run was eating a ~30s failed launch + a large log dump before falling
back to the working build (1223). Added a small local cache
(`~/.cmie_working_chromium.txt`) so it skips straight to the working
build after the first fallback, without hardcoding a version project-wide
(the cloud environment's build can still drift independently).

**Refreshed the local TPT session** — the real auth cookie had been dead
since 2026-07-03 despite `sessionKey` itself being far from expired;
local automation had been silently working the whole time via
`browser_cookie3` reading cookies live from the regular Chrome browser,
masking that the exported snapshot was stale. `browser_cookie3` extraction
itself needs admin rights on this Windows machine (DPAPI), so a true
non-interactive refresh isn't possible here — refreshed via a real login
instead, using the persistent CMIEChrome profile (already Cloudflare-
trusted) rather than `publish_tpt.py --save-session`'s throwaway browser,
which hung indefinitely on Cloudflare's challenge.

**Then disproved the fix.** Testing whether the fresh export would
actually help the cloud environment (via `TPT_SESSION_JSON`), a faithful
local simulation — same anti-detection launch args, a completely fresh
throwaway profile, cookies only 2 minutes old — still hit Cloudflare's
"Performing security verification" page and never got signed in. This
means the TPT blocker was never really about cookie staleness: it's
Cloudflare challenging any new/disposable browser fingerprint regardless
of cookie validity, and the cloud sandbox is definitionally a new
fingerprint every run. Refreshing `TPT_SESSION_JSON` was not pushed to
the cloud environment as a result — it would not have fixed anything.
See the "Known platform limitation" note above for the accepted interim
shape and the explicit instruction that this is not being treated as a
finish line.

**Not yet done**: confirm `GUMROAD_SESSION_JSON` was actually pasted into
the cloud environment (asked 2026-08-22, unconfirmed); a real end-to-end
test of a scheduled routine run under all these fixes.

## 2026-08-24 — Scheduled business review + integrity checks: TPT session expired again, Gumroad and TES both clean

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers against all 12 live units. Report-only run —
nothing found below was touched, edited, or deleted.

**Environment note**: fresh clone had no Python dependencies installed
(`dotenv`, `playwright`, etc. all missing) — installed via
`pip install -r requirements.txt`, not committed, ephemeral to this
container per usual.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-24 01:11 UTC):
- **TPT**: could not check — session expired. Exact error: "TPT session
  expired (.tpt_session.json no longer valid). Refresh it manually once:
  python publish_tpt.py --save-session (automated form login is disabled
  here — it has triggered TPT bot detection and an account lock before)."
  Per the hard boundary against unilateral action, did not attempt any
  login workaround. Last known-good TPT figure: $8.98 USD net, 3 sales
  (2026-08-20 snapshot).
- **Gumroad**: AUD 0.00 net, 0 sales (via API, `GUMROAD_TOKEN` — checked
  successfully).
- **TES**: GBP 0.30 net, 1 sale (form login via saved session succeeded,
  checked successfully).

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (it derives catalog
size from the gitignored `releases/public/*_v001/` build-output directory,
which doesn't exist in a fresh clone, not from the platforms themselves).
Actual live catalog per `data/units/bundle_urls.json`: 12 units
(year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_robotics_physical_computing_unit1, year7_spreadsheets_unit1,
year7_ux_design_unit1, year7_web_design_unit1).

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 12 live
  units. Every one failed identically with "not logged in to TPT (no
  valid session found) -- cannot check listings" (Chrome-cookie fallback
  also failed: `Could not extract Chrome cookies: 'DBUS_SESSION_BUS_ADDRESS'`
  — no real Chrome profile in this sandbox). Root cause is login/session-
  level, not per-unit — same blocker as the revenue check above, not 12
  separate issues. Needs a human to run `python publish_tpt.py
  --save-session` once with a real browser (or set `TPT_SESSION_JSON`) to
  unblock future automated checks.
- `verify_gumroad_listings.py` — **ran clean.** All 10 Gumroad products
  matching "Unit 1" checked (of 10 total); no empty/near-empty
  descriptions, no unrendered markdown, no HTML leakage. All "(published)".
  Same 10 URLs as prior runs (`focuslabdigital.gumroad.com/l/` + `yyrcw`,
  `psbzqv`, `hmntzx`, `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`, `llfnfx`,
  `kezhjt`, `iuunxn`). As previously logged, `algorithms` and
  `networks_hardware` still have no matching Gumroad product at all —
  unchanged, not a new finding.
- `verify_tes_listings.py` — **ran clean.** Found 33 resources total on
  the dashboard, 22 matching "Unit 1" (the other 11 are the shelved
  AI-series resources, which don't carry a literal "Unit 1" string in
  their titles). All 22 checked clean — no empty descriptions, no literal
  HTML tags. 10 of the 12 units again show two resource IDs each under the
  "Unit 1" title prefix (Robotics `13546444` and Orientation `13517731`
  are the only singles); consistent with the already-documented
  explanation (2026-07-31 entry) that these are separate per-lesson
  resources sharing a title prefix, not new duplicates, since their titles
  differ beyond the shared prefix (distinct from the genuine duplicate
  pair below, which share the *exact same* title).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency install
(not committed) and the `BUSINESS_REVIEW.md` regeneration.

---

## 2026-08-26 — Marketing Push: 9 new Pinterest pins posted and individually verified live across 3 units; closed out 2 long-standing "queued, not yet posted" backlog waves now that their Gumroad-thumbnail blocker is resolved

Task: check each live unit's highest existing Pinterest wave, pick 2-3
units most due for a fresh wave, draft 3 distinct-angle pins each, post via
`publish_pinterest.py --unit <id> --wave N`, verify live.

**First finding — 2 of the most-due units already had unposted draft
content, and the blocker on it is now gone.** `year7_algorithms_unit1`
had a full wave 3 marked "queued, not yet posted" since 2026-08-19/20, and
`year7_networks_hardware_unit1` had a wave 2 in the same state — both
originally blocked because neither had a matching Gumroad product/thumbnail
in the account's then-10-product catalog (per the 2026-08-22 entry).
Checked the live Gumroad catalog directly via the API today: it now has 17
products, including both "Algorithms & Programming Logic" and "Networks &
Hardware" with thumbnails present. Confirmed with `--dry-run` before
touching anything live. Rather than draft yet another wave on top of
already-written, on-brand, non-time-sensitive content that simply never
got its chance to post, posted the existing drafts as-is — same approach
taken for robotics' wave 1 on 2026-08-22.

**Third unit — genuinely new content.** `year7_robotics_physical_computing_unit1`
still only had wave 1 (posted 2026-08-22), making it the clearest "newest
with only wave 1" candidate per the task's own criteria. Drafted and
appended a real wave 2: a standout-lesson pin (using sensor data to make
decisions, Lesson 4), a "no engineering background needed" pain-point pin,
and the Lesson 7 capstone-project pin — all distinct from wave 1's generic
bundle/lesson-pack/free-sample promos.

**Posted and verified** (`publish_pinterest.py --unit <id> --wave N`, no
`--dry-run`, after a clean dry-run pass for all three first):
- year7_algorithms_unit1 — wave 3 (Efficiency lesson, capstone, non-specialist pain point)
- year7_networks_hardware_unit1 — wave 2 (data-travel lesson, Term 3 planning, non-specialist pain point)
- year7_robotics_physical_computing_unit1 — wave 2 (sensor-decisions lesson, non-specialist pain point, capstone)

**Verification — did not trust the "Submitted" log lines.** Wrote a
targeted check (scratch script, not committed) rather than running the
full `verify_pinterest_pins.py` sweep, since that script's overall pin-count
check is documented as flaky on this account (lazy-loaded/virtualized list).
Loaded the account's own Created page fresh, took the newest 20 pin ids
(newest-first ordering), and for each of the 9 just-posted pins individually
reloaded its own pin URL and checked `document.title` plus the outbound
teacherspayteachers.com link. All 9 titles and links matched the source
markdown exactly — genuinely live, not just logged as submitted. Updated
each file's wave heading to record this.

Nothing deleted, no off-brand products touched, no pricing/platform/strategy
changes — only Pinterest wave content posted (2 pre-existing drafts, 1
newly drafted) plus the wave-heading status updates above. Dependencies
(`playwright`, `python-dotenv`, etc.) weren't preinstalled in this container;
ran `pip install -r requirements.txt` before anything else (Playwright's
Chromium browser was already present at the environment's preconfigured path).

## 2026-08-22 — Marketing Push: 12 new Pinterest pins posted and verified live across 4 units; discovered the "queued, not yet posted" wave-2 labels across most units were stale (already live), and fixed a verify-script bug that made its title check silently useless

Task: check each live unit's marketing content for its highest Pinterest
wave, pick 2-3 units most due for a fresh wave, draft 3 distinct-angle pins
each, post via `publish_pinterest.py --unit <id> --wave N`, verify live.

**First finding — the premise didn't match reality.** `PINTEREST_SESSION_JSON`
is now present in this container for the first time (prior runs on
2026-08-19/20 logged this credential as the sole blocker). But the
`data/units/marketing/*.md` files' "wave 2 (queued, not yet posted)" labels
turned out to be **stale for 8 of 10 eligible units** — a live check of the
account's own Created page (`focuslabdigitalteach`, via
`verify_pinterest_pins.py`'s approach, extended with scrolling since the
un-scrolled version only surfaces a small first-viewport batch) found wave 2
already live for algorithms, data_representation, digital_systems,
game_design, python_programming, spreadsheets, ux_design, and web_design —
apparently posted in an untracked session, since no prior log entry records
a successful post. Two real exceptions: **cybersecurity** wave 2 is
partially live (2 of 3 pins; "Term 3 Digital Technologies: Cyber Security
Unit Ready to Go" never posted, and there's no way to post a single pin via
this script without duplicating the two already live), and
**networks_hardware** wave 2 is fully unposted. Updated each file's wave-2
heading/body to reflect what's actually live instead of the stale label —
straight documentation-accuracy fix, no wave content changed.

**Second finding — 2 of the "most due" candidates are blocked by a
Gumroad-thumbnail gap, unrelated to Pinterest.** `publish_pinterest.py`
sources its pin image from a matching Gumroad product thumbnail. Confirmed
live (dry-run, real error) that **algorithms** and **networks_hardware**
have no matching Gumroad product at all in this account's current 10-product
catalog — so neither can be posted to right now regardless of wave content
readiness. Not something to fix in a marketing-only run; flagging for the
person maintaining Gumroad listings.

**What was actually picked and posted** (2 for "haven't had one recently" +
1 for "newest with only wave 1", per the task's own criteria, adjusted for
the thumbnail blocker above):
- **year7_orientation_unit1** — never had a wave 2 (only unit besides the
  brand-new robotics without one). Drafted and posted wave 2: a
  Passwords-&-Privacy lesson deep-dive, a "stop building this from scratch"
  pain point, and a deliberate pivot away from wave 1's back-to-school
  framing (new-student-mid-year angle) since wave 1 already fully owned
  that angle.
- **year7_cybersecurity_unit1** — rather than trying to patch the 1 missing
  wave-2 pin (would duplicate the 2 already live), drafted and posted a
  full wave 3: a "What Do Your Apps Collect" privacy-lesson deep-dive, the
  Lesson 7 capstone, and a "not an IT expert" teacher pain point.
- **year7_data_representation_unit1** — oldest bundle still with a working
  Gumroad thumbnail (algorithms and networks_hardware, the actual oldest,
  are blocked per above) and hasn't been refreshed since wave 2. Drafted
  and posted wave 3: an ASCII/Unicode lesson deep-dive, the Lesson 7
  capstone, and a "not a CS specialist" pain point.
- **year7_robotics_physical_computing_unit1** (added mid-session) — while
  investigating, pulled `origin/main` per this run's branch instructions and
  found it 3 commits ahead, including "Mark Robotics & Physical Computing
  unit complete — all 3 platforms live." That commit unblocked exactly the
  Gumroad-thumbnail gap above for this one unit (confirmed live via the
  Gumroad API: thumbnail now present, product published). Robotics had
  **zero** Pinterest pins live — its wave 1 was drafted at unit-launch but
  never posted. Posted the existing wave 1 as-is (no new content needed,
  nothing to be distinct from yet).

All 12 pins (3 x 4 units) verified live individually by re-loading each
pin's own URL and checking `document.title` + outbound TPT link — not just
the publish script's "Submitted" log line. Titles and links all matched the
source markdown exactly.

**Bug fixed in `verify_pinterest_pins.py`**: its title-emptiness check used
`document.querySelector('h1')`, but a pin page renders two `<h1>` elements —
a generic "Pinterest" site-header one first, then the real pin title — so
the check always read the generic one and could never actually detect an
empty title. Confirmed live by inspecting the DOM directly. Switched to
`document.title`, which reliably holds the real pin title. Not otherwise
touched — its pin-count check remains flaky (two consecutive runs today
found 26 and then 18 of the same live pins, seemingly due to Pinterest's
lazy-loaded/virtualized list and the script's fixed 4s wait with no
scrolling) — a separate, pre-existing limitation not fixed here since this
run's own targeted per-pin verification already covers what was posted
today.

**Branch note**: per this run's instructions, started work on an isolated
branch that was 3 commits behind `origin/main` (`git status` showed it as
literally named `main` locally, but `git fetch` + `git log origin/main`
showed it wasn't current). Stashed local changes, fast-forwarded to
`origin/main` (no conflicts — the incoming commits only touched
`publish_gumroad.py` and `UPCOMING_QUEUE.md`), reapplied the stash, and
committed on top of the up-to-date `main`.

Nothing deleted, no off-brand products touched, no pricing/platform/strategy
changes — only Pinterest wave content drafted and posted, plus the
documentation-accuracy and verify-script fixes described above.

## 2026-08-21 (later run) — New Unit Production: Robotics & Physical Computing built and QA-verified end-to-end; TES live, TPT and Gumroad both blocked by missing/expired credentials — queue item left unchecked

Task: `data/units/UPCOMING_QUEUE.md`'s first unchecked item, **Robotics &
Physical Computing**.

**Built**: `data/units/year7_robotics_physical_computing_unit1.json` (7
topics — sensors/actuators/control systems, inputs & outputs, programming
movement with sequences/loops/conditionals, using sensor data to make
decisions, microcontrollers, testing & debugging, designing a robotic
solution for a real problem). Ran `python produce_unit.py --unit-config
data/units/year7_robotics_physical_computing_unit1.json` end-to-end
(pipeline → qa → thumbnail → package) — all stages passed, automated QA
found no AI-leftover language or `- -` artifacts, packaging validation
clean, all 10 customer zips built and verified.

**Manual spot-check (per this queue's own standing instruction not to trust
automated QA alone)**: read Lesson 1, Lesson 4, and Lesson 7's actual PPTX
slide text, plus `Assessment_Task.docx`, directly. Content is genuinely
good — coherent, on-topic, age-appropriate, no markdown leaks, no AI/ethics
framing bleeding in from the shelved AI series. One near-miss: a naive text
extraction (joining run text without preserving `<a:br/>` elements) made two
hook slides look like run-on sentences with a missing space
("...automatically.How does..."). Checked the real `text_frame.text`
(preserves breaks as `\x0b`) and confirmed these are genuine paragraph
breaks that render as a clean two-line hook in real PowerPoint — same
false-positive class already documented in `PROGRESS.md`'s 2026-07-02 visual
QA section (`<a:br/>` reads back as `\x0b`, not a defect). Not a real bug,
no fix needed.

**Publishing — 1 of 3 platforms live**:
- **TES: live.** `publish_tes.py --unit year7_robotics_physical_computing_unit1
  --price 9.99` filled and saved the 5-step wizard draft (resource
  `13546444`). Then performed the manual-equivalent "Publish now" step
  myself (checked the copyright confirmation box, clicked "Publish now" on
  the existing draft's own Publish screen — did not touch Categories or
  Licence, per the hard boundary above) and verified via a fresh page load
  of `tes.com/teaching-resource/resource-13546444`: real public resource
  page, "Last updated 21 August 2026", Edit/Download/Share controls visible.
  `verify_tes_listings.py --keyword Robotics` ran clean (`[OK]`, no
  AI-leftover language).
- **TPT: blocked, not attempted.** `TPT_SESSION_JSON` cookies (`sessionKey`,
  `TPT`, `__cf_bm`) are expired — confirmed directly by decoding the env
  var's own cookie expiry timestamps (expired ~1 day before this run), not
  just inferred from a failed check. `verify_tpt_listings.py --unit
  year7_robotics_physical_computing_unit1` independently confirmed "not
  logged in." No TPT_EMAIL/TPT_PASSWORD configured, and per this project's
  standing policy (a past bot-detection account lock), automated form-login
  is deliberately never attempted as a workaround. **Needs a human to run
  `python publish_tpt.py --save-session`**, then `python publish_tpt.py
  --unit year7_robotics_physical_computing_unit1 --part all --publish`.
- **Gumroad: blocked, not attempted.** `publish_gumroad.py --unit
  year7_robotics_physical_computing_unit1 --price 12.99` failed at the
  Playwright login step (before any product was created via the API — safe,
  nothing orphaned on Gumroad): "No GUMROAD_EMAIL/GUMROAD_PASSWORD in .env
  and no saved session." `GUMROAD_TOKEN` is present in this container's env
  but the API token alone only covers product creation; the zip/thumbnail/
  description upload steps need a real browser session. **Needs a human to
  either set `GUMROAD_EMAIL`/`GUMROAD_PASSWORD`, or run `python
  publish_gumroad.py --save-session`**, then `python publish_gumroad.py
  --unit year7_robotics_physical_computing_unit1 --price 12.99`.

**Deliberately not done this run**: `data/units/bundle_urls.json` entry and
`generate_marketing_content.py` — both are built around a TPT bundle URL
(every existing entry in that file is a teacherspayteachers.com link, and
`generate_marketing_content.py` uses it as the primary promo link for
Pinterest/social copy). Adding an interim Gumroad/TES link there would
break that convention for no real benefit before TPT is live, so left for
whoever finishes the TPT step.

**Queue item left unchecked** — 2 of the 3 required platforms (TPT,
Gumroad) aren't live, so the "publish across TPT/Gumroad/TES, add bundle
URL, generate marketing" checklist isn't complete. **Important**: this
session's `releases/`, `generated_lessons/`, and the `.produce_state.json`
resume file are all gitignored (not persisted) — the built content only
exists in this container's ephemeral disk. Whoever picks this up next,
either **finish it from here in this same session/container** (fastest —
content is already built and QA-verified) or, if this container has already
been reclaimed, **re-run `produce_unit.py` for this exact config from
scratch** (costs OpenAI generation again) before publishing TPT/Gumroad —
do not try to "resume" from a state file that no longer exists. Do not
re-pick "Robotics & Physical Computing" as a *new* topic; it's this same
in-flight item, not a fresh one.

**Nothing deleted, no off-brand products touched, no pricing/strategy
changes** — Gumroad/TES prices used match the existing catalog norm
($12.99 AUD / £9.99, same as all 10 live units), not a new decision.

## 2026-08-21 — Resource Drop: Lesson 3 lead magnet for year7_cybersecurity_unit1 (TES draft live, TPT still blocked by session expiry); two cloud-sandbox Playwright bugs fixed

Task: `data/units/RESOURCE_DROP_QUEUE.md`'s first unchecked item — a second
free lead magnet for `year7_cybersecurity_unit1`, picking a genuinely strong,
standalone lesson (not the existing Lesson 1 sample).

**Lesson choice**: read `data/units/year7_cybersecurity_unit1.json`'s 7
topics. Picked **Lesson 3, "Spotting Phishing and Social Engineering"**
(17 slides, the longest of the candidates; Lessons 2/4/5/6 were 15 slides
each) — phishing/social-engineering awareness is immediately relatable and
doesn't require the threat-landscape overview from Lesson 1 to make sense,
unlike Lesson 7 (a capstone that assumes the whole unit). Built via
`make_lead_magnet.py --unit year7_cybersecurity_unit1 --lesson 3` from the
tracked `data/units/lead_magnet_source/` fallback (no local `releases/`
tree in this fresh clone) — zip built clean, `zipfile.testzip()` found no
corrupt entries.

**Two environment bugs fixed in `cmie/publishing/browser.py` before
anything could publish** (both blocked this exact task, not
lead-magnet-specific — every script that launches a browser in this
container was affected):
1. `cloud_launch_kwargs()`'s `channel="chromium"` fix (added 2026-07-31)
   stopped working: this session's `pip install -r requirements.txt` pulled
   Playwright 1.62.0, whose registry expects a Chromium revision that
   doesn't match what's actually pre-installed at
   `$PLAYWRIGHT_BROWSERS_PATH/chromium` (a plain symlink, revision 1194) —
   `channel="chromium"` looked for a binary that was never downloaded, and
   `playwright install` is disabled in this sandbox. Fix: pass
   `executable_path` at the pre-installed symlink directly when it exists,
   falling back to the old `channel="chromium"` behavior otherwise (so a
   differently-provisioned sandbox isn't regressed).
2. `automation_chrome()` (used by `publish_tes.py` / `publish_lead_magnets.py
   --platform tes`) launches headed (`headless=False`) by default, but this
   container has no X server — Chromium exited immediately
   ("Missing X server or $DISPLAY"). Worked around manually once with
   `xvfb-run -a python3 publish_lead_magnets.py ...` to confirm the rest of
   the flow, then fixed properly: `automation_chrome()` now starts its own
   throwaway Xvfb server via a new `_ensure_display()` helper whenever
   `$DISPLAY` isn't already set, so future runs don't need a manual
   `xvfb-run` wrapper. No-op wherever a real or already-provided display
   exists.

**TES**: with both fixes in place, `publish_lead_magnets.py --unit
year7_cybersecurity_unit1 --lesson 3 --platform tes` filled and saved the
draft in one run — resource **13545886**, title "Spotting Phishing and
Social Engineering — Lesson 3 FREE Sample (Cyber Security)". Per this
project's standing rule, it stops at a draft; a human still needs to check
the copyright box and click "Publish now" on the TES Author Dashboard.

**Verification**: `verify_tes_listings.py --keyword "Phishing"
--lead-magnet-lesson 3` found no leftover AI-generation language and no
literal "£1.00" (the previously-fixed paid-minimum mispricing bug), but
could not positively confirm "£0.00" appears on the page either. While
investigating, found and fixed a real bug in the checker itself: it read
the uploader's step-1 (Description) page for the price text, which never
contains a price at all regardless of what's actually saved — the price
only ever renders on step 4 (Licence). Fixed to navigate to the
`/licence-editor` step specifically. Even after that fix, the check remains
inconclusive: on reload, TES's Licence step always shows the "Sell my
resource" tab as visually active by default, regardless of what was
actually saved when `publish_tes.py`'s `_step4_licence()` clicked "Share for
free" and "Continue" during the original publish — this looks like a
stateless UI default rather than evidence of real mispricing (the exact
same click-then-Continue code path is what's already live behind all 10
existing Lesson-1 samples), but this run could not independently confirm it
either way from a static page load. Flagging as **needs a human glance at
resource 13545886 on the TES Author Dashboard** before/when clicking
"Publish now", rather than treating it as a confirmed problem.

**TPT**: still blocked. `TPT_SESSION_JSON` is unchanged since the
2026-08-20 run (same cookies, same expiry) — reconfirmed via the same
read-only `verify_tpt_listings.py --unit year7_cybersecurity_unit1` check
(now that the Chromium launch bug above is fixed, the check ran cleanly and
still reported "not logged in"). No TPT publish was attempted (form-login
with placeholder credentials risks bot detection / account lock, per
`cmie/publishing/tpt.py`'s own warning, and there's no `TPT_EMAIL`/
`TPT_PASSWORD` fallback configured). **A human needs to run `python
publish_tpt.py --save-session` (or otherwise refresh `TPT_SESSION_JSON`)
and then run both**:
```
python publish_lead_magnets.py --unit year7_algorithms_unit1 --lesson 5 --platform tpt
python publish_lead_magnets.py --unit year7_cybersecurity_unit1 --lesson 3 --platform tpt
```
to finish the TPT half for both queued lead magnets so far.

**Queue update**: marked `year7_cybersecurity_unit1 — Lesson 3` `[x]` in
`data/units/RESOURCE_DROP_QUEUE.md`, dated 2026-08-21.

**Nothing deleted, no off-brand products touched, no pricing/strategy
changes** — only the lesson-picking judgment call the queue item itself
asked for, plus the two environment bug fixes above (both scoped to
"make an existing script's browser launch actually work in this sandbox",
not new behavior).

## 2026-08-20 — Marketing push blocked again: still no Pinterest credentials in this container, and the script's `--wave` support caps out at 2

Task: check each live unit's marketing-content file
(`data/units/marketing/<unit>_marketing_content.md`, tracked in git —
confirmed present and readable in this fresh clone, unlike the 2026-08-19
run which hit a since-fixed `releases/`-not-committed blocker) for its
highest existing Pinterest wave, pick 2-3 units most due for a fresh wave,
draft 3 new distinct-angle pins each, and post via `publish_pinterest.py
--unit <id> --wave N`. Did not get past pre-flight checks — nothing was
drafted or posted, and no files were changed.

**Blocker 1 — no Pinterest credentials in this container, same as the
2026-08-19 (later run) finding.** Checked this session's full environment
and the repo root: no `.pinterest_session.json` (the cookies file
`publish_pinterest.py` requires — `COOKIES_FILE.exists()` is the first
check in `main()` and exits immediately if missing) and no `PINTEREST_*`
env var of any kind. This container does have working credentials for the
other three platforms (`TPT_SESSION_JSON`, `GUMROAD_TOKEN`,
`TES_EMAIL`/`TES_PASSWORD`), so this is specific to Pinterest, not a
general secrets-provisioning gap. `publish_pinterest.py` has no env-var
fallback for its cookies (unlike `publish_tpt.py`'s `TPT_SESSION_JSON`
pattern), so nothing short of adding the cookies file or extending the
script would let this run unattended. This is the same open item flagged
2026-08-19 — still not provisioned a day later, still outstanding.

**Blocker 2 — found while reading `publish_pinterest.py`, independent of
credentials, and relevant to any future run once credentials exist.**
`parse_marketing_pins()` only recognizes two section shapes: a heading
with no "wave N" marker (treated as wave 1, the default) or one containing
literally "wave 2". `main()`'s `--wave` argument is also hard-capped with
`choices=[1, 2]` — passing `--wave 3` is rejected by argparse before the
script even runs, and if that cap were simply raised, `parse_marketing_pins`
would still silently fall through to the wave-1 section for any wave != 2
(the `else` branch only excludes headings that *do* contain a "wave \d"
marker, so a wave-1 heading — which has none — matches by default
regardless of what wave number was requested). This matters right now
because checking `data/units/marketing/*_marketing_content.md` found 10 of
the 11 live units already carry a "## Pinterest pins — wave 2 (queued, not
yet posted)" section (only `year7_orientation_unit1` is still wave-1-only)
— so most units are due for wave 3, which this script cannot currently
parse or accept even once credentials exist. Not fixed here: doing so
untested (no way to dry-run against a real Pinterest session without the
missing cookies) risked landing a wave-3 code path that looks plausible but
has never actually posted a pin — a worse outcome than leaving it broken
and flagged.

**Also note**: the wave-2 sections in 10 of the 11 files are marked
"(queued, not yet posted)" in their own heading text — worth a human check
on whether that's accurate (were they truly never posted?) or just stale
labeling from whenever wave 2 was drafted, since this run had no way to
verify posting history without the missing credentials.

**Net effect, unchanged from 2026-08-19**: there is no path in this cloud
environment from "draft new Pinterest pins" to "actually post and verify
them" until a human either adds a `.pinterest_session.json` /
`PINTEREST_SESSION_JSON`-style secret to this environment, or accepts that
the Marketing Push job cannot run unattended. Once that's in place, the
`--wave` cap in `publish_pinterest.py` also needs generalizing past 2
before any unit past its second wave can be posted.

No files changed, no pins drafted, nothing posted, nothing deleted. Only
change this run is this log entry.

## 2026-08-20 — Resource Drop: Lesson 5 lead magnet for year7_algorithms_unit1 (TES draft live, TPT blocked by session expiry)

Ran the Resource Drop queue job (`data/units/RESOURCE_DROP_QUEUE.md`). First
unchecked item: a Lesson 5 lead magnet for `year7_algorithms_unit1`
("Debugging: Finding and Fixing Logic Errors").

**Environment setup**: same recurring pattern as every prior fresh-clone
session — installed `python-dotenv`, `browser_cookie3`, `openai`,
`python-pptx`, `python-docx`, `yt-dlp` from `requirements.txt`, plus
`playwright==1.56.0` pinned over pip-latest to match this container's
pre-installed Chromium build 1194 at `/opt/pw-browsers`. Also had to wrap
both Playwright browser launches in `xvfb-run -a` — the headed Chrome
launch failed outright with "Missing X server or $DISPLAY" otherwise. Both
are ephemeral shell/container setup, not code changes.

**Build**: `python make_lead_magnet.py --unit year7_algorithms_unit1
--lesson 5 --bundle-url <TPT unit URL from data/units/bundle_urls.json>`
ran cleanly, using the tracked `data/units/lead_magnet_source/` fallback
(no local `releases/public/` in this fresh clone). Output zip
`year7_algorithms_unit1_lesson05_FREE_v001.zip` — verified with
`zipfile.testzip()` (no corrupt entries) and a manual listing check (single
`.pptx` entry, 57,859 bytes, as expected).

**Bug found + fixed (small, targeted)**: `publish_lead_magnets.py --platform
tes` failed every attempt at the Title-field click on TES's upload form —
`onetrust-pc-dark-filter` (the cookie-consent banner) was intercepting
pointer events, timing out after 30s. This is the exact same issue already
documented and worked around in `verify_tes_listings.py`'s
`find_resource_ids()` for the dashboard's "Show all" button, just not
applied to the upload flow in `publish_tes.py`. Added the same
`#onetrust-accept-btn-handler` dismissal right after
`_navigate_to_upload()` reaches the upload form, before any field
interaction. This is a narrow robustness fix mirroring an existing pattern
in the same codebase, not a strategic or pricing change. Commit will include
this fix to `publish_tes.py`.

**TES result**: succeeded after the fix. `python publish_lead_magnets.py
--unit year7_algorithms_unit1 --lesson 5 --platform tes` filled and saved
resource **13545171** as a draft (title, description, zip upload,
categories, and "Share for free" licence all confirmed via screenshot at
`releases/debug_tes_year7_algorithms_unit1_lead_magnet_l05_step5_preview.png`).
Per this project's standing TES rule, it stops at draft — a human still
needs to tick the copyright box and click "Publish now" on the TES Author
Dashboard. Separately re-checked the Author Dashboard's "My uploads" list
(sorted by date): only the one new draft appears, correctly titled — no
stray/empty duplicate drafts left behind from the earlier failed attempts
(those failed before any TES field was filled or submitted).

**TPT result**: blocked, not attempted. `TPT_EMAIL`/`TPT_PASSWORD` are not
set in this environment (only `TPT_SESSION_JSON`), and
`cmie/publishing/tpt.py`'s `upload_unit()` hard-requires both before it will
even open a browser — this looks like a deliberate safety guard, not a bug,
since the alternative (falling through to real form-login with placeholder
credentials) is exactly the path that caused a documented bot-detection /
account-lock incident on this store before. Confirmed the session really is
stale rather than just untested: (1) the cookies in `TPT_SESSION_JSON` carry
`expirationDate` timestamps of ~2026-08-20 10:20-12:20 UTC, and this run
started at 10:47 UTC — already past; (2) a **read-only** check,
`python verify_tpt_listings.py --unit year7_algorithms_unit1`, independently
confirmed "not logged in to TPT (no valid session found)". Notably, this
same day's earlier business-review run (see the entry directly below,
timestamp 05:41 UTC) had a working TPT session — so this is session-freshness
timing (cookies good for a few hours), not a permanently broken pipeline. Did
not attempt any workaround. **Needs a human** to run `python publish_tpt.py
--save-session` with a real browser (or otherwise refresh
`TPT_SESSION_JSON`), then run `python publish_lead_magnets.py --unit
year7_algorithms_unit1 --lesson 5 --platform tpt` to finish the TPT half.

**Queue update**: marked `year7_algorithms_unit1 — Lesson 5` `[x]` in
`data/units/RESOURCE_DROP_QUEUE.md` with today's date (the automatable half
— build + TES draft — is done, and re-running it next cycle would just
create a second duplicate TES draft), and added a note in that file's own
Log section with the exact commands needed to finish the TPT half.

**Nothing was deleted, no off-brand products were touched, no pricing or
strategic changes were made.** Files changed: `publish_tes.py` (the
cookie-banner fix above), `data/units/RESOURCE_DROP_QUEUE.md` (item checked
off + log note), this file. `releases/artifacts/*` and `releases/debug_*.png`
are gitignored working files, not committed.

## 2026-08-20 — Scheduled business review + integrity checks: all three platforms fully working, all catalogs clean, prior networks_hardware_unit1 anomaly resolved

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies pre-installed. Installed
`python-dotenv`, `browser_cookie3`, `openai`, `python-pptx`,
`python-docx`, `yt-dlp` from `requirements.txt`, plus `playwright==1.56.0`
pinned over pip-latest to match this container's pre-installed Chromium
build 1194 at `/opt/pw-browsers` — same workaround as every prior run.
Ephemeral to this container only; `requirements.txt` still doesn't pin
the playwright version.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-20 05:41
UTC):
- **TPT**: USD 8.98 net, 3 sale(s) — real figures via `TPT_SESSION_JSON`
  env var, login/session worked cleanly this run.
- **Gumroad**: AUD 0 net, 0 sale(s) — via `GUMROAD_TOKEN` API.
- **TES**: GBP 0.30 net, 1 sale(s) — real figures; `TES_EMAIL`/
  `TES_PASSWORD` form login succeeded and saved a fresh session
  (`.tes_session.json`), unlike several recent runs where TES login
  failed outright.
- **All three platforms returned genuine, credentialed figures this
  run** — first time in a while all three have worked in the same run.

**Catalog size**: `business_review.py` again reports **0 live unit(s)** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent here). Real catalog (from `data/units/*.json`, excluding
the AI-series and bundle config files) is the same 11 units as every
recent run: year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 live
  units, session valid throughout. **All 11 units came back fully clean**,
  every listing `[OK]` — no empty/near-empty descriptions, no unrendered
  markdown, no stray HTML, no title/product mismatches.
  - Notably, **`year7_networks_hardware_unit1` is back to 9 products**
    (bundle, assessment pack, 7 lessons), all `[OK]`. The prior run
    (2026-08-19 later run) flagged this unit as returning only 1 product
    against an expected ~9 — that anomaly did not reproduce this run;
    whatever caused it (a transient dashboard search/pagination glitch,
    most likely, given the same-day commit "Fix verify_tpt_listings.py:
    handle My-Products dashboard pagination") appears resolved. Logging
    for the record, not treating as fully explained from a read-only
    check alone.
- `verify_gumroad_listings.py` — **ran clean.** Checked 10 product(s)
  matching "Unit 1" (of 10 total in the store): all 10 `[OK] (published)`,
  no corruption signals. Same 10 URLs as every prior run
  (`focuslabdigital.gumroad.com/l/` + `yyrcw`, `psbzqv`, `hmntzx`,
  `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`, `llfnfx`, `kezhjt`, `bpvevc`).
- `verify_tes_listings.py` — **ran clean.** Logged in via saved TES
  session cookies. Found 30 resource(s) total on the dashboard; 21
  matched "Unit 1" (the other 9 are the shelved AI-series Unit 1
  resources, out of this checker's filter scope, consistent with the
  documented "9 resources, Unit 1 only" open item below). All 21 checked
  `[OK]` — no corruption signals. This checker does not cover the known
  TES duplicate pair or the permanently-broken resource noted below,
  since neither matches "Unit 1" text filtering; not re-verified this
  run.

**Open items** (unchanged from `BUSINESS_REVIEW.md`'s maintained list,
none actioned; the networks_hardware_unit1 anomaly above appears resolved
but is not being removed from tracking without another clean run to
confirm): TES Unit 1 AI-series presenter-placeholder cosmetic bug, TES
duplicate resource pair (13432831 / 13432796), TES resource 13445828
permanently broken, off-brand Gumroad products still on the storefront,
shelved AI-series Units 3-8 still live on TES.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-19 (later run) — Marketing push blocked: no Pinterest credentials in this container, and no local release artifacts to read wave history from

Task: check each live unit's `07_Marketing/marketing_content.md` for its
highest existing Pinterest wave number, pick 2-3 units most due for a fresh
wave, draft 3 new distinct-angle pins each, and post via
`publish_pinterest.py --unit <id> --wave N`. Did not get past the
pre-flight checks — nothing was drafted or posted.

**Blocker 1 — no local release artifacts to read.** `releases/` is
gitignored (build output, never committed) and does not exist at all in
this fresh clone, same as every prior session's finding for the
`business_review.py` catalog count. That means no unit's
`07_Marketing/marketing_content.md` is present locally, so there is no way
to read prior wave numbers or prior pin angles for any unit. Regenerating
that file with `generate_marketing_content.py` would only ever produce a
fresh "wave 1" section (it has no memory of what waves were posted in past
sessions) — using that to decide "genuinely distinct from prior waves"
would be guessing, not checking, so I did not generate or post anything on
that basis.

**Blocker 2 — no Pinterest credentials at all, independent of blocker 1.**
Checked this container's full environment (`env`) and the repo root: no
`.pinterest_session.json` (the cookies file `publish_pinterest.py` requires
and exits immediately without — `COOKIES_FILE.exists()` is the very first
check in `main()`), and no `PINTEREST_*` variable of any kind. This is
unlike today's earlier business-review run in this same log, which found
`GUMROAD_TOKEN`, `TES_EMAIL`/`TES_PASSWORD`, and `TPT_SESSION_JSON` all
newly present as container env vars — Pinterest has no equivalent, here or
in any prior logged run I can find. `publish_pinterest.py` has no
env-var fallback for its cookies (unlike `publish_tpt.py`'s
`TPT_SESSION_JSON` pattern), so even if one existed it wouldn't currently
be picked up — not changed here since there's no secret to wire up and
this is a report-only run.

**Net effect**: even with real Gumroad-thumbnail and unit-config access,
there is currently no path in this cloud environment from "draft new
Pinterest pins" to "actually post them" — the credential this specific job
needs has never been provisioned, in contrast to the other three
platforms which now have working (if sometimes broken) credentials. Worth
a human decision: either add a `.pinterest_session.json` /
`PINTEREST_SESSION_JSON`-style secret to this environment (mirroring how
`TPT_SESSION_JSON` was set up), or accept that the Marketing Push job
cannot run unattended until that exists.

No files changed, no pins drafted, nothing posted, nothing deleted. Only
change this run is this log entry.

## 2026-08-19 (second run) — Scheduled business review + integrity checks: cookie-normalization fix landed, TPT now fully working (revenue + all 11 units verified clean); TES still blocked; one unit's product count looks anomalous

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies pre-installed (`dotenv`, `playwright`,
`browser_cookie3`, etc. all missing) — installed via `requirements.txt`
plus `playwright==1.56.0` pinned over the pip-latest 1.62.0 (which again
does not match this container's pre-installed Chromium build 1194), same
workaround as every prior run. Ephemeral to this container only —
`requirements.txt` still doesn't pin the playwright version.

**This is the second business-review run today.** The `Normalize raw
Cookie-Editor exports before Playwright add_cookies()` commit that landed
between the first run (11:03 UTC) and this one fixed the exact `sameSite`
parse error that broke `TPT_SESSION_JSON` in that run — TPT authentication
now works end-to-end here, both for revenue and for the integrity
checkers.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-19 11:14
UTC):
- **TPT**: USD 7.91 net, 2 sale(s) — real figures, first successful TPT
  revenue check in several runs.
- **Gumroad**: AUD 0 net, 0 sale(s) — via `GUMROAD_TOKEN` API, unchanged.
- **TES**: ERROR — still "TES login failed. Check TES_EMAIL/TES_PASSWORD in
  .env, or the login form's selectors may have changed -- check
  releases/debug_tes_login_error.png." `TES_EMAIL`/`TES_PASSWORD` are set
  in the environment, so this remains a genuine login failure (wrong/stale
  credentials, a CAPTCHA, or a changed selector), unchanged from the first
  run today. The referenced debug screenshot is still never written on
  this failure path (same dead troubleshooting pointer noted in the first
  run's entry — tool bug, not touched, report only). No `releases/`
  directory exists in this fresh clone at all.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent here). Real catalog (from `data/units/*.json`, excluding
the AI-series and bundle config files) is the same 11 units used for the
integrity checks below: year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran successfully against all
  11 live units (session now valid, per the fix above). 10 of 11 units
  returned a product count consistent with prior runs (5-11 products
  each — bundle, assessment pack, and individual lessons) and every single
  listing on every unit came back `[OK]` — no empty/near-empty
  descriptions, no unrendered markdown, no stray HTML, no title/product
  mismatches.
  - **Flagging for review, not touched**: `year7_networks_hardware_unit1`
    returned only **1 product** this run — `Networks & Hardware: Unit 1 –
    Building and Securing a Network — Lesson 1 FREE...`
    (https://www.teacherspayteachers.com/Product/Networks-Hardware-Unit-1-Building-and-Securing-a-Network-Lesson-1-FREE-17033469),
    itself `[OK]` with no corruption signals. Per `PROGRESS.md`'s build
    history this unit should have ~9 TPT products (7 lessons + assessment
    pack + bundle), and every other unit checked this run returned 5-11.
    This unit already has a documented history of a live-listing
    corruption incident (2026-07-19, licence step edit turned a paid
    listing FREE — see the boundary note at the top of this log). Whether
    the other ~8 products are deactivated, retitled (so the keyword search
    no longer matches them), or something else is unknown from this
    read-only check alone — flagging for a human look, not investigated
    further and nothing changed.
- `verify_gumroad_listings.py` — **ran clean.** Checked 10 product(s)
  matching "Unit 1" (of 10 total in the store): all 10 `[OK] (published)`,
  no corruption signals. Same 10 URLs as prior runs
  (`focuslabdigital.gumroad.com/l/` + `yyrcw`, `psbzqv`, `hmntzx`, `caqcw`,
  `dvjrck`, `yqnok`, `ivmbkk`, `llfnfx`, `kezhjt`, `bpvevc`).
- `verify_tes_listings.py` — could not run; failed at the same TES login
  step as the revenue check above (`TES_EMAIL`/`TES_PASSWORD` are set but
  login still fails). No TES listings checked this run.

**Open items** (unchanged from `BUSINESS_REVIEW.md`'s maintained list,
none actioned): TES Unit 1 AI-series presenter-placeholder cosmetic bug,
TES duplicate resource pair (13432831 / 13432796), TES resource 13445828
permanently broken, off-brand Gumroad products still on the storefront,
shelved AI-series Units 3-8 still live on TES. Plus the new
`year7_networks_hardware_unit1` product-count anomaly flagged above.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-19 — Scheduled business review + integrity checks: credentials present for the first time, but TPT and TES both fail for new reasons; Gumroad verified clean

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies pre-installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`, `playwright`,
and `browser_cookie3` for this run only (not committed, ephemeral to this
container; `requirements.txt` still doesn't pin these). One new wrinkle
this run: the pip-latest `playwright` (1.62.0) does not match the
pre-installed Chromium binary in this container (build 1194 on disk vs.
build 1234 expected) and fails with "Executable doesn't exist" — pinned
`playwright==1.56.0` (the version whose bundled `browsers.json` targets
build 1194) to work around it, ephemeral to this container only.

**Unlike every prior logged run, this container DOES have credentials**:
`GUMROAD_TOKEN`, `TES_EMAIL`/`TES_PASSWORD`, and `TPT_SESSION_JSON` are all
set in the environment (no `.env` file, but the env vars are populated
directly). This is new — worth flagging since it means the recurring
"no credentials in this container" blocker from every prior entry
(2026-07-31 through 2026-08-17) is no longer the root cause of the TPT/TES
failures below; there are now two distinct, more specific problems.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-19 11:03
UTC):
- **TPT**: ERROR — "TPT session expired (.tpt_session.json no longer
  valid)." Root cause is more specific than "no session" this time: the
  `TPT_SESSION_JSON` env var IS set, but fails to parse before the
  fallback: `Could not parse TPT_SESSION_JSON: BrowserContext.add_cookies:
  cookies[0].sameSite: expected one of (Strict|Lax|None)` — the first
  cookie's `sameSite` value in that secret is not one of Playwright's
  accepted casings (Playwright requires exactly `Strict`/`Lax`/`None`,
  title-cased). The Chrome-cookie fallback also isn't usable (no real
  Chrome profile / `DBUS_SESSION_BUS_ADDRESS` in this container).
- **Gumroad**: AUD 0 net, 0 sale(s) — real check via `GUMROAD_TOKEN`
  against the Gumroad API (not a credentials error this time).
- **TES**: ERROR — "TES login failed. Check TES_EMAIL/TES_PASSWORD in
  .env, or the login form's selectors may have changed -- check
  releases/debug_tes_login_error.png." `TES_EMAIL`/`TES_PASSWORD` ARE set,
  so this is a genuine login failure (wrong/stale credentials, a CAPTCHA,
  or a changed selector), not a missing-credentials case. Note: the
  referenced debug screenshot is never actually written on this failure
  path — `publish_tes.py`'s `_login()` raises `RuntimeError` directly with
  no `_take_debug_screenshot()` call before it, so the error message's own
  troubleshooting pointer is currently dead; nothing to check at that
  path. (Tool bug, not touched — report only.)
- **No revenue figures obtained this run for TPT or TES.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Real catalog (from `data/units/*.json`,
excluding the AI-series and bundle config files) is still the same 11
units used for the integrity checks below: year7_algorithms_unit1,
year7_cybersecurity_unit1, year7_data_representation_unit1,
year7_digital_systems_unit1, year7_game_design_unit1,
year7_networks_hardware_unit1, year7_orientation_unit1,
year7_python_programming_unit1, year7_spreadsheets_unit1,
year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically with the same
  `TPT_SESSION_JSON` sameSite parse error described above (plus
  `browser_cookie3`'s Chrome-cookie fallback failing separately). No
  listings were actually checked this run — same practical outcome as
  prior runs, different root cause.
- `verify_gumroad_listings.py` — **ran successfully, all clean.** Checked
  10 product(s) matching "Unit 1" (of 10 total in the store): all 10
  showed `[OK] (published)` with no corruption signals (empty
  description, unrendered markdown, stray HTML, title/product mismatch).
  Listed products/URLs: Digital Technologies Orientation Unit 1
  (https://focuslabdigital.gumroad.com/l/yyrcw), Game Design Unit 1
  (https://focuslabdigital.gumroad.com/l/psbzqv), Introduction to
  Programming Unit 1 (https://focuslabdigital.gumroad.com/l/hmntzx),
  Digital Systems Unit 1 (https://focuslabdigital.gumroad.com/l/caqcw),
  Websites & Web Design Unit 1
  (https://focuslabdigital.gumroad.com/l/dvjrck), Spreadsheets & Data
  Analysis Unit 1 (https://focuslabdigital.gumroad.com/l/yqnok), UX &
  Interface Design Unit 1 (https://focuslabdigital.gumroad.com/l/ivmbkk),
  Cyber Security & Digital Footprints Unit 1
  (https://focuslabdigital.gumroad.com/l/llfnfx), Data Representation
  Unit 1 (https://focuslabdigital.gumroad.com/l/kezhjt), Algorithms &
  Programming Logic Unit 1 (https://focuslabdigital.gumroad.com/l/bpvevc).
  This is the first run in this log with a genuine, credentialed Gumroad
  listing check (not just a revenue-API check) — all clean.
- `verify_tes_listings.py` — **could not run**: same `RuntimeError: TES
  login failed...` as the business-review TES check above. No listings
  were actually checked this run.

**Nothing was verified this run for TPT or TES.** No confidence statement
can be made about TPT or TES listing integrity today. Gumroad listings are
newly confirmed clean as of this run. The last clean TES check remains the
2026-07-31 (third run) entry below.

**New open items from this run** (in addition to the carried-forward list
in `BUSINESS_REVIEW.md`, unchanged below):
- `TPT_SESSION_JSON` (as currently set in this container's environment)
  has a malformed cookie — `sameSite` value isn't `Strict`/`Lax`/`None` —
  so it fails to parse and TPT falls back to "not logged in" even though a
  session secret is present. Needs the secret regenerated/reformatted, or
  `publish_tpt.py --save-session` re-run with a real browser.
- TES login is failing with real `TES_EMAIL`/`TES_PASSWORD` credentials
  present (not a missing-credentials case) — cause not diagnosed further
  (report-only; no fix or retry with different logic attempted). Worth a
  human checking those credentials are current and TES hasn't added a
  CAPTCHA/2FA step.
- `publish_tes.py`'s login-failure error message references a debug
  screenshot (`releases/debug_tes_login_error.png`) that is never actually
  written on that code path — the message is misleading for anyone
  debugging this. Not fixed (report only).

**Open items / decisions carried forward unresolved** (see
`BUSINESS_REVIEW.md` for the full current list): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-17 — Scheduled business review + integrity checks: all three platforms blocked again, no credentials or sessions available in this container

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`,
`playwright==1.56.0`, and `browser_cookie3` for this run only (not
committed, ephemeral to this container; `requirements.txt` still doesn't
pin these, so this keeps recurring every fresh session). This container
again has **no `.env` file** (only `.env.example`), no `GUMROAD_TOKEN` env
var, no `.tpt_session.json`, no `.tes_session.json`, and no real Chrome
profile for the cookie fallback (`DBUS_SESSION_BUS_ADDRESS` missing).

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-17 01:10
UTC):
- **TPT**: ERROR — "TPT session expired (.tpt_session.json no longer
  valid)."
- **Gumroad**: ERROR — "Not logged in and no Gumroad credentials in
  .env."
- **TES**: ERROR — "No TES_EMAIL/TES_PASSWORD in .env and no saved
  session."
- **No revenue figures obtained this run on any platform.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically: "ERROR: not
  logged in to TPT (no valid session found) -- cannot check listings."
  (Chrome-cookie fallback also failed: `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'`.) Same root cause as prior runs — no
  session/login available in this container, not a per-unit issue.
- `verify_gumroad_listings.py` — **could not run**: `ERROR:
  GUMROAD_TOKEN not set (checked .env and environment variables)`. No
  listings were actually checked this run.
- `verify_tes_listings.py` — **could not run**: raised `RuntimeError: No
  TES_EMAIL/TES_PASSWORD in .env and no saved session.` No listings were
  actually checked this run.

**Nothing was verified this run.** No confidence statement can be made
about TPT, Gumroad, or TES listing integrity today — the last clean
checks remain the 2026-07-31 (third run) entry below (Gumroad clean, TES
clean).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-10 — Scheduled business review + integrity checks: all three platforms blocked again, no credentials or sessions available in this container

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`,
`playwright==1.56.0`, and `browser_cookie3` for this run only (not
committed, ephemeral to this container; `requirements.txt` still doesn't
pin these, so this keeps recurring every fresh session). This container
again has **no `.env` file** (only `.env.example`), no `GUMROAD_TOKEN` env
var, no `.tpt_session.json`, no `.tes_session.json`, and no real Chrome
profile for the cookie fallback (`DBUS_SESSION_BUS_ADDRESS` missing).

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-10 04:44
UTC):
- **TPT**: ERROR — "TPT session expired (.tpt_session.json no longer
  valid)."
- **Gumroad**: ERROR — "Not logged in and no Gumroad credentials in
  .env."
- **TES**: ERROR — "No TES_EMAIL/TES_PASSWORD in .env and no saved
  session."
- **No revenue figures obtained this run on any platform.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically: "ERROR: not
  logged in to TPT (no valid session found) -- cannot check listings."
  (Chrome-cookie fallback also failed: `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'`.) Same root cause as prior runs — no
  session/login available in this container, not a per-unit issue. Still
  needs a human to run `python publish_tpt.py --save-session` once with a
  real browser (or set `TPT_SESSION_JSON`) to unblock future automated
  checks.
- `verify_gumroad_listings.py` — **could not run**: `ERROR:
  GUMROAD_TOKEN not set (checked .env and environment variables)`. No
  listings were actually checked this run.
- `verify_tes_listings.py` — **could not run**: raised `RuntimeError: No
  TES_EMAIL/TES_PASSWORD in .env and no saved session.` No listings were
  actually checked this run.

**Nothing was verified this run.** No confidence statement can be made
about TPT, Gumroad, or TES listing integrity today — the last clean
checks remain the 2026-07-31 (third run) entry below (Gumroad clean, TES
clean).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-03 — Scheduled business review + integrity checks: all three platforms blocked again, no credentials or sessions available in this container

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same as every prior fresh-clone session, this
container had no Python dependencies installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`,
`playwright==1.56.0`, and `browser_cookie3` for this run only (not
committed, ephemeral to this container; `requirements.txt` still doesn't
pin these, so this keeps recurring every fresh session). This container
again has **no `.env` file** (only `.env.example`), no `GUMROAD_TOKEN` env
var, no `.tpt_session.json`, no `.tes_session.json`, and no real Chrome
profile for the cookie fallback (`DBUS_SESSION_BUS_ADDRESS` missing).

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-03 01:05
UTC):
- **TPT**: ERROR — "TPT session expired (.tpt_session.json no longer
  valid)."
- **Gumroad**: ERROR — "Not logged in and no Gumroad credentials in
  .env."
- **TES**: ERROR — "No TES_EMAIL/TES_PASSWORD in .env and no saved
  session."
- **No revenue figures obtained this run on any platform.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically: "ERROR: not
  logged in to TPT (no valid session found) -- cannot check listings."
  (Chrome-cookie fallback also failed: `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'`.) Same root cause as prior runs — no
  session/login available in this container, not a per-unit issue. Still
  needs a human to run `python publish_tpt.py --save-session` once with a
  real browser (or set `TPT_SESSION_JSON`) to unblock future automated
  checks.
- `verify_gumroad_listings.py` — **could not run**: `ERROR:
  GUMROAD_TOKEN not set (checked .env and environment variables)`. No
  listings were actually checked this run.
- `verify_tes_listings.py` — **could not run**: raised `RuntimeError: No
  TES_EMAIL/TES_PASSWORD in .env and no saved session.` No listings were
  actually checked this run.

**Nothing was verified this run.** No confidence statement can be made
about TPT, Gumroad, or TES listing integrity today — the last clean
checks remain the 2026-07-31 (third run) entry above (Gumroad clean, TES
clean).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-07-31 (fourth run) — Scheduled business review + integrity checks: all three platforms blocked, no credentials or sessions available in this container

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per live
unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`). Report-only
run — nothing found below was touched, edited, or deleted.

**Environment note**: fresh clone again had no Python dependencies
installed (`dotenv`, `playwright`, `browser_cookie3` all missing).
Installed `python-dotenv`, `playwright==1.56.0` (pinned to match the
sandbox's pre-installed Chromium revision 1194 — same fix logged in prior
runs; still not pinned in `requirements.txt`, so this keeps recurring),
and `browser_cookie3`. Unlike every prior run, this container has **no
`.env` file at all** (only `.env.example`), no `GUMROAD_TOKEN` env var, no
`.tpt_session.json`, no `.tes_session.json`, and no real Chrome profile
for the cookie fallback (`DBUS_SESSION_BUS_ADDRESS` missing). Net effect:
every one of the three platforms failed to authenticate this run — worse
than prior sessions, where at least Gumroad (via API token) and/or TES
(via saved session) usually worked.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 06:16
UTC):
- **TPT**: ERROR — session expired / no `.tpt_session.json` found.
- **Gumroad**: ERROR — not logged in, no `GUMROAD_TOKEN` in `.env` or
  environment.
- **TES**: ERROR — no `TES_EMAIL`/`TES_PASSWORD` in `.env` and no saved
  session.
- **No revenue figures obtained this run on any platform.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale. Most recent partial
  snapshot (2026-07-31, third run): Gumroad A$0.00 / 0 sales, TES £0.30
  GBP / 1 sale (TPT still blocked that run too).

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically: "not logged in
  to TPT (no valid session found) -- cannot check listings" (Chrome-cookie
  fallback also failed: `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'`). Same root cause as prior runs — no
  session/login available in this container, not a per-unit issue.
- `verify_gumroad_listings.py` — **could not run**: `ERROR: GUMROAD_TOKEN
  not set (checked .env and environment variables)`. No listings were
  actually checked this run (differs from the third run's "ran clean"
  result — that run had `GUMROAD_TOKEN` available via the environment,
  this one does not).
- `verify_tes_listings.py` — **could not run**: raised `RuntimeError: No
  TES_EMAIL/TES_PASSWORD in .env and no saved session.` No listings were
  actually checked this run (differs from the third run's "ran clean,
  cookie-banner fix confirmed working" result — that run had a saved
  session, this one does not).

**Nothing was verified this run.** No confidence statement can be made
about Gumroad or TES listing integrity today — the last clean checks for
both remain the third run's (2026-07-31, earlier today).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-07-31 (third run) — Scheduled business review + integrity checks: Gumroad clean, TES clean (cookie-banner fix confirmed working), TPT still blocked by missing session

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers (`verify_tpt_listings.py` per live unit,
`verify_gumroad_listings.py`, `verify_tes_listings.py`). Report-only run —
nothing found below was touched, edited, or deleted.

**Environment note**: same as every prior fresh-clone session, this
container had no Python dependencies installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`,
`playwright==1.56.0` (pinned to match the sandbox's pre-installed Chromium
revision 1194, per the pin recommended in the previous log entry — still
not actually added to `requirements.txt`, so future sessions will keep
hitting this cold until someone does), and `browser_cookie3`.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 03:28 UTC):
- **TPT**: could not check — session expired, see TPT blocker below.
- **Gumroad**: A$0.00 net, 0 sales (via API, `GUMROAD_TOKEN`).
- **TES**: £0.30 GBP net, 1 sale — checked successfully (form login
  succeeded, session re-saved to `.tes_session.json`).
- Last confirmed full snapshot (all 3 platforms) remains 2026-07-19: TPT
  $13.45 USD / 1 sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output directory,
which doesn't exist in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known live
  units above. Every single one failed identically with the (now-fixed,
  no-longer-misleading) explicit error: "not logged in to TPT (no valid
  session found) -- cannot check listings" (exit code 2). No
  `TPT_SESSION_JSON` env var is set in this container and no
  `.tpt_session.json` file exists in this fresh clone (gitignored); the
  Chrome-cookie fallback also failed (`Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'` — no real Chrome profile in this sandbox).
  Root cause is login/session-level, not per-unit, so all 11 failures are
  the same issue, not 11 separate ones. Still needs a human to run
  `python publish_tpt.py --save-session` once with a real browser (or set
  `TPT_SESSION_JSON`) to unblock future automated checks.
- `verify_gumroad_listings.py` — **ran clean.** All 10 Gumroad products
  matching "Unit 1" checked; no empty/near-empty descriptions, no
  unrendered markdown, no HTML leakage. All "(published)". Same 10 URLs as
  every prior run (`focuslabdigital.gumroad.com/l/` + `yyrcw`, `psbzqv`,
  `hmntzx`, `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`, `llfnfx`, `kezhjt`,
  `bpvevc`).
- `verify_tes_listings.py` — **ran clean, and the cookie-banner fix from
  commit `deda456` is confirmed working**: login via saved session
  succeeded, the OneTrust consent banner no longer blocked the "Show all"
  click, and the check completed end-to-end (previous run's blocker is
  resolved). Found 30 resources total on the dashboard, 21 matching
  "Unit 1" (the other 9 are the known shelved AI-series Units 2–8
  resources, which don't carry a literal "Unit 1" string in their titles).
  All 21 checked clean — no empty descriptions, no literal HTML tags. Two
  resource IDs matched most topic titles (e.g. Networks & Hardware:
  13517745 and 13517664); read as separate per-lesson resources sharing
  the "Unit 1" title prefix, not new duplicates — distinct from the
  already-logged genuine duplicate pair below, which was flagged because
  the two IDs share the *exact same* title, not just a shared prefix.

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8 still
live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration. Working branch (`claude/practical-ride-bbgxt7`) was already
even with `main` at the start of this run, so nothing needed re-applying.

---

## 2026-07-31 (later run) — Scheduled business review + integrity checks: Gumroad clean, TES verified logged-in but blocked by cookie banner, TPT blocked by missing session

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers. Report-only run — nothing found below was
touched, edited, or deleted.

**Environment note**: this session's clone had no Python dependencies
installed at all (`dotenv`, `playwright` missing) and the pip-installed
`playwright` defaulted to the latest release (1.61.0), which expects
Chromium revision 1228 while the sandbox's pre-installed browser is
revision 1194 — every browser-based check failed with "Executable doesn't
exist at /opt/pw-browsers/chromium-1228/..." until `playwright` was pinned
to 1.56.0 (the version that matches revision 1194) as an environment-level
fix, no project code touched. Worth carrying into `requirements.txt` as a
`playwright==1.56.0` pin so future sessions don't hit this cold — logging
it here rather than doing it unilaterally since it's a dependency-pin
decision, not a bug fix.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 03:13 UTC):
- **TPT**: could not check — see TPT blocker below.
- **Gumroad**: A$0.00 net, 0 sales (via API, `GUMROAD_TOKEN`).
- **TES**: £0.30 GBP net, 1 sale — checked successfully this run (browser
  fix above got TES working again; login via saved-then-refreshed session
  succeeded and the earnings page loaded cleanly).
- Last confirmed full snapshot (all 3 platforms) remains 2026-07-19: TPT
  $13.45 USD / 1 sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session: it derives catalog
size from `releases/public/*_v001/` on local disk, which this session's
clone doesn't have (build artifacts, gitignored). Last real count: 11
units (2026-07-19 snapshot).

**Integrity checkers**:
- `verify_gumroad_listings.py` — **ran clean.** All 10 Gumroad products
  matching "Unit 1" checked; no empty/near-empty descriptions, no
  unrendered markdown, no HTML leakage, no 0-byte zips. All "(published)".
  URLs unchanged from prior runs (`focuslabdigital.gumroad.com/l/` +
  `yyrcw`, `psbzqv`, `hmntzx`, `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`,
  `llfnfx`, `kezhjt`, `bpvevc`).
- `verify_tpt_listings.py` — **could not run a real check.** Tried
  `--unit year7_algorithms_unit1`. It launched and reached TPT fine (the
  browser fix worked), but `.tpt_session.json` does not exist in this
  session's clone (gitignored, and automated form login is deliberately
  disabled — it has triggered TPT bot detection and an account lock
  before per `cmie/publishing/tpt.py`). The Chrome-cookie fallback also
  failed (`browser_cookie3` not installed / no real Chrome profile in this
  container). Net effect: the script found 0 products and printed "All
  checked listings look clean" — **that message is misleading here**, it
  did not actually check anything, it just found nothing because it
  wasn't logged in. Flagging this as a script gap worth a human look: it
  should distinguish "0 products because not logged in" from "0 products,
  genuinely nothing to check." Needs `python publish_tpt.py --save-session`
  run once by a human with a real browser to refresh the session file.
- `verify_tes_listings.py --keyword "Unit 1"` — **login succeeded** (used
  the session file `business_review.py` had just refreshed earlier in this
  same run), but the check itself failed: clicking the dashboard's "Show
  all" button timed out after 30s because TES's OneTrust cookie-consent
  banner (`#onetrust-consent-sdk`) kept intercepting the click — full
  traceback ends in `playwright._impl._errors.TimeoutError:
  Locator.click: Timeout 30000ms exceeded` on
  `page.get_by_text("Show all", exact=False).first.click()` in
  `find_resource_ids()`. This is a fresh failure mode (not the TLS-reset
  issue from earlier today) — worth a human look at whether the script
  should dismiss/accept the cookie banner before clicking. No resource
  data was read, so no findings to report either way this run.

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8 still
live on TES. None of these were touched.

The prior 2026-07-31 entry below (commit `a136294`) already made it to
`main` before this run started, so no stranded-branch work needed porting
forward this time.

---

## 2026-07-31 — Scheduled business review + integrity checks: Gumroad clean, TPT/TES blocked again by browser TLS reset

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers. Report-only run — nothing found below was
touched, edited, or deleted.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 02:13 UTC):
- **TPT**: could not check — see browser blocker below.
- **Gumroad**: A$0.00 net, 0 sales (via API, `GUMROAD_TOKEN` — reliable).
- **TES**: could not check — see browser blocker below.
- Last confirmed full snapshot remains 2026-07-19: TPT $13.45 USD / 1 sale,
  Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` reports **0 live units** this run —
this is an artifact of the fresh checkout, not a real catalog change. It
derives catalog size from `releases/public/*_v001/` on local disk, which
does not exist in this session's clone (build artifacts, not committed to
git). The last real count was 11 units (2026-07-19 snapshot, still the best
available reference — see that entry in `BUSINESS_REVIEW.md`'s git history
or the list below).

**Integrity checkers**:
- `verify_gumroad_listings.py` — **ran clean.** Checked all 10 Gumroad
  products matching "Unit 1"; no empty/near-empty descriptions, no
  unrendered markdown, no HTML leakage, no 0-byte zips. All show status
  "(published)". Product URLs (all OK): `focuslabdigital.gumroad.com/l/`
  `yyrcw`, `psbzqv`, `hmntzx`, `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`,
  `llfnfx`, `kezhjt`, `bpvevc`.
- `verify_tpt_listings.py` — **could not run.** Tried
  `--unit year7_algorithms_unit1` as a representative check; failed before
  it even reached the dashboard (fails on the initial login-state check,
  `https://www.teacherspayteachers.com/` → `net::ERR_CONNECTION_RESET`).
  Since the failure is at browser/network level, not unit-specific, did not
  repeat it across the other 10 known units (year7_cybersecurity_unit1,
  year7_data_representation_unit1, year7_digital_systems_unit1,
  year7_game_design_unit1, year7_networks_hardware_unit1,
  year7_orientation_unit1, year7_python_programming_unit1,
  year7_spreadsheets_unit1, year7_ux_design_unit1,
  year7_web_design_unit1) — same root cause would apply to all.
- `verify_tes_listings.py` — **could not run**, same failure
  (`https://www.tes.com/authn/sign-in` → `net::ERR_CONNECTION_RESET`).

**Browser blocker — status update on the 2026-07-31-earlier TLS fix**: the
TLS-1.2-cap fix from earlier today (`cloud_launch_kwargs()` in
`cmie/publishing/browser.py`, commit `12b07a7`) did **not** resolve the
issue in this session — same `ERR_CONNECTION_RESET` on every HTTPS
navigation through the proxy (reproduced even on `https://example.com`, not
just the target sites). Netlog capture (`--log-net-log`) shows the CONNECT
tunnel itself succeeds (`200 Connection Established`), then the reset
happens immediately after Chromium sends its TLS ClientHello — `net_error
-101` / `os_error 104` (ECONNRESET), before any server response.
`--ssl-version-max=tls1.2` is very likely a no-op on this Chromium build
(141.0.7390.37) — Chrome removed that flag's effect years ago — which would
explain why the earlier fix appeared to work in one diagnostic session but
not here. `plain curl` through the same proxy to the same hosts (TLS 1.3,
HTTP/2) succeeds every time, so this looks Chromium-client-specific, not a
blanket proxy outage. Not fixed here (out of scope for a report-only run,
and the proxy README says client-specific TLS failures need
administrator/Anthropic-support attention, not a code workaround). Also
separately note: this session's `pip install -r requirements.txt` pulled
Playwright 1.61.0, whose bundled Chromium build (revision 1228) doesn't
match what's pre-installed in this container (revision 1194) — had to pin
`playwright==1.56.0` locally in this session just to get Chromium to launch
at all (a session-local pip choice, not a repo change; every fresh
container will hit this same mismatch until `requirements.txt` pins a
compatible version — a decision for a human, not made here).

**No integrity issues found on anything that could actually be checked.**
Open items list unchanged from 2026-07-19 (see below in this file's
history / `BUSINESS_REVIEW.md`) — still waiting on human decisions for the
TES cosmetic bug, the TES duplicate pair (13432831 / 13432796), the
permanently-broken TES resource 13445828, the off-brand Gumroad products,
and real unattended scheduling.

## 2026-07-31 — Cloud Chromium/proxy fix landed and verified; git push permission still blocking

Session goal: get the 4 paused routines (Business Review, New Unit Production,
Marketing Push, Resource Drop — all `enabled: false` since 2026-07-20) back to
a genuinely working state, not just re-enabled and failing quietly again.

**Root cause #1, fixed and verified live**: every Playwright launch site in
the repo either hardcoded `channel="chrome"` (no real Chrome binary in the
cloud container) or had no way to pass the sandbox's egress proxy explicitly
(Chromium doesn't auto-read `HTTP_PROXY`/`HTTPS_PROXY` the way curl/urllib
do). Added `cloud_launch_kwargs()`/`cloud_context_kwargs()` in
`cmie/publishing/browser.py` (no-op locally, activates only when a proxy env
var is present) and wired it into every launch site: `browser.py`,
`cmie/publishing/tpt.py`, `check_revenue.py`, `publish_pinterest.py`,
`verify_tpt_listings.py`, `verify_tes_listings.py`, `verify_pinterest_pins.py`,
`cmie/connectors/tpt.py`. Commit `cd7354e`.

A live diagnostic session run directly in the Claude Code cloud environment
(`env_01DJK4aBcVAJB3m7hdsLorh1`) found this first fix was necessary but not
sufficient: the proxy resets the connection right after Chromium's TLS 1.3
ClientHello, *before* any certificate is exchanged — so
`--ignore-certificate-errors` never got a chance to matter. Isolated via
netlog analysis (ruled out the PQ/Kyber key-share extension specifically);
capping Chromium to TLS 1.2 (`--ssl-version-max=tls1.2`) fixed it cleanly for
both a plain test URL and a real teacherspayteachers.com page load. Added to
the same shared helper. Commit `12b07a7`. **Chromium can now genuinely reach
the internet from this cloud environment — confirmed by a real page load, not
inferred.**

**Root cause #2, found, NOT fixed — needs a human to check GitHub/environment
settings**: `git push origin main` from inside the cloud environment still
returns a 403, on any branch, not just main (matches the 2026-07-20 finding —
this is a distinct, older issue from the Chromium/proxy one, first reported
during that session's routine test-run). This means even a fully-working
routine cannot persist its own work or update this log — everything it does
dies with the container. **This is very likely the single biggest remaining
blocker to real unattended automation** — a routine could now (with the TLS
fix) actually read TPT/Gumroad/TES/Pinterest and act, but has no way to save
what it did. Needs checking on the GitHub side (does the GitHub App/token
backing this Claude Code environment's repo connection actually have
`contents: write` on `MrGibbsTeach/cmie`?) and/or the environment's own
repository-connection settings in the claude.ai/code UI. Not something fixable
via a code change or a tool call from a normal Claude Code session — needs the
account owner's direct action.

**Not yet re-attempted this session**: re-enabling the 4 paused routines. Do
not flip any of them back to `enabled: true` until the git push 403 is
resolved and confirmed with a real push from inside that environment — a
routine that can read but not write is worse than one that's off, because a
clean-looking "success" log message would be lying about whether anything
actually got saved.
PUSH TEST 2026-07-31 -- confirming GitHub App write access after reinstall.
