# Engineering BOM Validation System

A Python tool comparing synthetic engineering and manufacturing BOM exports, flagging duplicate part numbers, missing parts, revision mismatches, and quantity discrepancies. Generates a formatted Excel discrepancy workbook.

## Run
```bash
pip install -r requirements.txt
python src/validate.py --engineering data/engineering.csv --manufacturing data/manufacturing.csv --output reports/bom_discrepancies.xlsx
pytest -q
```

Input CSV columns: `part_number,revision,quantity`. Part numbers are case-sensitive. Duplicate part numbers are reported; the last record is used for cross-source comparison.

**Limitations:** Single-level part-number comparison, synthetic data only, no live CAD/SAP/PLM integration. Not an engineering approval system.
