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

## Model comparison: one small model, one run
Run on 2026-10-15 with `python -m src.compare_models <folder>`. Raw output: `outputs/model_comparison.json`.

**Setup.** Qwen/Qwen2.5-0.5B-Instruct (the `main` files as downloaded on 2026-10-15; the commit hash was not recorded), float32 on CPU (Intel Core Ultra 5 235U, 31 GB RAM), torch 2.14.1+cpu, transformers 5.19.0, greedy decoding, a single run. The planned model was the 1.5B version; I switched to 0.5B because the 3 GB download ran at about 1 MB/s on this network. The 58 pairs are every candidate pair the final policy produces on the synthetic set (29) and the hard set (29). The model never saw `entity_id` or the free-text note.

**A. Guarded review** (the model explains a pair and `src/llm_review.py` checks it)
| Outcome | Pairs |
|---|---|
| Accepted (agreed with the policy) | 1 |
| Rejected, policy result used instead | 57 |
| of which: contradicted the policy | 32 |
| of which: missing JSON keys | 14 |
| of which: evidence not lists of strings | 9 |
| of which: invalid recommendation value | 2 |
| Upgrades over the policy that got through | 0 |

Time: 6.7 seconds per pair for the model, against milliseconds for the policy. The guard did its job: every unusable output was replaced by the deterministic result and none changed a recommendation. But a 0.5B model could not produce the required output reliably, so it added nothing here.

**B. Names only** (hypothesis 3: the model sees just two names and answers SAME, DIFFERENT or UNSURE)
| Truth | Pairs | said SAME | said UNSURE | unparsable |
|---|---|---|---|---|
| different people | 27 | 6 | 20 | 1 |
| same person | 31 | 9 | 20 | 2 |

The model mostly abstained (40 of 58 UNSURE), which is the right instinct. But 6 of its 15 SAME answers were wrong (40%). Two of those were identical names belonging to different people (Fatma Ibrahim, Omar Nabil), which no reading of a name can settle; the rest were one-letter variants (Hana/Hanan, Salma/Selma, Ahmed/Ahmad Hassan). On those same six pairs the policy answered likely_different three times and needs_review three times, never likely_match.

**Limits.** One very small model, one run, 58 pairs, prompts not tuned, no other model. A larger model could behave differently, so this says nothing about models in general. The hosted-API route was tried and was not possible: the Hugging Face account had no credits (HTTP 402), so `--remote` mode was only tested against a fake server and a real 402 response.
## Hard set (data/hard_cases.csv, data/hard_gold_pairs.csv)
36 records, 21 gold pairs, written after the design was frozen; the policy was not changed in response. Categories: ibn/bin variants, Arabic script versus Latin, diacritics, nickname, dropped Al, email case and id whitespace, three-way variants, ids reused by different people, a misleading note.
| Strategy | Gold agreement | False merges | True pairs not surfaced | Candidates outside gold |
|---|---|---|---|---|
| naive_name_only | 7/21 | 10 | 4 | 2 |
| final_default_config | 21/21 | 1 (115/116) | 0 | 8 |
The false merge is two different people with similar names and the same student id: the policy trusts one matching unique identifier. The gold label for that pair follows the policy, and the audit test lists it as a documented exception. The 8 outside-gold candidates are pairs of different people with similar names; none is likely_match. Raw output: outputs/hard_results.json.

## Independent labelling check (prepared, not yet answered)
All gold labels were written by the author of the policy. To get a second opinion, `python -m src.labelling make` builds a blind sheet of 24 candidate pairs (8 likely_match, 6 likely_different, 10 needs_review, sampled with seed 16 from both sets) showing only name, email, student ID and organization, with the policy answer, gold label, ground truth and free-text notes hidden. `python -m src.labelling score <file>` compares a reviewer's answers with the policy and the gold labels and writes `outputs/human_label_results.json`. Details and files are in `labelling/README.md`. No reviewer has answered it yet, so there are no results here, and every agreement figure above should still be read as agreement with the author's own labels.

## Limits of this evidence
Small synthetic set written by the same author as the labels and the fix; 29/29 is expected after a fix aimed at those cases and is not evidence of generalization. The first run used a pure-python implementation of the fuzz.ratio definition; re-running `python -m src.evaluate` and `python -m src.stress` with real RapidFuzz 3.14.6 gave the same gold agreement, false merges, threshold sweep and homonym workload numbers. Unit tests (40) pass under unittest.
