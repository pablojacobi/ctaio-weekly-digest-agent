from main import (
    SUBJECT_MAX_CHARS,
    find_digest_issues,
    rebuild_digest_deterministic,
    validate_digest,
)

ITEMS = [
    {"title": "Item A", "source": "mock://a", "summary": "summary A " * 10},
    {"title": "Item B", "source": "mock://b", "summary": "summary B " * 10},
]


def build_digest(subject: str) -> dict:
    body = "\n\n".join(f"## {i['title']}\n{i['summary']}" for i in ITEMS)
    return {"subject": subject, "body": body, "items": ITEMS}


def test_valid_digest_has_no_issues():
    assert find_digest_issues(build_digest("Weekly digest")) == []


def test_overlong_subject_is_flagged():
    digest = build_digest("x" * (SUBJECT_MAX_CHARS + 1))
    assert "subject_missing_or_too_long" in find_digest_issues(digest)


def test_missing_item_is_flagged():
    digest = build_digest("Weekly digest")
    digest["body"] = digest["body"].replace("Item B", "Item ?")
    assert any(i.startswith("item_missing_from_body") for i in find_digest_issues(digest))


def test_deterministic_fallback_passes_validation():
    fallback = rebuild_digest_deterministic(ITEMS)
    assert find_digest_issues(fallback) == []


def test_validate_repairs_invalid_subject_via_fallback():
    repaired = validate_digest(build_digest("x" * 200))
    assert len(repaired["subject"]) <= SUBJECT_MAX_CHARS
    assert find_digest_issues(repaired) == []
