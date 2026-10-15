# AI usage log

## How to read this
The brief describes five days; this project took four calendar days, 13 to 16 October 2026. AI was my main way of working on every one of them. The entries are in date order. Each one says which tool I used, what I asked, what it produced, what I checked and where it was wrong. I did not stretch four days into five. The brief's five phases (define, baseline, model layer, stress, ship) are marked on the days they actually happened.

## Tools
| Tool | Used on | For |
|---|---|---|
| ChatGPT | 13 Oct | Brainstorming ideas, choosing the problem, drafting the five-day plan. The chat is not stored in this repository; the plan it produced is what I took into the build session. |
| Claude (one chat session) | 14 Oct | The first complete build: scaffold, code, synthetic data, tests, app, evaluation, stress scripts and first drafts of the documents. |
| GitHub Copilot in VS Code (several sessions) | 14, 15 and 16 Oct | Running the project, auditing the documents, fixing bugs, adding the hard set, the model comparison and the walkthrough, publishing, packaging. |

## 13 October: define (ChatGPT)
- Task: pick a real, hard problem and plan the work.
- What I did: brainstormed ideas with ChatGPT and picked the problem I know first-hand: local organizations each wrote my name, "Mennatullah", in a different way. ChatGPT helped turn that into a testable question (can a tool say "probably the same", "probably different" or "needs review" while being honest about its evidence?) and into the five-day plan.
- Output carried forward: the plan, pasted as the first prompt on 14 October.
- Check: none beyond reading it. The conversation is not in the repository.

## 14 October: build, baseline and first stress (Claude, then Copilot)
Prompts to Claude, all of them:
1. The full five-day plan, pasted with no instruction.
2. "I need you to implement all those steps and return the required deliverables: intent.md, Final directive.md, a working solution (repo, demo link or recorded walkthrough), a short write-up (the problem, what you unlearned, how you used AI, what failed), your AI usage log for the 5 days."
3. "Continue please" (twice, after status pauses).

What Claude produced, by phase:
- Define: layout, `intent.md`, a first `Final directive.md`, 42 synthetic records and 29 gold pairs. The labels were written from the policy rules before anything was run.
- Baseline: normalization, similarity, identifier comparison, the policy, the pipeline and the Streamlit app. Result: 20 of 29 gold pairs agreed, 0 false merges, 3 true pairs missed. That miss is what the rest of the project grew from (see the retrospective).
- Model layer: `src/llm_review.py`, which discards any model output that is malformed, invents an email or ID, or tries to upgrade the policy's recommendation, with 10 tests using fake generators so no model is needed. A test caught a real bug: the checker rejected a genuine email because it counted the full stop at the end of the sentence.
- Stress: a name-only strawman, a threshold sweep, a 120-person homonym test (7,140 pairs), before and after snapshots, and the design change to aggressive normalization with a regression test.
- Documents: README, write-up, retrospective, first log.

Where Claude went wrong or decided without asking: the first folder creation used shell brace expansion and made one folder with a literal `{a,b}` name; a comma inside a CSV field broke the gold file; RapidFuzz and Streamlit could not be installed in that session, so it wrote a pure-Python stand-in for `fuzz.ratio` without being asked; and the first documents described the app as finished when it had only been syntax-checked.

Prompts to Copilot, later the same day:
1. "understand the folder and run it"
2. "ok what needs to be updated in the repo?"
3. "yes do all the fixes"
4. "Do them please then update everything to not have any ToDos"
5. "fix the model run part and also the Final Directive.md too"
6. A request to make everything written logical and humane, noting that ChatGPT was used for brainstorming first.

What Copilot did: installed the requirements and ran 33 tests, the evaluation and the stress test with real RapidFuzz (identical results to the pure-Python run); launched the app; found a stale-results bug (a new CSV of the same shape showed the previous file's pairs) and fixed it; added a harder second set the policy was not tuned on (36 records, 21 pairs: Arabic-script names, diacritics, a nickname, `ibn`/`bin`, dropped "Al", email case and ID whitespace differences, a misleading note, two different people sharing a student ID); added a test that audits both gold files against ground truth; wrote the model comparison script and a written walkthrough; and corrected the documents that still said the app had never been launched.

Result of the hard set: 21 of 21 labelled pairs agree, but there is 1 false merge (the shared student ID). The name-only strawman gets 7 of 21 with 10 false merges. I left the false merge in the results rather than tuning it away.

## 15 October: the model comparison, publishing and packaging (Copilot)
Prompts, in order: "Push the repo here https://github.com/MennaElnashar/Name-Bridge.git"; "Can't we just use the hf model without downloading it locally?"; "use sth free"; "any other smaller model?"; a Hugging Face token pasted into the chat for a hosted run; "delete the model and push the repo"; "you can stop the streamlit and please revise this Objective".

- Model comparison. The network proxy blocked model weights for a long time (HTTP 403). When it opened, the planned Qwen2.5-1.5B download was only 7% done after several minutes at about 0.8 MB/s, so I switched to Qwen2.5-0.5B-Instruct, which downloaded completely (988,097,824 bytes, size checked against the server). The first downloader stalled at 0 MB, probably on Hugging Face's Xet transfer path; plain `curl` with resume worked.
- Hosted alternative. A `--remote` mode was added and tested with a fake server. A real call with the pasted token returned HTTP 402 (no credits) for every model I tried, including Kimi, so there is no hosted result. The token was used only as an environment variable, written to no file and not in the repository. Because it was pasted into a chat, it should be revoked.
- Results, 58 candidate pairs on CPU, one run: my checker rejected 57 of 58 outputs and let no upgrade through; shown only two names the model said SAME on 6 of 27 pairs of different people, though it answered UNSURE on most pairs. The policy handled all six correctly. One very small model, so I do not generalize.
- Publishing. The first push failed for lack of credentials. A browser sign-in then picked up my work account, which has no access to the repository, so GitHub refused it with a 403 and nothing was pushed; the stored credential was removed. Signing in again with the personal account worked.
- Packaging. Screenshots and a short scripted walkthrough video were recorded from the running app, a small display bug was fixed (the inspected-record table showed the pandas row index beside the real record ID), and a submission bundle was made.

## 16 October: final revision, labelling check and README (me, with Copilot)
The work from the 15th carried on past midnight, so this day is mostly the "ship" phase: making the evidence easy to find and checking my own work. The entries are in the order things happened.

Prompts, in order: "we are in 16 october now", then "I don't have time for recording but you can add some captions if you want", "How can I revoke the token?", "What do you mean by that?"; "i deleted the token. Please give me the evaluation sheet for labelling"; "The csv file is updated now please check it"; "data is missing means cannot tell"; "did you update the github repo?"; "The readme lacks some information and routing to the folders content and details and the problem statement is too short (also i can't find the screenshot and videos)"; "Now it is ready for submission right?"; "what are you doing?"; and, last, "in the ai usage log i see you didn't add 16 october details at all", which is why this section was rewritten.

- **First, the video and the token.** I had no time to record my own narration, so Copilot re-recorded the scripted walkthrough with on-screen captions (68 seconds), checking a frame to confirm the captions were readable. I asked how to revoke the Hugging Face token I had pasted into the chat and what the "nobody reviewed the labels" warning meant. Copilot explained both, and I deleted the token myself.
- **Next, the token check and the labelling sheet.** Copilot confirmed the old token now returns 401, then built a blind labelling sheet of 24 pairs (Excel with a dropdown, a printable PDF and a CSV) with a separate answer key, a scorer and tests. The sheet hides the policy's answer, my gold label, the ground truth and the free-text note.
- **Then I answered the sheet and Copilot scored it.** I filled in the CSV myself. The first scoring run found zero answers because my edit to the scorer had not applied (a multi-line text replacement missed because of line endings), so I made the scorer accept natural wording ("same", "different", "unsure") and added a test. I told Copilot that "data is missing" means "cannot tell", so six answers were counted that way, and my original file is kept untouched in `labelling/completed/owner_as_returned.csv`. Copilot then asked who had answered the sheet; I said I had, so every document now calls it a second pass by the project owner, not an independent review.
- **Result.** 20 of 24 answers agree with the policy, and I agreed with all 14 of the policy's firm calls. We made the same mistake on the shared-student-ID pair. Details are in `docs/evaluation_protocol.md`.
- **A bug in the scorer.** The first version reported 0 cases of the policy recommending a match for two different people; the real number is 1. Copilot found it by checking that pair by hand: booleans read back from a CSV are text, and the test had only used in-memory booleans. It was fixed and covered by a new test.
- **Then a GitHub check.** I asked whether GitHub was updated. Instead of just saying yes, Copilot compared the remote and local commits and listed the files on the remote.
- **Then the README rewrite.** I said the README lacked detail and routing, the problem statement was too short, and I could not find the screenshots or video. Copilot rewrote the README (a demo section, a long problem statement with a table of spelling variants, how it works, results, quick start, a map of every folder, reviewer table), added short READMEs for `data/`, `outputs/` and `docs/`, and made an animated preview GIF from the screenshots (the available ffmpeg could not encode GIFs). All 66 relative links were checked, and the page was opened on GitHub to confirm the images render.
- **Meanwhile, my own edit on GitHub.** I embedded the walkthrough video in the README using GitHub's uploader so it plays inline. Copilot noticed the remote was one commit ahead of its copy, pulled my commit first so nothing was overwritten, and then continued.
- **Last, the final check.** When I asked if it was ready, Copilot ran a last sweep: it found two stale test counts (40 instead of 46), fixed them, re-ran all 46 tests, checked the repository for secrets (none), confirmed local and remote matched, and rebuilt the submission PDFs and zip.
- **My own checks today.** I answered the labelling sheet from the sheet alone, deleted the token, edited the README on GitHub, and noticed this log was missing today's work.
## Where the AI was wrong or overclaimed
- The first documents claimed more than had been checked (an app never launched, a similarity function never compared to RapidFuzz). Both were later checked and the documents corrected.
- The README's "zero false merges" held only until the hard set was added.
- A first edit of the model comparison script left an outdated field in its summary; a test caught it.
- A first rewrite of the write-up said I had found the problem "by working through everyday records work", which I had not told it. I corrected it with the real origin: my own name.
- The Final directive lost a sentence during one edit; it was noticed and restored.
- When asked to rewrite the 16 October entry, the first version of the log had left most of that day out. This section is the correction.
- Two stale test counts (40 instead of 46) survived in the Final directive and the plan until the final check.
- The first version of the labelling scorer reported 0 cases of the policy recommending a match for two different people. The real number is 1 (the shared-ID pair). The bug was that booleans read back from a CSV are text, and the test had only used in-memory booleans. It was caught by checking a pair by hand, then fixed and covered by a new test.

## Checks by the AI versus checks by a person
- The gold labels are checked against ground truth by a test that the AI wrote. That is a consistency check.
- I labelled a blind 24-pair sample myself on 16 October. That is a second pass by the project owner, who knows the policy, not an independent review.
- No one outside the project has reviewed the gold labels, the hard cases or the walkthrough. Read every number in this repository with that in mind.
