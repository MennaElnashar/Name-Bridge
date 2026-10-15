"""Day 3 comparison: deterministic policy versus a local model. Run:  python -m src.compare_models [model_id]

Two measurements on every candidate pair from data/synthetic_names.csv and data/hard_cases.csv:
  A. guarded review: the model explains a policy-generated pair through src/llm_review.py.
     Reports how often its output is accepted, how often it downgrades, how often it is rejected and why.
  B. names only (hypothesis 3): the model sees only the two names and is asked whether they are the same
     person. Reports false merges (SAME on different people) against ground truth entity_id.
Needs the optional packages in requirements.txt (transformers, torch). Greedy decoding, no sampling.
model_id may be a Hugging Face id or a local folder containing a chat model (config.json, tokenizer, weights);
a local folder is loaded offline, so no network access is needed."""
import json
import platform
import sys
import time
from pathlib import Path

from .llm_review import review_pair
from .pipeline import find_candidates, read_csv_preserving
from .policy import PolicyConfig

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
NAME_ONLY_PROMPT = ("Two records have these names written in Latin script.\nName 1: {a}\nName 2: {b}\n"
                    "Are they the same person? Answer with exactly one word: SAME, DIFFERENT or UNSURE.")


def load_generator(model_id):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    local = Path(model_id).is_dir()
    try:
        tok = AutoTokenizer.from_pretrained(model_id, local_files_only=local)
        model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32, local_files_only=local)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Could not load model '{model_id}': {exc}\n"
                         "Pass an existing local model folder, or allow huggingface.co on your network.")
    model.eval()
    info = {"model_id": model_id, "torch": torch.__version__, "dtype": "float32", "device": "cpu",
            "decoding": "greedy", "revision": getattr(model.config, "_commit_hash", None)}

    def generate(prompt, max_new_tokens):
        msgs = [{"role": "user", "content": prompt}]
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        with torch.no_grad():
            out = model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=False)
        return tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)

    return generate, info


def collect_pairs():
    sets = []
    for data in ("synthetic_names.csv", "hard_cases.csv"):
        df = read_csv_preserving(ROOT / "data" / data)
        pairs = find_candidates(df, cfg=PolicyConfig())
        sets.append((data, df, pairs))
    return sets


def main(model_id=DEFAULT_MODEL, limit=None):
    limit = int(limit) if limit else None
    generate, info = load_generator(model_id)
    info.update({"python": platform.python_version(), "machine": platform.processor()})
    guarded, name_only = [], []
    t_guard = t_name = 0.0
    n = 0
    for data, df, pairs in collect_pairs():
        recs = {r["record_id"]: r for r in df.to_dict("records")}
        ent = dict(zip(df.record_id, df.entity_id))
        for p in pairs.to_dict("records"):
            if limit and n >= limit:
                break
            n += 1
            a, b = recs[p["record_id_a"]], recs[p["record_id_b"]]
            # the model never sees ground truth or free-text notes
            view = lambda r: {k: v for k, v in r.items() if k not in ("entity_id", "note")}
            t0 = time.time()
            res = review_pair(p, view(a), view(b), lambda prompt: generate(prompt, 220))
            t_guard += time.time() - t0
            guarded.append({"set": data, "a": p["record_id_a"], "b": p["record_id_b"],
                            "policy": p["recommendation"], "status": res["status"],
                            "fallback_reason": res["fallback_reason"],
                            "model_recommendation": res["recommendation"]})
            t0 = time.time()
            raw = generate(NAME_ONLY_PROMPT.format(a=a["name"], b=b["name"]), 6).strip().upper()
            t_name += time.time() - t0
            answer = "SAME" if raw.startswith("SAME") else "DIFFERENT" if raw.startswith("DIFF") else \
                "UNSURE" if raw.startswith("UNSURE") else "OTHER"
            name_only.append({"set": data, "a": p["record_id_a"], "b": p["record_id_b"],
                              "name_a": a["name"], "name_b": b["name"], "raw": raw, "answer": answer,
                              "truth_same_person": ent[p["record_id_a"]] == ent[p["record_id_b"]]})
            print(f"{n:3d} {p['record_id_a']}/{p['record_id_b']} policy={p['recommendation']:<16} "
                  f"guard={res['status']}:{res['fallback_reason'] or res['recommendation']} name_only={answer}", flush=True)

    ok = [g for g in guarded if g["status"] == "model_ok"]
    diff_pairs = [x for x in name_only if not x["truth_same_person"]]
    same_pairs = [x for x in name_only if x["truth_same_person"]]
    reasons = {}
    for g in guarded:
        if g["status"] != "model_ok":
            reasons[g["fallback_reason"]] = reasons.get(g["fallback_reason"], 0) + 1
    summary = {
        "pairs": len(guarded),
        "guarded_review": {
            "accepted": len(ok), "rejected_and_fell_back": len(guarded) - len(ok), "rejection_reasons": reasons,
            "accepted_agree_with_policy": sum(g["model_recommendation"] == g["policy"] for g in ok),
            "accepted_downgraded_to_needs_review": sum(g["model_recommendation"] != g["policy"] for g in ok),
            "accepted_upgrades_over_policy": sum(g["model_recommendation"] not in (g["policy"], "needs_review") for g in ok),
            "seconds_total": round(t_guard, 1), "seconds_per_pair": round(t_guard / max(len(guarded), 1), 2)},
        "names_only": {
            "different_people_pairs": len(diff_pairs),
            "model_said_SAME_on_different_people": sum(x["answer"] == "SAME" for x in diff_pairs),
            "model_said_UNSURE_on_different_people": sum(x["answer"] == "UNSURE" for x in diff_pairs),
            "same_person_pairs": len(same_pairs),
            "model_said_SAME_on_same_person": sum(x["answer"] == "SAME" for x in same_pairs),
            "answers_not_parsable": sum(x["answer"] == "OTHER" for x in name_only),
            "seconds_total": round(t_name, 1), "seconds_per_pair": round(t_name / max(len(name_only), 1), 2)},
    }
    out = {"environment": info, "summary": summary, "guarded": guarded, "names_only": name_only}
    path = ROOT / "outputs" / "model_comparison.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2), "\nwrote", path)


if __name__ == "__main__":
    main(*(sys.argv[1:3] or [DEFAULT_MODEL]))
