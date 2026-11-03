"""Compare synthetic engineering and manufacturing BOM exports."""
import argparse
import csv
from collections import Counter
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

REQUIRED = {"part_number", "revision", "quantity"}

def read_bom(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing required columns in {path}: {sorted(REQUIRED - set(reader.fieldnames or []))}")
        rows = list(reader)
    for i, row in enumerate(rows, 2):
        row["part_number"] = row["part_number"].strip()
        row["revision"] = row["revision"].strip()
        if not row["part_number"]:
            raise ValueError(f"Blank part number at row {i}")
        try:
            row["quantity"] = int(row["quantity"])
        except (ValueError, TypeError):
            raise ValueError(f"Invalid quantity at row {i}") from None
        if row["quantity"] <= 0:
            raise ValueError(f"Quantity must be positive at row {i}")
    return rows

def compare(engineering, manufacturing):
    errors = []
    for side, rows in (("engineering", engineering), ("manufacturing", manufacturing)):
        counts = Counter(x["part_number"] for x in rows)
        for part, count in sorted(counts.items()):
            if count > 1:
                errors.append({"part_number":part,"issue":"DUPLICATE_PART","engineering":"" if side=="manufacturing" else count,"manufacturing":count if side=="manufacturing" else "","detail":f"{side}: {count} rows"})
    e = {x["part_number"]:x for x in engineering}
    m = {x["part_number"]:x for x in manufacturing}
    for part in sorted(e.keys() | m.keys()):
        a,b=e.get(part),m.get(part)
        if a is None or b is None:
            errors.append({"part_number":part,"issue":"MISSING_IN_ENGINEERING" if a is None else "MISSING_IN_MANUFACTURING","engineering":"present" if a else "missing","manufacturing":"present" if b else "missing","detail":""})
            continue
        for field,issue in (("revision","REVISION_MISMATCH"),("quantity","QUANTITY_MISMATCH")):
            if a[field] != b[field]:
                errors.append({"part_number":part,"issue":issue,"engineering":a[field],"manufacturing":b[field],"detail":field})
    return errors

def excel_report(errors, output):
    wb=Workbook();ws=wb.active;ws.title="Discrepancies"
    cols=["part_number","issue","engineering","manufacturing","detail"]
    ws.append([c.replace('_',' ').title() for c in cols])
    for item in errors: ws.append([item.get(c,"") for c in cols])
    ws.freeze_panes="A2";ws.auto_filter.ref=ws.dimensions
    for cell in ws[1]: cell.font=Font(color="FFFFFF",bold=True);cell.fill=PatternFill("solid",fgColor="17365D")
    for col,width in {"A":22,"B":30,"C":20,"D":20,"E":36}.items():ws.column_dimensions[col].width=width
    summary=wb.create_sheet("Summary");summary.append(["Metric","Value"]);summary.append(["Total discrepancies",len(errors)])
    for issue,count in sorted(Counter(e["issue"] for e in errors).items()):summary.append([issue,count])
    summary.column_dimensions['A'].width=32;summary.column_dimensions['B'].width=18
    Path(output).parent.mkdir(parents=True,exist_ok=True);wb.save(output)

def main():
    p=argparse.ArgumentParser();p.add_argument('--engineering',required=True);p.add_argument('--manufacturing',required=True);p.add_argument('--output',default='reports/bom_discrepancies.xlsx');a=p.parse_args()
    errors=compare(read_bom(a.engineering),read_bom(a.manufacturing));excel_report(errors,a.output)
    print(f"{len(errors)} discrepancies; report: {a.output}")
if __name__=='__main__':main()
