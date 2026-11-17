# Engineering BOM Validation System

**Engineering BOM reconciliation · Configuration data integrity · Revision comparison · Discrepancy reporting**

## Project overview

The Engineering BOM Validation System is a Python command-line application that compares engineering and manufacturing bill of materials (BOM) exports to identify inconsistencies in part identification, revision, and quantity data.

Engineering and manufacturing BOMs represent related but distinct views of product information. Differences between their exported records can require investigation before the information is used in downstream planning or configuration reviews. This application provides a repeatable, record-level comparison and produces an Excel discrepancy workbook that identifies items requiring review.

The demonstration uses synthetic CSV datasets. It is an offline validation tool, not an enterprise PLM or production release system.

## Validation workflow

1. **Load engineering and manufacturing exports.** Read two CSV files using the same required fields: `part_number`, `revision`, and `quantity`.
2. **Validate input records.** Confirm required columns, nonblank part numbers, valid integer quantities, and quantities greater than zero.
3. **Identify duplicate part records.** Report part numbers appearing multiple times within either source.
4. **Reconcile part coverage.** Identify part numbers present in one source but absent from the other.
5. **Compare shared records.** Flag differences in revision identifiers and quantities for matching part numbers.
6. **Generate an Excel report.** Produce a detailed discrepancy worksheet and an issue-count summary for engineering review.

The output identifies data exceptions; it does not determine which BOM is authoritative or automatically resolve conflicts.

## Implemented validation rules

| Validation area | Rule | Reported issue |
|---|---|---|
| File structure | Each CSV must include `part_number`, `revision`, and `quantity` | Invalid input raises an error |
| Part identification | Part number must not be blank | Invalid input raises an error |
| Quantity integrity | Quantity must be a positive integer | Invalid input raises an error |
| Duplicate records | A part number occurs more than once within one BOM | `DUPLICATE_PART` |
| BOM completeness | Part appears in manufacturing but not engineering | `MISSING_IN_ENGINEERING` |
| BOM completeness | Part appears in engineering but not manufacturing | `MISSING_IN_MANUFACTURING` |
| Revision alignment | Matching part numbers have different revision values | `REVISION_MISMATCH` |
| Quantity alignment | Matching part numbers have different quantities | `QUANTITY_MISMATCH` |

Part-number matching is case-sensitive. Revision values are compared directly as strings; the tool does not validate the revision against a released baseline.

**Duplicate handling:** Duplicate part numbers are reported as exceptions. During cross-source comparison, the program constructs a dictionary keyed by part number, so the *last occurrence* of a duplicate is used for its revision and quantity comparison. It does not aggregate duplicate quantities or automatically choose an approved record.

## Demonstration dataset

The repository includes two synthetic BOM exports:

- `data/engineering.csv` — five engineering part records.
- `data/manufacturing.csv` — six manufacturing rows, including a duplicate part number.

The sample deliberately includes a part present only in engineering, a part present only in manufacturing, duplicate manufacturing entries, and revision and quantity differences for a shared part.

This dataset exercises all five discrepancy classifications and demonstrates the comparison results without using confidential engineering or employer data.

## Excel report

The generated workbook contains two worksheets.

### Discrepancies

Each reported exception has the following fields:

| Field | Description |
|---|---|
| Part Number | Part identifier associated with the discrepancy |
| Issue | Standardized discrepancy classification |
| Engineering | Engineering-side value, presence indicator, or duplicate count |
| Manufacturing | Manufacturing-side value, presence indicator, or duplicate count |
| Detail | Field or source-specific information describing the exception |

The worksheet includes a formatted header, frozen header row, autofilter, and fixed column widths for easier review.

### Summary

The summary worksheet displays the total number of discrepancy findings and a count for each detected issue category. The total represents **findings**, not necessarily unique affected parts: a single part can generate multiple findings.

## Run the demonstration

The application uses Python, `openpyxl` for workbook generation, and `pytest` for automated tests.

```bash
python -m pip install -r requirements.txt

python src/validate.py \
  --engineering data/engineering.csv \
  --manufacturing data/manufacturing.csv \
  --output reports/bom_discrepancies.xlsx

pytest -q
```

Both input files must contain:

```text
part_number,revision,quantity
```

The output workbook is saved to `reports/bom_discrepancies.xlsx` in the example. The application creates the destination directory when needed.

## Repository structure

```text
data/
  engineering.csv        Synthetic engineering BOM
  manufacturing.csv      Synthetic manufacturing BOM
src/
  validate.py            CSV validation, BOM comparison, and Excel reporting
tests/
  test_validate.py       Automated reconciliation and report-creation tests
requirements.txt         Python dependencies
README.md                Project documentation
```

## Automated tests

The repository includes tests that:

- Confirm the demonstration inputs produce all five expected discrepancy types.
- Verify that the application creates an Excel report file.
- Confirm that identical single-record BOM inputs produce no discrepancies.

The code also contains input validation rules that are not individually covered by the current test suite.

## Engineering configuration relevance

The comparison illustrates foundational engineering configuration and master-data controls:

- **BOM reconciliation:** Identifies differences between engineering and manufacturing part lists.
- **Revision traceability:** Surfaces inconsistent revision attributes associated with the same part number.
- **Configuration data quality:** Flags missing parts, duplicate identifiers, and inconsistent quantities.
- **Exception management:** Provides a standardized discrepancy list for engineering or manufacturing review.
- **Status reporting:** Summarizes the number and classification of detected discrepancies.
- **Repeatable analysis:** Applies the same comparison logic to similarly structured exports.

The process can support a preliminary configuration-data review, but discrepancies require investigation against approved source records and the organization's change-control procedures before any configuration decision is made.

## Scope and limitations

This project is a single-level, offline BOM comparison and reporting demonstration.

- No direct connections to Creo, Windchill, SAP, or other CAD/PLM/ERP environments.
- No assembly hierarchy, multi-level BOM explosion, or parent-child quantity rollups.
- No interpretation of approved engineering change orders, release statuses, effectivity dates, or configuration baselines.
- No automated reconciliation decisions, engineering sign-off, or production release.
- No part-number normalization; comparisons remain case-sensitive.
- Duplicate part numbers are flagged, but the last matching row is used for cross-source comparisons.
- No verification that one source is authoritative or that a BOM difference is necessarily an error.
- Sample inputs are synthetic and do not contain employer information.

## Potential enhancements

Additional functionality could include multi-level BOM hierarchy comparison, baseline-aware revision validation, explicit duplicate resolution rules, change-order references, discrepancy disposition tracking, and comparisons across multiple configuration versions. These capabilities are not implemented in the current repository.

## Related projects

[Engineering Change & Revision Tracker](https://github.com/YSayaovong/Engineering-Change-Revision-Tracker) · [Creo CAD Configuration Validation Toolkit](https://github.com/YSayaovong/Creo-CAD-Application-Support-Toolkit)
