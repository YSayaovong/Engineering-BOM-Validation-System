"""Regression tests for the synthetic single-level BOM validator."""
import csv
import subprocess
import sys
from pathlib import Path

import pytest
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from validate import compare, excel_report, main, read_bom


@pytest.fixture
def sample_rows():
    return (
        read_bom(ROOT / "data" / "engineering.csv"),
        read_bom(ROOT / "data" / "manufacturing.csv"),
    )


def write_csv(path, rows, fieldnames=("part_number", "revision", "quantity")):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_sample_discrepancies(sample_rows):
    findings = compare(*sample_rows)
    assert {f["issue"] for f in findings} == {
        "DUPLICATE_PART", "MISSING_IN_ENGINEERING",
        "MISSING_IN_MANUFACTURING", "REVISION_MISMATCH", "QUANTITY_MISMATCH",
    }
    assert len(findings) == 5


def test_equal_boms():
    row = {"part_number": "P1", "revision": "A", "quantity": 3}
    assert compare([row], [row]) == []


def test_duplicate_does_not_select_last_record():
    engineering = [
        {"part_number": "P1", "revision": "A", "quantity": 1},
        {"part_number": "P1", "revision": "C", "quantity": 9},
    ]
    manufacturing = [{"part_number": "P1", "revision": "B", "quantity": 7}]
    findings = compare(engineering, manufacturing)
    assert [f["issue"] for f in findings] == ["DUPLICATE_PART"]


def test_duplicate_only_in_manufacturing():
    row = {"part_number": "P1", "revision": "A", "quantity": 1}
    findings = compare([row], [row, row])
    assert [f["issue"] for f in findings] == ["DUPLICATE_PART"]


def test_duplicate_part_missing_from_other_side():
    row = {"part_number": "P1", "revision": "A", "quantity": 1}
    findings = compare([row, row], [])
    assert [f["issue"] for f in findings] == [
        "DUPLICATE_PART", "MISSING_IN_MANUFACTURING",
    ]


@pytest.mark.parametrize("quantity", ["", "0", "-1", "1.2", "1e2", "abc"])
def test_invalid_quantities(tmp_path, quantity):
    path = write_csv(tmp_path / "invalid.csv", [
        {"part_number": "P1", "revision": "A", "quantity": quantity}
    ])
    with pytest.raises(ValueError):
        read_bom(path)


@pytest.mark.parametrize("field", ["part_number", "revision"])
def test_blank_mandatory_fields(tmp_path, field):
    row = {"part_number": "P1", "revision": "A", "quantity": "1"}
    row[field] = " "
    with pytest.raises(ValueError):
        read_bom(write_csv(tmp_path / "invalid.csv", [row]))


def test_missing_columns(tmp_path):
    with pytest.raises(ValueError, match="missing required columns"):
        read_bom(write_csv(
            tmp_path / "bad.csv", [{"part_number": "P1", "quantity": "1"}],
            fieldnames=("part_number", "quantity"),
        ))


def test_duplicate_headers(tmp_path):
    path = tmp_path / "headers.csv"
    path.write_text("part_number,revision,revision,quantity\nP1,A,A,1\n")
    with pytest.raises(ValueError, match="duplicate CSV column"):
        read_bom(path)


def test_extra_csv_field(tmp_path):
    path = tmp_path / "extra.csv"
    path.write_text("part_number,revision,quantity\nP1,A,1,EXTRA\n")
    with pytest.raises(ValueError, match="extra CSV fields"):
        read_bom(path)


def test_empty_bom_rejected(tmp_path):
    with pytest.raises(ValueError, match="no BOM records"):
        read_bom(write_csv(tmp_path / "empty.csv", []))


def test_valid_quantity_and_whitespace(tmp_path):
    path = write_csv(tmp_path / "valid.csv", [
        {"part_number": " P1 ", "revision": " A ", "quantity": " 0003 "}
    ])
    assert read_bom(path) == [{"part_number": "P1", "revision": "A", "quantity": 3}]


def test_report_content_and_summary(tmp_path, sample_rows):
    findings = compare(*sample_rows)
    output = tmp_path / "reports" / "result.xlsx"
    excel_report(findings, output)
    book = load_workbook(output)
    try:
        assert book.sheetnames == ["Discrepancies", "Summary"]
        assert book["Discrepancies"].max_row == len(findings) + 1
        assert book["Discrepancies"].freeze_panes == "A2"
        summary = dict(list(book["Summary"].values)[1:])
        assert summary["Total discrepancies"] == 5
        assert all(summary[issue] == 1 for issue in {
            "DUPLICATE_PART", "MISSING_IN_ENGINEERING",
            "MISSING_IN_MANUFACTURING", "REVISION_MISMATCH", "QUANTITY_MISMATCH"
        })
    finally:
        book.close()


@pytest.mark.parametrize("value", ["=1+1", "+SUM(1,1)", "-2+3", "@SUM(A1)"])
def test_report_escapes_formula_injection(tmp_path, value):
    finding = {
        "part_number": value, "issue": "REVISION_MISMATCH",
        "engineering": "A", "manufacturing": "B", "detail": "revision",
    }
    output = tmp_path / "safe.xlsx"
    excel_report([finding], output)
    book = load_workbook(output)
    try:
        cell = book["Discrepancies"]["A2"]
        assert cell.data_type != "f"
        assert cell.value == "'" + value
    finally:
        book.close()


def test_cli_default_files(tmp_path):
    output = tmp_path / "sample.xlsx"
    assert main(["--output", str(output)]) == 0
    assert output.exists()


def test_cli_missing_file_returns_failure(tmp_path, capsys):
    result = main([
        "--engineering", str(tmp_path / "missing.csv"),
        "--output", str(tmp_path / "report.xlsx"),
    ])
    assert result == 1
    assert "BOM validation error:" in capsys.readouterr().err


def test_cli_runs_from_another_directory(tmp_path):
    output = tmp_path / "result.xlsx"
    run = subprocess.run(
        [sys.executable, str(ROOT / "src" / "validate.py"), "--output", str(output)],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert run.returncode == 0, run.stderr
    assert output.exists()
