"""NameBridge Streamlit app. Run:  streamlit run app.py
Works without any model. Never merges or deletes records; decisions are only recorded."""
import io

import pandas as pd
import streamlit as st

from src import matching
from src.pipeline import find_candidates, names_to_frame, read_csv_preserving
from src.policy import PolicyConfig

st.set_page_config(page_title="NameBridge", layout="wide")
st.title("NameBridge")
st.caption("Similar names. Different spellings. Better decisions. Use synthetic data only for demos.")

mode = st.radio("Input", ["Upload CSV", "Paste names", "Load synthetic example"], horizontal=True)
df = None
try:
    if mode == "Upload CSV":
        up = st.file_uploader("CSV file", type=["csv"])
        if up is not None:
            df = read_csv_preserving(io.BytesIO(up.getvalue()))
    elif mode == "Paste names":
        txt = st.text_area("One name per line", height=150)
        if txt.strip():
            df = names_to_frame(txt)
    else:
        df = read_csv_preserving("data/synthetic_names.csv")
except Exception as exc:  # unsupported or unreadable file
    st.error(f"Could not read input: {exc}")

if df is not None and not df.empty:
    cols = list(df.columns)
    c1, c2, c3 = st.columns(3)
    name_col = c1.selectbox("Name column", cols, index=cols.index("name") if "name" in cols else 0)
    rest = [c for c in cols if c != name_col]
    uniq = c2.multiselect("Unique identifier columns (email, ID)", rest,
                          default=[c for c in ("email", "student_id") if c in rest])
    soft = c3.multiselect("Context columns (organization)", [c for c in rest if c not in uniq],
                          default=[c for c in ("org",) if c in rest])
    id_col = "record_id" if "record_id" in cols else "__row__"
    if id_col == "__row__":
        df[id_col] = [str(i) for i in range(1, len(df) + 1)]
    threshold = st.slider("Name similarity threshold", 60, 95, 80)
    dups = int(df.duplicated().sum())
    if dups:
        st.warning(f"{dups} fully duplicated row(s) in the input.")
    try:
        cfg = PolicyConfig(name_threshold=float(threshold), unique_cols=uniq, soft_cols=soft)
        pairs = find_candidates(df, name_col=name_col, id_col=id_col, cfg=cfg)
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    st.caption(f"Similarity backend: {matching.BACKEND}")
    data_hash = int(pd.util.hash_pandas_object(df.astype(str), index=False).sum())
    key = f"{name_col}|{data_hash}|{threshold}|{','.join(uniq)}|{','.join(soft)}"
    if st.session_state.get("key") != key:
        st.session_state["key"] = key
        st.session_state["pairs"] = pairs

    pairs = st.session_state["pairs"]
    want = st.multiselect("Show", ["likely_match", "needs_review", "likely_different"],
                          default=["likely_match", "needs_review", "likely_different"])
    view = pairs[pairs.recommendation.isin(want)]
    st.write(f"{len(view)} of {len(pairs)} candidate pairs")
    st.dataframe(view[["record_id_a", "record_id_b", "name_a", "name_b", "similarity",
                       "recommendation", "review_decision"]])

    if len(view):
        idx = st.selectbox("Inspect pair", list(view.index),
                           format_func=lambda i: f"{pairs.at[i, 'name_a']}  /  {pairs.at[i, 'name_b']}")
        row = pairs.loc[idx]
        st.subheader(f"{row.name_a}  /  {row.name_b}")
        st.write(f"**Recommendation:** {row.recommendation} (similarity {row.similarity})")
        st.write(f"**Why:** {row.reason}")
        st.write(f"Matching: {row.matching_ids or 'none'} | Conflicting: {row.conflicting_ids or 'none'} | "
                 f"Missing: {row.missing_ids or 'none'}")
        a = df[df[id_col] == row.record_id_a].iloc[0]
        b = df[df[id_col] == row.record_id_b].iloc[0]
        shown = [c for c in df.columns if c not in ("entity_id", "__row__")]
        st.table(pd.DataFrame([a[shown], b[shown]]))
        d = st.selectbox("Your decision", ["", "same person", "different people", "unsure"], key=f"d{data_hash}_{idx}")
        n = st.text_input("Note", key=f"n{data_hash}_{idx}")
        if st.button("Record decision"):
            st.session_state["pairs"].at[idx, "review_decision"] = d
            st.session_state["pairs"].at[idx, "reviewer_note"] = n
            st.rerun()

    st.download_button("Download pairs, evidence and decisions (CSV)",
                       st.session_state["pairs"].to_csv(index=False).encode("utf-8-sig"),
                       "namebridge_review.csv", "text/csv")
