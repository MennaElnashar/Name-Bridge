# data/

Synthetic data only: every name, email and ID is invented.

| File | Rows | What it is |
|---|---|---|
| `synthetic_names.csv` | 42 records | The first evaluation set. Columns: `record_id, name, email, student_id, org, note, entity_id` |
| `gold_pairs.csv` | 29 pairs | Hand-written expected answer for each pair: `record_id_a, record_id_b, gold, category`. Written from the policy rules before the first run |
| `hard_cases.csv` | 36 records | The harder second set (Arabic-script name, diacritics, a nickname, `ibn`/`bin`, dropped "Al", email case and ID whitespace differences, a misleading note, two different people sharing a student ID). Same columns as the first set. UTF-8 |
| `hard_gold_pairs.csv` | 21 pairs | Expected answers for the hard set. Pair 115/116 follows the policy although the ground truth says different people; this is documented, not hidden |

`entity_id` is the ground truth (which real person a record belongs to). It is used only to score results and is never given to the matcher. The `note` column holds free text that the tool must ignore, for example "same person as record 25 (confirmed)", which is deliberately misleading.

Both gold files are checked against `entity_id` by `tests/test_gold_labels.py`. They were written by the same author as the policy, so agreement with them is not independent evidence; see [docs/evaluation_protocol.md](../docs/evaluation_protocol.md).