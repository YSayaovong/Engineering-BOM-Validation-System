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


def test_duplicate_requires_review_before_comparison():
    engineering = [
        {"part_number": "X", "revision": "A", "quantity": 1},
        {"part_number": "X", "revision": "B", "quantity": 3},
        {"part_number": "Y", "revision": "A", "quantity": 1},
        {"part_number": "Y", "revision": "A", "quantity": 1},
    ]
    manufacturing = [
        {"part_number": "X", "revision": "C", "quantity": 8},
        {"part_number": "X", "revision": "D", "quantity": 10},
    ]
    issues = compare(engineering, manufacturing)
    assert [(x["part_number"], x["issue"]) for x in issues] == [
        ("X", "DUPLICATE_PART"),
        ("Y", "DUPLICATE_PART"),
        ("X", "DUPLICATE_PART"),
    ]
    assert issues == compare(list(reversed(engineering)), list(reversed(manufacturing)))
    assert issues[0]["engineering"] == issues[2]["manufacturing"] == 2
    resolved = compare(engineering[:1], manufacturing[:1])
    assert {x["issue"] for x in resolved} == {"REVISION_MISMATCH", "QUANTITY_MISMATCH"}
