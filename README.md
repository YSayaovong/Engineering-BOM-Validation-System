# Engineering BOM Validation System

A Python tool comparing synthetic engineering and manufacturing BOM exports, flagging duplicate part numbers, missing parts, revision mismatches, and quantity discrepancies. Generates a formatted Excel discrepancy workbook.

## Run
```bash
pip install -r requirements.txt
python src/validate.py --engineering data/engineering.csv --manufacturing data/manufacturing.csv --output reports/bom_discrepancies.xlsx
pytest -q
```

Input CSV columns: `part_number,revision,quantity`. Part numbers are case-sensitive. A duplicate part number produces a review exception per affected source. Cross-source checks for that part resume once both exports have a single authoritative row per part. See the [requirements and acceptance criteria](docs/reconciliation-case-study.md).

**Limitations:** Single-level part-number comparison, synthetic data only, no live CAD/SAP/PLM integration. Not an engineering approval system.
