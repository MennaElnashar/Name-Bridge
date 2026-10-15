# Retrospective

`intent.md` is left as it was written on day one. This page records how my understanding changed since then.

## What I believed, and what happened
- I thought more aggressive name normalization would cost precision. It cost review workload instead (about 32% more flagged pairs on the homonym test). False merges stayed at 0 on the first set because the policy only recommends a match when an identifier agrees.
- Hypothesis 1, similarity cannot establish identity: supported. The name-only baseline made 8 false merges on the first set and 10 on the hard set.
- Hypothesis 2, identifiers help: supported, with a limit. They separated spelling variants from different people, but the hard set showed one shared student ID can still produce a false merge (records 115 and 116). The same limit shows in the shared mailbox on pair 22 and 23, which the policy correctly sends to review.
- Hypothesis 3, models infer identity from spelling when they should abstain: partly supported, for one very small model. Shown only two names, Qwen2.5-0.5B-Instruct answered UNSURE on 40 of 58 pairs, which is the right instinct, but said SAME on 6 of 27 pairs of different people. Two of those were identical names of different people, which nobody can settle from the name. One model, one run, so I do not generalize.
- Hypothesis 4, keeping a person's chosen spelling is separate from matching: supported. Names were identical in every export, including spacing, casing and the literal name "Nan".

## What went wrong
- The first baseline treated spacing variants as different names.
- The model-output checker rejected a legitimate email.
- The app could show stale pairs for a new file of the same shape.
- The early documents said more than had been verified.
- The hard set found a false merge I had not planned for.
- The model comparison was blocked by the network for a long time. The 1.5B model I planned was too slow to download, a hosted API needed credits the account did not have, and I finally ran a 0.5B model, which was too weak to follow the required output format (57 of 58 outputs rejected by the guard).

## A second pair of eyes (mine only)
On 16 October I labelled a blind 24-pair sample from the sheet alone (details in `docs/evaluation_protocol.md`). I agreed with all 14 firm calls the policy made, and so I also treated a shared student ID as proof for two different people (pair 115 and 116 again). It is not an independent check, but it moves the false merge from "a quirk of my code" to "what a careful person does with these fields". Where the policy abstained and I committed, I was right three times out of four, and the one miss was the mixed-evidence case (matching email, conflicting ID) that rule 3 sends to review.

## An open decision
A single matching student ID, with no email, currently gives "likely match". Capping that case at "needs review" would remove the false merge on 115 and 116, at the cost of more review work. I did not change the policy after seeing the hard set, because that would have turned a test set into a tuning set. It is the next thing to decide, with a reviewer who owns real data.

## What I would do next
Get a person outside the project to answer the blind sheet in `labelling/` and to label a new set; repeat the model comparison with a stronger model, ideally 7B or larger; add Arabic-script matching; decide the single-identifier question above.