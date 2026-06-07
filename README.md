# Migration Economics Re-analysis

This repository is for re-analysing the data behind `dp16472.pdf`: Nam and Portes, *Migration and Productivity in the UK: An Analysis of Employee Payroll Data*.

## Get the Data

Source data files are not committed to git. Download and verify them with:

```sh
bash scripts/download_sources.sh
```

The files will be written to `data/sources/`. Source URLs, notes, and checksums are documented in `data/sources/SOURCES.md`.

## Python Environment

This project uses `uv` for Python dependency management:

```sh
uv sync
```

## Extract Analysis Tables

After downloading the sources, extract tidy CSV and Parquet tables with:

```sh
uv run python scripts/extract_sources.py
```

Outputs are written to `data/processed/`:

- `hmrc_payrolled_employments_2021.csv` / `.parquet`
- `hmrc_payrolled_employments_2022.csv` / `.parquet`
- `ons_labour_productivity_by_region_industry.csv` / `.parquet`
- `ons_paye_rti_nuts1_by_nationality.csv` / `.parquet`

The extracts are long-form tables intended for pandas, statsmodels, or similar statistical analysis workflows.

The extractor preserves original source labels and adds canonical join columns so related tables can be merged despite naming differences between HMRC and ONS workbooks:

- `region_code` / `region_canonical` use standard UK country and NUTS1-style region labels.
- `industry_code` / `industry_canonical` use SIC 2007 section codes `A` to `U`, plus `TOTAL` for whole-economy rows.
- `nationality_code` / `nationality_canonical` harmonise `UK`, `EU`, `NON_EU`, and `TOTAL` groups where nationality is present.

Extraction fails with a list of unmapped labels if a source workbook contains a region, industry, or nationality label that cannot be assigned to a canonical key.
