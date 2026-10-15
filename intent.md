# NameBridge: Intent

Status: Day 1 contract. Hypotheses below are hypotheses, recorded before the evaluation was run. Later changes of understanding are logged in docs/retrospective.md, not here.

## How this started
I ran into this problem myself. Local organizations each wrote my name, "Mennatullah", in a different way, so one person was recorded in many forms. I explored it on 13 October in a brainstorming conversation with ChatGPT, turned it into a testable question and a five-day plan, and wrote this contract before building anything. How AI was used, day by day, is in docs/ai_usage_log.md.

## Problem statement
Arabic names written in Latin script have many valid spellings (Mohamed, Muhammad, Mohammed; Abdelrahman, Abd El Rahman; Mennatullah, Menna Allah). Registration and records systems either miss that two records are the same person, or merge people who only have similar names. Both errors are costly: duplicates distort counts, wrong merges destroy or leak a real person's data.

## Target user and workflow
An analyst, administrator or organizer holding a CSV of records. Today they sort by name and eyeball, or run a fuzzy match and trust the score. NameBridge changes this to: upload CSV, see candidate pairs with the evidence behind each, record a decision per pair, export everything. Nothing is merged or deleted by the tool.

## Why existing approaches fall short
- Exact matching misses spelling and spacing variants.
- Fuzzy matching alone answers "are these names alike?", not "are these the same person?". Similar names of different people look identical to it.
- Neither approach reports uncertainty or missing evidence.

## Core design principle
Three separate questions: (1) are the spellings similar enough to check, (2) is there evidence the records are the same person, (3) is that evidence strong enough to recommend a match. When unsure, the answer is "needs review".

## In scope
Pasted names or CSV input; transparent similarity-based candidate generation; identifier comparison (email, student ID, organization); three-way recommendation (likely_match, needs_review, likely_different); human decision recording; CSV export; evaluation on a synthetic dataset; an optional local-model explanation layer that is validated and can be switched off.

## Out of scope
Automatic merging or deletion; verifying legal identity; training a model; covering every dialect and transliteration convention; production-scale deployment; real personal records in any demo.

## Initial hypotheses (to test, not findings)
1. String similarity finds useful candidates but cannot establish identity.
2. Contextual identifiers help separate spelling variants from different people.
3. Models may infer identity from spelling alone when they should abstain.
4. Preserving a person's chosen spelling is a separate capability from matching.

## Success criteria
- Zero false merges on the evaluation set (likely_match across different people).
- Pairs with no discriminating evidence are never given false certainty.
- Original spellings appear unchanged in every export.
- The app and all tests work with no model loaded.
- A stranger can install, test and run the demo from the README.

## Privacy, safety, reliability constraints
Synthetic data only in the repository and demo. No credentials or tokens committed. No hosted model API required. Free-text notes are never treated as evidence. Any model output that is malformed, invents identifiers or contradicts the policy is discarded.
