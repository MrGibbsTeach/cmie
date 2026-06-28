# CMIE Project Progress

_Last updated: 2026-06-28_

---

## Direction Change (2026-06-26)

**The original 8-unit "AI & Data Literacy Series" is shelved.** Per user direction: those units were practice/test units, built around a Canva-dependent workflow that's no longer being used. Don't resume work on Units 1-8 (TPT/Gumroad/TES publishing for that series) unless explicitly asked — the user may pick them up personally later. The packaging audit and Gumroad fixes from earlier in this file are still accurate *for that series* but are no longer the active priority.

**New direction: fully automated unit creation, no Canva, lesson-by-lesson + bundle listings on TPT.** First unit under this approach — Networks & Hardware Unit 1 — is built and live on TPT as of today. See "Networks & Hardware Unit 1 — TPT Launch" below for full details. This is now the template for future units.

---

## Networks & Hardware Unit 1 — TPT Launch (2026-06-26)

**Status: all 9 products live on TPT.** 7 individual lessons + assessment + full bundle, all under FocusLab Digital.

| Product | Price | Status |
|---|---|---|
| Lesson 1: What Is a Network? | $2.50 | ✅ Live |
| Lesson 2: Selecting Network Hardware | $2.50 | ✅ Live |
| Lesson 3: Wired vs Wireless Nets | $2.50 | ✅ Live |
| Lesson 4: How Data Travels Across a Network | $2.50 | ✅ Live |
| Lesson 5: Network Security Basics | $2.50 | ✅ Live |
| Lesson 6: Connecting & Troubleshooting | $2.50 | ✅ Live |
| Lesson 7: Designing a Network | $2.50 | ✅ Live |
| Assessment Pack | $3.50 | ✅ Live |
| Full Bundle (all 7 lessons + assessment + workbook + roadmap + teacher guide) | $12.99 | ✅ Live |

**Also live on Gumroad**: full bundle, `https://gumroad.com/products/rrdvk/edit` — A$12.99, currently **published** (not a draft — confirm before assuming Gumroad listings default to draft; this one is live).

---

## Independent QA Pass + Fixes (2026-06-27)

The user ran an independent QA review (via a separate Cowork session) of the Networks & Hardware Unit 1 deliverables — opened the actual zip, read every PPTX/docx, and compared against the Gumroad listing's promises. Full report is in conversation history; summary of findings and fixes:

**Verdict from the QA pass: "Functional but not polished."** No false claims — everything promised in the listing was present — but several presentation-quality bugs, three of which turned out to be the *same systemic bug class found and fixed twice before* (raw markdown leaking into rendered output) and two more newly-discovered AI-specific content leaks (the AI series' hardcoded assumptions leaking into a non-AI unit, same bug class as the Packaging Audit and Listing Generator fixes from 2026-06-26, just in different files).

**Fixed (root cause, not just this unit's files):**
1. **`markdown_to_docx()` in [full_product_pipeline.py](cmie/pipeline/full_product_pipeline.py) didn't handle inline `**bold**` or markdown pipe tables** — every generated docx (roadmap, assessment task, teacher guide) showed literal `**Year level:**` asterisks, and the roadmap's lesson-sequence table rendered as a raw `| 1 | What Is a Network? |` wall of pipe characters instead of a Word table. This is the fourth distinct instance of "markdown leaks into a rich output format" found this week (Gumroad description, TPT description, now docx generation) — added real inline-bold parsing (`add_runs_with_bold`) and markdown-table-to-Word-table conversion (`add_markdown_table`).
2. **`workbook_generator.py`'s `_lesson_specific_task()`** had a bare `"design" in title` branch that incorrectly matched our "Designing a Network for a Real Scenario" lesson and inserted an AI/fairness-themed task ("How does your fix improve fairness?") — gated it to require an actual AI/fairness keyword co-occurring, not just the word "design" alone.
3. **`workbook_generator.py` line ~147** had an unconditional "How could data or AI be used fairly here?" prompt baked into every lesson's Section 2, regardless of topic — replaced with a topic-neutral "What's one important thing to consider in this scenario?"
4. **`assessment_generator.py`'s `infer_unit_focus()`** generic fallback (for any unit not matching "ethics/bias/fair" or "model/prediction/classification/recommendation") was *itself* AI-themed ("This is a Lower Secondary AI and data literacy unit...", "AI outcomes") — this is the most significant find, because it doesn't just affect static template text, it's fed directly into the AI generation prompt. That's *why* this unit's actual assessment task talks about "fairness in AI outcomes" despite having nothing to do with AI. Replaced with a genuinely generic fallback that references the actual unit name and lesson titles instead of assuming an AI topic.
5. **`readme_generator.py`** had a hardcoded "No specialist AI background is required" bullet in every teacher guide — changed to "No specialist background in the topic is required."
6. **Rubric had no marks/grade bands** — added a generic A (Exemplary) / B (Proficient) / C (Developing) / D (Beginning) mapping to `render_rubric_table()`'s header row.
7. **`README.docx` → `Teacher_Guide.docx`** — renamed in `stage_packaging()` to match the `05_Teacher_Guide/` folder it lives in.

**Deliberately NOT fixed (user's call, not a bug worth chasing):**
- L02/L03 hook text has stray vertical-tab characters (missing punctuation between two sentences) and L01/L05/L06 have a blank "Extension ideas:" heading with no content. Both are AI-generation-output gaps, not template bugs. User's instruction: *"just do better next time, don't worry about remaking anything"* — i.e. don't regenerate this unit's lesson content, just be aware for future units. **Do not spend time fixing these unless asked.**
- This unit's actual assessment task content (the AI-framed scenario text generated under the old buggy prompt) was also left as-is — the root-cause fix in `assessment_generator.py` (#4 above) prevents this for *future* units, but the user explicitly chose not to regenerate this unit's already-published assessment.
- No images/diagrams added to the PPTX decks (flagged as "longer-term" by the QA report itself, not urgent).

**Re-packaged and re-deployed:**
- Regenerated `Assessment_Task.docx`, `Assessment_Rubric_and_Marking.docx` (new grade bands), `Student_Workbook.docx` (no more AI question), `Unit_Roadmap.docx` (real table, no `**`), `Teacher_Guide.docx` (renamed, fixed bullet) — all verified by reading the actual docx XML/runs after regeneration, not just assumed from source code changes.
- Rebuilt `year7_networks_hardware_unit1_v001_PUBLIC.zip`, `_BUNDLE.zip`, and `_assessment_v001.zip` in `releases/artifacts/`.
- **Gumroad bundle (`rrdvk`) updated and verified** — deleted the old zip attachment, uploaded the corrected one, confirmed via reload it shows the real file size (545.3 KB), not "0 byte." This Gumroad listing turned out to be **already published/live** (not a draft as previously assumed) — worth double-checking publish status before assuming "draft" on any Gumroad product going forward.
- **TPT bundle and assessment listings updated too (2026-06-28).** Added `replace_product_file(product_id, new_zip_path)` to `cmie/publishing/tpt.py` — TPT's edit page is at `/itemsDigital/editNext/{product_id}`, the existing file is removed via its `.delete-btn` (first one on the page = the main Product file slot; there are 7 total — Product/Preview/Video/Thumb1-4 — in that DOM order), then the new file uploads into `input[type='file']#ItemDigitalProduct` (note: there are *two* elements sharing that id on the page, one a hidden non-file input — must scope the selector to `input[type='file']` or Playwright throws a strict-mode violation). TPT renames the uploaded file to match the product's URL slug, not the original filename — **verify by "Last updated" timestamp + file size after a fresh reload, not by filename.**
  - Assessment product (id `16818101`): replaced, verified — "Last updated: Jun 27, 2026", 67.42 kB matching the new zip.
  - Bundle product (id `16818112`): replaced, verified — "Last updated: Jun 28, 2026", 545.31 kB = exact byte match to the local `_v001_PUBLIC.zip` (558398 bytes / 1024 = 545.31 KB).
  - **Another submit-detection false negative happened here**: the bundle's file is much bigger than typical, so the SPA's post-submit navigation took longer than the 10s poll window — logged "Submit may have failed" even though the reload-verification immediately below it confirmed success. Extended the poll to 30s in `replace_product_file()`. *This is now the third time a submit/upload success has been wrongly reported as a failure due to checking too soon* (Gumroad async upload, TPT new-product submit, now TPT edit-product submit) — the pattern is reliable enough to state as a rule: **any "did this persist" check on Gumroad or TPT needs a poll loop of at least 20-30s, never a single fixed-delay check.**
  - The 7 individual lesson zips were untouched by the QA fixes (only docx/roadmap content changed, not the PPTX slides) so they were not touched on TPT.

---

All verified by checking the actual `My-Products` list after submission, not just trusting a clean script exit — see "lessons learned" below for why that distinction mattered twice today.

### Pipeline changes (no Canva, direct PPTX)

- **New unit config**: `data/units/year7_networks_hardware_unit1.json` — Year 7 Digital Technologies, 7 topics.
- **New pipeline stage** `stage_pptx_slides()` in [full_product_pipeline.py](cmie/pipeline/full_product_pipeline.py) — calls `cmie/generator/pptx_generator.py` (already complete, just previously disconnected — `batch_generate.py`'s comment said "Legacy PPTX generation has been removed from the active workflow" in favor of Canva CSV) directly on each lesson's JSON to produce a branded PPTX deck. No Canva, no manual export step.
- **`stage_packaging()` updated** to prefer these direct PPTX decks (`unit_root/slides/*.pptx`) over the old Canva-CSV path when building the public release folder — copies into `01_Lesson_Slides/` instead of `01_Lesson_Slides_CSV/`.
- Ran the full pipeline once end-to-end: `python -m cmie.pipeline.full_product_pipeline --unit-config data/units/year7_networks_hardware_unit1.json` — generated all 7 lessons, slides, assessment, workbook, roadmap, teacher guide, listings, and packaging in one pass. Validation passed with no structural issues.

### Listing generator bugs found and fixed (systemic, not unit-specific)

`cmie/generator/listing_generator.py` was built only ever tested against the AI & Data Literacy series and had several hardcoded assumptions that broke for a non-AI topic:

- **`generate_workbook_listing()` / `generate_assessment_listing()`** had hardcoded AI-specific fallback copy ("Explain key AI and data concepts...", "Reflect on how AI systems work in practice") that fired whenever the unit title didn't match `ethics/bias/systems/model` keywords — i.e. for *any* non-AI unit. Fixed both fallbacks to be topic-neutral.
- **Lesson listing copy claimed "Canva-ready slide content included in the unit CSV workflow"** unconditionally — wrong for direct-PPTX units (there's no CSV at all). Added `has_pptx_slides` detection; now says "Fully editable PowerPoint (PPTX) slide deck" when that's actually what's shipping.
- **Lesson numbering bug**: listings were numbered by `enumerate(sorted(lessons_dir.glob("*.json")))` — alphabetical by filename slug, not by each lesson's actual `lesson_number`. This silently mislabeled listings (e.g. the real "Lesson 1" was labelled "Lesson 6" in its own title) AND meant the listing folder numbering didn't match the slide/zip numbering at all, which would have caused **wrong listing copy attached to the wrong lesson's zip** if not caught. Fixed by sorting on each lesson's actual `lesson_number` field from its JSON.
- **`listing_reader.py`'s default tags** were hardcoded to include "AI literacy" regardless of topic. Fixed to a topic-neutral default; per-unit tags should be passed explicitly via `--tags` anyway (see below).

### `publish_tpt.py` / `cmie/publishing/tpt.py` — multi-part support and UI-redesign fixes

TPT had redesigned several form fields since this script was last used (same pattern as the Gumroad redesign from earlier sessions). Fixed:

- **Added `--part` support** to `publish_tpt.py` (`lesson01`..`lesson07`, `assessment`, `bundle`) so one unit can publish as multiple distinct TPT products instead of a single bundle. Matches lesson zips to listings **by slug, not by number** — the listing folders and the slide files are numbered independently (alphabetical vs. sequence), so number-based matching would have attached the wrong listing to the wrong zip.
- **Wrong password**: TPT_PASSWORD in `.env` was stale from a prior account-lock recovery — confirmed via the actual "email/password combination doesn't match" UI error, not assumed. Fixed by the user updating `.env` directly.
- **Subject Area and Tag fields are now React-Select comboboxes with a fixed, server-side vocabulary** — typing free text searches existing options, it does not create new ones. Old selectors (matching on `name`/`placeholder`/`aria-label` containing "tag") matched a hidden mirror input, not the real one. Fixed via `_select_react_select_option()` which types a search term and clicks the option with an exact (or substring) text match. Confirmed-real tag vocabulary terms used: "Lessons", "Activities", "Career and Technical Education", "Critical Thinking and Problem Solving" — topic-specific tags like "Network"/"Hardware"/"STEM"/"Technology" do **not** exist in TPT's controlled vocabulary (tested and confirmed empty).
- **New required "Tax Code" field** didn't exist when this script was last used. Added `_set_tax_code()`, defaults to "Other Digital Goods - No Physical Media" (generic digital-download category, fits any non-physical teaching resource).
- **Thumbnail upload**: TPT now defaults to "Auto generate thumbnails from the product file," which fails for PPTX/zip uploads ("We cannot generate images from your file"). Fixed by clicking "Upload thumbnails now" first, then targeting the real file input by its id (`#ItemDigitalThumb1`) — it has no `accept`/`name` attribute the old selector could match on.
- **Description field renders raw markdown literally** (same bug as the Gumroad fix from an earlier session) — extracted the fix into a shared `cmie/publishing/markdown_utils.py::markdown_to_html()` used by both `publish_gumroad.py` and `cmie/publishing/tpt.py`, instead of duplicating the conversion logic a second time.
- **Removed the interactive `input()` pause** at the end of `upload_unit()` — incompatible with a non-interactive automation environment (caused `EOFError`). The non-auto-publish path now just leaves the form filled and logs instructions instead of blocking.
- **Two false-success/false-failure bugs in submit detection**, both from checking too early or too broadly:
  - Checking `page.url` for "still on /New/" immediately after a fixed 3s wait was too soon — the SPA navigates client-side with more latency than that. Fixed by polling for up to 10s instead of a fixed wait.
  - The error-detection regex matched the words "required"/"error" anywhere on the page, which falsely flagged a *successful* submission as failed because our own listing copy contains the phrase "No prep required." Narrowed to match only TPT's actual validation-message pattern (`^Please (select|upload|enter|fix|choose)`).
- **Generated a thumbnail** for this unit (`releases/thumbnails/year7_networks_hardware_unit1_thumbnail.png`) via the existing `cmie/publishing/thumbnail.py` generator — none existed before since this unit never went through the old series' thumbnail step.

### Lessons learned (apply to future units/platforms)

- **Never trust an in-session screenshot or a clean script exit as proof an action persisted.** This bit us twice today on TPT alone (after already learning it on Gumroad in an earlier session): once from checking too early (false failure), once from an overly broad error-text match (false... also failure, ironically — the bias so far has been false negatives on TPT, not false positives, which is the safer direction but still required fixing). Always verify via the actual products list / a fresh page load.
- **A platform's UI changing between sessions is the norm, not the exception**, for both Gumroad and TPT. Budget time for "re-verify the selectors still work" at the start of any publishing session, rather than assuming a script that worked before still works.
- **Controlled-vocabulary fields (tags, subject, categories) need to be discovered, not guessed.** Topic-specific words usually aren't in the vocabulary; generic-but-real terms are the fallback.

---

## Revenue

| Platform | Live listings | Revenue to date |
|----------|--------------|-----------------|
| TPT      | 10 (1 from shelved AI series + 9 from Networks & Hardware Unit 1) | $0 |
| TES      | 0            | $0              |
| Gumroad  | 0 (draft pending review, shelved series) | $0 |

**Target:** $200,000 AUD/year

---

## Content Pipeline — AI & Data Literacy Series (Year 7)

8-unit series.

| Unit | Title | Generated | Validated | Slides (actual PPTX) | Customer-ready zip | Listings | Thumbnail | TPT | Gumroad |
|------|-------|-----------|-----------|------------------------|---------------------|----------|-----------|-----|---------|
| 1 | Data Foundations | ✅ | ✅ | ✅ 7 pptx | ✅ `_v001_PUBLIC.zip` | ✅ | ✅ | ✅ Live | 🔶 Draft ready |
| 2 | Data + AI Models | ✅ | ✅ | ❌ **only CSV exists, never exported from Canva** | ❌ blocked | ✅ | ✅ | ❌ | ❌ blocked |
| 3 | AI Ethics + Bias | ✅ | ✅ | ✅ 7 pptx | ✅ `_v001_PUBLIC.zip` | ✅ | ✅ | ❌ | 🔶 Ready |
| 4 | AI Systems + Applications | ✅ | ✅ | ✅ 7 pptx | ✅ `_v001_PUBLIC.zip` | ✅ | ✅ | ❌ | 🔶 Ready |
| 5 | AI in Education | ✅ | ✅ | ✅ 7 pptx | ✅ `_v001_PUBLIC.zip` | ✅ | ✅ | ❌ | 🔶 Ready |
| 6 | AI in Business | ✅ | ✅ | ✅ 7 pptx | ✅ `_v001_PUBLIC.zip` | ✅ | ✅ | ❌ | 🔶 Ready |
| 7 | AI in Healthcare | ✅ | ✅ | ✅ 7 pptx | ✅ `_v001_PUBLIC.zip` | ✅ | ✅ | ❌ | 🔶 Ready |
| 8 | AI in Society | ✅ | ✅ | ✅ 7 pptx | ✅ `_v001_PUBLIC.zip` | ✅ | ✅ | ❌ | 🔶 Ready |

**Notes:**
- Unit 1 TPT live at FocusLab Digital, $29.99, published 2026-06-15.
- **Unit 2 is the only unit blocked on content** — its Canva CSV was generated but nobody did the manual import-to-Canva-and-export-PPTX step, so there are zero slides anywhere for it. Cannot be packaged or sold until that's done.
- Units 3-8 had their slides manually exported from Canva at some point (sitting in `releases/public/<unit>_v001/01_Lesson_Slides/` already) — this was already done, just not previously surfaced/used correctly by the packaging script (see "Packaging audit" below).
- Thumbnails generated for all 8 units in `releases/thumbnails/` (1500x1125 marketing covers; Gumroad needs a square crop, handled automatically by `publish_gumroad.py`).
- **The real customer-facing deliverable is `releases/artifacts/<unit>_v001_PUBLIC.zip`** — not the old `<unit>_v001.zip`. See "Packaging audit" section for why.

---

## System Components

| Component | Status | Notes |
|-----------|--------|-------|
| AI lesson engine | ✅ Done | `cmie/generator/ai_lesson_engine.py` |
| Workbook generator | ✅ Done | DOCX output |
| Assessment generator | ✅ Done | |
| Canva CSV slide generator | ✅ Done | Per-unit CSVs in `releases/*/04_Slides_CSV/` |
| PPTX generator | 🔄 In progress | `cmie/generator/pptx_generator.py` — untracked, status unknown |
| Listing generator | ✅ Done | TPT, TES, Gumroad copy |
| Packaging | ⚠️ Needs filtering | `package_release()`/`stage_packaging()`'s internal zip still includes raw production files — see Packaging Audit. Customer-facing zips are now `<unit>_v001_PUBLIC.zip`, built by cleaning `releases/public/<unit>_v001/`. That cleanup step is currently a manual one-off script, not yet folded into the pipeline itself — worth automating if more units get added later. |
| Full product pipeline | ✅ Done | `cmie/pipeline/full_product_pipeline.py` |
| Unit config generator | ✅ Done | Generates `data/units/*.json` |
| Thumbnail generator | ✅ Done | `cmie/publishing/thumbnail.py` — Pillow, branded 1500x1125 covers |
| TPT publishing automation | ⚠️ Blocked | `cmie/publishing/tpt.py` + `publish_tpt.py` — Playwright works, but TPT bot detection blocks automated login. Account was temporarily locked (recovered). Workaround needed: either use `--save-session` to cache manual login, or wait for account unlock + try cookie extraction. |
| Gumroad publishing automation | ✅ Working, self-verifying | `publish_gumroad.py` — Playwright-based. API creates product, Playwright uploads zip/thumbnail/description, clicks Save, then reloads the page to verify the upload actually persisted (added 2026-06-26 after finding Gumroad finalizes uploads async on the backend). |
| CMIE Studio webapp | 🔄 In progress | `webapp/` — FastAPI backend + Next.js frontend; builder and jobs pages exist; purpose: web UI for generate/publish workflow |

---

## Packaging Audit (2026-06-26) — found by user spot-checking the zip contents

The user manually reviewed what was inside the Unit 1 zip after seeing it in the Gumroad draft and caught that it was full of files no customer should ever receive. This turned into a full audit of all 8 units' packaging. **This is exactly the kind of check that should happen by default going forward — see "Process fix" at the bottom.**

**What was wrong:** `package_release()` in [packaging.py](cmie/generator/packaging.py) and the "Internal zip" step in `stage_packaging()` ([full_product_pipeline.py](cmie/pipeline/full_product_pipeline.py)) just zip the *entire* raw `releases/<unit>/` folder with zero filtering. `publish_gumroad.py` was uploading that zip directly. It contained:
- `05_Canva_Prompts/` and scattered `*-canva-prompt.txt` files — the AI prompts used to *build* the Canva designs, not something a buyer needs.
- `assessment/*.json`, `lessons/*.json`, `marketing/marketing_assets.json` — raw pipeline data structures, redundant once the polished docx/pptx exist.
- `validation_report.md` — our own internal QA report.
- A `PUBLIC_RELEASE_TEST/` folder containing the one real customer-facing file (`Student_Workbook.docx`), misnamed/mislocated from a one-off test script (`render_unit1_workbook_docx_only.py`).
- Raw `.md` files for the assessment/workbook/roadmap/teacher-guide — directly unusable by a teacher who doesn't know what to do with a markdown file.

**The actual fix already existed and was just never wired up correctly**: `stage_packaging()` already has a "Public editable folder" step that converts everything to clean `.docx` via `markdown_to_docx()` and assembles `releases/public/<unit>_v001/` with numbered folders (`01_Lesson_Slides`, `02_Assessment`, `03_Student_Workbook`, `04_Unit_Roadmap`, `05_Teacher_Guide`) — this is the right structure. It just wasn't being used as the Gumroad upload source, and it had its own smaller hygiene issues:
- A `06_Listings/` folder with our own TPT/TES/Gumroad marketing copy riding along — never customer-facing.
- Stray QA screenshots (`Screenshot 2026-04-28....png`) dropped into `02_Assessment/`, `03_Student_Workbook/`, `05_Teacher_Guide/`, and loose at the folder root.
- Redundant nested zips duplicating content already present as docx (`Assessment_Rubric_and_Marking.zip`, `README.zip`, etc.) — a zip-inside-a-zip is bad UX for a buyer too.
- The raw `*_canva_slides.csv` import file sitting alongside the final exported PPTX — internal production format, not needed once the PPTX exists.
- A few oddly-named slide files from duplicate uploads: `Lesson 6 (1).pptx`, `Lesson 7 (1).pptx`, `Lesson 5 (1).pptx`.
- **Unit 1 specifically**: it used an older/legacy slide pipeline (direct PPTX generation into `releases/year7_ai_data_unit1/slides/`) instead of the CSV-based one (`04_Slides_CSV`) that `stage_packaging()` expects to copy from — so regenerating its public folder via the pipeline silently produced **zero slides**. Had to manually copy the legacy PPTX files in. **If any future unit also used the legacy path, check for this.**
- **Unit 1 also had a manually-curated `releases/public/year7_ai_data_unit1_v001 - EDITED READY FOR RELEASE/` folder** that someone had already cleaned up by hand — discarded in favor of regenerating fresh from the pipeline (user's call), but worth knowing that kind of manual curation has happened before and might exist for other units too if something looks unexpectedly polished.

**Fix applied:**
1. Re-ran `stage_packaging()` for Units 1 and 2 (Unit 2 had no public folder at all before this — never went through packaging).
2. Cleaned all of Units 1, 3-8's public folders: removed `06_Listings`, screenshots, redundant zips, raw Canva CSVs; renamed the `(1)`-suffixed slide files; renamed `01_Lesson_Slides_CSV` → `01_Lesson_Slides` since it no longer contains a CSV.
3. Zipped each cleaned folder as `releases/artifacts/<unit>_v001_PUBLIC.zip` — kept distinct from the old internal zip rather than overwriting it, so the internal full-source backup zip still exists if ever needed.
4. Updated `publish_gumroad.py` to prefer `*_PUBLIC.zip` and warn loudly if it ever has to fall back to the old internal zip for a unit.
5. **Unit 2 could not be fixed this way** — there's no PPTX to package at all. It's excluded from this round; needs the manual Canva export step done first.
6. Fixed the already-uploaded Unit 1 Gumroad draft (`cqwjlt`) to swap in the cleaned `_PUBLIC.zip` (see "Async upload" below for why that took several tries).

---

## Async Upload Trap (2026-06-26) — cost ~30 min of false debugging, now fixed in the script

While swapping the cleaned zip into the live `cqwjlt` draft, every upload attempt showed the correct filename but **"0 byte"** after a page reload — looked like total upload failure. Spent a while testing theories (corrupted zip, broken product, session state) before finding the real cause:

**Gumroad finalizes uploads asynchronously on the backend.** The client-side "Cancel" button disappearing (i.e. the browser→Gumroad transfer finishing) does **not** mean the file is done processing server-side. If you click Save and reload within ~30-60 seconds, the file can show "0 byte" — and it will actually self-correct to the right size if you just wait longer and reload again. The fix isn't "upload again," it's "wait longer." (This was proven directly: an earlier "broken" 0-byte upload in a throwaway test product self-corrected to the right size purely from elapsed time, with zero further action.)

**Fixed in `publish_gumroad.py`:**
- `_upload_content_zip()` now waits for the "Cancel" button to disappear, then adds a 20s buffer before saving (previously just a flat 6s wait — nowhere near enough).
- Added `_verify_after_reload()`, called at the end of `publish_unit()` — reloads the edit page and checks the zip's displayed size. If it's "0 byte," retries up to 4 times with 30s gaps before logging a hard error. This means future runs will tell you definitively whether the upload truly persisted, instead of a screenshot lying about it.

**Process lesson — applies beyond Gumroad:** never trust an in-session screenshot as proof a save persisted. Always verify via an actual page reload (a fresh `page.goto()`, not just "wait and screenshot the same page"). This bit us twice today — once with the description/zip not saving at all (no Save button click), once with the zip async-finalizing. Both times the in-session view looked completely correct.

---

## Process Fix — Going Forward

Per user direction (2026-06-26): every error, mistake, or inefficiency found while doing this work should be logged and fixed immediately, not just patched silently — the goal is the *system* getting better each session, not just this session's task getting done. Concretely, from now on:
- Before considering any unit "ready for Gumroad," spot-check the actual zip contents (`python -m zipfile -l <zip>` or equivalent) for internal-only files, not just the listing/description.
- Treat "looks right in this session" and "is actually saved" as two different claims requiring two different checks (see Async Upload Trap above).
- When a packaging/generation step has clearly already been solved once before for one unit (e.g. Unit 1's manually-curated folder), check whether that pattern needs to be replicated for the others before assuming a fresh pipeline run is sufficient.

---

## Publishing Automation — TPT

Status: **Blocked — bot detection**

The Playwright TPT publisher (`publish_tpt.py`) was used to manually publish Unit 1 (user handled browser, script handled form fill). Units 2-8 blocked because:
- TPT detects and blocks automated Playwright browsers (Verification failed error)
- Attempting form login too many times temporarily locked the account
- Account is now unlocked but the automation problem remains

**Fix options:**
1. `python publish_tpt.py --save-session` → opens browser, user logs in manually, cookies saved for future headless runs (requires admin to extract Chrome DPAPI cookies — this is the primary blocker)
2. Manually publish Units 2-8 using the browser while script fills the form (semi-automated)
3. Use `--remote-debugging-port` to connect Playwright to an already-logged-in Chrome instance

---

## Publishing Automation — Gumroad

Status: **Fixed and verified end-to-end on Unit 1 (including persistence after reload) — ready to run `--all` for Units 2-8**

`publish_gumroad.py` built with Playwright. Architecture:
1. Gumroad API (`POST /v2/products`) creates the product with title + AUD price
2. Playwright navigates to the returned edit URL (`gumroad.com/products/{slug}/edit`)
3. Playwright uploads the zip via the **Content tab** ("Upload your files" → "Computer files" → file chooser), then clicks **Save**
4. Playwright uploads the thumbnail via the **Product tab**'s Thumbnail section, padded to square on the fly with Pillow
5. Playwright fills the description via clipboard paste of markdown converted to HTML, then clicks **Save**

**What works (confirmed live 2026-06-21, verified by reloading the page after each save — not just trusting the in-session screenshot):**
- Session login + cookie caching (`.gumroad_session.json`)
- API product creation (title + price) — returns edit URL
- Zip upload via Content tab, persists after reload
- Thumbnail upload — full design visible, nothing cropped off, persists after reload
- Description renders as proper headings/bullets (not raw markdown), persists after reload
- Draft for manual review: `https://focuslabdigital.gumroad.com/l/cqwjlt` — title, price (A$29.99), zip, thumbnail, and description all confirmed correct as of 2026-06-21.

**2026-06-20 session — found Gumroad had redesigned the edit page**, breaking the old script (old selectors: `text=Computer files` for zip, `button:has-text('Upload')` for thumbnail — both gone).

**2026-06-21 session, first pass — fixed the three upload mechanics, but missed that edits weren't actually saving:**
- Playwright + Chromium browser binaries installed into the project's `venv` (were missing).
- **Zip upload** (`_upload_content_zip`, renamed from `_upload_cover_zip`): sellable file lives under the **Content tab** now. Flow: click "Content" tab → "Upload your files" → "Computer files" → file chooser.
- **Thumbnail upload**: the Thumbnail section's control is a `<label>` wrapping a hidden `<input type="file">`, not a button that opens a file chooser — locate the input directly and `set_input_files()`.
- **Description fill**: convert markdown to HTML, write both `text/html` and `text/plain` to the clipboard via `ClipboardItem`, then `Ctrl+V` so the rich-text editor renders real headings/lists instead of literal `##`/`-`.
- First test run *looked* successful (in-session screenshots showed everything correct), but the user caught — by reloading the page manually — that the description was empty and the zip was completely missing. Only the thumbnail had actually persisted.

**2026-06-21 session, second pass — root cause and real fix:**
- **Root cause**: Gumroad's Product and Content tabs each have their own "Save changes" / "Save and continue" button. Direct file inputs (thumbnail) upload and persist immediately on file selection, but rich-text editor content (description text, and the zip's file-embed block in the Content tab's editor) only commits to the database when you explicitly click that tab's Save button. The script was never clicking Save, so the browser closed before those edits were written — silently lost.
- **Fix**: added `_save_changes()` helper (clicks `button:has-text('Save changes'), button:has-text('Save and continue')`), called after the Content-tab zip upload and again after the Product-tab description fill.
- **Second bug found while fixing**: re-uploading a thumbnail when one already exists fails, because once an image is set, the `<input type="file">` is replaced in the DOM by an `<img>` + a "Remove" button — there's no file input to target anymore. Fixed by detecting and clicking "Remove" first (via `get_by_role("button", name="Remove")`) before looking for the input.
- **Thumbnail crop quality bug also found**: the original center-crop approach cut off text on both edges (e.g. "WHAT'S INCLUDED" → "HAT'S INCLUDED", "7 COMPLETE LESSON PLANS" partially clipped) because the source thumbnails are wide (1500x1125) designs with content spread across the full width. Replaced `_square_crop()` with `_pad_to_square()` — pads with the image's own corner background color instead of cropping, so the full design is visible, just letterboxed.
- All four fields (zip, thumbnail, description, title/price) re-verified correct **after a real page reload**, not just an in-session screenshot — this is the standard to hold future verification to, since Gumroad's save behavior is non-obvious.
- Deleted the orphaned `bycna` test product (2026-06-20) and throwaway test products created while debugging (`qutlse`/`TEST_PROBE_DELETE_ME`) — account is clean.

(See "Packaging Audit" and "Async Upload Trap" sections above for the 2026-06-26 follow-up fixes — the zip source and the save-verification logic both changed since this was first written.)

**Credentials:**
- `GUMROAD_TOKEN` — in `.env`
- `GUMROAD_EMAIL` / `GUMROAD_PASSWORD` — in `.env`
- Session cached in `.gumroad_session.json`

---

## Publishing Automation — TES

Status: **Not started** — lower priority, tackle after Gumroad is running.

---

## Current Bottleneck (shelved-series context — not the active priority)

The items below describe the *shelved* AI & Data Literacy series and are kept for reference only. See "Networks & Hardware Unit 1 — TPT Launch" near the top of this file for the active work.

1. **Unit 2's slides don't exist** — only the Canva CSV was generated, nobody did the manual Canva-import-and-export step. Not being pursued unless the user picks the old series back up.
2. **TPT bot detection** — resolved; TPT is unlocked and publishing works (see Networks & Hardware section).
3. Gumroad mechanics for the old series are fixed/verified but on hold per user direction.

---

## Next Session — Start Here

**Priority 1: DONE (2026-06-28)** — corrected bundle + assessment files pushed to both Gumroad and TPT, verified on both. See "Independent QA Pass + Fixes" above for full detail. `cmie/publishing/tpt.py` now has `replace_product_file()` for editing an existing product's attached file, reusable for any future correction.

**Priority 2: Decide the next unit's topic** and repeat the Networks & Hardware playbook:
1. Write `data/units/<new_unit_id>.json` (title, year_level, subject, 7 topics).
2. Run `python -m cmie.pipeline.full_product_pipeline --unit-config data/units/<new_unit_id>.json` — generates lessons, direct PPTX slides (no Canva), assessment, workbook, roadmap, teacher guide, listings, and packaging in one pass.
3. Generate a thumbnail: see the `generate_thumbnail()` call pattern used for Networks & Hardware in this session.
4. Package per-lesson + assessment + bundle zips (see the `_package_networks_unit.py`-style script used this session — copy individual PPTX files from `releases/public/<unit>_v001/01_Lesson_Slides/` and the assessment docx from `02_Assessment/` into their own zips, plus a full bundle zip of the whole public folder).
5. Publish each part: `python publish_tpt.py --unit <unit_id> --part lesson01..lesson07,assessment,bundle --tags "Lessons, Activities, Career and Technical Education, Critical Thinking and Problem Solving" --publish`. Always verify against the real `My-Products` list afterward, not just the script's log output.

**Priority 3: List the Networks & Hardware unit on TES too** — Gumroad's bundle is already live (see above). TES not started. `publish_gumroad.py` still only knows how to publish one zip per unit (the bundle) — fine for Gumroad's use case, but would need the same kind of `--part` support `publish_tpt.py` has if per-lesson Gumroad listings are ever wanted.

**Priority 4: Commit all untracked work**
```
git add cmie/publishing/ webapp/ publish_tpt.py publish_gumroad.py pptx_generator.py PROGRESS.md .env.example start.ps1
git commit -m "Add publishing automation: TPT Playwright + Gumroad hybrid (API + Playwright)"
```
