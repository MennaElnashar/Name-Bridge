# Independent labelling check

**Why.** The 50 gold labels (29 on the first set, 21 on the hard set) were written by the same author as the policy, so "29 of 29" only shows the code agrees with that author. This check asks a person who did not write the policy to answer a sample blind.

**What is in the sheet.** 24 candidate pairs sampled with a fixed seed from the 58 pairs the policy produces on both data sets (8 likely_match, 6 likely_different, 10 needs_review; 13 from the first set, 11 from the hard set). For each pair the reviewer sees only name, email, student ID and organization, in shuffled order and with A and B randomly swapped. The policy's answer, the gold label, the ground-truth entity id and the free-text note are hidden.

**What the reviewer answers.** "Same person", "Different people" or "Cannot tell", which map to likely_match, likely_different and needs_review.

## Files
| File | Give to the reviewer? |
|---|---|
| `labelling_sheet.xlsx` | Yes. Excel sheet with an instructions tab and a dropdown on the answer column |
| `labelling_sheet_printable.pdf` | Yes. The same 24 pairs to fill in by hand or on a phone |
| `labelling_sheet.csv` | Yes, if they prefer plain text |
| `answer_key.csv` | **No.** It holds the policy and gold answers |

The reviewer should not open the app or the repository first (the sheet says so).

## How to score it
```
python -m src.labelling score path\to\completed_sheet.xlsx     # or the .csv
```
It prints, and writes to `outputs/human_label_results.json`: how many answers agree with the policy and with the gold labels, every disagreement, where the reviewer said "same" and the policy said "different" (or the reverse), and how often the policy made a firm call where the reviewer said "cannot tell". If the reviewer used the PDF, copy their answers into the `Your answer` column of the CSV first.

## How to read the result
Agreement with the policy shows the policy's three-way calls look sensible to a second person; it does not prove accuracy. Disagreements are the useful part: each one is a case where the author's judgement and a second person's differ, and should be discussed in `docs/retrospective.md`. With 24 pairs and one reviewer, treat it as a spot check.

## Status
Answered once, on 16 October 2026, by the project owner from the sheet alone. That is a second pass by the person who directed the project and knows its rules, **not an independent review**; nobody outside the project has answered it yet.
- `completed/owner_as_returned.csv` is the file exactly as returned (answers "same" and "different").
- `completed/owner_cannot_tell_applied.csv` is the version that was scored: six answers (P04, P06, P07, P13, P17, P20) whose comment said "data is missing" were counted as "Cannot tell", which the owner confirmed is what was meant. The original answers are kept in the "Original answer" column.
- Results are in `docs/evaluation_protocol.md` and `outputs/human_label_results.json`.
The scorer accepts natural wording ("same", "different", "unsure") as well as the dropdown values. Regenerate the sheet with `python -m src.labelling make` (needs `openpyxl`).
