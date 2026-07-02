# Visual QA Sweep — releases/public/ (Agent 2)

Date: 2026-07-02. Reviewer: Visual QA agent (rendered-output review, not just text grep).
Scope: 2 live units at full rigor; 8 shelved AI-series units at reduced depth (noted below).

## URGENT — flagged during sweep (not a QA finding, needs owner attention)

At ~16:27 today, WHILE this read-only sweep was running, almost the entire
`releases/public/year7_algorithms_unit1_v001/` folder was deleted by another process:
all 7 PPTX decks, Student_Workbook.docx, Unit_Roadmap.docx, Teacher_Guide.docx, both
assessment docx, and the per-lesson listings. Only `06_Listings/unit/` + 2 listing md
files remain. This unit is LIVE on TPT. This agent ran read-only operations only
(verified: every open was read-only; no writes/deletes under releases/). git status
shows another sprint agent actively rewriting the pipeline (`produce_unit.py`,
`package_unit.py`, modified `cmie/generator/*`, `cmie/pipeline/*`) — likely a
regenerate-in-place that cleared the folder first. Note: `releases/` is NOT tracked in
git, so there is no VCS safety net if the rebuild fails.
All Algorithms findings below are from renders/extractions taken BEFORE the deletion.

---

## Rendering method + limitations (read first)

- PPTX: every slide of both live units exported to PNG via PowerPoint COM automation
  (real PowerPoint rendering, 1280x720), reviewed as contact sheets. For the shelved AI
  series: all slides of the live-on-TPT "EDITED READY FOR RELEASE" unit 1 exported; units
  3 and 5 sampled (2 decks each); units 2, 4, 6-8 covered by structured text extraction
  only (python-pptx/python-docx) — reduced depth, noted per unit.
- DOCX: converted to PDF via Word COM for visual review where session budget allowed
  (visually reviewed: Networks roadmap + teacher guide, live-TPT AI unit rubric); all
  docx in all 11 folders additionally scanned via structured extraction (markdown
  leaks, vertical tabs, blank headings, off-slide shapes, AI-language in non-AI units,
  placeholder text).
- Limitation: two session-limit cutoffs killed the Word-to-PDF batch twice, and
  multi-page PDF page-rendering was unavailable (no poppler); the student workbooks and
  assessment tasks were reviewed by structured extraction, not visually. Mitigation:
  extraction found no markup/structure defects in the live units' workbooks, and the
  same generator's roadmap/rubric tables render correctly in Word (verified visually).
  Slide review of the two live units is fully visual (every slide).
- A note on the known "stray vertical-tab" issue: in the current PPTX files these are
  `<a:br/>` line-break elements, NOT literal control characters. In actual PowerPoint
  rendering they display as clean line breaks (verified visually on Networks L02/L03
  and Algorithms L03/L05/L06 hooks). python-pptx merely *reports* them as \x0b. As
  shipped, they are not a visible defect.

---

## Ranking (most broken first)

1. year7_ai_data_unit3-8 (shelved; truncated slide text, {point3} placeholder, md leaks) — BROKEN
2. year7_ai_data_unit1 "EDITED READY FOR RELEASE" (LIVE on TPT) — minor-to-moderate issues
3. year7_ai_data_unit2 (shelved; no slide decks at all, listings promise CSV) — incomplete package
4. year7_ai_data_unit1_v001 (original, superseded by EDITED copy) — moderate issues
5. year7_algorithms_unit1_v001 (LIVE on TPT) — ship-quality slides (but see URGENT above)
6. year7_networks_hardware_unit1_v001 (LIVE on TPT + Gumroad) — ship-quality / minor issues

---

## 1. year7_ai_data_unit3 through unit8 (shelved; 9 old TES listings still live)

VERDICT: BROKEN (slides unusable as paid product). Reviewed visually: unit3 L1+L5,
unit5 L1+L4. Units 4, 6, 7, 8 share the same generator/template (13 slides/deck, same
structure) and were covered by text extraction only — reduced depth, but the same
defects appear in extraction, so the verdict very likely extends to them.

Slide defects (visual, systemic):
- HARD MID-WORD TEXT TRUNCATION on most content slides. Examples:
  - unit3_lesson1.pptx slide 3 hook: "...but always picks stude"
  - unit3_lesson1.pptx slide 5: "unfair choices due to the d", "works wel",
    "because it's a comput"
  - unit5 Lesson 1.pptx slide 6 title: "AI PERSONALIZES LEARNIN" (truncated AND
    overlapping the body text box); body: "recommends books m", "perfect way to teac"
  - Pattern = text cut at a fixed character count, no ellipsis. Appears on slides
    3, 5, 6 (and similar body slides) of every sampled deck.
- LITERAL TEMPLATE VARIABLE rendered on a slide: unit3_lesson5.pptx slide 7 shows a
  bullet reading "{point3}". An unfilled generator placeholder in shipped output.
- Generic repeated filler: "QUICK STARTER — List 3 examples of data / Where is AI
  used? / Share one idea" is identical on slide 4 of decks in unit3 AND unit5,
  regardless of lesson topic.
- Reflection/check slides are topic-agnostic boilerplate ("What is the key idea?",
  "What did you learn today?") in every sampled deck.

DOCX defects (extraction; predate the 2026-06-27 markdown fix, worth documenting):
- Every unit 3-8: literal `**bold**` markdown in Assessment_Task.docx (4-6 hits each),
  Unit_Roadmap.docx (4-10 hits + raw `| pipe | table |` rows, 9 per file), and
  05_Teacher_Guide/README.docx (8 hits each).
- unit4 also has a stray extra 04_Unit_Roadmap/README.docx with `**` leaks.
- Teacher guide is a README.docx (differs from live units' Teacher_Guide.docx naming).

Listing check: units 3-8 have NO 06_Listings folder in the public release. The 9 live
TES listings for this series were created from elsewhere; contents cannot be verified
against these folders.

## 2. year7_ai_data_unit1_v001 - EDITED READY FOR RELEASE (LIVE on TPT)

VERDICT: minor-to-moderate issues. All 8 decks reviewed visually (Canva-designed,
20in x 11.25in). Slides look designed and rich (real illustrations) — the strongest
visual product of the whole catalogue — but:

- RAW MARKDOWN IN A SHIPPED DOCX (visually confirmed in Word-rendered PDF, pages 1-2):
  `02_Assessment/Assessment_Rubric_and_Marking.docx` renders as literal markdown:
  "# Assessment rubric and marking guide", "## Rubric", "### General notes", and the
  entire rubric as raw pipe-table lines (`| Criterion | Exemplary | ... |` /
  `|---|---|---|---|---|`) in plain body text. A paying teacher opens this and sees
  unrendered markup instead of a table. This is the live TPT product. (The
  accompanying Assessment PDF is fine; the docx is the broken piece.)
- "Presented by [Presenter Name]" placeholder text on lesson title slides (e.g.
  01-data-shapes... slide 1, 04-data-quality... slide 1).
- 01-data-shapes-the-ai-world slide 3: quote attributed to "— Unknown". Looks
  unfinished in a paid product.
- 04-data-quality... slide 6: AI-generated keyboard image with gibberish key labels
  ("Cnery!", "Orygn", "Rida", "25th/52'"). Noticeable on projection.
- Package structure differs from listing template: no separate Unit_Roadmap folder
  (roadmap lives under 04_Teacher_Guide/), teacher guide is screenshots + a GIF +
  roadmap docx rather than a written guide, and a stray `02_Assessment.zip` plus
  two desktop screenshots ("Screenshot 2026-03-30 ...") are shipped inside the
  product folder.

## 3. year7_ai_data_unit2_v001 (shelved)

VERDICT: incomplete package (extraction-based review — reduced depth).
- NO slide decks: only `01_Lesson_Slides_CSV/year7_ai_data_unit2_canva_slides.csv`.
  The unit listing copy honestly says "Canva-ready lesson slide CSV" — so listing and
  contents match — but as a product folder it is not sellable as-is, and the lesson
  listings under 06_Listings describe lesson slides.
- Same docx markdown leaks as units 3-8: `**` in Assessment_Task.docx (6), roadmap
  `**` (10) + 9 raw pipe-table rows, README.docx (8).

## 4. year7_ai_data_unit1_v001 (original, superseded)

VERDICT: moderate issues; superseded by the EDITED copy (which is what shipped).
- Same docx markdown leaks as the rest of the shelved series (Assessment_Task 6,
  Unit_Roadmap 10 x `**` + 9 pipe rows, README 8).
- Slides are an older 13.3in variant of the Canva deck; line-break rendering fine.
- Redundant duplicate of the EDITED folder — archival candidate, keeping both under
  releases/public/ invites publishing the wrong one.

## 5. year7_algorithms_unit1_v001 (LIVE: TPT live, Gumroad draft)

VERDICT (pre-deletion content): ship-quality slides / minor issues.
All 107 slides rendered and reviewed. Template consistent, no cropped or cut-off text,
no markdown artifacts, hooks' line breaks render cleanly.

Findings:
- Slide 5 hook line breaks in L03/L05/L06 are the same `<a:br/>` construct as the
  Networks known issue — visually they render as clean paragraph breaks, not stray
  characters. No action needed on visual grounds.
- L01 slide 14 has only 2 reflection questions where other decks (and Networks) have
  3 — minor inconsistency.
- The Networks known defect "blank Extension ideas: heading" did NOT recur in the
  Algorithms Teacher Notes slides sampled (L01, L07 both have content after
  "Extension ideas:").
- Assessment topic in the listing ("Designing and Debugging an Algorithm for a School
  Event") could not be re-verified visually because the files were deleted mid-sweep
  (see URGENT). Pre-deletion extraction showed NO AI/fairness contamination anywhere
  in this unit — the old buggy assessment prompt did NOT leak into Algorithms.
- Workbook/rubric/roadmap (pre-deletion extraction): clean; no `**`, no pipe tables;
  rubric content properly in a real table.
- Flowcharts lesson (L03) teaches flowchart symbols with no flowchart graphic at all —
  the known "no images" gap hurts most here (noted, not leading with it).
- Listing-promise check (against pre-deletion inventory): 7 lessons Y, PPTX per
  lesson Y, roadmap Y, workbook Y, assessment task + rubric + marking guide Y.
  Teacher guide included though not promised (fine).

## 6. year7_networks_hardware_unit1_v001 (LIVE: TPT + Gumroad)

VERDICT: ship-quality / minor issues. All 105 slides rendered and reviewed; docx
reviewed by extraction + partial visual.

New findings only (known issues not re-litigated):
- AI-framing contamination is WIDER than documented: the known issue covers the
  assessment task, but "protect data quality and fairness in AI outcomes" language
  also appears in the summative-assessment overview paragraph of
  `04_Unit_Roadmap/Unit_Roadmap.docx` (visually confirmed, roadmap p2) and of
  `05_Teacher_Guide/Teacher_Guide.docx` (p3), and in
  `02_Assessment/Assessment_Rubric_and_Marking.docx` (rubric criteria + common
  mistakes, e.g. "maintaining data quality and fairness in AI systems"). The roadmap's
  driving question itself is clean. Same defect class as the known issue, larger blast
  radius than the note implied (4 docx, not 1).
- The "Teacher Guide" is a document literally headed "README" — 4 sparse pages of
  generic how-to-use bullets, no per-lesson teaching notes (those live only on each
  deck's final Teacher Notes slide). Not broken, but thin for something labelled
  Teacher Guide. Its "What's included" list also omits the rubric/teacher guide.
- L03 title slide + workbook heading say "Wired vs Wireless Nets" — truncated-looking
  abbreviation ("Nets") in a student-facing title.
- Minor: inconsistent end punctuation on slide bullets (some bullets have periods,
  some don't, same slide); hook sentences missing final periods (e.g. L02 slide 5).
- Video slide in every lesson says "Video URL will be provided by your teacher" with
  a dummy player — by design, but a buyer may read "not included" as a gap; worth a
  line in the listing.
- Listing-promise check: 7 lessons Y, editable PPTX Y, roadmap Y, workbook Y,
  assessment task/rubric/marking guide Y. Matches.

---

## Regenerate-or-leave decision list (open questions for the user, no action taken)

1. AI-series units 3-8 slide decks: truncated mid-word text + `{point3}` placeholder =
   not sellable. Series is shelved, BUT 9 TES listings from it are still live — do those
   TES products contain these decks? If yes: pull or regenerate. Decision needed.
2. "EDITED READY FOR RELEASE" unit (live on TPT): regenerate
   `Assessment_Rubric_and_Marking.docx` (raw markdown) and re-upload? Small fix, live
   revenue product. Also: strip screenshots/zip from package, fix "[Presenter Name]"
   and "— Unknown" if the deck is ever touched again.
3. Networks unit: AI-framing extends to roadmap + teacher guide + rubric, not just the
   assessment task. User said leave as-is for the assessment — does that stand for the
   roadmap driving question too, or is a regen of the 4 docx worth it now that the
   2026-06-27 pipeline is clean?
4. Algorithms unit: content was ship-quality; folder was deleted mid-sweep by pipeline
   work — verify the regenerated output before any re-publish, and confirm the live TPT
   zip still matches what QA'd clean.
5. ai_data_unit1 original folder: archive it (duplicate of EDITED) to prevent
   wrong-folder publishing accidents. (Move to archive/ — needs user OK, destructive.)
6. ai_data_unit2: folder has no decks (CSV only) — archive or complete; unit-level
   listing is honest but lesson listings imply decks.
7. Housekeeping: releases/ is not in git. Given point 4 (in-place deletion), consider
   tracking releases/public/ or snapshotting before pipeline runs.
