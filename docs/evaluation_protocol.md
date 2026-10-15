# Evaluation protocol

Gold labels are checked against ground-truth entity ids by tests/test_gold_labels.py (an automated consistency check, not a human review).

Reproduce: `python -m src.evaluate` and `python -m src.stress` (writes outputs/eval_results.json and outputs/stress_results.json). Pre-change snapshots: outputs/eval_before_day4.json, outputs/stress_day4.json.

## Data
- data/synthetic_names.csv: 42 invented records (columns record_id, name, email, student_id, org, note, entity_id). entity_id is ground truth and is never given to the matcher.
- data/gold_pairs.csv: 29 hand-labelled pairs with the expected recommendation and a category. Labels were written before the first run, from the policy rules in the plan (not from system output).
- Stress set: 120 distinct people generated from 30 first names and 30 surnames (seed 7), no identifiers.

## Strategies
- naive_name_only: similarity above 80 means likely_match. A deliberate strawman for hypothesis 1.
- baseline_conservative: the phase 2 baseline (word boundaries kept).
- experimental_aggressive / final_default_config: the phase 4 redesign (spacing and vowel folding).

## Metrics
False merges (likely_match across different entities); false splits (likely_different within one entity); true same-person pairs never surfaced; gold review pairs given false certainty; gold agreement; candidates not in gold; names preserved byte for byte.

## Results (similarity backend: RapidFuzz 3.14.6; identical to the earlier pure-python Indel ratio run)
| Strategy | Gold agreement | False merges | True pairs not surfaced | Review pairs given false certainty |
|---|---|---|---|---|
| naive_name_only | 2/29 | 8 | 7/18 | 12/17 |
| baseline_conservative | 20/29 | 0 | 3/18 | 0/17 |
| final (aggressive) | 29/29 | 0 | 0/18 | 0/17 |

Threshold sweep (gold agreement out of 29): conservative 24, 23, 20, 17, 12 at thresholds 70, 75, 80, 85, 90. Aggressive 29, 29, 29, 26, 24; at 70 it also produced 2 candidate pairs outside the gold set.

Homonym stress (120 different people, no identifiers): conservative flagged 37 pairs, aggressive 49 (+32%).

## Model comparison: no results
src/llm_review.py (10 guard tests) and src/compare_models.py (stub-model test) exist. The planned model, Qwen/Qwen2.5-1.5B-Instruct on CPU (Intel Core Ultra 5 235U, 31 GB RAM, torch 2.14.1+cpu, transformers 5.19.0), could not be downloaded: huggingface.co returned 403 through the network proxy, and no mirror was used. The script also accepts a local model folder, loaded offline (checked end to end with a tiny random model, whose output was discarded). So there are no model numbers: no false-merge, abstention or timing comparison. The script reports, for guarded review, accepted, rejected and downgraded outputs and time per pair, and for names-only prompting, how often the model says SAME on different people (hypothesis 3). It writes outputs/model_comparison.json when run.

## Hard set (data/hard_cases.csv, data/hard_gold_pairs.csv)
36 records, 21 gold pairs, written after the design was frozen; the policy was not changed in response. Categories: ibn/bin variants, Arabic script versus Latin, diacritics, nickname, dropped Al, email case and id whitespace, three-way variants, ids reused by different people, a misleading note.
| Strategy | Gold agreement | False merges | True pairs not surfaced | Candidates outside gold |
|---|---|---|---|---|
| naive_name_only | 7/21 | 10 | 4 | 2 |
| final_default_config | 21/21 | 1 (115/116) | 0 | 8 |
The false merge is two different people with similar names and the same student id: the policy trusts one matching unique identifier. The gold label for that pair follows the policy, and the audit test lists it as a documented exception. The 8 outside-gold candidates are pairs of different people with similar names; none is likely_match. Raw output: outputs/hard_results.json.

## Limits of this evidence
Small synthetic set written by the same author as the labels and the fix; 29/29 is expected after a fix aimed at those cases and is not evidence of generalization. The first run used a pure-python implementation of the fuzz.ratio definition; re-running `python -m src.evaluate` and `python -m src.stress` with real RapidFuzz 3.14.6 gave the same gold agreement, false merges, threshold sweep and homonym workload numbers. Unit tests (33) pass under unittest.
