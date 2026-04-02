# AnteNiceneFathersDataAnalysis

Small starter project for analyzing Scripture citation patterns in the *Ante-Nicene Fathers* ThML corpus.

## What this currently does

The parser in `data_processer.py` scans one or more ThML/HTML volumes and extracts `<scripRef ...>` tags, then writes:

- Per-volume files (e.g., `outputs/references_long_volume_1.csv`)
- `outputs/references_long.csv` – one row per Scripture reference across all processed volumes
- `outputs/book_counts_by_author.csv` – frequency by Church Father (`author_id`) and Bible book across all processed volumes
- `outputs/book_counts_overall.csv` – overall frequency by Bible book across all processed volumes
- `outputs/book_counts_volume_comparison.csv` – canonical book list (including deuterocanonical books) with total and per-volume counts for Volumes 1–3
- `outputs/parse_diagnostics.csv` – parser coverage diagnostics for each input volume (total scripture reference tags from `<scripRef>` and `<scripCom>`, Bible/non-Bible split, multi-book `osisRef` tags, unexpected `osisRef` tag names, and exact duplicate rows removed)

## Quick start

```bash
python data_processer.py
```

By default, this processes:

- `texts/AnteNiceneVolume1.html`
- `texts/AnteNiceneVolume2.html`
- `texts/AnteNiceneVolume3.html`

Optional flags:

```bash
python data_processer.py --input texts/AnteNiceneVolume1.html --input texts/AnteNiceneVolume2.html --out-dir outputs
```

## Notes

- This is currently regex-streaming based (dependency-free).
- Parsing now runs across whole-file content so `<scripRef>` tags split across line breaks are still captured.
- Bible references are grouped as `new_testament`, `deuterocanonical`, or `old_testament_or_other`.
- Deuterocanonical/additional OSIS books are retained as distinct books in outputs (e.g., `AddDan`, `PrAzar`, `Sus`, `Bel`, `AddEsth`, `EpJer`) to preserve research visibility.
- `parse_diagnostics.csv` is intended as a quick integrity check to detect potential missed-reference patterns.
