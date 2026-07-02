# New Unit Proposals — Year 7 Digital Technologies (Agent 3, Sprint 2026-07-02)

Status: PROPOSAL ONLY. No pipeline runs, no configs created, no content generated.

## Context checked before proposing

- Existing catalog (do not overlap): `year7_networks_hardware_unit1` (covers AC9TDI8K01 hardware selection, AC9TDI8K02 data transmission/network security) and `year7_algorithms_unit1` (covers AC9TDI8P05 algorithm design, AC9TDI8P06 tracing/debugging).
- Shelved-but-live AI & Data Literacy series on TES (9 listings): AI ethics/bias, AI systems/applications, AI in sectors, data foundations, data+AI models. All three proposals below stay out of AI territory and out of "what is data / data feeds models" framing.
- Curriculum codes verified against the official ACARA v9 Years 7–10 Digital Technologies content descriptions PDF (not from memory).
- Config format confirmed against `data/units/year7_algorithms_unit1.json`: unit_id, title, year_level "Lower Secondary", 7 topics, concepts → skills → applied design lesson last.
- Demand sanity-checked via web search on TPT/TES (sources at bottom).

---

## Candidate 1: Data Representation — Binary & How Computers See the World

**Unit title:** Data Representation: Unit 1 – Binary and How Computers See the World
**Pitch:** Students discover how everything on a screen — numbers, text, images, sound — is really just 1s and 0s, and learn to encode data themselves.

**Suggested unit_id:** `year7_data_representation_unit1`

**Why it sells**
- Curriculum fit is the strongest of any remaining Year 7–8 topic: directly hits **AC9TDI8K03** ("investigate how digital systems represent text, image and audio data using integers") and **AC9TDI8K04** ("explain how and why digital systems represent integers in binary"). These two codes are mandatory core and completely uncovered by our catalog.
- High search demand: "binary numbers", "binary code worksheets" and "data representation" are heavily searched TPT/TES terms; TES's top KS3 data representation packs (UK Year 7 = same age band) show sustained sales. Dual-market appeal: maps to AU DigiTech, UK KS3 Computing, and US CS middle school.
- Competition exists but is fragmented — mostly single worksheets and binary puzzle novelties. A coherent 7-lesson unit + assessment pack matching our bundle format is a genuine gap.

**7-lesson sequence**
1. **Why Computers Speak in 1s and 0s** — What digital data is and why digital systems store everything as binary states (switches, on/off, integers).
2. **Counting in Binary: Numbers to Bits** — Place value in base-2 and converting small decimal numbers to binary and back.
3. **Binary Conversions and Simple Binary Addition** — Fluency practice converting both directions plus adding two small binary numbers.
4. **Text as Data: ASCII and Unicode** — How characters are stored as integer codes, including encoding and decoding secret messages.
5. **Images as Data: Pixels and Bitmaps** — How images become grids of binary values, including bit depth and creating pixel art from binary strings.
6. **Sound as Data: Sampling** — How audio waves are sampled and stored as sequences of integers, and how sample rate affects quality.
7. **Designing a Data Encoding Scheme for a Real Scenario** — Applied design task: students design and document their own encoding scheme (e.g. a pixel-art message system or emoji code) and swap-decode with peers.

**Overlap risks:** Minimal. "How Data Travels Across a Network" in the Networks unit touches packets, not representation. Not in AI-series territory as long as lessons stay on encoding mechanics, not "data for insights/models" — the sequence above does.

---

## Candidate 2: Cyber Security & Digital Footprints — Staying Safe and Secure Online

**Unit title:** Cyber Security & Digital Footprints: Unit 1 – Protecting Yourself Online
**Pitch:** A practical personal-security unit where students learn to spot phishing, lock down accounts with MFA, and take control of their digital footprint.

**Suggested unit_id:** `year7_cybersecurity_unit1`

**Why it sells**
- Biggest raw demand of the three: "cyber safety", "internet safety", "digital footprint" and "digital citizenship" are perennial top search terms on both TPT and TES, with strong purchase seasons (back-to-school, Safer Internet Day in February).
- Direct v9 fit: **AC9TDI8P13** ("explain how multi-factor authentication protects an account when the password is compromised and identify phishing and other cyber security threats") and **AC9TDI8P14** ("investigate and manage the digital footprint existing systems and student solutions collect and assess if the data is essential to their purpose"). Both codes are new-in-v9 emphasis and uncovered by our catalog.
- Gap vs competition: the market is flooded with PSHE-style "be nice online" posters and wordsearches. Very few products teach the technical DigiTech angle (MFA mechanics, phishing anatomy, threat types) at Year 7 level — that's our lane and matches the FocusLab Digital positioning.

**7-lesson sequence**
1. **The Cyber Threat Landscape** — What cyber security is and the main threat types students actually face (phishing, malware, scams, account takeover).
2. **Passwords and Multi-Factor Authentication** — Why passwords fail, what makes them strong, and how MFA protects an account even when the password is compromised.
3. **Spotting Phishing and Social Engineering** — Anatomy of phishing messages and manipulation tactics, with real-style examples students classify as legit or scam.
4. **Your Digital Footprint** — What active and passive footprints are, who can see them, and how they persist and compound over time.
5. **What Apps Collect About You** — Auditing the data an app or game collects and assessing whether each data point is essential to its purpose.
6. **Managing and Cleaning Up Your Footprint** — Practical controls: privacy settings, permissions, safe sharing decisions, and reducing unnecessary data trails.
7. **Designing a Cyber Security Plan for a Real Scenario** — Applied design task: students build a security plan and awareness campaign for a realistic persona (e.g. a new student setting up their first phone).

**Overlap risks:** Two to manage. (1) Networks unit has one lesson "Network Security Basics" — keep this unit at the personal/account level (MFA, phishing, footprint), not network hardware/firewalls; the sequence above does. (2) Lesson 5 brushes near the shelved AI series' "data collection" territory — frame it strictly as footprint management per AC9TDI8P14, no AI, no data-model framing. Listings copy should say "personal cyber security", not "data literacy".

---

## Candidate 3: User Experience & Interface Design — Designing Apps People Love

**Unit title:** UX & Interface Design: Unit 1 – Designing Apps People Love
**Pitch:** Students think like product designers: define real problems, write user stories, wireframe an app, and test their designs on real users.

**Suggested unit_id:** `year7_ux_design_unit1`

**Why it sells**
- Strong v9 fit across the whole "Investigating and defining / Generating and designing" chain: **AC9TDI8P04** (define and decompose real-world problems with design criteria and user stories), **AC9TDI8P07** (design the user experience of a digital system), **AC9TDI8P08** (generate, modify, communicate and evaluate alternative designs), **AC9TDI8P10** (evaluate solutions against design criteria, user stories and future impact). Four content descriptions in one unit — great for curriculum-alignment copy in listings.
- Lowest competition of the three: TPT search for "UX design" returns thin, mostly high-school or one-off wireframe templates; code.org's CSD Unit 4 proves the topic is standard middle-years content, but almost nobody sells a ready-made unit for it. Real whitespace.
- Strategic catalog fit: it is the natural "design" companion to the Algorithms unit (design the interface, then build the logic), enabling cross-sell copy and future mega-bundles.

**7-lesson sequence**
1. **Good Design, Bad Design: What Is UX?** — What user experience means and why some apps feel effortless while others frustrate, using compare-and-critique examples.
2. **Knowing Your User: Problems and User Stories** — Defining and decomposing a real-world problem and writing user stories in the "As a… I want… so that…" format.
3. **Design Criteria: How Will We Know It's Good?** — Turning user stories into measurable design criteria that will later be used to judge the solution.
4. **Interface Building Blocks** — Common UI elements (buttons, menus, icons, navigation, layout) and the conventions that make interfaces predictable.
5. **Wireframing and Paper Prototyping** — Sketching low-fidelity wireframes of an app screen flow and turning them into a testable paper prototype.
6. **Accessibility and Inclusive Design** — Designing for different users and abilities: contrast, text size, touch targets, and evaluating designs against accessibility checks.
7. **Designing an App Interface for a Real Scenario** — Applied design task: students design, user-test and iterate a complete app interface for a chosen scenario, evaluated against their own design criteria.

**Overlap risks:** Minimal. Algorithms unit ends with "Designing an Algorithm for a Real Problem" — different artifact (logic vs interface); position UX unit as the front-end complement. No contact with Networks or AI-series territory.

---

## Recommendation (if forced to rank)

1. **Data Representation** — strongest curriculum obligation (teachers must teach K03/K04), proven search volume, fits our worksheet/slide format perfectly.
2. **Cyber Security & Digital Footprints** — biggest demand, but needs the positioning discipline noted above to avoid catalog/AI-series bleed.
3. **UX & Interface Design** — best whitespace and best strategic fit, slightly more speculative demand.

All three together would give FocusLab Digital near-complete coverage of the v9 Years 7–8 band alongside the existing Networks and Algorithms units.

## Sources used for demand/curriculum checks

- ACARA v9 Years 7–10 Digital Technologies achievement standards and content descriptions PDF (v8.australiancurriculum.edu.au/media/7736) — all AC9TDI8 codes verified verbatim
- Digital Technologies Hub Years 7–8 scope and sequence (digitaltechnologieshub.edu.au)
- TPT browse results: "binary numbers", "data representation", "cyber safety", "digital footprint", "internet safety", "ux design"
- TES: KS3 Data Representation Year 7 packs; Digital Footprint online safety lessons
- code.org CSD Unit 4 (User Interfaces) as evidence UX is standard middle-years content

---

AWAITING TOPIC APPROVAL — do not run pipeline until user signs off.
