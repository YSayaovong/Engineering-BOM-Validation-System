# Engineering BOM Validation System

**Engineering configuration management | BOM reconciliation | Data quality**

A reproducible Python portfolio demonstration of a common manufacturing problem: engineering and manufacturing bills of materials disagree before release. The tool compares **synthetic** CSV exports and creates a formatted Excel discrepancy workbook for review.

## Business problem and approach
Discrepant part numbers, quantities and revisions can create downstream clarification and rework. This project provides a repeatable *screening* step, not an engineering approval or release decision.

1. Read two BOM exports with `part_number,revision,quantity`.
2. Identify duplicate part numbers and compare engineering versus manufacturing records.
3. Flag missing parts, revision mismatches and quantity discrepancies.
4. Export an Excel discrepancy workbook for a reviewer to investigate.

## Run locally
```bash
python -m pip install -r requirements.txt
python src/validate.py --engineering data/engineering.csv --manufacturing data/manufacturing.csv --output reports/bom_discrepancies.xlsx
pytest -q
```

**Review the output:** inspect the discrepancy workbook, verify each flagged record against its source, and document corrective actions in your organization's authorized change process.

## What this demonstrates
- BOM and engineering master-data validation
- Exception reporting and data reconciliation
- Repeatable Python workflows and automated testing
- Engineering configuration review concepts

## Known limitations
- Synthetic sample data; **no employer data**
- Single-level part-number comparison, not a multi-level assembly explosion
- Part numbers are case-sensitive
- Duplicate part numbers are flagged, but the **last** occurrence is used for cross-source comparison
- No live Creo, SAP or PLM connection; no engineering sign-off or production release capability

## Portfolio context
Relevant to **Engineering Configuration Analyst**, **Engineering Change Analyst**, and **Engineering Master Data Analyst** roles. This is a demonstration of methods, not a claim of measured workplace savings or production deployment.

[View related engineering change workflow](https://github.com/YSayaovong/Engineering-Change-Revision-Tracker) · [Portfolio website repository](https://github.com/YSayaovong/operations-analytics-portfolio)
