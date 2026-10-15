# Implementation plan (as executed)

The plan came from brainstorming with ChatGPT on 13 October 2026 and was carried out with AI help on 14 and 15 October, with a final revision by the author on 16 October. The order below is the order things were really done.

1. Scaffold and written spec (`intent.md`, first `Final directive.md`).
2. The deterministic core: normalization, similarity, identifier evidence, policy, pipeline.
3. Synthetic data and hand-written gold labels, then the evaluation script and unit tests.
4. The Streamlit app.
5. The optional model-checking layer and its tests.
6. Stress tests, then the design change to aggressive normalization.
7. Documents.
8. Follow-up session: ran everything, fixed the stale-results bug, added a harder second set, a gold-label audit, the model comparison script and a written walkthrough, then corrected the documents.

Modules: `src/normalization.py`, `matching.py`, `evidence.py`, `policy.py`, `pipeline.py`, `llm_review.py`, `compare_models.py`, `evaluate.py`, `stress.py`; `app.py`; `tests/` (40 tests).

Outcome: the app launches and is documented in `docs/walkthrough.md`. The model comparison ran once with Qwen2.5-0.5B-Instruct on CPU (the 1.5B model was too slow to download; a hosted API needed credits). The project is published at https://github.com/MennaElnashar/Name-Bridge.
