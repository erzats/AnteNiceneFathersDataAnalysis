# Roadmap to ANF Citation Question-Answering

This roadmap is aimed at getting the project to a reliable state where users can ask:

- Which Fathers quoted Tobit and where?
- Which Psalm was most frequently quoted?
- Which books were never quoted?
- Which Fathers quoted broadly but not from deuterocanonical books?

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

- [ ] Add validation checks for malformed OSIS references and ambiguous book IDs.
- [ ] Track quote confidence levels (exact citation vs probable allusion).
- [ ] Add regression fixtures for known edge cases per volume.
- [ ] Capture duplicate-reference rationale in diagnostics.

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
