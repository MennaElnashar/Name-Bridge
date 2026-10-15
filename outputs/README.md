# outputs/

Result files produced by the code in this repository. Re-running the commands overwrites them.

| File | Made by | What it holds |
|---|---|---|
| `eval_results.json` | `python -m src.evaluate` | First set, all four strategies (name-only, conservative baseline, aggressive, final): agreement with gold, false merges, missed pairs |
| `eval_before_day4.json` | snapshot | The same evaluation taken **before** the normalization redesign (the file name says "day4" because that is when the redesign happened). Compare with `eval_results.json` for the before and after |
| `hard_results.json` | `python -m src.evaluate` | The hard set: name-only versus final policy |
| `stress_results.json` | `python -m src.stress` | Threshold sweep (70 to 90) and the 120-person homonym test |
| `stress_day4.json` | snapshot | The stress results before the redesign |
| `model_comparison.json` | `python -m src.compare_models` | Raw output of the one model run (Qwen2.5-0.5B-Instruct, CPU): every pair, the guard status and the names-only answer |
| `human_label_results.json` | `python -m src.labelling score` | The project owner's blind 24-pair pass scored against the policy and gold labels |
| `namebridge_review_example.csv` | the app's export | A sample export with the evidence columns |

Read the numbers with the caveats in [docs/evaluation_protocol.md](../docs/evaluation_protocol.md).