import pytest

from agentkit import cost_report, llm, pipeline, reset_call_log, route


@pytest.fixture(autouse=True)
def clean_call_log():
    reset_call_log()
    yield
    reset_call_log()


def test_route_picks_correct_tier():
    assert route(hard=False) == "cheap"
    assert route(hard=True) == "strong"


def test_pipeline_runs_steps_in_order():
    executed = []

    def first(value):
        executed.append("first")
        return value + ["first"]

    def second(value):
        executed.append("second")
        return value + ["second"]

    result = pipeline(first, second)([])
    assert executed == ["first", "second"]
    assert result == ["first", "second"]


def test_cost_report_accumulates():
    assert cost_report()["calls"] == 0
    llm("short prompt", model="cheap")
    llm("a much longer prompt that should count more tokens", model="strong")
    report = cost_report()
    assert report["calls"] == 2
    assert report["tokens_by_model"]["cheap"] > 0
    assert report["tokens_by_model"]["strong"] > 0
    assert report["total_tokens"] == sum(report["tokens_by_model"].values())
    assert report["total_cost_usd"] > 0


def test_llm_is_deterministic_and_rejects_unknown_tier():
    assert llm("same prompt") == llm("same prompt")
    with pytest.raises(ValueError):
        llm("prompt", model="gpt-9")
