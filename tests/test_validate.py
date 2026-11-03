import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from validate import compare, read_bom, excel_report

def test_detects_discrepancies(tmp_path):
    root=Path(__file__).resolve().parents[1]
    issues=compare(read_bom(root/'data/engineering.csv'),read_bom(root/'data/manufacturing.csv'))
    assert {x['issue'] for x in issues}=={'DUPLICATE_PART','MISSING_IN_ENGINEERING','MISSING_IN_MANUFACTURING','REVISION_MISMATCH','QUANTITY_MISMATCH'}
    excel_report(issues,tmp_path/'out.xlsx')
    assert (tmp_path/'out.xlsx').exists()

def test_equal_boms():
    row={'part_number':'X','revision':'A','quantity':1}
    assert compare([row],[row])==[]
