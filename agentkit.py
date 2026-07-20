import hashlib
import json
import sys
import time

MODEL_TIERS = ("cheap", "strong")

COST_PER_1K_TOKENS = {
    "cheap": 0.0005,
    "strong": 0.015,
}

_call_log: list[dict] = []


def log(msg: str, **fields) -> None:
    entry = {"ts": round(time.time(), 3), "msg": msg, **fields}
    print(json.dumps(entry, ensure_ascii=False), file=sys.stderr)


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def llm(prompt: str, model: str = "cheap") -> str:
    if model not in MODEL_TIERS:
        raise ValueError(f"unknown model tier: {model!r}, expected one of {MODEL_TIERS}")
    digest = hashlib.sha256(prompt.encode()).hexdigest()[:8]
    response = f"[{model}:{digest}] stub response for: {prompt[:60]}"
    tokens = _approx_tokens(prompt) + _approx_tokens(response)
    _call_log.append({"model": model, "tokens": tokens, "prompt": prompt[:120]})
    log("llm_call", model=model, tokens=tokens)
    return response


def route(hard: bool) -> str:
    return "strong" if hard else "cheap"


def pipeline(*steps):
    def run(value=None):
        for step in steps:
            started = time.perf_counter()
            value = step(value)
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            log("step_done", step=step.__name__, latency_ms=elapsed_ms)
        return value

    return run


def cost_report() -> dict:
    total_tokens = sum(call["tokens"] for call in _call_log)
    tokens_by_model = {tier: 0 for tier in MODEL_TIERS}
    for call in _call_log:
        tokens_by_model[call["model"]] += call["tokens"]
    total_cost = sum(
        tokens_by_model[tier] / 1000 * COST_PER_1K_TOKENS[tier] for tier in MODEL_TIERS
    )
    return {
        "calls": len(_call_log),
        "total_tokens": total_tokens,
        "tokens_by_model": tokens_by_model,
        "total_cost_usd": round(total_cost, 6),
    }


def reset_call_log() -> None:
    _call_log.clear()
