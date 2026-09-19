# FocusLab Digital — Revenue Tracker
_Last updated: 2026-09-17 (manual entry from a TPT dashboard screenshot the user shared — check_revenue.py still not confirmed reliable, see note below)_

## TPT
**Gross sales:** $88.47 USD
**Your earnings (after commission + transaction fees):** $44.70 USD
**Total sales:** 13

| Date | Order ID | Product | Price | Commission | Txn fee | Earnings |
|------|----------|---------|-------|-----------|---------|----------|
| 2026-09-13 | 345371687 | Organising Files & Folders \| Unit 1 – Getting Started for the Year \| Lesson 3 | $2.50 | $1.13 | $0.30 | $1.07 |
| 2026-09-09 | 344969762 | Debugging Logic Errors \| Unit 1 – Thinking Like a Programmer \| Lesson 5 | $2.50 | $1.13 | $0.30 | $1.07 |
| 2026-09-04 | 344388699 | Introduction to Programming: Unit 1 – Writing Your First Python Programs (Year 7) | $12.99 | $5.85 | $0.30 | $6.84 |
| 2026-08-31 | 343843899 | Binary Conversions & Addition \| Unit 1 – Binary and How Computers See the World \| Lesson 1 | $2.50 | $1.13 | $0.30 | $1.07 |
| 2026-08-31 | 343775861 | Representing Algorithms with Flowcharts \| Unit 1 – Thinking Like a Programmer \| Lesson 1 | $2.50 | $1.13 | $0.30 | $1.07 |
| 2026-08-26 | 343258039 | HTML Basics: Structuring a Web Page \| Unit 1 – Building Your First Website \| Lesson 1 | $2.50 | $1.13 | $0.30 | $1.07 |
| 2026-08-19 | 342478193 | Text as Data: ASCII & Unicode \| Unit 1 – Binary and How Computers See the World \| Lesson 1 | $2.50 | $1.13 | $0.30 | $1.07 |
| 2026-08-17 | 342243256 | Organizing Code with Functions \| Unit 1 – Writing Your First Python Programs I | $2.50 | $1.13 | $0.30 | $1.07 |
| 2026-08-16 | 342103085 | Digital Systems: Unit 1 – How Computers Actually Work (Year 7) | $12.99 | $5.85 | $0.30 | $6.84 |
| 2026-07-28 | 340420803 | Cyber Security & Digital Footprints: Unit 1 – Protecting Yourself Online | $12.99 | $5.85 | $0.30 | $6.84 |
| 2026-07-15 | 339960853 | AI & Data Literacy Series \| Unit 1 Data Foundations \| Complete Unit | $25.00 | $11.25 | $0.30 | $13.45 |
| 2026-05-19 | 337700440 | Simple Japanese Hiragana chart with practice | $2.50 | $1.13 | $0.30 | $1.07 |
| 2026-05-11 | 336973974 | Data Shapes the AI World \| No Prep Digital Tech Lesson 1 | $4.50 | $2.03 | $0.30 | $2.17 |

Tax collected for seller to remit varies per order per the screenshot (TPT remits most of it on its own); not re-summed here, doesn't affect the earnings column above.

## Gumroad
**Total revenue:** A$0.00 AUD
**Total sales:** 0
_(per user statement 2026-09-17: no sales on any platform other than TPT — consistent with every prior automated check)_

## TES
**Total revenue:** £0.30 GBP net
**Total sales:** 1

| Date | Product | List price | Tax | Txn fee | TES royalty | Net profit |
|------|---------|-------------|-----|---------|--------------|------------|
| 2026-07-18 | Spreadsheets & Data Analysis: Unit 1 – Making Sense of Data... | £1.00 | -£0.17 | -£0.20 | -£0.33 | £0.30 |

Confirmed 2026-09-17 via the user's own TES Sales dashboard screenshot (UK store, last-90-days view, "data up to date as of 16 Sep 2026", only 1 transaction shown). This matches what the 2026-07-31 automated `check_revenue.py` runs had already found — the earlier "no sales outside TPT" statement was about *new* sales, not this one, so the discrepancy flagged above is resolved: TES has exactly 1 lifetime sale, still this one, nothing since.

---
## Summary
| Platform | Revenue |
|----------|---------|
| TPT | $88.47 USD gross / $44.70 USD earnings |
| Gumroad | A$0.00 AUD |
| TES | £0.30 GBP net (1 sale, 2026-07-18) |

_Note: figures are in each platform's native currency. TPT pays in USD, Gumroad in AUD, TES in GBP._

_Correction 2026-08-19: the previous entry read "$13.45 USD, 1 sale" — that figure was the **earnings** on a single order (339960853), not total revenue, and it missed the other 5 orders entirely._

_Correction 2026-09-17: added 7 orders (2026-08-19 through 2026-09-13) from a user-shared TPT dashboard screenshot that `check_revenue.py` had never captured — this file was silently a month stale. `check_revenue.py`'s TPT session reliability is still not fixed; see review notes for 2026-09-17. Re-run `python check_revenue.py --save` once the session is confirmed working so this file stops needing manual patching._

## 2026-09-19 — Flagship full-curriculum bundle launched (no sales yet, catalogue value note)

New product: **"The Complete Digital Technologies Curriculum"** (`complete_digital_technologies_curriculum`) — 14 units / 98 lessons combining the whole existing catalog plus one newly-built unit (Artificial Intelligence Literacy, filling the one real strand gap against a 12-strand full-coverage curriculum). Live on all 3 platforms same day:
- TPT: $199.00 — https://www.teacherspayteachers.com/Product/The-Complete-Digital-Technologies-Curriculum-Full-Year-Bundle-14-Units-98-17692631
- Gumroad: A$299.00, `published: true` verified via API — https://focuslabdigital.gumroad.com/l/jdedx
- TES: £149.00, TES-PAID licence, verified live via direct public-page load — https://www.tes.com/teaching-resource/resource-13579629

No sales yet (published today). This realizes the 2026-08-27 standing flag ("build a full-curriculum bundle offer... $150-500") — see project memory for full build detail and one open item (a stray draft duplicate on TES from a follow-up metadata-fix attempt, not deleted per standing no-delete-without-authorization policy).
