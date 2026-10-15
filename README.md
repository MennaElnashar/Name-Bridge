# NameBridge

Similar names. Different spellings. Better decisions. A human-in-the-loop tool for reviewing possible duplicate records with Arabic names in Latin script. It never merges or deletes anything.

## Run
```
pip install -r requirements.txt
python -m unittest discover -s tests -t .   # or: pytest
python -m src.evaluate                      # evaluation (synthetic set and hard set)
python -m src.stress                        # stress tests
streamlit run app.py                        # app (works with no model)
python -m src.compare_models <model id or local folder> [limit]   # optional: model comparison (needs transformers, torch); a local folder loads offline
```
Use data/synthetic_names.csv. Do not upload real personal records to a public demo. A step-by-step demo is in docs/walkthrough.md.

## Status
| Item | State |
|---|---|
| Deterministic pipeline, policy, export | Built; 37 tests pass (unittest and pytest) |
| Evaluation, hard set and stress test | Run with RapidFuzz 3.14.6; results in docs/evaluation_protocol.md |
| Gold-label audit | Automated check against ground-truth entity ids (tests/test_gold_labels.py) |
| Streamlit app | Launched and exercised (Streamlit 1.50); demo in docs/walkthrough.md |
| Local model layer | Guard, 10 guard tests and the comparison script (tested with a stub model) built. The comparison was not run: huggingface.co returned 403 from this network, so no model could be downloaded. To run it: allow huggingface.co, or pass a local model folder (offline loading was checked with a tiny random model, which is not a real result) |
| Publishing | Not published. This environment had no GitHub account or credentials; the project is this folder |

## Documents
intent.md, Final directive.md, docs/writeup.md, docs/ai_usage_log.md, docs/evaluation_protocol.md, docs/retrospective.md, docs/walkthrough.md, docs/implementation_plan.md. The AI usage log covers ChatGPT (brainstorming), Claude (build) and GitHub Copilot (review and fixes).

## Known limitations
Synthetic data only; Latin script only; small gold sets written by the same author as the policy; ids reused by different people produce a false merge (hard set pair 115/116); no model comparison results.