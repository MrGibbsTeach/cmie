# Sprint Agent 1 — Generator Bug Audit (2026-07-02)

## Summary

Systematic pass over ai_lesson_engine.py, workbook_generator.py, assessment_generator.py, readme_generator.py, and markdown_to_docx()/stage_packaging() in full_product_pipeline.py, hunting the 5 target bug classes. Found and fixed 10 new bugs at the root. All fixes verified by running the changed functions on sample input (scratchpad, not releases/). All 5 files compile; no published content was regenerated or touched.

Biggest find: the ACTIVE lesson-architect prompt hardcoded "The lesson is part of an AI and data literacy unit" for every unit — this is the root cause of AI framing bleeding into Networks & Hardware content, upstream of all the previously-fixed downstream symptoms.

## Bugs Found & Fixed

### 1. Architect prompt hardcodes AI-literacy unit framing (class 1 — worst offender)
- File: cmie/generator/ai_lesson_engine.py, build_lesson_architect_prompt() (was line 61)
- Root cause: prompt text "The lesson is part of an AI and data literacy unit." sent for EVERY unit via the active 3-stage pipeline (architect → writer → critic).
- Fix: replaced with unit-derived framing: "The lesson is part of the unit '{cfg.micro_unit_name}'. Keep all content, examples, and framing specific to this unit's actual subject matter."
- Affected published units: Networks & Hardware U1 and Algorithms & Programming Logic U1 (both TPT-live) were generated with this AI framing in the prompt. Likely explains residual AI flavour in their content. Human call on regeneration.

### 2. Legacy single-stage lesson prompt hardcodes AI & data literacy context (class 1)
- File: cmie/generator/ai_lesson_engine.py, build_lesson_prompt() (~line 300)
- Root cause: "The lesson must support a Lower Secondary AI & data literacy unit. Students have been working with data, personal data, ... bias and fairness, recommendation systems..." — hardcoded.
- Note: this path (build_lesson_prompt/_call_openai_for_lesson) is DEAD CODE — not called by the current pipeline. Fixed anyway (unit-derived wording) so a revival can't reintroduce the bug.
- Affected published units: none via current pipeline; old year7_ai_data units used it, where the framing was correct.

### 3. Stray control characters from AI output not sanitised (class 4 — root fix for the published VT bug)
- Files: cmie/generator/ai_lesson_engine.py (new sanitize_ai_text() + regexes near top, ~lines 35–60); applied at all 3 JSON-parse points in ai_lesson_engine and in assessment_generator.generate_assessment_schema(); also applied to file text at the top of markdown_to_docx() in cmie/pipeline/full_product_pipeline.py.
- Root cause: nothing between OpenAI JSON and pptx/docx rendering stripped control chars. This is the template-level root of the Networks L02/L03 vertical-tab hook-text artifact (published content itself deliberately left as-is per user).
- Fix: recursive sanitiser — \r\n→\n, VT/FF/U+2028/U+2029→\n, all other C0/C1 controls stripped — applied at the AI-JSON parse boundary (covers slides/pptx, workbook, assessment, presenter notes for all future units) plus defensively in markdown_to_docx.
- Verified: sanitize_ai_text on nested dict/list with \x0b, \x0c, \r\n, \x01, U+2028 produces clean output; markdown_to_docx sample with embedded \x0b renders clean.
- Note: current releases/year7_networks_hardware_unit1 lesson JSONs and PPTXs scan clean for control chars (likely regenerated since the artifact was logged), so no re-verification of the published symptom was possible.

### 4. Empty headings rendered into DOCX (class 3 — root fix for blank "Extension ideas:")
- File: cmie/pipeline/full_product_pipeline.py, markdown_to_docx() — new section_is_empty() helper.
- Root cause: any "### "/"#### " heading with no body (AI-output gap) rendered as a dangling heading.
- Fix: ###/#### headings whose section is empty (next non-blank line is another heading, "---", or EOF) are skipped. Conservative: #/## headings untouched (## LESSON drives page breaks and always has content).
- Related class-3 fix in ai_lesson_engine.build_slide_deck(): empty hook_scenario now falls back to a topic-derived prompt instead of rendering a "Hook Scenario" slide with an empty body.
- Affected published units: Networks L01/L05/L06 blank "Extension ideas:" stays as-is per user; future units protected.

### 5. markdown_to_docx: unhandled inline/block markdown (class 2)
- File: cmie/pipeline/full_product_pipeline.py, markdown_to_docx().
- Previously unhandled, now converted:
  - *italic* → italic runs; \`inline code\` → Consolas runs; [text](url) → "text (url)" (add_runs_with_bold extended into a small inline parser; bold logic preserved)
  - "#### " headings → Heading 3 (previously rendered as literal "#### text")
  - "* " and "+ " bullet markers (previously literal text paragraphs)
  - nested (indented ≥2 spaces) bullets → "List Bullet 2" (previously flattened)
- Deliberately NOT converted: numbered lists ("1. step") stay as plain paragraphs with the literal marker — python-docx's "List Number" style shares one numbering sequence document-wide, so two separate lists would render 1..4 then 5..7. Literal markers read correctly; noted in a code comment.
- Verified end-to-end: sample md exercising every case → docx inspected run-by-run (styles, bold/italic/code runs, tables, response box, skipped empty sections all correct).
- Affected published units: any docx in the two TPT-live units containing italics/H4/star bullets would have literal markers. Spot check advised if regenerating for other reasons.

### 6. Workbook "fair" branch hardcodes "AI decision" (class 1)
- File: cmie/generator/workbook_generator.py, _lesson_specific_task().
- Root cause: any lesson title containing "fair" (e.g. "Fair Testing") got "Decide if the AI decision is fair".
- Fix: wording now topic-neutral: "Decide if the decision or system described is fair".
- Affected published units: neither live unit has a "fair" lesson title — no impact; latent bug for future units.

### 7. Workbook "design" branch used bare substring "ai" (class 1 — bug in the previous fix)
- File: cmie/generator/workbook_generator.py, _lesson_specific_task().
- Root cause: the 2026-06 fix required AI co-occurrence via `"ai" in t` — substring match false-positives on "explain", "email", "maintain", "training" etc. "Designing and Explaining Your Algorithm" would have fired the fairness task.
- Fix: new _title_mentions_ai() using word-boundary regex (\bai\b | artificial intelligence | machine learning).
- Verified: "Designing and Explaining Your Algorithm" → generic task; "Designing Better AI Systems" → design branch.

### 8. infer_unit_focus AI-themed branches fire on non-AI keywords (class 1/5)
- File: cmie/generator/assessment_generator.py, infer_unit_focus().
- Root cause: branch 1 fired on bare "ethics"/"bias"/"fair" and branch 2 on bare "model"/"prediction"/"classification"/"recommendation" — injecting a fully AI-specific scenario/title/task-focus into the generation prompt. "OSI model", "network model", "fair use" would all trigger AI-framed assessments. This is the remaining root of the Networks AI-framed assessment (its generic-fallback half was fixed 2026-06; the false-positive branches were not).
- Fix: both branches now also require an explicit AI mention (word-boundary regex, same terms as #7).
- Verified: Networks lesson set including "The OSI model" + "Fair use of shared networks" → neutral fallback ("Applying Networks & Hardware"); genuine AI units still hit both AI branches.
- Affected published units: Networks & Hardware assessment stays as-is per user's call.

### 9. README hardcodes "7 lessons in total" (template bug)
- File: cmie/generator/readme_generator.py (~line 88).
- Root cause: fixed string regardless of actual lesson count; wrong for any non-7-lesson unit.
- Fix: dynamic `f"- {len(lessons)} lessons in total"` (omitted when no lessons found).
- Affected published units: both live units happen to have 7 lessons — no live impact; latent for future units.
- Verified against the real Networks lessons dir → "- 7 lessons in total".

### 10. Personal-data comparison slide: wrong example on the "Non-Personal Data" side (class 1/content)
- File: cmie/generator/ai_lesson_engine.py, _build_visual_comparison_slide(), "personal data" branch.
- Root cause: right_example was "Photos, chat messages, or videos" — copy-pasted from the structured/unstructured slide; those are examples of PERSONAL data, i.e. the exactly wrong side of the comparison.
- Fix: replaced with "Average rainfall, class test averages, or total website visits".
- Affected published units: the 8 shelved year7_ai_data units (9 TES-live AI-series listings) — the "personal data" lesson deck teaches an incorrect example. Flagging for human decision; listings not touched.

### Also fixed in passing
- ai_lesson_engine.build_slide_deck() real_world fallback body and default speaker notes hardcoded data/bias framing ("Why does quality or bias matter here?", "ask students what data is being used and why quality or bias matters") → now topic-neutral. Default speaker notes are normally overwritten by the AI presenter-notes pass, but survive it when that pass fails or skips a slide.

## Open Questions / Waiting on User

1. Regenerate the two TPT-live units? Bug #1 (architect prompt) means Networks & Hardware U1 and Algorithms U1 were generated under AI-literacy framing. Content quality call, not mine to make.
2. _build_visual_comparison_slide() "bias"+"fair" branch is AI-framed ("Can lead to unfair or inaccurate AI decisions"). It only fires when a topic title contains both "bias" and "fair", which today means AI units — left unchanged, but a future non-AI "bias and fairness in data" lesson would get AI wording. Change wording, or accept?
3. Personal-data slide fix (#10) corrects a factually wrong example that IS live in the shelved TES AI-series decks. Worth a targeted re-export of just that deck, or leave with the shelved series?
4. stage_packaging() builds the internal zip BEFORE the required-files existence check, so a broken run still produces an internal artifact zip. Cosmetic/ordering; left alone — flag if you want it moved after the check.

## Verified Already-Fixed Items (brief)

Confirmed present in current code, not re-reported:
- markdown_to_docx: add_runs_with_bold (**bold** → runs) — present, now extended (see #5); pipe-table → Word table (add_markdown_table) — present; "- - text" repeated-bullet strip — present.
- workbook "design" branch AI/fairness co-occurrence guard — present (tightened, see #7); topic-neutral Section-2 prompt ("What's one important thing to consider in this scenario?") — present at line ~147.
- assessment infer_unit_focus generic fallback is topic-neutral and references actual unit name + lesson titles — present.
- readme_generator "No specialist background in the topic is required" — present.
- render_rubric_table A/B/C/D grade bands — present.
- stage_packaging README.docx → Teacher_Guide.docx (05_Teacher_Guide/Teacher_Guide.docx) — present.

## Verification performed

- sanitize_ai_text unit-tested on nested structures with VT/FF/CR-LF/C0/U+2028.
- markdown_to_docx run on a scratchpad sample covering headings 1–4, empty sections, bold/italic/code/links, nested/star/flattened bullets, pipe table, response box, embedded \x0b — output docx inspected paragraph-by-paragraph and run-by-run.
- _lesson_specific_task, infer_unit_focus, build_lesson_architect_prompt, build_slide_deck fallbacks tested on AI and non-AI titles.
- generate_unit_readme + generate_student_workbook re-run against the real releases/year7_networks_hardware_unit1/lessons JSONs into the scratchpad — dynamic lesson count correct, zero AI-term leakage.
- All 5 edited files pass py_compile; ai_lesson_engine.py source scanned clean of stray control characters (an earlier editing mishap introduced some; repaired and re-verified).
