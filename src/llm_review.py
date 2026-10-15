"""Optional local-model layer. The model may only explain an already-generated pair.

Everything here is testable without a model: pass any generate_fn(prompt) -> str.
If the output is malformed, invents evidence, or contradicts the policy, we fall back
to the deterministic recommendation and flag it for human review."""
import json
import re

ALLOWED = {"likely_match", "needs_review", "likely_different"}
KEYS = {"recommendation", "supporting_evidence", "conflicting_evidence", "missing_evidence", "reasoning_summary"}
_TOKEN = re.compile(r"[\w.+-]+@[\w.-]+|\b[A-Za-z]\d{3,}\b")  # emails and ID-like tokens


def build_prompt(pair: dict, rec_a: dict, rec_b: dict) -> str:
    return (
        "You review one candidate pair of records. You do NOT decide identity.\n"
        "Use only the facts below. Never invent identifiers. Name similarity alone does not establish identity.\n"
        f"Record A: {json.dumps(rec_a, ensure_ascii=False)}\nRecord B: {json.dumps(rec_b, ensure_ascii=False)}\n"
        f"Matching identifiers: {pair['matching_ids'] or 'none'}; conflicting: {pair['conflicting_ids'] or 'none'}; "
        f"missing: {pair['missing_ids'] or 'none'}\nPolicy recommendation: {pair['recommendation']}\n"
        "Reply with JSON only, keys: recommendation (likely_match|needs_review|likely_different), "
        "supporting_evidence[], conflicting_evidence[], missing_evidence[], reasoning_summary."
    )


def _extract_json(text: str):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def validate(obj, policy_rec: str, source_text: str):
    """Returns (ok, reason). The model may match the policy or downgrade to needs_review, never upgrade."""
    if not isinstance(obj, dict) or not KEYS <= set(obj):
        return False, "malformed or missing keys"
    if obj["recommendation"] not in ALLOWED:
        return False, "invalid recommendation value"
    if obj["recommendation"] not in (policy_rec, "needs_review"):
        return False, "contradicts policy recommendation"
    lists = [obj["supporting_evidence"], obj["conflicting_evidence"], obj["missing_evidence"]]
    if not all(isinstance(x, list) and all(isinstance(i, str) for i in x) for x in lists):
        return False, "evidence fields must be lists of strings"
    if not isinstance(obj["reasoning_summary"], str):
        return False, "reasoning_summary must be a string"
    blob = " ".join(sum(lists, []) + [obj["reasoning_summary"]])
    src = source_text.casefold()
    for tok in (t.rstrip(".,;:") for t in _TOKEN.findall(blob)):  # sentence punctuation is not part of an identifier
        if tok.casefold() not in src:
            return False, f"invented identifier: {tok}"
    return True, "ok"


def review_pair(pair: dict, rec_a: dict, rec_b: dict, generate_fn):
    prompt = build_prompt(pair, rec_a, rec_b)
    source_text = json.dumps([rec_a, rec_b], ensure_ascii=False)
    try:
        obj = _extract_json(generate_fn(prompt))
    except Exception as exc:  # model load/inference failure must never break the app
        return _fallback(pair, f"model error: {type(exc).__name__}")
    ok, why = validate(obj, pair["recommendation"], source_text)
    if not ok:
        return _fallback(pair, why)
    return {"status": "model_ok", "fallback_reason": "", **{k: obj[k] for k in KEYS}}


def _fallback(pair, reason):
    return {"status": "fallback_to_policy", "fallback_reason": reason,
            "recommendation": pair["recommendation"], "supporting_evidence": [],
            "conflicting_evidence": [], "missing_evidence": [],
            "reasoning_summary": "Model output rejected; deterministic policy result shown. Human review required."}


def load_qwen_generate(model_id="Qwen/Qwen2.5-3B-Instruct", revision=None):
    """NOT exercised in the sandbox this repo was built in. Record model id, revision,
    hardware and timing yourself (docs/evaluation_protocol.md, Day 3)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer  # optional dependency
    tok = AutoTokenizer.from_pretrained(model_id, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(model_id, revision=revision, device_map="auto")

    def generate(prompt: str) -> str:
        msgs = [{"role": "user", "content": prompt}]
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(model.device)
        out = model.generate(ids, max_new_tokens=300, do_sample=False)
        return tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
    return generate
