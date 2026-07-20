"""Weekly digest agent workflow for ctaio.dev (CTO/CIO audience).

Pipeline: fetch_feed_items -> summarize_items -> compose_digest -> validate_digest -> publish_digest
Runs fully offline: the LLM is mocked in agentkit.py and the feed is a static stub.
Run: python3 main.py
"""

import json
from pathlib import Path

from agentkit import cost_report, llm, log, pipeline, route

MOCK_FEED = [
    {"title": "EU AI Act enforcement timeline", "source": "mock://policy-watch", "hard": True},
    {"title": "GPU spend benchmarks", "source": "mock://infra-digest", "hard": False},
    {"title": "Agent framework consolidation", "source": "mock://oss-radar", "hard": False},
]

SUBJECT_MAX_CHARS = 80
MIN_BODY_WORDS = 40
OUTBOX_DIR = Path("out")


def fetch_feed_items(_=None) -> list[dict]:
    log("feed_fetched", count=len(MOCK_FEED), note="static mock feed, no network")
    return list(MOCK_FEED)


def summarize_items(items: list[dict]) -> list[dict]:
    summarized = []
    for item in items:
        summary = llm(
            f"Summarize for a CTO audience: {item['title']}",
            model=route(hard=item["hard"]),
        )
        summarized.append({**item, "summary": summary})
    return summarized


def compose_digest(items: list[dict]) -> dict:
    subject = llm(
        "Write a compelling subject line for this week's CTAIO executive digest",
        model=route(hard=True),
    )
    body = "\n\n".join(
        f"## {item['title']}\n{item['summary']}\n(source: {item['source']})"
        for item in items
    )
    return {"subject": subject.strip(), "body": body, "items": items}


def find_digest_issues(digest: dict) -> list[str]:
    issues = []
    if not digest["subject"] or len(digest["subject"]) > SUBJECT_MAX_CHARS:
        issues.append("subject_missing_or_too_long")
    for item in digest["items"]:
        if item["title"] not in digest["body"]:
            issues.append(f"item_missing_from_body:{item['title']}")
    if len(digest["body"].split()) < MIN_BODY_WORDS:
        issues.append("body_below_min_words")
    return issues


def rebuild_digest_deterministic(items: list[dict]) -> dict:
    subject = f"[mock fallback] CTAIO weekly: {items[0]['title']}"[:SUBJECT_MAX_CHARS]
    body = "\n\n".join(
        f"## {item['title']}\n{item['summary']}\n(source: {item['source']})"
        for item in items
    )
    return {"subject": subject, "body": body, "items": items}


def validate_digest(digest: dict) -> dict:
    issues = find_digest_issues(digest)
    if issues:
        log("validation_failed", issues=issues, action="deterministic_fallback")
        digest = rebuild_digest_deterministic(digest["items"])
        issues = find_digest_issues(digest)
        if issues:
            raise ValueError(f"digest invalid after fallback: {issues}")
    log("validation_passed", subject=digest["subject"])
    return digest


def publish_digest(digest: dict) -> dict:
    OUTBOX_DIR.mkdir(exist_ok=True)
    artifact = OUTBOX_DIR / "weekly_digest.md"
    artifact.write_text(f"# {digest['subject']}\n\n{digest['body']}\n")
    log("digest_published", artifact=str(artifact), delivery="mock (no email sent)")
    return {"artifact": str(artifact), "subject": digest["subject"]}


def main() -> None:
    log("run_start", workflow="ctaio_weekly_digest")
    weekly_digest = pipeline(
        fetch_feed_items,
        summarize_items,
        compose_digest,
        validate_digest,
        publish_digest,
    )
    result = weekly_digest()
    log("run_end", **result)
    print(json.dumps(cost_report(), indent=2))


if __name__ == "__main__":
    main()
