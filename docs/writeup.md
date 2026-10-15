# NameBridge: a safer way to decide whether two names are the same person

## The problem
In Latin script, one Arabic name has many legitimate spellings: Mohamed, Muhammad, Mohammed; Abdelrahman, Abd El Rahman; Mennatullah, Menna Allah. Record systems fail in two opposite ways. They miss that two records are one person, which distorts counts. Or they merge two different people because their names look alike, which can destroy or leak a real person's data. A similarity score cannot tell these apart, because "similar name" is not the same as "same person".

I found this by working through where name matching goes wrong in everyday records work, first by brainstorming with ChatGPT and then by narrowing it to one testable question: can a tool recommend "probably the same" or "probably different" while being honest about how much evidence it has?

## What I built
A local Streamlit app, with a plain Python core that runs without any model. You give it a CSV or pasted names. It lists candidate pairs by name similarity, then looks separately at identifiers (email, student ID), treats organization as weak context, and ignores free-text notes. A written policy gives one of three answers: likely match, needs review, likely different. When evidence is missing or contradictory, the answer is "needs review". You record your own decision on each pair and export everything. Nothing is merged or deleted, and original spellings are exported exactly as they came in. An optional local model can explain a pair, but its output is thrown away if it is malformed, invents an identifier, or tries to upgrade the recommendation.

## What I unlearned
I started out believing the key lever was the name-similarity setting, and that being more aggressive about spelling variants would trade accuracy for coverage. The measurements said something different:
- On my first synthetic set, aggressive spelling normalization made no false merges at all. What it changed was review workload: about 32% more pairs to look at in a 120-person test. The identifiers, not the similarity score, were doing the safety work. A name-only rule made 8 false merges on the same data.
- Then I over-learned it. I began to treat "an identifier matches" as safe. A harder second set showed otherwise: two different people who share one student ID are still recommended as a match. One matching identifier is strong evidence, not proof.

## How I used AI
ChatGPT came first, for brainstorming the problem and shaping the five-day plan. I then gave the plan to Claude in a build session, which produced the code, data, tests, app and first documents. A second session in VS Code with GitHub Copilot ran everything, found where the documents were out of date, and fixed and extended the project, including the hard set and the gold-label audit. The full prompts, who did what, and where the AI was wrong are in `docs/ai_usage_log.md`. One honest point: the work was compressed into a few sessions on 2026-10-14 and 2026-10-15, so the log follows the plan's five phases rather than pretending to be five calendar days.

## What failed
1. The first baseline missed spacing variants. "Mennatullah Hassan" and "Menna Allah Hassan" with the same email scored below the threshold and were reported as different. Three true pairs were never surfaced (20 of 29 agreed). Fix: normalize spacing and common vowel variants (29 of 29, still no false merges), with a regression test.
2. The model-output checker rejected a real email because of a trailing full stop. A test caught it.
3. The app could show a previous file's results when a new CSV had the same shape. Found on review, fixed.
4. The first documents claimed more than had been checked (an app never launched, a similarity function never compared to RapidFuzz). Both were later checked, and the documents corrected.
5. The hard set exposed a real false merge: the shared student ID case. I left it in the results.
6. The model comparison took several attempts. The network proxy blocked model downloads for a long time; when it opened, the 3 GB Qwen2.5-1.5B download was too slow, and a hosted API needed credits the account did not have. I finally ran Qwen2.5-0.5B-Instruct on CPU. It was too weak to follow the required output format: my checker rejected 57 of its 58 outputs and let no upgrade through, so it harmed nothing and helped nothing. Shown only two names, it said SAME on 6 of 27 pairs of different people (identical names, one-letter variants), though it answered UNSURE on most pairs. One small model, one run: a hint about hypothesis 3, not a verdict.

## Results
- Synthetic set (42 records, 29 pairs): name-only gets 2 of 29 with 8 false merges. The final policy gets 29 of 29 with 0 false merges.
- Stress growth: baseline on that set, then a threshold sweep and a 120-person homonym test (7,140 pairs, 49 flagged), then a harder 36-record set with Arabic-script names, diacritics, a nickname, `ibn`/`bin`, dropped "Al" and reused IDs. There the policy agrees on 21 of 21 labelled pairs but makes 1 false merge; name-only gets 7 of 21 with 10 false merges.
- Model comparison (Qwen2.5-0.5B-Instruct, CPU, one run, 58 pairs): guard accepted 1 of 58 outputs and no upgrade; names only, the model said SAME on 6 of 27 pairs of different people. The policy handled all six correctly.
- 40 tests pass, and the app launches. See `docs/walkthrough.md`.

## Limits
Synthetic data only, Latin script only (an Arabic-script name was only surfaced through a matching email). The labels were written by the same author as the policy, and only a test has checked them against the ground truth. No person has reviewed them. Model results come from one very small model in one run. The walkthrough is written rather than recorded. It is not ready for real personal records.

## Where things are
Repository target: https://github.com/MennaElnashar/Name-Bridge (pushing needs the owner's GitHub sign-in). `intent.md`, `Final directive.md`, `README.md`, `docs/ai_usage_log.md`, `docs/walkthrough.md`, `docs/evaluation_protocol.md`, `docs/retrospective.md`, and the result files in `outputs/`.