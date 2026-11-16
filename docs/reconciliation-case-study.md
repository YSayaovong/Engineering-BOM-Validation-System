# BOM reconciliation case study

## Decision

Before releasing an assembly, engineering and manufacturing need to agree on which parts, revisions, and quantities belong in the build. The analyst's job is to identify exceptions and give each team enough information to resolve them.

**Scope:** Synthetic, single-level exports. Each source has one authoritative row per part number. A repeated part number may be valid in a multilevel BOM, which is outside this case study.

| Rule | Acceptance criterion | Proposed follow-up |
| --- | --- | --- |
| BR-01 · Duplicate part | Two or more rows for a part in either source produce a duplicate exception for that source. The part is held from missing, revision, and quantity comparisons until resolved. Row order has no effect. | The owner of the affected source verifies the authoritative record, corrects the export, and reruns reconciliation. |
| BR-02 · Missing part | A unique part appearing in just one export produces a missing exception that identifies the absent source. | The engineering and manufacturing owners verify scope and release timing. |
| BR-03 · Revision mismatch | Unique records with the same part number and different revisions produce a revision exception. | Engineering confirms the revision approved for the build. |
| BR-04 · Quantity mismatch | Unique records with the same part number and different quantities produce a quantity exception. | Manufacturing verifies the planned quantity with engineering. |

In the included sample, CABLE-400 appears twice in the manufacturing export, so it is held for review. BOLT-200 is unique on both sides and produces separate revision and quantity exceptions. The workbook summary counts exception rows. A part may have several exceptions.

Run the sample from the [README](../README.md) and compare the workbook with the rules above. The automated tests cover the sample exceptions, a clean comparison, and duplicate routing, including order independence and comparison after correction.
