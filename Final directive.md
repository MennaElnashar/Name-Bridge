# NameBridge: Final Directive

Operating rules for the tool and for any AI assistant working on it. Finalized from what the evaluation actually showed (see docs/retrospective.md).

## 1. Objective
Help a human decide whether records with differently spelled Latin-script Arabic names refer to the same person, while stating how much evidence supports each recommendation. Never decide identity on behalf of the user.

## 2. Similarity is not evidence
- Name similarity only decides whether a pair is worth looking at (candidate generation).
- Only identifiers count as identity evidence: unique identifiers (email, student ID) and, weakly, context (organization).
- Evidence observed in testing: a name-only rule produced 8 false merges on the synthetic set and 10 on the hard set; the identifier policy produced 0 on the synthetic set and 1 on the hard set (two different people sharing one student ID, pair 115/116). One matching identifier is therefore strong but not proof.
- Free-text notes, comments and "confirmed" claims are never evidence.

## 3. Decision rules (src/policy.py)
1. Names similar and a unique identifier matches and none conflict: likely_match. This is a recommendation for a human to confirm, not an identity decision: identifiers can be reused or shared (known false merge, hard set 115/116).
2. Names similar and a unique identifier conflicts and none match: likely_different.
3. A unique identifier matches while another unique identifier conflicts: needs_review (shared or reused identifiers exist).
4. Names similar, no corroborating or conflicting identifier: needs_review.
5. Names differ but a unique identifier matches: needs_review. Investigate; never silently merge.
6. Identical names with distinct unique identifiers: not assumed to be the same person.
7. Organization differences alone never make records different; they are reported only.
8. Anything else, and any doubt: needs_review.

## 4. Abstention
Abstain (needs_review) when identifiers are absent, partially missing, or contradictory. Missing evidence must be listed as missing, never filled in.

## 5. Normalization
Matching uses a separate normalized form. The displayed and exported name is always the original string, byte for byte. Default similarity folds spacing and common vowel variants (a change made after the phase 4 stress test). This raises review workload (about 32% more flagged pairs on the homonym stress test) and is threshold sensitive (best at 75 to 80). Revisit before any use on real data.

## 6. What the optional model may do
Summarize an already generated pair: supporting, conflicting and missing evidence, in the required JSON shape. It may agree with the policy or downgrade to needs_review. Nothing here is required for the app to work.
Run with `python -m src.compare_models <model id or local folder>` (or `--remote` for a hosted model). The model is never required; when it is absent or unreachable, the policy result stands. Measured so far, for one small model (Qwen2.5-0.5B-Instruct, one run): the guard rejected 57 of 58 outputs and accepted no upgrade, and shown only two names the model said SAME on 6 of 27 pairs of different people. That is evidence for these rules, not a claim about models in general.

## 7. What the model must never do
Upgrade a recommendation, introduce identifiers not in the records, treat spelling alone as proof, merge or delete records, or be required for the app to run.

## 8. Required output structure
Model: JSON with recommendation, supporting_evidence[], conflicting_evidence[], missing_evidence[], reasoning_summary. Export CSV columns: record_id_a, record_id_b, name_a, name_b, similarity, recommendation, reason, matching_ids, conflicting_ids, missing_ids, soft_conflicts, review_decision, reviewer_note.

## 9. Errors and regressions
Malformed, invented or contradictory model output: fall back to the policy result and flag for human review. Unreadable or empty input: show a clear error. Every failure found gets a regression test before it is considered fixed. `python -m unittest discover -s tests -t .` (40 tests, including the gold-label audit) and `python -m src.evaluate` (synthetic and hard sets) must pass before release. A known, documented failure (hard set 115/116) is reported, not hidden by tuning the policy.

## 10. Honesty requirements
Gold labels are written by the same author as the policy and are only audited automatically against ground-truth entity ids, plus one blind 24-pair second pass by the project owner (not independent); say so whenever results are quoted. A result that was not produced is reported as not run, with the reason, and a result from one small model or one run is labelled as such (the model comparison is one 0.5B model, one run).
Report only measured results, say which backend and data produced them, and do not generalize from synthetic data.
