# AGENTS.md

Guidance for coding agents working in this repository.

## Repository Context

This repository is trying to re-analyse data from a paper regarding the impact of migration on the economy.

## Commands

Use `uv` for the Python environment.

- Install/sync dependencies: `uv sync`
- Download source workbooks: `bash scripts/download_sources.sh`
- Extract analysis tables: `uv run python scripts/extract_sources.py`
- Lint Python: `uv run ruff check .`

## File Handling

- Use `rg` or `rg --files` for discovery when available.
- For large documents, read or process them in chunks.
- Preserve filenames and document metadata unless the task requires changes.
- Source workbooks live in `data/sources/` and are not committed.
- Generated CSV/Parquet extracts live in `data/processed/` and are not committed.

## Change Verification

For documentation-only changes, verify by reviewing the edited file.
For extraction code changes, run `uv run python scripts/extract_sources.py` and `uv run ruff check .`.
Run the narrowest relevant checks first, then broader checks when the change affects shared behavior.
