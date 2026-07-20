# ctaio.dev — weekly digest agent workflow

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
