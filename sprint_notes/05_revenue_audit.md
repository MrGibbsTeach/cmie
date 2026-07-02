# 05 — Revenue & Monetization Audit
_Agent 5, 2026-07-02. All dashboard data pulled read-only today; nothing published, edited, deleted, or spent._

## The single most important insight

**The problem is not price, product, or even listing quality — it is that nothing drives traffic and nothing converts cold traffic.** TES proves it with real numbers: 264 views, 0 purchases in 3+ months. TPT's own best-sellers in this exact niche ("computer networks middle school") have only 1–6 reviews, i.e. this is a low-velocity niche where a zero-review store with generic tags, AU-English titles ("Lower Secondary", "Digital Technologies") and no free lead magnet is effectively invisible to US buyers. Meanwhile the fastest revenue lever — 4 finished drafts — has been sitting unpublished for 4 days, and **61 live TPT products aren't even tracked in PROGRESS.md** (the store has 80 live products, not 19). The machine generates product fine; it has no acquisition side at all.

---

## 1) Real Numbers (verified 2026-07-02)

| Platform | Revenue | Sales | Source | Confidence |
|---|---|---|---|---|
| Gumroad | **A$0.00** | 0 (lifetime) | Gumroad Sales API via `check_revenue.py` | Authoritative |
| TES | **£0.00 / US$0.00** | 0 purchases, 0 reviews, **264 views, 2 downloads** since author signup 21 Mar 2026; Bronze tier | Author Dashboard (`/teaching-resources/dashboard/overview`), read-only Playwright | Authoritative |
| TPT | **$0 (corroborated, not dashboard-verified)** | — | Public store: zero reviews on every CMIE-era product; the store's single 5.0 review sits on a pre-CMIE legacy product | High |

**TPT BLOCKER:** `.tpt_session.json` is expired (`/My-Products` redirects to `Request-Authorization?authModal=login`) and the old `/Seller-Dashboard/Earnings` URL 404s. I deliberately did **not** attempt automated TPT form login — that triggered bot detection and a temporary account lock before. Needs one manual `python publish_tpt.py --save-session` login from you (see §5).

The 2 TES "downloads" are on paid-only resources — most likely author-side test downloads, not customer activity (uncertain, noted not guessed).

`check_revenue.py --save` was run and REVENUE.md now holds these numbers. During the audit I fixed the TES half of the script (it was navigating to 404 URLs, using a login selector TES's form doesn't have, and its regexes didn't match the real dashboard text). TES revenue checking now works end-to-end; TPT correctly reports the expired-session blocker instead of the misleading "layout may have changed."

**Costs note:** COSTS.md says $0.00 spent, but the pipeline consumes OpenAI API credits (`cmie/marketing/marketing_generator.py`, lesson engine). That spend is happening somewhere and isn't in COSTS.md — worth reconciling before trusting margin math.

---

## 2) Full Listing Inventory

### TPT — public store "FocusLab Digital" (Eaton, WA, Australia): **80 live products** (PROGRESS.md says 19)
Store: 5.0 rating from **1 review** (on a legacy product), **4 followers**.

| Group | Products | Price | Live since | Tracked in PROGRESS.md? |
|---|---|---|---|---|
| Networks & Hardware Unit 1 | 7 lessons + assessment + bundle | $2.50 / $3.50 / $12.99 | 26–27 Jun 2026 | Yes |
| Algorithms & Programming Logic Unit 1 | 7 lessons + assessment + bundle | $2.50 / $3.50 / $12.99 | 28 Jun 2026 | Yes |
| AI & Data Literacy Unit 1 (legacy single listing) | 1 | $29.99 | 15 Jun 2026 | Yes |
| **AI & Data Literacy Units 1–5, fully broken out** | ~39 (lessons $4.50 each; workbooks; assessments; roadmaps; unit bundles $31.50→$25) | see left | ~Mar–Apr 2026 (est.) | **No — untracked** |
| **AI & Data Literacy 4-unit mega bundle** | 1 | $126→**$85** | untracked | **No** |
| **Legacy personal products** (Hiragana chart, DT career posters, WWII role-play scripts, SCSA poster, Women in Tech posters, Economics Monopoly cards) | 6 | $2.00–$5.00 | pre-CMIE | **No** |

Live-listing quality problems seen on the public store today:
- **Literal `**bold**` markdown** in both new units' live bundle descriptions ("Summative assessment: \*\*Designing and Securing a School Network Report\*\*"). The markdown→HTML fix clearly didn't cover this field.
- Typos/duplications on AI-series listings: "Unit **Radmap**", "Designing Fair AI Designing Fair AI", **two Lesson 5/Lesson 6 both titled "What Is AI Bias?"**, "Designing a Simple AI Model" listed as both Lesson 2 and Lesson 7 of Unit 2, Unit 3's bundle description is a copy-paste of Unit 2's lesson list, "Assessment Pack |Unit 5" spacing.
- Grade band shows 7th–9th while thumbnails say "Year 7" — minor inconsistency.

### TES — author `claytongibbs`, shop displays "FocusLab Digital": 9 live + 3 drafts

| Resource | Price | Status | Created | Views | Sales |
|---|---|---|---|---|---|
| Data Shapes the AI World – L1 | £4.00 | Live | 21 Mar | 26 | 0 |
| Data Shapes the AI World – L1 **(exact duplicate)** | £4.00 | Live | 21 Mar | 25 | 0 |
| What Counts as Personal Data? – L2 | £4.00 | Live | 28 Mar | 33 | 0 |
| Structured vs Unstructured Data – L3 | £4.00 | Live | 28 Mar | 29 | 0 |
| Understanding Data Quality – L4 | £4.00 | Live | 28 Mar | 31 | 0 |
| Bias in Training Data & Fairness – L5 | £4.00 | Live | 28 Mar | 29 | 0 |
| How Recommendation Systems Use Your Data – L6 | £4.00 | Live | 28 Mar | 28 | 0 |
| Designing Fair Data Collection – L7 | £4.00 | Live | 28 Mar | 33 | 0 |
| "Designing Fair AI Designing Fair AI" – AI Ethics L1 | £4.00 | Live | 07 Apr | 30 | 0 |
| Algorithms & Programming Logic U1 bundle | (£9.99 intended) | **Draft** | 28 Jun | — | — |
| Networks & Hardware U1 bundle | (£9.99 intended) | **Draft** | 28 Jun | — | — |
| Networks & Hardware U1 bundle **(duplicate draft, failed delete)** | — | **Draft** | 28 Jun | — | — |

Views sum to exactly the dashboard's 264. Author profile is incomplete (TES shows a "Complete profile" nudge — a stated conversion factor in their own guidance). New bundle drafts have **no cover image** (deliberately skipped in `publish_tes.py`).

### Gumroad — 7 products on the same "focuslabdigital" storefront (API-verified)

| Product | Price | Status | Sales |
|---|---|---|---|
| Networks & Hardware U1 bundle (`rrdvk`) | A$12.99 | **Live** | 0 |
| Algorithms U1 bundle (`bpvevc`) | A$12.99 | Draft | 0 |
| AI & Data Literacy U1 (`cqwjlt`, shelved) | A$29.99 | Draft | 0 |
| What Counts as Personal Data? – Lesson 2 | A$4.00 | Draft (untracked) | 0 |
| **Small Contractor SWMS Starter System (Australia)** | **A$129.00** | **Live (off-brand)** | 0 |
| **ADHD Productivity Hacks** | A$5.00 | **Live (off-brand)** | 0 |
| Free SWMS Audit Readiness Checklist | A$0 | Draft (off-brand) | 0 |

The teaching brand shares its storefront with construction-safety and ADHD-productivity products. Any teacher who clicks through to the store sees SWMS documents next to Year 7 lessons.

---

## 3) Why $0 — per-platform diagnosis

### TPT (the main market — and the main miss)
Most plausible primary factor: **cold-start invisibility in a low-velocity niche, worsened by AU-English titles.**
1. **Zero reviews, zero sales history.** TPT search ranking is driven heavily by sales/review velocity and CTR. A store whose CMIE products all show "(0)" starts on page N for every query. Note: even the *best-sellers* for "computer networks middle school" have only 1–6 reviews — this niche has low absolute volume, so page-1 placement matters even more.
2. **Titles carry the wrong keywords.** "Lower Secondary" and "Digital Technologies" are Australian/UK terms. TPT's buyer base is overwhelmingly US teachers searching "middle school computer science", "computer networks unit", "coding lesson". Our titles literally do not contain "middle school" or "computer science".
3. **Tags are generic by necessity** (TPT's controlled vocabulary rejected topic tags; only "Lessons", "Activities", "Career and Technical Education", "Critical Thinking and Problem Solving" exist) — so titles/descriptions carry ~all the SEO weight, and ours are thin ("This unit develops student understanding of key concepts in Digital Technologies" — zero keyword density, no standards alignment, no page/slide counts).
4. **Seasonality:** the new units went live 26–28 June — the exact bottom of the US demand year. Back-to-school (Aug–Sep) is the window that matters.
5. **No free lead magnet** to generate downloads → reviews → ranking. This is the standard TPT cold-start playbook and we haven't run it.
6. **Conversion drags for the few who do land:** literal `**markdown**` in live descriptions, text-only thumbnails (competitors show actual resource pages), no preview file callout, AI-series listings with duplicated/typo'd titles and mismatched lesson numbers.
7. **Pricing is fine.** $12.99 bundle vs $10.50–$15 comparables; $2.50/lesson is actually *below* the $4.50–$5 norm. Price is not the constraint — do not discount further.

### TES
**Traffic exists (264 views) but converts at 0% — this is a price/social-proof/positioning problem, not pure invisibility.**
1. £4.00 for a single lesson from a 0-review author is above what TES's free-heavy market pays a stranger. Comparable single KS3 Computing lessons: £1–£4; whole bundles: £8–£15.
2. The two resources most likely to sell (the £9.99 unit bundles) are **unpublished drafts**.
3. Titles are AI-series artifacts ("Data Shapes the AI World – Lesson 1") with no "KS3", "Computing", or curriculum keywords UK buyers search.
4. Zero reviews, incomplete author profile, a **visible duplicate listing** (looks careless to buyers), no cover images planned on the new drafts.
5. Positive: TES's UK "Computing"/Australian curriculum framing actually fits this content better than TPT's US market does — and TES is where we have proof of impressions.

### Gumroad
**Gumroad is a checkout, not a marketplace.** It has essentially no organic discovery for this niche. With zero external traffic (no social, no email list, no SEO content, no links from anywhere), 0 sales is the *expected* output regardless of listing quality. Secondary issue: off-brand products (A$129 SWMS system, ADHD hacks) share the storefront. Gumroad should be treated as infrastructure (a place to send traffic we generate), not as a channel that produces customers.

### Structural honesty check vs the $200k/yr target
Top-1% TPT sellers earn ~$50–100k/yr after years of catalog + review building. Two units + a mispositioned AI series at ~$0/month is not "early days of a working plan", it's a missing acquisition layer. The realistic path to meaningful revenue is: catalog breadth (the pipeline's actual strength) × correct keywords × review flywheel × the Aug–Sep window, plus at least one channel we control (email list / direct-to-school). $200k from passive marketplace listings alone is not a credible 12-month outcome; treat marketplace revenue as the proving ground and the sellable *system* as the bigger asset.

---

## 4) Prioritized Next Moves (impact vs effort)

| # | Move | Expected impact | Effort | Approval needed? |
|---|---|---|---|---|
| 1 | **Publish the 4 finished drafts** (TES ×2 bundles at £9.99, Gumroad Algorithms `bpvevc`; decide the TES duplicate draft + `cqwjlt` fate) | Medium — first realistic TES sale candidates; zero marginal build cost | ~15 min | **Yes — publishing is a live action** |
| 2 | **Free lead-magnet lesson on TPT and TES before August** (repackage Lesson 1 of each new unit as a free product whose last page links to the bundle + asks for a review) | High — the standard cold-start fix for both platforms; builds downloads/reviews/followers that compound into rank | Low (assets exist; pipeline can add a "free sampler" packaging step) | **Yes — publishing** |
| 3 | **US-keyword retitle + copy fix on the 18 new-unit TPT listings** ("Middle School Computer Science", "Computer Networks Unit", grade-explicit; kill the literal `**…**`; add slide/page counts and CSTA/ACARA alignment lines to descriptions) | High for the Aug window — titles are the main SEO surface since tags are generic | Low-medium (generator fix + re-push via existing edit automation) | **Yes — edits live listings** |
| 4 | **Ship 3–5 more units in July** with the proven pipeline (keyword-optimized titles from day one) so the catalog is broad for US back-to-school (Aug/Sep) and AU Term 3 (late July) | High — catalog breadth is the strongest lever the system actually owns; niche is low-velocity per product, so breadth wins | Medium (mostly automated; user sign-off on topics) | Topic sign-off only; publishing needs approval |
| 5 | **TES AI-series relaunch**: fix duplicate listing, retitle with KS3/Computing keywords, drop lessons to ~£2.50–£3 (or make Lesson 1 free), complete author profile, add cover images | Medium — TES is the only platform with proven impressions; conversion fixes act on real traffic | Low-medium | **Yes — live listings + prices** |
| 6 | **Thumbnail/preview upgrade**: covers showing actual slide screenshots (not text-only), plus a multi-page preview PDF on TPT listings | Medium (CTR + conversion) | Medium — automatable in `thumbnail.py`/packaging | New assets no; swapping on live listings yes |
| 7 | **Platform strategy**: TPT primary; TES elevated to co-primary (curriculum fit + proven traffic); Gumroad demoted to link-destination only; evaluate Teach Starter / Amped Up Learning / direct-to-AU-school outreach for Term 3 | Medium-high long term | Decision now, work later | **Yes — strategy decision** |
| 8 | **Storefront hygiene**: separate or hide off-brand products (SWMS/ADHD on Gumroad; Hiragana/WWII/Economics on TPT are more defensible as generic teaching resources) | Low-medium (trust/conversion) | Low | **Yes — touches live products** |
| 9 | **Manual TPT session refresh** so `check_revenue.py` can verify TPT earnings weekly (then schedule it) | Enables tracking (no direct revenue) | 2 min of your time | **Yes — your login** |
| 10 | **Track the untracked**: PROGRESS.md's inventory is off by 61 TPT products and 3 Gumroad products; revenue strategy can't be right if the catalog list is wrong (logged here; PROGRESS.md deliberately not edited per sprint rules) | Hygiene | Low | No |

Explicitly **not** recommended: further price cuts on the new units (already at/below market), paid ads (no conversion evidence yet to spend against), and any more per-lesson TES uploads of the shelved AI series.

## 5) Waiting On You (decision list)

1. **Publish the 4 drafts?** TES Networks bundle, TES Algorithms bundle (£9.99 each), Gumroad Algorithms `bpvevc` (A$12.99). Also: delete the duplicate TES Networks draft, and keep-or-kill the shelved `cqwjlt` (A$29.99) and untracked "Personal Data L2" (A$4) Gumroad drafts. *Fastest possible revenue action; everything is built.*
2. **TPT manual login** (`python publish_tpt.py --save-session`) — unblocks revenue verification; I did not attempt automated login due to the prior bot-detection account lock.
3. **Approve live-listing edits** (move #3/#5/#6): retitles, markdown-artifact fixes, typo fixes ("Unit Radmap", duplicated titles, wrong lesson numbers), TES price test, cover images. Per hard rules, none of this was touched.
4. **Duplicate live TES listing** "Data Shapes the AI World – Lesson 1": delete one copy? (Live listing — untouched.)
5. **Free-lesson strategy**: OK to give away Lesson 1 of each unit as a lead magnet on TPT + TES?
6. **July build plan**: pick 3–5 unit topics now so the catalog is live before mid-August (US BTS) — suggest staying in AU Year 7–8 Digital Technologies scope that doubles as US middle-school CS: Data Representation (binary), Cybersecurity & Online Safety, Websites/HTML basics, Spreadsheets & Data Analysis, Digital Systems/How Computers Work.
7. **Off-brand storefront split** (SWMS/ADHD off the teaching Gumroad; hobby TPT items into an inactive category or separate store).
8. **Platform expansion**: evaluate Teach Starter (AU-native, Term 3 timing) and/or direct-to-school outreach — yes/no on a scouting task.

---

### Side findings / systemic fixes made during this audit
- `check_revenue.py` TES flow repaired and verified working (real dashboard URL `tes.com/teaching-resources/dashboard/overview`, `get_by_label` login selector matching `publish_tes.py`, extraction patterns matching real dashboard text, resource-management URL corrected). TPT flow now reports the expired-session blocker accurately (change was already partially in place from Agent 4's session; both edits coexist).
- TES sessions expire fast (two expired within hours during the audit) — any scheduled TES revenue check must rely on the `.env` credential login path, which now works.
- The exact TES uploads URL for future automation: `https://www.tes.com/teaching-resources/dashboard/resource-management/uploads` ("Show all" filter included).
