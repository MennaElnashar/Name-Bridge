# Walkthrough

A step-by-step demo of the app. Every result below comes from running the code in this repository on the synthetic data (RapidFuzz 3.14.6, Streamlit 1.50). The screenshots were captured from the running app. A silent, scripted screen recording of the same flow is in [walkthrough.webm](walkthrough.webm) (under a minute, 5 MB; open it in a browser).

## 1. Start
```
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501 and choose **Load synthetic example** (42 invented records).

## 2. Candidate pairs
With the default threshold of 80 the app lists 29 candidate pairs: 6 likely_match, 17 needs_review and 6 likely_different. The **Show** filter narrows them by recommendation, and the table shows the similarity and any decision you have recorded.

![Candidate pairs](img/01_candidate_pairs.png)

## 3. Inspect a pair
Select a pair under **Inspect pair**. The panel shows the recommendation, the reason, which identifiers match, conflict or are missing, and both original records side by side.

**Likely match:** Mennatullah Hassan and Menna Allah Hassan, similarity 91.7. The spellings differ but the email matches and nothing conflicts.

![Likely match](img/02_likely_match.png)

**Needs review (shared mailbox):** Sara Adel and Mariam Tarek share an email address although their names differ. The tool flags it and does not merge: a shared or reused identifier is a reason to look, not proof of identity.

![Shared mailbox](img/03_shared_mailbox_needs_review.png)

**Likely different:** two Fatma Ibrahim records with identical names but different emails and student IDs. A name-only tool would merge them.

![Identical names, different people](img/04_identical_names_likely_different.png)

## 4. Record a decision
Pick "same person", "different people" or "unsure", add a note if you like and press **Record decision**. Nothing is merged or deleted; the decision is only stored next to the pair, and notes are never used as evidence.

![Decision recorded](img/05_decision_recorded.png)

## 5. Export
**Download pairs, evidence and decisions (CSV)** writes the columns listed in section 8 of Final directive.md. In the exported file from this demo the decision and the note are saved on the pair, and every name is exactly as entered. A sample is in `outputs/namebridge_review_example.csv`.

## 6. Your own data
"Paste names" takes one name per line (no identifiers, so most pairs end as needs_review). "Upload CSV" needs a name column; choose identifier and context columns in the selectors. Use synthetic data only on a shared demo.