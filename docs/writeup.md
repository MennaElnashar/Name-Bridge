# NameBridge: a safer way to decide whether two names are the same person

## The problem
I ran into this myself. Local organizations each wrote my name, "Mennatullah", in a different way. In Latin script an Arabic name has many legitimate spellings (Mohamed, Muhammad, Mohammed; Abdelrahman, Abd El Rahman; Mennatullah, Menna Allah), and record systems fail in two opposite ways. They miss that two records are one person, which distorts counts. Or they merge two different people because their names look alike, which can destroy or leak a real person's data. A similarity score cannot tell these apart, because "similar name" is not the same as "same person". The question I set myself: can a tool say "probably the same", "probably different" or "needs review", and be honest about how much evidence it has?

## What I built
A local Streamlit app with a plain Python core that runs without any model. You give it a CSV or pasted names. It lists candidate pairs by name similarity, then looks separately at identifiers (email, student ID), treats organization as weak context and ignores free-text notes. A written policy gives one of three answers: likely match, needs review, likely different. Missing or contradictory evidence always gives "needs review". You record your own decision on each pair and export everything. Nothing is merged or deleted, and original spellings are exported exactly as entered. An optional local model can explain a pair, but its output is discarded if it is malformed, invents an identifier or tries to upgrade the recommendation. See `docs/walkthrough.md` for screenshots and a short video.

## What I unlearned
I started out believing the key lever was the name-similarity setting: being more aggressive about spelling variants would raise recall but create false matches. The measurements said otherwise:
- On my first set, aggressive spelling normalization made no false merges. It cost review workload instead (+32% flagged pairs in a 120-person test). The identifiers, not the similarity score, were doing the safety work: a name-only rule made 8 false merges on the same data.
- Then I over-learned it and began to treat "an identifier matches" as safe. A harder set showed two different people who share one student ID are still recommended as a match. One matching identifier is strong evidence, not proof.

## How I used AI
AI was my main way of working on every day. Full detail, with every prompt and where the AI was wrong, is in `docs/ai_usage_log.md`.
- 13 Oct, ChatGPT: brainstorming, choosing the problem, drafting the five-day plan.
- 14 Oct, Claude: built the first complete version from the plan (code, data, tests, app, evaluation, first documents). Copilot in VS Code then ran everything, found stale claims and a real bug, and added the hard set, an audit of the labels, and the model comparison script.
- 15 Oct, Copilot: ran the model comparison, tried a hosted model, published the repo, recorded the walkthrough and packaged the submission.
- 16 Oct: my final revision of the documents, with Copilot making the edits and re-recording the captioned walkthrough.
It took four calendar days, not five, and the log says so rather than stretching it.

## What failed
1. The first baseline missed spacing variants: "Mennatullah Hassan" and "Menna Allah Hassan" with the same email scored below the threshold and were reported as different. Three true pairs were never surfaced (20 of 29 agreed). Fix: normalize spacing and common vowel variants (29 of 29, still no false merges), with a regression test.
2. The model-output checker rejected a real email because of a trailing full stop. A test caught it.
3. The app could show a previous file's results when a new CSV had the same shape. Found on review and fixed.
4. The early documents claimed more than had been checked (an app never launched, a similarity function never compared to RapidFuzz). Both were later checked and the documents corrected.
5. The hard set exposed a real false merge (shared student ID). I left it in the results.
6. The model comparison took many attempts: a blocked network, a 3 GB download too slow, a hosted API that needed credits. I finally ran a 0.5B model on CPU, which was too weak to follow the required format.

## Stress growth
| Stage | What was tested | What it showed |
|---|---|---|
| Baseline (14 Oct, first build) | 42 records, 29 hand-labelled pairs; clear identifiers | Name-only: 2 of 29 agree, 8 false merges. First policy: 20 of 29, 3 true pairs missed |
| Stress 1 | Threshold sweep (70 to 90) and 120 different people, 7,140 pairs, no identifiers | Fix works only in a narrow band (29 of 29 at 75 to 80, 26 at 85, 24 at 90). Workload rises from 37 to 49 flagged pairs |
| Stress 2 | 36 records, 21 pairs written to be harder: Arabic script, diacritics, a nickname, `ibn`/`bin`, dropped "Al", ID reuse, a misleading note | 21 of 21 labelled pairs agree but 1 false merge (shared student ID). Name-only: 7 of 21, 10 false merges |
| Model stress | 58 pairs given to Qwen2.5-0.5B-Instruct, CPU, one run | My checker rejected 57 of 58 outputs and let no upgrade through. Shown only two names it said SAME on 6 of 27 pairs of different people. The policy handled all six correctly |

## Limits
Synthetic data only, and Latin script only (an Arabic-script name was only surfaced through a matching email). The labels and the policy were written by the same author with AI help, and only a test has checked the labels against ground truth; nobody else has reviewed them (a blind 24-pair sheet for an independent reviewer is prepared in `labelling/` but has not been answered). The model result is one very small model in one run. It is not ready for real personal records.

## Where things are
Repository: https://github.com/MennaElnashar/Name-Bridge. Start with `README.md`. The five deliverables are `intent.md`, `Final directive.md`, the working app (run commands in the README, walkthrough in `docs/walkthrough.md`), this write-up, and `docs/ai_usage_log.md`. Evidence is in `docs/evaluation_protocol.md`, `docs/retrospective.md` and `outputs/`.