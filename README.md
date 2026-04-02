# AnteNiceneFathersDataAnalysis

Small starter project for analyzing Scripture citation patterns in the *Ante-Nicene Fathers* ThML corpus.

## What this currently does

The parser in `data_processer.py` scans a ThML/HTML volume and extracts `<scripRef ...>` tags, then writes:

- `outputs/references_long.csv` – one row per Scripture reference
- `outputs/book_counts_by_author.csv` – frequency by Church Father (`author_id`) and Bible book
- `outputs/book_counts_overall.csv` – overall frequency by Bible book

## Quick start

```bash
python data_processer.py
```

Optional flags:

```bash
python data_processer.py --input texts/AnteNiceneVolume1.html --out-dir outputs
```

## Notes

- This is currently regex-streaming based (dependency-free).
- Bible references are grouped as `new_testament`, `deuterocanonical`, or `old_testament_or_other`.
- The included sample file is Volume 1; add more volumes and run the same script on each file to grow your dataset.
