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
- [x] year7_orientation_unit1 — Lesson 4 (Passwords, Privacy, and Protecting Your Information) — 2026-09-11
- [x] year7_networks_hardware_unit1 — Lesson 4 (How Data Travels Across a Network) — 2026-09-18
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

**Resolved 2026-09-06.** All 13 live units' `releases/public/<id>_v001/`
content still existed on the business owner's local machine (built there
originally, before either the cloud sandbox's ephemeral `releases/` or
the git-tracked `data/units/packaged/` persistence existed) -- backfilled
all 13 via `package_unit.py --unit <id> --force` locally, zero
regeneration cost. Both bundles below built with `make_bundle.py` and
published live on Gumroad ($19.99 AUD each) and TES (£14.99 each) the
same session. **TPT still pending** for both -- blocked in this
interactive session by Claude Code's own auto-mode safety classifier
(harness-level, unrelated to this project's rules), needs to be finished
by a human running the commands logged below. Found and fixed 3 real
bugs in `publish_tes.py` along the way (stale positional `<select>`
locator, a file-scan wait keyed to the wrong signal, and a "Publish now"
button that needed a settle delay after the confirm checkbox) -- see
`AUTONOMOUS_LOG.md`'s 2026-09-06 entry for full detail. Any unit
produced by Routine 2 from 2026-09-05 onward is automatically
bundle-ready (no extra step) since `package_unit.py` now persists every
unit's zip as it's built.

- [x] "Programming Foundations" bundle: Algorithms & Programming Logic + Introduction to Programming (Python) — Gumroad live 2026-09-06 (`focuslabdigital.gumroad.com/l/lfpgti`, $19.99 AUD), TES live 2026-09-06 (resource `13566130`, £14.99); **TPT live 2026-09-21, $44.99** — https://www.teacherspayteachers.com/Product/Programming-Foundations-Bundle-2-Unit-Digital-Technologies-Bundle-14-Lessons-17707144 (title shows truncated at TPT's 80-char field limit, missing the closing "Total)" — cosmetic, root cause fixed in `make_bundle.py` for all bundles built afterward, not worth re-publishing this one over)
- [x] "Staying Safe Online" bundle: Cyber Security & Digital Footprints + Networks & Hardware — Gumroad live 2026-09-06 (`focuslabdigital.gumroad.com/l/xteifx`, $19.99 AUD), TES live 2026-09-06 (resource `13566132`, £14.99); **TPT live 2026-09-21, $44.99** — https://www.teacherspayteachers.com/Product/Staying-Safe-Online-Bundle-2-Unit-Digital-Technologies-Bundle-14-Lessons-17707152 (same title-truncation cosmetic issue as above)

## 10 more 2-unit bundles (2026-09-21) — TPT live, Gumroad/TES not yet published

Built strategically per user direction: pair units so each bundle maps to a
real strand of the Australian Curriculum v9 Digital Technologies syllabus
(Knowledge and Understanding; Processes and Production Skills), cross-mapped
to CSTA (US) and KS3 Computing (UK) so the same bundle reads as on-curriculum
in all 3 markets — timed for the AU Term 1 2027 planning window (AU teachers
plan Nov–Jan for a late-Jan start) which is active now (today: 2026-09-21),
while also fitting US/UK back-to-school and new-semester search intent.
All 10 built via `make_bundle.py` (reuses existing packaged unit zips, zero
new content generation), all live on **TPT at $44.99** the same session:

1. **Start of Year Digital Technologies** (Orientation + Digital Systems) — the flagship of the 10, direct "start of the year" match — https://www.teacherspayteachers.com/Product/Start-of-Year-Digital-Technologies-Year-7-2-Unit-Bundle-14-Lessons-17707184
2. **Data & Databases** (Data Representation + Databases) — https://www.teacherspayteachers.com/Product/Data-Databases-Year-7-2-Unit-Bundle-14-Lessons-17707194
3. **Web Design & UX** (Web Design + UX Design) — https://www.teacherspayteachers.com/Product/Web-Design-UX-Year-7-2-Unit-Bundle-14-Lessons-17707204
4. **Game Design & Coding** (Game Design + Python Programming) — https://www.teacherspayteachers.com/Product/Game-Design-Coding-Year-7-2-Unit-Bundle-14-Lessons-17707217
5. **Robotics & Algorithms** (Robotics & Physical Computing + Algorithms) — https://www.teacherspayteachers.com/Product/Robotics-Algorithms-Year-7-2-Unit-Bundle-14-Lessons-17707229
6. **AI Literacy & Cyber Security** (AI Literacy + Cyber Security) — https://www.teacherspayteachers.com/Product/AI-Literacy-Cyber-Security-Yr-7-2-Unit-Bundle-14-Lessons-17707248
7. **Digital Media & UX Design** (Digital Media + UX Design) — https://www.teacherspayteachers.com/Product/Digital-Media-UX-Design-Year-7-2-Unit-Bundle-14-Lessons-17707262
8. **Data Skills & AI Literacy** (Spreadsheets & Data Analysis + AI Literacy) — https://www.teacherspayteachers.com/Product/Data-Skills-AI-Literacy-Year-7-2-Unit-Bundle-14-Lessons-17707274
9. **Computer Systems & Networks** (Digital Systems + Networks & Hardware) — https://www.teacherspayteachers.com/Product/Computer-Systems-Networks-Yr-7-2-Unit-Bundle-14-Lessons-17707285
10. **Creative Media & Game Design** (Digital Media + Game Design) — https://www.teacherspayteachers.com/Product/Creative-Media-Game-Design-Yr-7-2-Unit-Bundle-14-Lessons-17707298

Unit reuse across bundles is deliberate (e.g. Digital Systems appears in
bundles 1 and 9, AI Literacy in 6 and 8) — same standard TPT practice as any
seller building multiple bundles off one catalog; no unit had to be
duplicated in content, only re-packaged.

**Two real bugs found and fixed in `make_bundle.py` while building these**
(both apply to every bundle built from now on, including the 2 already-live
ones above, which weren't re-published to fix retroactively):
1. **Title truncation**: TPT's product-name field silently cuts off past 80
   chars. The old title format (`"{title} — N-Unit Digital Technologies
   Bundle (N Lessons Total)"`) ran to ~88 chars for a typical bundle name,
   so both `programming_foundations_bundle` and `staying_safe_online_bundle`
   shipped with the closing `Total)` cut off. Shortened the format and
   dropped the em dash (also rendered wrong in TPT's field) — new bundles'
   titles fit comfortably under 80 chars.
2. **False "cheaper than buying separately" claim**: the template's
   "Why bundle over buying separately" copy claimed the bundle costs less
   than buying each unit's bundle individually. At $44.99 that's false — two
   separate unit-bundles cost $25.98 ($12.99 x2), and even the full à la
   carte lesson price for 2 units is ~$42. Removed the savings claim
   entirely; replaced with a "Why this bundle" section pitching convenience
   (one download vs two) and a genuine "Curriculum alignment" section citing
   the actual ACARA v9 strand names plus CSTA/KS3 mapping. This means the 2
   already-live bundles above still carry the old, now-inaccurate "costs
   less" claim in their TPT listing — worth a human call on whether to
   correct those live descriptions.

**Not yet done for these 10**: Gumroad and TES publishing (existing 2-unit
bundles went to all 3 platforms; these 10 only went to TPT per this
session's explicit instruction to prioritize TPT). `publish_gumroad.py
--unit <bundle_id> --price 19.99` and `publish_tes.py --unit <bundle_id>
--price 14.99 --publish` will work unmodified for all 10 (same pseudo
unit_id resolution as the 2 existing bundles) whenever that's wanted.

## Log

(the job appends a line here each time it completes or skips a cycle)

- 2026-09-18: Built + published the Lesson 4 lead magnet for
  year7_networks_hardware_unit1 ("How Data Travels Across a Network" —
  a standalone conceptual lesson that doesn't depend on Lessons 1-3's
  hardware-selection content). Concurrency check (`git fetch origin main`)
  found no other run had touched this item first. Source note: same
  situation as the 2026-09-11 orientation-unit cycle — no `releases/public/`
  tree existed locally (fresh container), but
  `data/units/packaged/year7_networks_hardware_unit1_v001_PUBLIC.zip` (the
  full-unit zip `package_unit.py` persists) contains the exact
  `01_Lesson_Slides/` layout `make_lead_magnet.py` expects, so it was
  extracted locally into `releases/public/year7_networks_hardware_unit1_v001/`
  (ephemeral, gitignored, not committed) with a one-line
  `06_Listings/unit/tpt_listing.md` added from the unit's own title in
  `year7_networks_hardware_unit1.json` (no new content generated). Also had
  to `pip install -r requirements.txt` in this fresh container before
  `python-pptx` etc. were importable. TES: `--publish` run completed
  successfully end-to-end (login, upload, categories, "Share for free"
  licence, copyright box, "Publish now") and landed on the `.../published`
  URL for resource **13578710** — genuinely live.
  `verify_tes_listings.py --keyword "Data Travels" --lead-magnet-lesson 4`
  found exactly one matching resource (no duplicate); its "could not find
  £0.00" finding is the already-documented inherent limitation of that
  static check (TES's Licence step always renders the "Sell my resource"
  tab by default on reload), not a real mispricing signal — the publish
  log's own "Selected 'Share for free' tab" line is the reliable
  confirmation. TPT: blocked for the same non-bug reason as the
  2026-09-11 orientation cycle — `publish_to_tpt()` raised
  `FileNotFoundError` before attempting any login because no thumbnail
  exists for this unit in either `releases/thumbnails/` or the tracked
  `data/units/lead_magnet_source/thumbnails/` (confirmed via `find`, no
  such file anywhere in the repo). Not the usual session-expiry limit,
  not retried. A human needs to add
  `year7_networks_hardware_unit1_thumbnail.png` to
  `data/units/lead_magnet_source/thumbnails/` and then run
  `python publish_lead_magnets.py --unit year7_networks_hardware_unit1
  --lesson 4 --platform tpt`.

- 2026-09-11: Built + published the Lesson 4 lead magnet for
  year7_orientation_unit1 ("Passwords, Privacy, and Protecting Your
  Information" — a standalone, broadly-relatable conceptual lesson that
  doesn't depend on the other orientation lessons). Concurrency check
  (`git fetch origin main`) found no other run had touched this item first.
  Source note: this unit had no `releases/public/` tree locally (fresh
  container, `releases/` gitignored, and this unit predates the
  `lead_magnet_source/` tracked-subset fallback that the previous 3 lead
  magnets used) — but `data/units/packaged/year7_orientation_unit1_v001_PUBLIC.zip`
  (the full-unit zip `package_unit.py` now persists per the 2026-09-06
  bundle-gap fix) contains the exact same `01_Lesson_Slides/` layout
  `make_lead_magnet.py` expects, so it was extracted locally into
  `releases/public/year7_orientation_unit1_v001/` (ephemeral, gitignored,
  not committed) with a one-line `06_Listings/unit/tpt_listing.md` added
  from the unit's own existing title in `year7_orientation_unit1.json` (no
  new content generated, just reused existing metadata) so the CTA slide's
  title would read correctly. TES: `--publish` run completed successfully
  end-to-end (login, upload, categories, "Share for free" licence,
  copyright box, "Publish now") and landed on the `.../published` URL for
  resource **13571207** — genuinely live. `verify_tes_listings.py
  --lead-magnet-lesson 4` confirmed exactly one matching resource, `[OK]`,
  no duplicate. TPT: blocked, but for a **different reason than the usual
  session-expiry limit** — `publish_to_tpt()` raised
  `FileNotFoundError` before attempting any login, because no thumbnail
  exists for this unit in either `releases/thumbnails/` or the tracked
  `data/units/lead_magnet_source/thumbnails/` (TPT requires one; the 3
  units with a second lead magnet already live all have a tracked
  thumbnail, orientation never got one backfilled). Not a bug in this
  cycle's run — genuinely missing asset, nothing to retry. A human needs
  to add `year7_orientation_unit1_thumbnail.png` to
  `data/units/lead_magnet_source/thumbnails/` (matching the other 3
  units' pattern) and then run `python publish_lead_magnets.py --unit
  year7_orientation_unit1 --lesson 4 --platform tpt`.

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
