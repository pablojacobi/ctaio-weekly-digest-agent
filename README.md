# ctaio.dev — weekly digest agent workflow

[![ci](https://github.com/pablojacobi/ctaio-weekly-digest-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/pablojacobi/ctaio-weekly-digest-agent/actions/workflows/ci.yml)

Multi-step agentic pipeline that assembles a weekly executive digest for ctaio.dev
(CTO/CIO audience). 100% offline: the LLM and the feed are mocked, no API keys.

## Pipeline

`fetch_feed_items → summarize_items → compose_digest → validate_digest → publish_digest`

1. **fetch_feed_items** — pulls the week's items (static mock feed).
2. **summarize_items** — one LLM call per item; `route()` picks the cheap or strong
   model tier based on item complexity.
3. **compose_digest** — strong-tier LLM writes the subject line; body is assembled
   from the per-item summaries.
4. **validate_digest** — deterministic editorial rules (subject length, every item
   present in body, minimum word count). On failure it repairs via a deterministic
   fallback rebuild and re-validates; unrecoverable digests raise.
5. **publish_digest** — writes `out/weekly_digest.md` (mock delivery, no email sent).

Every step emits structured JSON logs (latency, model tier, tokens) and the run ends
with a cost report per model tier.

## Run

- `make run` — end-to-end pipeline (`python3 main.py`)
- `make test` — pytest
- `make check` — ruff + pytest

## Sample run

The validation failure below is intentional and visible by design: the mock LLM's
subject line exceeds the 80-char editorial limit, the gate catches it, and the
deterministic fallback repairs the digest before publishing.

```
{"msg": "run_start", "workflow": "ctaio_weekly_digest"}
{"msg": "feed_fetched", "count": 3, "note": "static mock feed, no network"}
{"msg": "step_done", "step": "fetch_feed_items", "latency_ms": 0.01}
{"msg": "llm_call", "model": "strong", "tokens": 39}
{"msg": "llm_call", "model": "cheap", "tokens": 33}
{"msg": "llm_call", "model": "cheap", "tokens": 37}
{"msg": "step_done", "step": "summarize_items", "latency_ms": 0.04}
{"msg": "llm_call", "model": "strong", "tokens": 41}
{"msg": "step_done", "step": "compose_digest", "latency_ms": 0.01}
{"msg": "validation_failed", "issues": ["subject_missing_or_too_long"], "action": "deterministic_fallback"}
{"msg": "validation_passed", "subject": "[mock fallback] CTAIO weekly: EU AI Act enforcement timeline"}
{"msg": "digest_published", "artifact": "out/weekly_digest.md", "delivery": "mock (no email sent)"}
```

Final cost report on stdout:

```json
{
  "calls": 4,
  "total_tokens": 150,
  "tokens_by_model": {"cheap": 70, "strong": 80},
  "total_cost_usd": 0.001235
}
```
