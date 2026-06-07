#!/usr/bin/env python3
"""Extract source spreadsheets into tidy analysis-ready tables."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = ROOT / "data" / "sources"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "processed"

HMRC_2021 = "Payrolled_employments_in_the_UK_by_region__industry_and_nationality__July_2014_to_June_2021.xlsx"
HMRC_2022 = (
    "Payrolled_employments_in_the_UK_by_region__industry_and_nationality__from_July_2014_"
    "to_December_2022_Data_tables.ods"
)
ONS_PRODUCTIVITY = "ons_region_by_industry_labour_productivity_1998_to_2019_indbyreg.xls"
ONS_RTI_FILES = [
    "ons_mws_rti_data_seasonally_adjusted_march2021.xlsx",
    "ons_nuts1_by_nationality_nsa_and_sa_mar2022.xlsx",
    "ons_nuts1_by_nationality_nsa_and_sa_mar2023.xlsx",
]

SKIP_SHEETS = {
    "cover",
    "cover sheet",
    "contents",
    "notes",
    "warning sheet",
    "lookups",
    "changes",
    "index",
    "guidance",
}

REGION_ALIASES = {
    "east": ("E12000006", "East of England"),
    "east midlands": ("E12000004", "East Midlands"),
    "england": ("E92000001", "England"),
    "london": ("E12000007", "London"),
    "north east": ("E12000001", "North East"),
    "north west": ("E12000002", "North West"),
    "northern ireland": ("N92000002", "Northern Ireland"),
    "scotland": ("S92000003", "Scotland"),
    "south east": ("E12000008", "South East"),
    "south west": ("E12000009", "South West"),
    "united kingdom": ("K02000001", "United Kingdom"),
    "uk": ("K02000001", "United Kingdom"),
    "wales": ("W92000004", "Wales"),
    "west midlands": ("E12000005", "West Midlands"),
    "yorkshire and the humber": ("E12000003", "Yorkshire and The Humber"),
    "yorkshire and the humber region": ("E12000003", "Yorkshire and The Humber"),
    "yorkshire and the humber, region": ("E12000003", "Yorkshire and The Humber"),
}

INDUSTRY_SECTIONS = {
    "A": "Agriculture, forestry and fishing",
    "B": "Mining and quarrying",
    "C": "Manufacturing",
    "D": "Electricity, gas, steam and air conditioning supply",
    "E": "Water supply; sewerage, waste management and remediation activities",
    "F": "Construction",
    "G": "Wholesale and retail trade; repair of motor vehicles and motorcycles",
    "H": "Transportation and storage",
    "I": "Accommodation and food service activities",
    "J": "Information and communication",
    "K": "Financial and insurance activities",
    "L": "Real estate activities",
    "M": "Professional, scientific and technical activities",
    "N": "Administrative and support service activities",
    "O": "Public administration and defence; compulsory social security",
    "P": "Education",
    "Q": "Human health and social work activities",
    "R": "Arts, entertainment and recreation",
    "S": "Other service activities",
    "T": (
        "Activities of households as employers; undifferentiated goods- and services-producing "
        "activities of households for own use"
    ),
    "U": "Activities of extraterritorial organisations and bodies",
}

INDUSTRY_ALIASES = {
    "accommodation and food service activities": ("I", INDUSTRY_SECTIONS["I"]),
    "administrative and support services": ("N", INDUSTRY_SECTIONS["N"]),
    "agriculture forestry and fishing": ("A", INDUSTRY_SECTIONS["A"]),
    "all industries": ("TOTAL", "All industries"),
    "arts entertainment and recreation": ("R", INDUSTRY_SECTIONS["R"]),
    "construction": ("F", INDUSTRY_SECTIONS["F"]),
    "education": ("P", INDUSTRY_SECTIONS["P"]),
    "energy production and supply": ("D", INDUSTRY_SECTIONS["D"]),
    "finance and insurance": ("K", INDUSTRY_SECTIONS["K"]),
    "health and social work": ("Q", INDUSTRY_SECTIONS["Q"]),
    "households extraterritorial organisations and unknown entities": ("T_U", "Households, extraterritorial organisations and unknown entities"),
    "information and communication": ("J", INDUSTRY_SECTIONS["J"]),
    "manufacturing": ("C", INDUSTRY_SECTIONS["C"]),
    "mining and quarrying": ("B", INDUSTRY_SECTIONS["B"]),
    "other service activities": ("S", INDUSTRY_SECTIONS["S"]),
    "professional scientific and technical": ("M", INDUSTRY_SECTIONS["M"]),
    "public administration and defence social security": ("O", INDUSTRY_SECTIONS["O"]),
    "real estate": ("L", INDUSTRY_SECTIONS["L"]),
    "whole economy": ("TOTAL", "All industries"),
    "transportation and storage": ("H", INDUSTRY_SECTIONS["H"]),
    "total": ("TOTAL", "All industries"),
    "water supply sewerage and waste": ("E", INDUSTRY_SECTIONS["E"]),
    "wholesale and retail repair of motor vehicles": ("G", INDUSTRY_SECTIONS["G"]),
}

NATIONALITY_ALIASES = {
    "all": ("TOTAL", "Total"),
    "eu": ("EU", "EU"),
    "eu nationals": ("EU", "EU"),
    "non-eu": ("NON_EU", "Non-EU"),
    "non eu": ("NON_EU", "Non-EU"),
    "non-eu nationals": ("NON_EU", "Non-EU"),
    "total": ("TOTAL", "Total"),
    "uk": ("UK", "UK"),
    "uk nationals": ("UK", "UK"),
}

SHEET_REGION_OVERRIDES = {
    "UK_for_UK,EU_and_nonEU": "United Kingdom",
    "UK_for_EU14,EU8,EU2_&_Other_EU": "United Kingdom",
}

NATIONALITY_PATTERNS = [
    ("non-EU", re.compile(r"^(?:total\s+)?non[- ]?eu nationals employment counts", re.I)),
    ("EU", re.compile(r"^(?:total\s+)?eu nationals employment counts", re.I)),
    ("UK", re.compile(r"^(?:total\s+)?uk nationals employment counts", re.I)),
    ("Total", re.compile(r"^total employment counts", re.I)),
]


@dataclass(frozen=True)
class Output:
    name: str
    frame: pd.DataFrame


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def label_key(value: object) -> str:
    text = clean_text(value).casefold()
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def canonical_region(value: object) -> tuple[str, str]:
    label = clean_text(value)
    key = re.sub(r"^the\s+", "", label_key(label))
    return REGION_ALIASES.get(key, ("UNMAPPED", label))


def canonical_industry(value: object) -> tuple[str, str]:
    label = clean_text(value)
    alias = INDUSTRY_ALIASES.get(label_key(label))
    if alias:
        return alias
    if label.startswith("ABDE:"):
        return "ABDE", "Non-manufacturing production and agriculture"
    if label.startswith("G-J & L-T:"):
        return "G_J_L_T", "Services excluding finance"
    if label.startswith("S and T:"):
        return "S_T", "Other service activities and households as employers"
    match = re.match(r"^([A-U])(?:\b|\s*[-:–—])", label, flags=re.I)
    if not match:
        match = re.search(r"\(([A-U])\)", label, flags=re.I)
    if match:
        code = match.group(1).upper()
        return code, INDUSTRY_SECTIONS[code]
    return "UNMAPPED", label


def canonical_nationality(value: object) -> tuple[str, str]:
    label = clean_text(value)
    return NATIONALITY_ALIASES.get(label_key(label), ("UNMAPPED", label))


def add_canonical_columns(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    frame = frame.copy()
    if "region" in columns:
        regions = frame["region"].map(canonical_region)
        frame["region_code"] = regions.map(lambda item: item[0])
        frame["region_canonical"] = regions.map(lambda item: item[1])
    if "industry" in columns:
        industries = frame["industry"].map(canonical_industry)
        frame["industry_code"] = industries.map(lambda item: item[0])
        frame["industry_canonical"] = industries.map(lambda item: item[1])
    if "nationality_group" in columns:
        nationalities = frame["nationality_group"].map(canonical_nationality)
        frame["nationality_code"] = nationalities.map(lambda item: item[0])
        frame["nationality_canonical"] = nationalities.map(lambda item: item[1])
    return frame


def validate_canonical_columns(frame: pd.DataFrame, output_name: str) -> None:
    unmapped = []
    for code_column, label_column in [
        ("region_code", "region"),
        ("industry_code", "industry"),
        ("nationality_code", "nationality_group"),
    ]:
        if code_column not in frame:
            continue
        labels = sorted(frame.loc[frame[code_column] == "UNMAPPED", label_column].dropna().unique())
        if labels:
            unmapped.append(f"{code_column}: {', '.join(labels)}")
    if unmapped:
        details = "\n  - ".join(unmapped)
        raise ValueError(f"Unmapped labels in {output_name}:\n  - {details}")


def normalise_region_name(sheet_name: str, title: str = "") -> str:
    if sheet_name in SHEET_REGION_OVERRIDES:
        return SHEET_REGION_OVERRIDES[sheet_name]
    cleaned = clean_text(sheet_name).replace("_", " ").strip()
    if cleaned.isdigit() and title:
        match = re.search(r"in (.+?) by industry", title, flags=re.I)
        if match:
            return match.group(1).replace("the United Kingdom", "United Kingdom")
    return cleaned


def find_header_row(df: pd.DataFrame, label: str = "Date") -> int:
    for idx, value in df.iloc[:, 0].items():
        if clean_text(value).casefold() == label.casefold():
            return int(idx)
    raise ValueError(f"Could not find {label!r} header row")


def parse_hmrc_column(column_name: object) -> tuple[str, str]:
    name = clean_text(column_name)
    for nationality, pattern in NATIONALITY_PATTERNS:
        if pattern.search(name):
            industry = pattern.sub("", name).strip()
            industry = re.sub(r"^(?:in|industry)\s+", "", industry, flags=re.I).strip()
            return nationality, industry or "All Industries"
    return "Unknown", name


def coerce_value(value: object) -> tuple[float | pd.NA, str]:
    if pd.isna(value):
        return pd.NA, ""
    if isinstance(value, str):
        stripped = value.strip()
        if re.fullmatch(r"\[[A-Za-z]\]", stripped):
            return pd.NA, stripped
        value = stripped.replace(",", "")
    try:
        return float(value), ""
    except (TypeError, ValueError):
        return pd.NA, clean_text(value)


def extract_hmrc_workbook(path: Path, release: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    workbook = pd.ExcelFile(path)
    for sheet in workbook.sheet_names:
        if clean_text(sheet).casefold() in SKIP_SHEETS:
            continue
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
        header_idx = find_header_row(raw)
        title = clean_text(raw.iloc[0, 0])
        region = normalise_region_name(sheet, title)
        headers = raw.iloc[header_idx]
        data = raw.iloc[header_idx + 1 :].copy()
        data = data[data.iloc[:, 0].notna()]

        for col_idx in range(1, len(headers)):
            nationality, industry = parse_hmrc_column(headers.iloc[col_idx])
            if nationality == "Unknown":
                continue
            for _, record in data.iterrows():
                value, marker = coerce_value(record.iloc[col_idx])
                rows.append(
                    {
                        "source_file": path.name,
                        "source_release": release,
                        "source_sheet": sheet,
                        "region": region,
                        "date": record.iloc[0],
                        "nationality_group": nationality,
                        "industry": industry,
                        "payrolled_employments": value,
                        "disclosure_marker": marker,
                    }
                )

    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["payrolled_employments"] = pd.to_numeric(frame["payrolled_employments"], errors="coerce")
    frame = frame.dropna(subset=["date"]).reset_index(drop=True)
    return add_canonical_columns(frame, ("region", "industry", "nationality_group"))


def extract_ons_rti_workbook(path: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    workbook = pd.ExcelFile(path)
    for sheet in workbook.sheet_names:
        if clean_text(sheet).casefold() in SKIP_SHEETS:
            continue
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
        header_idx = find_header_row(raw)
        region_row = raw.iloc[header_idx - 1].ffill()
        nationality_row = raw.iloc[header_idx]
        data = raw.iloc[header_idx + 1 :].copy()
        data = data[data.iloc[:, 0].notna()]
        seasonality_text = " ".join(clean_text(v) for v in raw.iloc[:header_idx, 0].dropna())
        seasonally_adjusted = "non-seasonally" not in seasonality_text.casefold()

        for col_idx in range(1, len(nationality_row)):
            region = clean_text(region_row.iloc[col_idx])
            nationality = clean_text(nationality_row.iloc[col_idx])
            if not region or not nationality:
                continue
            for _, record in data.iterrows():
                value, marker = coerce_value(record.iloc[col_idx])
                rows.append(
                    {
                        "source_file": path.name,
                        "source_sheet": sheet,
                        "region": region,
                        "date": record.iloc[0],
                        "nationality_group": nationality,
                        "seasonally_adjusted": seasonally_adjusted,
                        "payrolled_employees": value,
                        "disclosure_marker": marker,
                    }
                )

    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["payrolled_employees"] = pd.to_numeric(frame["payrolled_employees"], errors="coerce")
    frame = frame.dropna(subset=["date"]).reset_index(drop=True)
    return add_canonical_columns(frame, ("region", "nationality_group"))


def extract_productivity_workbook(path: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    workbook = pd.ExcelFile(path)
    for sheet in workbook.sheet_names:
        if clean_text(sheet).casefold() in SKIP_SHEETS:
            continue
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
        region_idx = find_header_row(raw, "Units:") + 2
        industry_idx = region_idx + 1
        region_row = raw.iloc[region_idx].ffill()
        industry_row = raw.iloc[industry_idx]
        data = raw.iloc[industry_idx + 1 :].copy()
        data = data[data.iloc[:, 0].notna()]
        unit = clean_text(raw.iloc[3, 1])
        table_title = clean_text(raw.iloc[0, 0])
        table_subtitle = clean_text(raw.iloc[1, 0])

        for col_idx in range(1, len(industry_row)):
            region = clean_text(region_row.iloc[col_idx])
            industry = clean_text(industry_row.iloc[col_idx])
            if not region or not industry:
                continue
            for _, record in data.iterrows():
                value, marker = coerce_value(record.iloc[col_idx])
                rows.append(
                    {
                        "source_file": path.name,
                        "source_sheet": sheet,
                        "measure": sheet,
                        "table_title": table_title,
                        "table_subtitle": table_subtitle,
                        "unit": unit,
                        "region": region,
                        "year": record.iloc[0],
                        "industry": industry,
                        "value": value,
                        "disclosure_marker": marker,
                    }
                )

    frame = pd.DataFrame(rows)
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["year"]).reset_index(drop=True)
    return add_canonical_columns(frame, ("region", "industry"))


def write_output(output: Output, output_dir: Path) -> None:
    validate_canonical_columns(output.frame, output.name)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{output.name}.csv"
    parquet_path = output_dir / f"{output.name}.parquet"
    output.frame.to_csv(csv_path, index=False)
    output.frame.to_parquet(parquet_path, index=False)
    print(f"{output.name}: {len(output.frame):,} rows -> {csv_path} and {parquet_path}")


def required_sources(source_dir: Path) -> list[Path]:
    return [source_dir / name for name in [HMRC_2021, HMRC_2022, ONS_PRODUCTIVITY, *ONS_RTI_FILES]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    missing = [path for path in required_sources(args.source_dir) if not path.exists()]
    if missing:
        names = "\n".join(f"  - {path}" for path in missing)
        raise SystemExit(f"Missing source files. Run scripts/download_sources.sh first:\n{names}")

    outputs = [
        Output("hmrc_payrolled_employments_2021", extract_hmrc_workbook(args.source_dir / HMRC_2021, "2021")),
        Output("hmrc_payrolled_employments_2022", extract_hmrc_workbook(args.source_dir / HMRC_2022, "2022")),
        Output("ons_labour_productivity_by_region_industry", extract_productivity_workbook(args.source_dir / ONS_PRODUCTIVITY)),
        Output(
            "ons_paye_rti_nuts1_by_nationality",
            pd.concat(
                [extract_ons_rti_workbook(args.source_dir / file_name) for file_name in ONS_RTI_FILES],
                ignore_index=True,
            ),
        ),
    ]

    for output in outputs:
        write_output(output, args.output_dir)


if __name__ == "__main__":
    main()
