# CMIE Project Progress

_Last updated: 2026-07-03_

---

## Sprint Consolidation — 5-Agent Parallel Audit (2026-07-02/03)

**Status: audit complete. Full detail in `sprint_notes/01–05` (kept alongside this file); this section is the consolidated summary.** Nothing was published, no live listing was edited, nothing was deleted, no money was deliberately spent (one small accidental OpenAI spend — see Incident below).

### Revenue & Monetization (Agent 5 — read this first)

**Verified numbers (2026-07-02):** Gumroad **A$0.00 / 0 lifetime sales** (API, authoritative). TES **£0.00 / 0 purchases — but 264 views and 0 reviews** since 21 Mar (author dashboard, read-only). TPT **$0 corroborated but not dashboard-verified**: `.tpt_session.json` is expired and automated login was deliberately not attempted (prior bot-detection account lock); zero reviews on every CMIE product on the public store. REVENUE.md now carries these real numbers via the repaired `check_revenue.py`.

**The single most important insight: the problem is not price, product, or listing polish — the machine has no acquisition side.** TES proves it with real traffic converting at 0%. And the fastest revenue lever — 4 finished drafts — has sat unpublished since 28 Jun.

**Inventory correction — this file's Revenue table was badly wrong:** the TPT store has **80 live products, not 19**. AI & Data Literacy Units 1–5 are fully broken out live ($4.50 lessons, $25 unit bundles, an $85 4-unit mega bundle, est. live since Mar–Apr) plus 6 pre-CMIE legacy products — none of it tracked here. Gumroad has 3 untracked products, including a **live A$129 construction-SWMS product and an ADHD guide on the same "focuslabdigital" storefront** as the teaching brand. Live-listing quality problems visible today: literal `**markdown**` in both new units' live TPT bundle descriptions, plus AI-series typos ("Unit Radmap", "Designing Fair AI Designing Fair AI", two lessons both titled "What Is AI Bias?").

**Why $0, per platform:**
- **TPT**: cold-start invisibility in a low-velocity niche (even niche best-sellers have only 1–6 reviews), worsened by AU-English titles ("Lower Secondary", "Digital Technologies") that miss US search terms ("middle school computer science"), generic-only tags (controlled vocabulary — titles carry all SEO weight and ours are thin), a late-June launch at the bottom of the US demand year, and no free lead magnet to start the download→review→rank flywheel. **Pricing is fine** ($2.50/lesson is below the $4.50–$5 norm; $12.99 bundle mid-market) — do not discount further.
- **TES**: traffic exists, conversion is the problem — £4/lesson from a 0-review author with an incomplete profile and a visible duplicate listing, while the two most sellable products (£9.99 unit bundles) are unpublished drafts. TES's UK/AU curriculum fit is actually better than TPT's; it's the only platform with proven impressions.
- **Gumroad**: a checkout, not a marketplace — zero organic discovery, zero external traffic pointed at it, so $0 is the expected output. Treat as infrastructure, not a channel.

**Honesty check vs the $200k/yr target:** top-1% TPT sellers earn ~$50–100k/yr after years of catalog and review building. The realistic play is catalog breadth (the pipeline's real strength) × correct keywords × review flywheel × the Aug–Sep back-to-school window, plus at least one owned channel — with the sellable *system* treated as the bigger asset.

**Prioritized moves (full table in `sprint_notes/05_revenue_audit.md` §4):** 1) publish the 4 finished drafts; 2) free lead-magnet Lesson 1 on TPT+TES before August; 3) US-keyword retitles + copy fixes on the 18 new-unit TPT listings; 4) ship 3–5 more units in July for US back-to-school + AU Term 3; 5) TES AI-series relaunch (dedupe, retitle, price test, profile, covers); 6) thumbnails showing real slide pages + preview PDFs; 7) TES elevated to co-primary, Gumroad demoted to link destination; 8) storefront hygiene (off-brand products); 9) TPT session refresh; 10) fix this file's inventory tracking. Explicitly not recommended: further price cuts, paid ads, more per-lesson TES uploads of the shelved series.

### Generator Audit (Agent 1) — 10 new root-cause fixes, all in the working tree

**Headline: `build_lesson_architect_prompt()` in `ai_lesson_engine.py` hardcoded "The lesson is part of an AI and data literacy unit" for EVERY unit** — the upstream root cause of all the AI-framing leaks previously patched one downstream symptom at a time. Both TPT-live units were generated under that prompt (now unit-derived). Regenerate-or-leave is the user's call.

Also fixed (detail + verification in `sprint_notes/01_generator_audit.md`): recursive `sanitize_ai_text()` at every AI-JSON parse boundary plus defensively in `markdown_to_docx()` (root fix for the vertical-tab class); empty ###/#### sections no longer render dangling headings (root fix for blank "Extension ideas:"); `markdown_to_docx()` now handles italics, inline code, links, #### headings, star/plus and nested bullets (numbered lists deliberately left literal — python-docx numbering restart limitation); the previous "design"-branch fix's bare `"ai" in title` substring false-positived on "explain"/"email" — now word-boundary regex, same fix applied to `infer_unit_focus()` whose branches fired on bare "model"/"fair" (an "OSI model" lesson would have gotten an AI-framed assessment); README's hardcoded "7 lessons in total" now dynamic; workbook "fair" branch de-AI'd; **a factually wrong slide example** in `_build_visual_comparison_slide()` — "Photos, chat messages, or videos" listed as NON-personal data — fixed at the generator, but the wrong version is live in the shelved TES series' decks.

### Visual QA (Agent 2) — rendered review, most-broken-first

Method: all 313 slides of the two live units + the live-TPT AI unit exported to PNG via PowerPoint COM and actually reviewed; key docx rendered via Word; everything else structured extraction (limitations noted in `sprint_notes/02_visual_qa.md`).

1. **AI-series units 3–8 (shelved, but 9 TES listings live): BROKEN** — systematic mid-word text truncation on most content slides ("always picks stude", title "AI PERSONALIZES LEARNIN" overlapping body), a literal `{point3}` template variable on unit3 L5 slide 7, identical topic-agnostic filler slides across units, pre-fix `**`/pipe-table leaks in every unit's assessment/roadmap/README docx. **Whether the 9 live TES products contain these decks needs checking — if yes, they're selling broken slides.**
2. **AI unit 1 "EDITED READY FOR RELEASE" (LIVE on TPT, $29.99): moderate** — `Assessment_Rubric_and_Marking.docx` renders as raw markdown (visually confirmed); "[Presenter Name]" placeholders, a "— Unknown" quote, gibberish AI-generated keyboard image, stray screenshots + zip shipped in the product.
3. **AI unit 2**: no decks at all (CSV only) — known, listing honest, still unsellable.
4. **Algorithms (LIVE): ship-quality slides** — no cropped text, no markdown artifacts, zero AI contamination. Minor: L01 has 2 reflection questions vs 3 elsewhere.
5. **Networks (LIVE): ship-quality/minor** — but **the AI-framing contamination is wider than previously documented: 4 docx, not 1** (roadmap, teacher guide, and rubric all carry "fairness in AI outcomes" language, visually confirmed, in addition to the known assessment task). Also "Wired vs Wireless **Nets**" title, thin README-style teacher guide.

Good news: the long-standing "stray vertical-tab" issue is actually `<a:br/>` line breaks that **render cleanly in real PowerPoint** — python-pptx merely reports them as `\x0b`. Not a visible defect as shipped. Both live units passed their listing-promise checks.

### Automation & Infrastructure (Agent 4)

- **`package_unit.py` (NEW, tested)** — the previously-manual packaging step is now `python package_unit.py --unit <id>`: builds all 10 customer zips with the packaging-audit hygiene rules enforced, validation, a no-overwrite guard, and post-write zip verification. Tested against both live units to scratch dirs: **all 20 zips identical (file lists + sizes) to the hand-built artifacts.**
- **`produce_unit.py` (NEW)** — one command chaining pipeline → automated QA spot-checks → thumbnail → package → optional TPT/Gumroad/TES **draft** publishing (never `--publish`; gated behind `--draft-publish`; stages skippable/resumable; publish output grep-filtered, never tailed). Tested through packaging only. Now also refuses to regenerate any already-shipped unit without `--allow-regenerate` (see Incident).
- **TES delete mystery SOLVED (root cause, read-only):** the dashboard's Delete is a client-side deferred delete — the actual `DELETE /api/v2/resources/{id}/draft` fires only in the Undo toast's `onClose` handler. **Reloading to verify before the toast auto-hides is precisely what cancels the delete.** Reliable procedure: delete, stay on the page until the toast closes (watch for the DELETE returning 2xx), then reload to confirm.
- **TPT auth state:** `.tpt_session.json` (Jun 27) is expired — TPT automation is currently blocked on a session refresh, not bot detection. `--save-session` needs **no admin/DPAPI** (that note referred to the separate browser_cookie3 path). Recommendation: periodic 2-minute manual `--save-session` refresh, CDP-attach to real Chrome as fallback, never automated form login.
- **`check_revenue.py` repaired (Agents 4+5, complementary fixes):** UTF-8 console crash, float-format crash on missing earnings, falsy-zero displayed as "?", TES flow completely rewritten to the real dashboard URLs, TPT now reports session expiry honestly instead of "layout may have changed", and the risky TPT form-login fallback removed. **Gumroad + TES legs verified working end-to-end; TPT leg blocked on the session refresh** (and its earnings extraction needs one verification pass after that — the old Earnings URL is dead). Auto-refresh proposed, not set up: daily Windows Task Scheduler run now; hybrid (cloud Gumroad-API + weekly local full scrape) later.

### ⚠️ Incident — live Algorithms unit regenerated in place (contained; one decision pending)

While testing `produce_unit.py`'s stage gating, its pipeline stage ran for real against `year7_algorithms_unit1` (output piped through `head` hid the evidence — the same output-truncation trap this file documents for publish scripts). ~7 OpenAI generations ran (small cost, logged for COSTS.md) and the unit's raw sources were regenerated in place; the public-folder rebuild then died on a OneDrive lock, deleting the customer folders mid-rebuild. `releases/` is not git-tracked.

**Contained:** all 10 published customer zips (Jun 28) were never touched — they are the exact bytes customers receive and remain the source of truth. `releases/public/.../01–05` was restored byte-verified from the `_PUBLIC.zip`, and the 5 surviving unit-level listing files restored. **Still on regenerated variants:** the raw lesson/slide/assessment sources and the 7 per-lesson listing .md files. Options: **A (recommended) restore via OneDrive recycle bin/version history** (everything predates 2026-06-28; live TPT pages also hold the as-published listing text verbatim), or B, adopt the regenerated content and accept local-vs-live divergence. Guard added so no shipped unit can be regenerated without `--allow-regenerate` (verified fails fast).

### New unit topics (Agent 3) — proposed, awaiting sign-off

Three candidates in `sprint_notes/03_new_units_PROPOSED.md`, each with a 7-lesson outline, grounded in verified ACARA v9 content descriptions and demand-checked: **Data Representation (binary)** — recommended first (mandatory codes, zero overlap, fragmented competition); **Cyber Security & Digital Footprints** (biggest raw demand; overlap risks vs Networks L5 and the AI series flagged with mitigations); **UX & Interface Design** (clearest whitespace, cross-sells with Algorithms). These align with Agent 5's July build-plan suggestions. **Pipeline not run — topics need approval first.**

### Waiting on you (every decision point from all five agents)

1. **Publish the 4 finished drafts?** TES Networks + Algorithms bundles (£9.99 each), Gumroad Algorithms `bpvevc` (A$12.99). Also keep-or-kill the shelved `cqwjlt` (A$29.99) and the untracked "Personal Data L2" (A$4) Gumroad drafts. Fastest possible revenue action.
2. **TPT session refresh** — run `python publish_tpt.py --save-session` (2 min, no admin). Unblocks TPT revenue checks and publishing.
3. **Approve new unit topics** (pick 1–3 of Agent 3's candidates; Agent 5 recommends 3–5 units live before mid-August).
4. **Algorithms source recovery: Option A (OneDrive restore, recommended) or B (adopt regenerated)** — see Incident.
5. **Approve live-listing edits** (none touched): US-keyword retitles + `**markdown**`/typo fixes on TPT; TES AI-series relaunch (dedupe, retitle, ~£2.50–£3 or free-L1 price test, profile completion, cover images); thumbnail/preview upgrades.
6. **Free lead-magnet Lesson 1** of each new unit on TPT + TES — yes/no.
7. **Deletes (procedures ready, nothing deleted):** TES duplicate draft `13503371` (root cause solved — stay on page until the toast closes); duplicate live "Data Shapes the AI World" TES listing; archive the superseded `year7_ai_data_unit1_v001` original folder.
8. **Regenerate-or-leave:** the two live units' content was generated under the AI-framed architect prompt (Agent 1 #1); Networks' AI contamination spans 4 docx not 1 (Agent 2); the live-TPT AI unit's raw-markdown rubric docx is a small high-value fix; AI-series 3–8 decks are broken — first check whether the 9 live TES products actually contain them.
9. **Revenue auto-refresh:** daily local Task Scheduler now vs hybrid cloud/local — pick one.
10. **Storefront hygiene:** split/hide off-brand products (A$129 SWMS + ADHD on the teaching Gumroad; legacy hobby items on TPT).
11. **Platform strategy:** TES to co-primary, Gumroad demoted to link destination, scout Teach Starter / direct-to-AU-school for Term 3 — yes/no.
12. **COSTS.md reconciliation:** OpenAI API spend (pipeline + the incident's ~7 calls) is real but untracked.
13. **One live test approval:** whether `publish_tpt.py` without `--publish` actually persists a retrievable TPT draft after the browser closes (unverified — determines the orchestrator's TPT stage design).
14. **Housekeeping:** `releases/` is not git-tracked — consider tracking `releases/public/` or snapshotting before pipeline runs (the incident had no VCS safety net).

---

## ⚠️ Important Discovery — TES Already Has Live Listings From the Shelved Series (2026-06-28)

While building TES publishing for the new units, found that **9 resources from the old AI & Data Literacy series are already live on TES**, dated March 2026 — months before this PROGRESS.md ever mentioned TES, and well before the "Direction Change" pivot. **This was never tracked anywhere in this file.** Specifics:

- 7 distinct AI Ethics + Bias lessons + 1 exact duplicate ("Data Shapes the AI World – Lesson 1" appears twice), all priced at £4.00, licence "TES-PAID", status live (not draft) — confirmed via real view counts (25-33 views each) and "Created: 21/28 Mar 2026" dates.
- £0.00 earnings / 0 sales on all of them so far.
- Found under Author Dashboard → Resource Management → My Uploads → "Show all" (not the default filtered view, and not the same place as "My Resources" which only shows purchased/downloaded items).
- **Not touched** — per the shelved-series policy, left these exactly as found. The duplicate "Data Shapes the AI World" listing is worth deleting at some point, but that's the user's call, not done automatically.

**Action for the user:** worth deciding whether to actively promote/price-check these existing TES listings, since they're real live products nobody has been tracking.

---

## Direction Change (2026-06-26)

**The original 8-unit "AI & Data Literacy Series" is shelved.** Per user direction: those units were practice/test units, built around a Canva-dependent workflow that's no longer being used. Don't resume work on Units 1-8 (TPT/Gumroad/TES publishing for that series) unless explicitly asked — the user may pick them up personally later. The packaging audit and Gumroad fixes from earlier in this file are still accurate *for that series* but are no longer the active priority. **Exception**: TES already has live listings from this series (see discovery note above) — don't delete or modify those without being asked, but they do exist and are worth knowing about.

**New direction: fully automated unit creation, no Canva, lesson-by-lesson + bundle listings on TPT (+ bundle on Gumroad and TES).** First unit — Networks & Hardware Unit 1 — went live 2026-06-26/27. Second unit — Algorithms & Programming Logic Unit 1 — went live 2026-06-28, noticeably faster than the first since the playbook now actually works end-to-end. TES publishing for both units' bundles added 2026-06-28. See the sections below for details. This is the proven template for future units.

---

## Algorithms & Programming Logic Unit 1 — TPT + Gumroad Launch (2026-06-28)

**Status: all 9 TPT products live + Gumroad bundle drafted (awaiting manual publish).**

| Product | Price | Status |
|---|---|---|
| Lesson 1: What Is an Algorithm? | $2.50 | ✅ Live on TPT |
| Lesson 2: Sequencing, Selection, and Repetition | $2.50 | ✅ Live on TPT |
| Lesson 3: Representing Algorithms with Flowcharts | $2.50 | ✅ Live on TPT |
| Lesson 4: Writing Pseudocode | $2.50 | ✅ Live on TPT |
| Lesson 5: Debugging Logic Errors | $2.50 | ✅ Live on TPT |
| Lesson 6: Efficiency: Comparing Algorithms | $2.50 | ✅ Live on TPT |
| Lesson 7: Designing an Algorithm | $2.50 | ✅ Live on TPT |
| Assessment Pack | $3.50 | ✅ Live on TPT |
| Full Bundle | $12.99 | ✅ Live on TPT, **draft on Gumroad** (`https://gumroad.com/products/bpvevc/edit` — confirmed unpublished, "Publish and continue" still showing pink/unclicked, unlike Networks & Hardware's which turned out already-live) |

**This run validated the fixed pipeline end-to-end with no major surprises** — config → `full_product_pipeline` → thumbnail → package → publish was much faster than Unit 1. Two small things worth noting:

1. **Found and fixed a new AI-output formatting quirk**: the assessment task's raw markdown had nested bullets flattened as `"- - text"` (AI artifact, not a generator bug) which rendered as a literal double-dash in the docx. Generalized the fix in `markdown_to_docx()`'s bullet handling to strip repeated leading `"- "` markers, since this could recur in any future unit's AI-generated content.
2. **Self-inflicted bug, caught and fixed**: accidentally ran `publish_tpt.py --part lesson02` twice (a `tail` pipe truncated the first run's success output, so it looked like it hadn't completed and got rerun), creating a duplicate "Sequencing, Selection, Repetition" product on TPT. Found TPT's delete mechanism — there's no delete button in the My-Products list itself, it's hidden inside "Quick Edit" → scroll down → "Permanently delete this product" → confirms by re-stating the exact product title before deleting. **Verified the correct duplicate's product ID via an explicit assertion before clicking delete** — got the row index right only on the second attempt, so don't assume `matches.first` is the one you just created. Lesson: **pipe TPT/Gumroad publish output through `grep -E "Submitted|ERROR|WARNING"` instead of `tail`**, so the success line is never accidentally cut off and mistaken for a failure that needs re-running.

No AI-specific language leaked anywhere in this unit's listings/workbook/assessment — confirms the 2026-06-27 generator fixes hold up on a second, unrelated topic.

---

## TES Publishing Built From Scratch (2026-06-28)

**Status: both units' bundles drafted on TES, awaiting manual review and publish.**

- Networks & Hardware bundle: draft saved, resource id `13503376` (plus one earlier duplicate from probe-testing, id `13503371` — attempted to delete it via the "Delete" link under Resource Management, got a "deleted" success toast with an Undo option, but **the duplicate was still present after a fresh reload** — the delete didn't actually persist for reasons not yet understood. Low priority to chase further since duplicate drafts cost nothing and aren't public; revisit if it matters later).
- Algorithms & Programming Logic bundle: draft saved cleanly, resource id `13503396`, no duplicate this time (more careful testing process).

**`publish_tes.py` was non-functional before today** — it assumed a single-page form, but TES's real upload flow is a 5-step wizard (Description → Add Files → Categories → Licence → Publish) where each step's fields only exist in the DOM once that step loads. Rewrote it entirely:

- **Added automated login** (cookie cache + `TES_EMAIL`/`TES_PASSWORD` form-login fallback, mirroring TPT/Gumroad) — previously TES only supported a fully manual one-time browser login via `cmie/publishing/browser.py::setup()`, with no credentials path at all.
- **Fixed `_check_logged_in()`**: it checked for `tes.com/login`/`tes.com/register` in the URL, but the real unauthenticated redirect target is `tes.com/authn/sign-in` — neither old string ever matched, so this check would have silently reported "logged in" even when redirected to the sign-in page. Would have caused every previous run to proceed as if authenticated and fail downstream.
- **Step 1 (Description)**: title + markdown description. Unlike Gumroad/TPT, **TES's editor natively supports raw markdown** (heading/bullet/bold syntax renders correctly) — no HTML conversion needed here, the opposite problem from the other two platforms.
- **Step 2 (Add Files)**: TES's help text only lists "PDF, Word, Smartboards, JPEG, Powerpoint, Excel, ePub" as supported formats — **zip is not mentioned but is in fact accepted** (verified directly, uploaded fine with the file name showing in "Uploaded files"). Also requires selecting a "resource type" — `"Unit of work"` matches our bundle product. Cover image upload was **deliberately skipped**: its file input shares discovery with the zip's, and a wrong index would silently overwrite the zip upload with the thumbnail (caught this almost happening during testing). Revisit later once a safe selector for the cover-image input specifically is confirmed.
- **Step 3 (Categories)**: age range / curriculum / subject dropdowns. **Must select by element id (`#main-age-range`, `#curriculum`, `#main-subject`), not position** — a hidden "additional age range" field sometimes mounts between visible fields and shifts any index-based locator, causing a `select_option` to target completely the wrong dropdown. Defaults used: age `11-14`, curriculum `Australian`, subject `Computing` — all good fits for this project's Year 7 Australian Digital Technologies content.
- **Step 4 (Licence)**: "Sell my resource" is the default tab; price field has id `#spinner`.
- **Step 5 (Publish)**: stops here deliberately — does **not** check the copyright confirmation box or click "Publish now". The resource is already saved as a draft on the Author Dashboard at this point (confirmed via the "Resource draft has been saved" toast) without needing that final click.
- **New CLI**: `python publish_tes.py --unit <unit_id> --price <gbp>`. Always publishes the bundle (`_PUBLIC.zip`), same priority as Gumroad — TES has no per-lesson concept built yet.

### Important discovery during this work — see the note at the top of this file

Found 9 already-live TES resources from the shelved AI series (dated March 2026, never tracked in this file before today). Not touched, just documented. See top of this file for detail.

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
| TPT      | 19 (1 shelved AI series + 9 Networks & Hardware + 9 Algorithms & Programming Logic) | $0 |
| TES      | 9 live, shelved AI series (just discovered, untracked until today) + 2 drafts awaiting manual publish (Networks & Hardware bundle, Algorithms bundle, £9.99 each) | $0 confirmed (AI series shows £0.00 earnings so far) |
| Gumroad  | 1 live (Networks & Hardware bundle, A$12.99) + 1 draft awaiting manual publish (Algorithms bundle, A$12.99) + 1 draft, shelved series (`cqwjlt`, AI Unit 1, not being pursued) | $0 |

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

**Priority 1: Review and publish the 4 pending drafts** (all built, none published — all waiting on a human click):
- Gumroad: Algorithms bundle draft, `https://gumroad.com/products/bpvevc/edit`, A$12.99.
- TES: Networks & Hardware bundle draft (Author Dashboard → Resource Management → My Uploads), £9.99.
- TES: Algorithms bundle draft, same location, £9.99.
- (Networks & Hardware's Gumroad bundle is already live, no action needed there.)
- Also decide what to do about the duplicate "Networks & Hardware" TES draft (delete attempt didn't persist — see TES section above) and the duplicate "Data Shapes the AI World" resource in the shelved AI series (see discovery note at top of file).

**Priority 2: Decide on the newly-discovered live TES AI-series resources** (see top of file) — they've been live since March with zero tracking. Worth a pricing/promotion review, or at minimum acknowledging they exist in whatever revenue tracking happens outside this file.

**Priority 3: Commit and consider pushing today's work** — committed locally as of this session (check `git log` for the latest commit); local branch was ahead of `origin/main` and not yet pushed as of the last check. Ask before pushing.

**Priority 4: Decide the third unit's topic** and repeat the now-proven playbook (gets faster each time):
1. Write `data/units/<new_unit_id>.json` (title, year_level, subject, 7 topics) — get user sign-off on the lesson sequence first.
2. Run `python -m cmie.pipeline.full_product_pipeline --unit-config data/units/<new_unit_id>.json` — generates lessons, direct PPTX slides (no Canva), assessment, workbook, roadmap, teacher guide, listings, and packaging in one pass.
3. Spot-check for AI-leftover language (`grep -rn "\bAI\b" releases/<unit_id>/`) and the nested-bullet artifact (`grep -n '^- - ' releases/<unit_id>/**/*.md`) before packaging — both are fixed at the generator level but worth a quick confirm on a new topic.
4. Generate a thumbnail via `cmie/publishing/thumbnail.py::generate_thumbnail()`.
5. Package per-lesson + assessment + bundle zips — still no reusable script for this exact step. Worth turning into a real script if a fourth unit happens.
6. Publish to TPT: `python publish_tpt.py --unit <unit_id> --part lesson01..lesson07,assessment,bundle --tags "Lessons, Activities, Career and Technical Education, Critical Thinking and Problem Solving" --publish`. **Pipe through `grep -E "Submitted|ERROR|WARNING"`, never `tail`**.
7. Publish the bundle to Gumroad: `python publish_gumroad.py --unit <unit_id> --price 12.99`.
8. Publish the bundle to TES: `python publish_tes.py --unit <unit_id> --price 9.99`.
9. Verify everything against the real dashboards, not script exit codes.
