# AnteNiceneFathersDataAnalysis

Starter project for analyzing Scripture citation patterns in the *Ante-Nicene Fathers* ThML corpus, now structured as a reusable parsing/query pipeline that can serve future MCP tooling.

## Current capabilities

The CLI entry point (`data_processer.py`) orchestrates a modular pipeline under `anf_pipeline/`.

### Parsing + outputs

For each input volume, the parser extracts `<scripRef ...>` and `<scripCom ...>` tags and writes:

- Per-volume files (e.g., `outputs/references_long_volume_1.csv`)
- `outputs/references_long.csv` – legacy long format (one row per Bible reference)
- `outputs/references_structured.csv` – enriched format for downstream retrieval systems (volume, normalized OSIS book list, chapter/verse starts, etc.)
- `outputs/book_counts_by_author.csv` – frequency by Church Father (`author_id`) and Bible book
- `outputs/book_counts_overall.csv` – overall frequency by Bible book
- `outputs/book_counts_volume_comparison.csv` – canonical book list (incl. deuterocanonical books) with total and per-volume counts for Volumes 1–3
- `outputs/parse_diagnostics.csv` – parser coverage diagnostics

### Query preview mode (MCP-ready direction)

You can now run ad hoc filters against parsed in-memory references for rapid exploration and to prototype retrieval behavior for a future MCP server.

Supported filters:

- `--query-author`
- `--query-work`
- `--query-book`
- `--query-volume`
- `--query-limit`

## Quick start

```bash
python data_processer.py
```

Defaults to:

- `texts/AnteNiceneVolume1.html`
- `texts/AnteNiceneVolume2.html`
- `texts/AnteNiceneVolume3.html`

With explicit inputs:

```bash
python data_processer.py \
  --input texts/AnteNiceneVolume1.html \
  --input texts/AnteNiceneVolume2.html \
  --out-dir outputs
```

With query preview:

```bash
python data_processer.py --query-author Irenaeus --query-book John --query-limit 5
```

## Architecture

- `anf_pipeline/parsing.py` – ThML parsing + diagnostics
- `anf_pipeline/aggregation.py` – CSV writers + count builders
- `anf_pipeline/query.py` – composable in-memory filtering engine
- `anf_pipeline/models.py` – stable data models (`Reference`, `ParseReport`)
- `anf_pipeline/constants.py` – canon ordering and classification constants

This separation keeps your existing CSV analytics workflow intact while creating a cleaner foundation for:

1. richer schema design,
2. persistent storage/indexing layers,
3. MCP server endpoints optimized for theological/apologetic/critical querying.
