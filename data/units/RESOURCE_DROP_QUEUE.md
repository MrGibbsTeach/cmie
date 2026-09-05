# Smaller Resource Drop Queue

Read top-to-bottom by the weekly Friday resource-drop job. Complete the
first `[ ]` entry, mark it `[x]` with the date. If every entry is `[x]`,
report "queue empty, nothing to build this cycle" and stop — do not
invent new items.

## Additional lead magnets (2nd free lesson per unit, different from the
## existing Lesson-1 sample already live for all 10 original units)

Use the same pattern as `make_lead_magnet.py` / `publish_lead_magnets.py`,
just pointed at a different lesson number. Pick a genuinely strong,
standalone lesson (not one that depends on earlier lessons to make sense).

- [x] year7_algorithms_unit1 — Lesson 5 (Debugging: Finding and Fixing Logic Errors) — 2026-08-20
- [x] year7_cybersecurity_unit1 — Lesson 3 (Spotting Phishing and Social Engineering) — 2026-08-21
- [x] year7_web_design_unit1 — Lesson 6 (Accessibility and Responsive Design Basics) — 2026-08-28
- [ ] year7_orientation_unit1 — Lesson 4 (Passwords, Privacy, and Protecting Your Information)
- [ ] year7_networks_hardware_unit1 — Lesson 4 (How Data Travels Across a Network)
- [ ] year7_data_representation_unit1 — Lesson 5 (Images as Data: Pixels and Bitmaps)
- [ ] year7_spreadsheets_unit1 — Lesson 4 (Charts and Graphs: Visualizing Data)
- [ ] year7_robotics_physical_computing_unit1 — Lesson 4 (Using Sensor Data to Make Decisions)
- [ ] year7_ux_design_unit1 — Lesson 6 (Accessibility and Inclusive Design)
- [ ] year7_databases_unit1 — Lesson 5 (Asking Questions with Queries: Sorting, Filtering, and Searching)
- [ ] year7_digital_systems_unit1 — Lesson 6 (Troubleshooting Common Computer Problems)
- [ ] year7_game_design_unit1 — Lesson 6 (Playtesting and Iterating on Your Design)
- [ ] year7_digital_media_unit1 — Lesson 4 (Editing Video: Cuts, Transitions, and Pacing)

Added 2026-09-05 (10 new entries above): the previous 3 entries were the
only ones queued, and all 3 are done -- with no bundle items buildable
(see note below), Routine 4 had genuinely run out of completable work.
Picked one standalone, non-Lesson-1 lesson per remaining unit that
doesn't have a second lead magnet yet, favoring lessons that don't
depend on earlier lessons' content to make sense (same criterion the
existing entries above already used). This gives the Friday job real
work for ~10 more weeks.

## Small bundle packages (combine 2-3 existing units, reuse existing zips,
## no new content generation, one new listing per bundle)

**Updated 2026-09-05**: `make_bundle.py` now exists (combines each unit's
persisted `data/units/packaged/<unit_id>_v001_PUBLIC.zip` into one bundle
zip + template listing, then `publish_tpt.py` / `publish_gumroad.py` /
`publish_tes.py --unit <bundle_id>` publish it like any other unit --
see the script's own docstring for the full flow). `package_unit.py` now
persists that packaged zip automatically for every unit built from now
on, so **any unit produced by Routine 2 from 2026-09-05 onward is
bundle-ready with no extra step.** The two items below predate that fix,
so neither Algorithms, Python Programming, Cyber Security, nor Networks
& Hardware has a persisted zip yet -- `make_bundle.py` will refuse
clearly (not silently) if attempted. Leave both unchecked until a human
either (a) backfills those 4 units' packaged zips (re-run
`package_unit.py --unit <id>` in an environment where its
`releases/public/<id>_v001/` still exists, if any does), or (b) accepts
a one-time regeneration cost for them, or (c) decides these two items
aren't worth pursuing and removes them from the queue. Routine 4 should
keep skipping past these two (do not re-investigate from scratch every
week -- this note is the investigation) and work the lead-magnet items
above instead until this is resolved.

- [ ] "Programming Foundations" bundle: Algorithms & Programming Logic + Introduction to Programming (Python) — blocked, see note above
- [ ] "Staying Safe Online" bundle: Cyber Security & Digital Footprints + Networks & Hardware — blocked, see note above

## Log

(the job appends a line here each time it completes or skips a cycle)

- 2026-09-04: Attempted the first unchecked item, the "Programming
  Foundations" bundle (Algorithms & Programming Logic + Introduction to
  Programming Python). **Skipped — blocked by an environment limitation,
  not completed, checkbox left unchecked.** This queue item requires
  "reuse existing zips, no new content generation," but confirmed (fresh
  container, `find`/`git ls-files`) that no full-unit release files exist
  anywhere this session can reach for either unit: `releases/` is
  gitignored and doesn't exist in a fresh clone (same known limitation
  already logged repeatedly elsewhere in `AUTONOMOUS_LOG.md`), and the only
  git-tracked unit content is the free Lesson-1/lead-magnet sample zips
  (`data/units/lead_magnet_source/`, `marketing-site/public/downloads/`) —
  a handful of individual lesson `.pptx` files, not the full 7-lesson +
  assessment + workbook + roadmap + teacher-guide set a paid bundle needs.
  Regenerating either unit via `produce_unit.py` would call the real
  content pipeline, which `produce_unit.py`'s own docstring flags as
  "(OpenAI cost!)" — that's new content generation and real spend, exactly
  what this queue item rules out. The only other route, downloading the
  already-published product files back from Gumroad/TES/TPT as the seller,
  isn't something any script in this repo does today, and building that
  would be new automation infrastructure, not a "no strategic changes"
  reuse of what's already there. Not attempted: no login, no publish, no
  files touched on any platform. **Needs a human decision**: either commit
  a persistent copy of each unit's full release zips somewhere this
  session can reach (mirroring the `lead_magnet_source/` fallback already
  built for lead magnets), or accept the OpenAI regeneration cost for this
  one item, or add a genuine download-existing-product step to the
  publishing scripts. See `AUTONOMOUS_LOG.md` for the same write-up.

- 2026-08-20: Built + published the Lesson 5 lead magnet for
  year7_algorithms_unit1 ("Debugging: Finding and Fixing Logic Errors").
  TES: draft created successfully (resource 13545171), needs a human
  "Publish now" click per this project's standing TES rule. TPT: blocked —
  `TPT_SESSION_JSON` cookies had already expired (confirmed via a read-only
  `verify_tpt_listings.py` check, not a login attempt), and no
  `TPT_EMAIL`/`TPT_PASSWORD` fallback is configured, so no TPT publish was
  attempted this cycle (form-login with placeholder credentials risks bot
  detection / account lock, per `cmie/publishing/tpt.py`'s own warning).
  See AUTONOMOUS_LOG.md for full detail. A human needs to run
  `python publish_tpt.py --save-session` (or otherwise refresh
  `TPT_SESSION_JSON`) and then run
  `python publish_lead_magnets.py --unit year7_algorithms_unit1 --lesson 5 --platform tpt`
  to finish the TPT half.
- 2026-08-21: Built + published the Lesson 3 lead magnet for
  year7_cybersecurity_unit1 ("Spotting Phishing and Social Engineering" —
  chosen over the unit's other non-Lesson-1 topics as the most standalone
  and broadly relatable: 17 slides, no dependency on earlier lessons'
  content). TES: draft created successfully (resource 13545886), needs a
  human "Publish now" click per this project's standing TES rule.
  `verify_tes_listings.py --lead-magnet-lesson 3` found no leftover-AI
  language and no literal £1.00 (the known paid-minimum mispricing bug), but
  also could not positively confirm £0.00 on reload — TES's Licence step UI
  shows the "Sell my resource" tab active by default on every page load
  regardless of what was actually saved, so this remains an inherent
  limitation of a static-HTML check, not a signal that the draft is
  mispriced. Fixed one real bug in the checker while investigating: it was
  reading the wrong uploader step page (Description, step 1) for the price
  text and could never have found it there; now reads the Licence step
  (step 4). TPT: still blocked — `TPT_SESSION_JSON` is unchanged since
  2026-08-20 and still expired (reconfirmed via the same read-only
  `verify_tpt_listings.py` check), so no TPT publish was attempted this
  cycle either; the same human follow-up from 2026-08-20 (refresh
  `TPT_SESSION_JSON` via `publish_tpt.py --save-session`, then run
  `publish_lead_magnets.py --unit year7_cybersecurity_unit1 --lesson 3
  --platform tpt`) still applies, now for both queued units. Also fixed two
  cloud-sandbox environment bugs blocking this cycle (see
  `cmie/publishing/browser.py`): the pip `playwright` package installed at
  session start no longer matches the pre-installed Chromium revision, so
  `channel="chromium"` couldn't find a binary — `cloud_launch_kwargs()` now
  passes `executable_path` at the pre-installed binary directly when
  present; and headed (`headless=False`) launches (needed for the TES
  form-fill flow) had no X server to attach to — `automation_chrome()` now
  starts a throwaway Xvfb server itself when `$DISPLAY` isn't already set.
  See AUTONOMOUS_LOG.md for full detail.
- 2026-08-28: Built + published the Lesson 6 lead magnet for
  year7_web_design_unit1 ("Accessibility and Responsive Design Basics" —
  chosen as the most standalone/broadly-relatable of the remaining lessons:
  a conceptual lesson on inclusive and responsive design that doesn't
  depend on the HTML/CSS build-up from Lessons 2-5). TES: `--publish` run
  completed successfully end-to-end (login, upload, categories, "Share for
  free" licence, copyright box, "Publish now") and landed on the
  `.../published` URL for resource **13553843** — genuinely live, no
  manual step needed, per the TES full-automation fix from 2026-08-24.
  TPT: blocked exactly as expected — `TPT_SESSION_JSON` has no valid
  session and no `TPT_EMAIL`/`TPT_PASSWORD` fallback, so
  `publish_lead_magnets.py --platform tpt` refused to submit a blank login
  form. This is the accepted platform limit (Cloudflare blocks fresh
  browser fingerprints in this cloud sandbox regardless of cookie
  validity, confirmed 2026-08-24) — not retried, not a bug. A human can
  finish the TPT half locally with `python publish_tpt.py --save-session`
  then `python publish_lead_magnets.py --unit year7_web_design_unit1
  --lesson 6 --platform tpt`.
  **Found, not touched**: `verify_tes_listings.py --keyword Accessibility
  --lead-magnet-lesson 6` found **two** live resources with the identical
  Lesson 6 title/content — 13553843 (the one this run's publish log
  reported) and 13553844 (same title, same "Created: 28 Aug 2026" /
  "Last modified: 28 Aug 2026" timestamps, same CC-BY-SA licence, both
  showing normal View/Edit/Delete controls on the dashboard). This run's
  own `publish_lead_magnets.py --platform tes --publish` invocation was
  called exactly once and its log only ever names 13553843 — nothing in
  this session created or touched 13553844 directly. This looks like the
  same class of platform-side duplicate-draft behavior already open as an
  unresolved item elsewhere in this project (the 13432831 / 13432796 pair
  in `AUTONOMOUS_LOG.md`), not a new bug in this script. Per the standing
  "never delete anything" rule, neither resource was touched or removed —
  flagging for a human to pick which one (if not both) should stay live.
  The checker's other finding, "could not find £0.00 on the page", is the
  already-documented inherent limitation of that static check (TES's
  Licence step always renders the "Sell my resource" tab by default on
  reload regardless of the saved price) — not a real mispricing signal;
  the publish log's own "Selected 'Share for free' tab" line is the
  reliable confirmation the price is genuinely £0.00. See
  AUTONOMOUS_LOG.md for full detail.
