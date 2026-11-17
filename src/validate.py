"""Validate synthetic engineering and manufacturing BOMs.

Single-level, case-sensitive part reconciliation for a demonstration dataset.
Does not integrate with an ERP/PLM system or approve engineering changes.
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

COLUMNS = ("part_number", "revision", "quantity")
ISSUE_COLUMNS = ("part_number", "issue", "engineering", "manufacturing", "detail")


def read_bom(path):
    """Read an input CSV; reject incomplete or malformed records."""
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError(f"{path}: duplicate CSV column names")
        missing = set(COLUMNS) - set(headers)
        if missing:
            raise ValueError(f"{path}: missing required columns: {sorted(missing)}")
        rows = []
        for line, record in enumerate(reader, start=2):
            if None in record:
                raise ValueError(f"{path}: extra CSV fields at record {line}")
            part = (record.get("part_number") or "").strip()
            revision = (record.get("revision") or "").strip()
            raw_quantity = (record.get("quantity") or "").strip()
            if not part:
                raise ValueError(f"{path}: blank part number at record {line}")
            if not revision:
                raise ValueError(f"{path}: blank revision at record {line}")
            if not re.fullmatch(r"[0-9]+", raw_quantity):
                raise ValueError(f"{path}: invalid integer quantity at record {line}")
            quantity = int(raw_quantity)
            if quantity <= 0:
                raise ValueError(f"{path}: quantity must be positive at record {line}")
            rows.append({"part_number": part, "revision": revision, "quantity": quantity})
    if not rows:
        raise ValueError(f"{path}: no BOM records found")
    return rows


def compare(engineering, manufacturing):
    """Report differences without choosing arbitrary duplicate source records."""
    findings = []
    e_groups = {}
    m_groups = {}
    for groups, rows, side in (
        (e_groups, engineering, "engineering"),
        (m_groups, manufacturing, "manufacturing"),
    ):
        for row in rows:
            groups.setdefault(row["part_number"], []).append(row)
        for part, matches in sorted(groups.items()):
            if len(matches) > 1:
                findings.append({
                    "part_number": part,
                    "issue": "DUPLICATE_PART",
                    "engineering": len(matches) if side == "engineering" else "",
                    "manufacturing": len(matches) if side == "manufacturing" else "",
                    "detail": f"{side}: {len(matches)} rows; comparison is ambiguous",
                })

    for part in sorted(e_groups.keys() | m_groups.keys()):
        e_matches = e_groups.get(part, [])
        m_matches = m_groups.get(part, [])
        if not e_matches or not m_matches:
            findings.append({
                "part_number": part,
                "issue": "MISSING_IN_ENGINEERING" if not e_matches else "MISSING_IN_MANUFACTURING",
                "engineering": "present" if e_matches else "missing",
                "manufacturing": "present" if m_matches else "missing",
                "detail": "",
            })
            continue
        # A duplicate source record cannot identify which revision or quantity is authoritative.
        if len(e_matches) != 1 or len(m_matches) != 1:
            continue
        eng, mfg = e_matches[0], m_matches[0]
        for field, issue in (
            ("revision", "REVISION_MISMATCH"),
            ("quantity", "QUANTITY_MISMATCH"),
        ):
            if eng[field] != mfg[field]:
                findings.append({
                    "part_number": part,
                    "issue": issue,
                    "engineering": eng[field],
                    "manufacturing": mfg[field],
                    "detail": field,
                })
    return findings


def safe_excel_value(value):
    """Avoid spreadsheet-formula interpretation for untrusted CSV strings."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def excel_report(findings, output):
    """Write exception-level and count-level Excel worksheets."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Discrepancies"
    sheet.append([column.replace("_", " ").title() for column in ISSUE_COLUMNS])
    for finding in findings:
        sheet.append([safe_excel_value(finding.get(field, "")) for field in ISSUE_COLUMNS])
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = PatternFill("solid", fgColor="17365D")
    for col, width in {"A": 22, "B": 30, "C": 20, "D": 20, "E": 44}.items():
        sheet.column_dimensions[col].width = width

    summary = workbook.create_sheet("Summary")
    summary.append(["Metric", "Value"])
    summary.append(["Total discrepancies", len(findings)])
    for issue, count in sorted(Counter(f["issue"] for f in findings).items()):
        summary.append([issue, count])
    summary.column_dimensions["A"].width = 32
    summary.column_dimensions["B"].width = 18

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(target)
    workbook.close()


def main(argv=None):
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--engineering", type=Path, default=project_root / "data" / "engineering.csv",
        help="Engineering BOM CSV (defaults to bundled synthetic example).",
    )
    parser.add_argument(
        "--manufacturing", type=Path, default=project_root / "data" / "manufacturing.csv",
        help="Manufacturing BOM CSV (defaults to bundled synthetic example).",
    )
    parser.add_argument(
        "--output", type=Path, default=project_root / "reports" / "bom_discrepancies.xlsx",
        help="Excel report destination.",
    )
    args = parser.parse_args(argv)
    try:
        findings = compare(read_bom(args.engineering), read_bom(args.manufacturing))
        excel_report(findings, args.output)
    except (OSError, ValueError, OverflowError) as exc:
        print(f"BOM validation error: {exc}", file=sys.stderr)
        return 1
    print(f"{len(findings)} discrepancies; report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
