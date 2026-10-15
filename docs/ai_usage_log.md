# AI usage log

## How to read this
The brief asks for five days of AI-assisted work. This project was built with AI at every step, but the build itself was compressed: both AI working sessions happened on 2026-10-14, after an earlier brainstorming stage whose date was not recorded. I have not rewritten that into five calendar days. The entries below follow the plan's five phases (define, baseline, model layer, stress, ship) in the order the work really happened, and each entry says who did what and what was checked.

## Tools and what each was used for
| Stage | Tool | Used for |
|---|---|---|
| 0. Brainstorming (before any code) | ChatGPT | Exploring problem ideas, settling on Latin-script Arabic name matching, shaping the five-day plan. The chat is not stored in this repository; its output is the plan that opened the build session. |
| 1. Build | Claude (one chat session) | Scaffold, modules, synthetic data, gold labels, tests, app, evaluation and stress scripts, first drafts of all documents. |
| 2. Review, fix and extend | GitHub Copilot in VS Code (one session) | Ran and exercised the project, audited the documents against reality, fixed bugs, added the hard set, the gold-label audit, the model comparison script and the walkthrough. |

## Prompts that were given
Build session (Claude):
1. The full NameBridge five-day plan, pasted with no instruction.
2. "I need you to implement all those steps and return the required deliverables: intent.md, Final directive.md, a working solution (repo, demo link or recorded walkthrough), a short write-up (the problem, what you unlearned, how you used AI, what failed), your AI usage log for the 5 days."
3. "Continue please" (twice, after status pauses).

Follow-up session (Copilot in VS Code):
1. "understand the folder and run it"
2. "ok what needs to be updated in the repo?"
3. "yes do all the fixes"
4. "Do them please then update everything to not have any ToDos"
5. "fix the model run part and also the Final Directive.md too"
6. A request to make everything written logical and humane, noting that ChatGPT was used for brainstorming first.
Also one decision question was answered: when the model download was blocked, the choice was "get huggingface.co allowed or give a local model folder", which is why `compare_models` accepts a local folder.

## Phase 1: define and scaffold (Claude)
- Task: turn the plan into a repository: intent, evaluation design, synthetic data.
- AI contribution: layout, `intent.md`, a first `Final directive.md`, 42 synthetic records and 29 gold pairs. The labels were written from the policy rules before anything was run.
- What went wrong: the first attempt to create folders used shell brace expansion and produced one folder with a literal `{a,b}` name. It was removed and redone. A comma inside a CSV field also broke the gold file until it was fixed.
- Still true afterwards: the labels and the policy come from the same author, so agreement between them proves less than it looks.

## Phase 2: deterministic baseline (Claude)
- Task: build a version that works without any model.
- AI contribution: normalization, similarity, identifier comparison, the policy, the pipeline, the Streamlit app.
- Decision made by the AI without being asked: RapidFuzz and Streamlit could not be installed in that session, so it wrote a small pure-Python stand-in for `fuzz.ratio` as a fallback.
- Result: baseline agreed with 20 of 29 gold pairs and made 0 false merges. It missed 3 true pairs. That is the failure the rest of the project grew out of (see the retrospective).

## Phase 3: model layer (Claude, then Copilot)
- Task: allow an optional local model to explain a pair, without letting it decide anything.
- AI contribution (Claude): `src/llm_review.py`, a checker that discards any model output that is malformed, invents an email or ID, or tries to upgrade the policy's recommendation, plus 10 tests using fake generators so no model is needed.
- Bug a test caught: the checker rejected a real email because it counted the full stop at the end of a sentence as part of the address. Fixed.
- AI contribution (Copilot): `src/compare_models.py`, which measures the guarded review and also asks the model, from names alone, whether two records are the same person (hypothesis 3). Tested with a stub model.
- What did not work: the planned model, Qwen2.5-1.5B-Instruct, could not be downloaded because the network proxy answered 403 for huggingface.co. A mirror host did respond to a connectivity check, but I did not download through it because that would sidestep the network's rules. `torch` and `transformers` were installed. The script now also loads a local model folder offline; this was verified end to end with a tiny random model whose output was thrown away. No model results exist.

## Phase 4: stress and redesign (Claude, then Copilot)
- Task: make the evaluation harder than the baseline's and see what breaks.
- AI contribution (Claude): a name-only strawman strategy, a threshold sweep, a 120-person homonym test (7,140 pairs), before and after snapshots, and the change to aggressive normalization with a regression test.
- AI contribution (Copilot): a second, harder set (36 records, 21 gold pairs) with Arabic-script names, diacritics, a nickname, dropped particles such as "Al", `ibn`/`bin`, email case and ID whitespace differences, a misleading note, and two different people who share a student ID. The policy was not changed after seeing it.
- Result: 21 of 21 gold pairs agree, but there is 1 false merge, the shared student ID case. The strawman gets 7 of 21 and makes 10 false merges. The false merge is left in the results on purpose.
- Caveat: the same AI-assisted author wrote the cases, so this is harder than the first set, not independent of the author.

## Phase 5: ship and document (Claude, then Copilot)
- AI contribution (Claude): README, write-up, retrospective, this log, first drafts of everything.
- AI contribution (Copilot): ran the app and checked it with Streamlit's AppTest; found and fixed a stale-results bug (two different same-shaped CSVs could show the first one's pairs); removed a deprecated option; wrote `docs/walkthrough.md` from real outputs; corrected the documents that still said the app had never been launched; added `tests/test_gold_labels.py`.
- Not done: the project is not published on GitHub, because this machine had no GitHub tooling or credentials. The walkthrough is written, not recorded on video.

## Where the AI was wrong or overclaimed
- The first documents described the app as finished while it had only been syntax-checked.
- The first documents implied a pure-Python similarity function was equivalent to RapidFuzz without checking. It was later checked: results were identical.
- A first edit of the model comparison script left an outdated field in its summary; a test caught it.
- The README's "zero false merges" held only until the hard set was added.

## Checks by the AI versus checks by a person
- Ground-truth consistency of the gold labels is checked by a test, written by the AI.
- No other person has reviewed the gold labels, the hard cases, or the walkthrough. Every number in this repository should be read with that in mind.