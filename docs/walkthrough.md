# Walkthrough

A written, step-by-step demo of the app. Every result below was produced by running the code in this repository on the synthetic data (RapidFuzz 3.14.6, Streamlit 1.50). It replaces a screen recording.

## 1. Start
```
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501. Choose **Load synthetic example** (42 invented records).

## 2. Candidate pairs
With the default threshold (80) the app lists 29 candidate pairs: 6 likely_match, 17 needs_review, 6 likely_different. Use the **Show** filter to narrow by recommendation.

## 3. Inspect a pair
Select a pair under **Inspect pair**. Two examples:
- Mennatullah Hassan / Menna Allah Hassan, similarity 91.7, **likely_match**: "similar names and matching email with no unique-identifier conflict".
- Mennatullah Hassan / Mennatallah Hassan, similarity 92.3, **likely_different**: "similar names but conflicting email, student_id". Near-identical spelling, different people.
- Sara Adel / Mariam Tarek, **needs_review**: "names differ but email matches; investigate the discrepancy (shared or reused identifier?) before any merge". A shared mailbox is surfaced, never merged.

## 4. Record a decision
Pick "same person", "different people" or "unsure", optionally add a note, press **Record decision**. Nothing is merged or deleted; the decision is only stored next to the pair. Notes are never used as evidence.

## 5. Export
**Download pairs, evidence and decisions (CSV)** writes the columns listed in Final directive.md section 8. Original spellings are exported byte for byte. A sample is in outputs/namebridge_review_example.csv.

## 6. Paste names or upload your own CSV
"Paste names" takes one name per line (no identifiers, so most pairs end as needs_review). "Upload CSV" needs a name column; pick identifier and context columns in the selectors. Use synthetic data only on a shared demo.
