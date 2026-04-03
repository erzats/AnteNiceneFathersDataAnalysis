# Roadmap to Patristic Scripture Citation Analysis

This project began as an ANF citation question-answering tool and is growing into a
broader patristic concordance. The roadmap is divided into three tracks:

- **Track A — ANF Foundation (Phases 1–7):** Complete and harden the core ANF dataset,
  query engine, and publication pipeline before expanding scope.
- **Track B — Corpus Expansion (Phases 8–11):** Add new source corpora once the ANF
  pipeline is stable. Each phase is independent and does not block the others.
- **Track C — Audience-Facing Features (Phases 12–14):** Tooling aimed at apologists,
  theologians, and lay users. Depends on Track A being complete; can draw from any
  corpus available at the time.

> **Scope note:** Corpus expansion is intentionally separated from foundation work.
> Phases 1–7 should reach a stable, deployed state before any Phase 8+ work begins.
> Adding new corpora before the ANF pipeline is solid will compound technical debt.

---

## ANF Foundation

Original goal: produce a reliable, deployable ANF citation dataset that directly
answers core historical questions.

---

## Phase 1 — Baseline question outputs (in progress)

Goal: produce deterministic artifacts that directly answer core historical questions.

- [x] Parse ANF volumes into normalized structured reference rows.
- [x] Emit targeted research CSVs:
  - `question_tobit_references.csv`
  - `question_psalm_popularity.csv`
  - `question_unquoted_books.csv`
  - `question_author_coverage.csv`
- [x] Add a report snapshot section that summarizes those questions at a glance.
- [x] Rebuild a query-ready SQLite dataset each run for open-ended ad hoc questions.

## Phase 2 — Data quality hardening

Goal: make outputs academically trustworthy.

- [x] Add validation checks for malformed OSIS references and ambiguous book IDs.
- [x] Track quote confidence levels (exact citation vs probable allusion).
- [x] Add regression fixtures for known edge cases per volume.
- [x] Capture duplicate-reference rationale in diagnostics.

## Phase 3 — Query interface and analyst ergonomics

Goal: support fast research iteration without manual CSV wrangling.

- [ ] Extend query engine with:
  - grouped aggregations (e.g., top books per Father),
  - threshold filters (e.g., Fathers citing >=N unique books),
  - deuterocanonical inclusion/exclusion toggles.
- [ ] Add CLI subcommands for named research questions.
- [ ] Provide reproducible notebook templates for exploratory analysis.

## Phase 4 — Retrieval/API layer (MCP-ready)

Goal: power interactive natural-language answers.

- [ ] Persist parsed data in a query-optimized local store (SQLite/DuckDB).
- [ ] Expose stable retrieval endpoints (or MCP tools) for:
  - citations-by-book,
  - coverage-by-author,
  - unquoted-books inventory.
- [ ] Add provenance fields for every answer row (volume/work/passage pointers).

## Phase 5 — Interpretation + publication

Goal: transition from raw extraction to publishable findings.

- [ ] Build longitudinal comparisons across ANF volumes and Fathers.
- [ ] Add interpretive markdown briefs for major patterns.
- [ ] Publish versioned datasets and changelog for reproducibility.

## Phase 6 — Robustness hardening

Goal: make the ANF pipeline and outputs production-quality before any scope expansion.

- [ ] **Passage-text retrieval:** Return the text surrounding a citation tag (from the
  ThML source), not just metadata. This transforms the tool from a citation index into
  a patristic concordance—the most-requested capability for apologists.
- [ ] **Three-tier confidence scoring:** Add `echo_allusion` below `probable_allusion`
  to distinguish thematic resonance from verbal parallel. Update MCP tools and exports.
- [ ] **Verse-range expansion:** Treat range citations (e.g., `Matt.5.3-12`) as covering
  all intermediate verses rather than only the start verse.
- [ ] **Parse failure surface area:** Emit `parse_diagnostics.csv` row count in the CLI
  run summary so degraded parse quality is immediately visible.
- [ ] **Incremental pipeline runs:** Allow re-parsing a single volume without rebuilding
  the entire database.
- [ ] **Expanded regression fixtures:** Grow Phase 2 fixtures to cover Syriac/Coptic
  fragment attribution, disputed-authorship works, and Ignatian long/short recension.
- [ ] **Cross-volume author deduplication:** Flag when the same Father's work appears
  across multiple ANF volumes to prevent double-counting in aggregate stats.

## Phase 7 — Web deployment and UI drill-down

Goal: make the project publicly accessible and navigable beyond top-level totals.

- [ ] **Deploy to Vercel:** Run the pipeline, commit generated JSON, and publish the
  web app. The infrastructure exists; this is a blocking gap for public usefulness.
- [ ] **Passage-level drill-down:** Clicking a book or author in the dashboard shows
  specific chapters and verses cited, not just totals.
- [ ] **Work-level granularity:** Drill down from author → individual work
  (e.g., *Against Heresies* book-by-book), since theological arguments depend on
  specific treatise context.
- [ ] **Dynamic API routes:** Replace static JSON with Next.js API routes backed by
  SQLite so filters (testament, author, book) work without pipeline reruns.
- [ ] **Footnote/bibliography export:** `--format footnote` option producing citations
  in Chicago/Turabian style (e.g., *ANF* vol. 3, Tertullian, *Against Praxeas*, ch. 7)
  for direct use in apologetics writing.

---

## Corpus Expansion

Each phase below adds a new source corpus. All share the same output schema and
MCP tools; only the parser and author metadata differ. Do not begin any of these
until Phase 6 is complete.

---

## Phase 8 — Nicene & Post-Nicene Fathers (NPNF)

Goal: extend the corpus through the fifth century using the same ThML pipeline.

**Sources:** NPNF Series 1 (Augustine, Chrysostom, Theodoret) and Series 2
(Athanasius, Basil, Gregory of Nyssa, Jerome, Ambrose). Both series are distributed
by CCEL in the same ThML format as the ANF—pipeline changes should be minimal.

- [ ] Download and validate NPNF ThML files from CCEL.
- [ ] Audit parser against NPNF ThML structure; patch edge cases.
- [ ] Add NPNF author metadata (display names, floruits, centuries) to `constants.py`.
- [ ] Extend `corpus` field in the database schema (`anf`, `npnf1`, `npnf2`).
- [ ] Update MCP tools and web UI to filter or compare by corpus.
- [ ] Add cross-corpus longitudinal view: citation frequency by century across ANF + NPNF.

**Why first:** Same format, near-zero new parser work, triples corpus size, adds the
Fathers most cited in Nicene-era doctrinal debates (Augustine alone dwarfs most
ANF authors in citation density).

## Phase 9 — Ecumenical Councils and Creeds

Goal: add the definitional documents of early Christian orthodoxy.

**Sources:** Nicaea (325), Constantinople (381), Ephesus (431), Chalcedon (451),
and optionally Trent (1545) and Vatican I (1870). Available in clean HTML from CCEL
and NewAdvent.

- [ ] Write a lightweight HTML parser for conciliar documents.
- [ ] Model councils as "authors" with `corpus = councils` and appropriate metadata
  (date, location, doctrinal focus).
- [ ] Extract Scripture citations from canon lists and doctrinal definitions.
- [ ] Add a `councils` page to the web UI showing which passages anchor each council's
  definitions.

**Why valuable:** These documents carry disproportionate apologetics weight. A query
like "which verses does the Council of Nicaea cite?" is unanswerable with any current
public tool.

## Phase 10 — Medieval Doctors

Goal: extend the corpus into the medieval period for Catholic and scholastic audiences.

**Sources (in priority order):**
1. *Summa Theologica* — Aquinas; dense Scripture citations in structured
   question/objection/reply format. NewAdvent HTML. Needs a custom parser.
2. *Exact Exposition of the Orthodox Faith* — John of Damascus; Eastern equivalent
   of the Summa, essential for Orthodox apologetics.
3. Anselm of Canterbury (*Cur Deus Homo*, *Proslogion*) — short works, available via
   CCEL.
4. Bernard of Clairvaux — considered the last Father by some traditions.

- [ ] Design a `corpus = medieval` schema extension to store the Summa's
  question/article structure alongside citation metadata.
- [ ] Write parsers for each source; the Summa parser is the most complex (distinguish
  *Sed contra* citations from *Respondeo* citations).
- [ ] Add author metadata for all medieval doctors.
- [ ] Update MCP tools to filter by corpus era (ante-nicene / nicene / medieval).

## Phase 11 — Reference Layer (CCC and Catholic Encyclopedia)

Goal: add modern authoritative documents as a *comparison layer*, not a citation corpus.

These sources are not citation corpora in the same sense—they are better used to
enrich and cross-reference the existing data.

**Catechism of the Catholic Church (CCC):**
- [ ] Parse CCC Scripture index to extract all cited passages.
- [ ] Add a query: *"Which verses does the CCC cite, and which Fathers also cited them?"*
  This surfaces patristic precedents for catechetical claims.
- [ ] Add a `ccc_cited` boolean column to the books/passages views.

**Catholic Encyclopedia (NewAdvent):**
- [ ] Do not parse as a citation corpus.
- [ ] Use as a metadata enrichment source: pull article summaries to annotate authors,
  works, and doctrinal topics in the existing database.
- [ ] Optionally surface links to relevant CE articles in the web UI author/work pages.

---

## Audience-Facing Features

These features depend on Track A (Phases 1–7) and can draw from any corpus available
at the time they are built. They are not blocked by corpus expansion.

---

## Phase 12 — Apologetics Tooling

Goal: direct support for the practical needs of apologists in debates and writing.

- [ ] **Proof-text lookup:** "Which Fathers cite John 1:1, in what works, and what is
  the surrounding context?" Returns passage text (from Phase 6), not just metadata.
- [ ] **Consensus view:** For a given verse, show what proportion of Fathers cite it
  and whether their usages agree — useful for demonstrating patristic consensus.
- [ ] **Counter-citation view:** Show Fathers whose usage of a passage differs from
  the majority — demonstrates genuine interpretive diversity where it exists.
- [ ] **Doctrinal topic tagging:** A small taxonomy (Trinity, Incarnation, Baptism,
  Eucharist, Petrine primacy, etc.) applied to works/citations, enabling queries like
  "citations of Psalm 110 in Trinitarian contexts."
- [ ] **Docker/devcontainer setup:** `docker compose up` parses texts, populates DB,
  and starts the web UI — reduces barrier to entry for non-technical apologists.

## Phase 13 — Theological Research Features

Goal: support academic theological analysis beyond simple citation counts.

- [ ] **Canonical development analysis:** Citation frequency per book plotted over
  time (by Father's century), showing which texts gained or lost authority during
  the ante-Nicene and Nicene periods.
- [ ] **Intertextual link detection:** Identify passage pairs that a Father cites
  together repeatedly (e.g., John 10:30 + John 17:21), revealing their own
  exegetical linkages.
- [ ] **Commentary vs. incidental distinction:** Flag citations where the surrounding
  ThML context indicates explicit commentary vs. passing quotation.
- [ ] **Original language provenance:** Note Greek vs. Latin source and link to Migne
  *Patrologia* references for Fathers working primarily in primary sources.
- [ ] **Reproducible notebook templates:** Expand Phase 3 notebooks into a documented
  library organized by research question type.

## Phase 14 — Laity-Facing Features

Goal: make the dataset accessible to faithful laypeople without technical or
academic training.

- [ ] **Plain-English topic search:** Given a topic (prayer, fasting, resurrection,
  Mary), return the most-cited scriptural passages and the Fathers who address them —
  no knowledge of OSIS codes required.
- [ ] **Liturgical calendar alignment:** Tag citations that correspond to passages used
  in traditional lectionaries (Roman Rite, Byzantine Divine Liturgy), so users can
  find patristic commentary on their Sunday readings.
- [ ] **Devotional reading plan export:** Generate a reading plan (e.g., "30 days of
  patristic citations on the Psalms") pulling the most-cited passages with surrounding
  Father text.
- [ ] **"Citation of the day" feed:** A daily highlight of one patristic citation with
  context, exportable as a social-media card or parish bulletin insert.
- [ ] **README stat badges:** Live citation count, number of Fathers covered, and
  verses cited — communicates dataset scale at a glance to potential users.
