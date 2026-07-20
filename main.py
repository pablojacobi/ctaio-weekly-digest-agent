import json

from agentkit import cost_report, llm, log, pipeline, route


def draft(topic: str) -> str:
    return llm(f"Draft a short piece about: {topic}", model=route(hard=False))


def refine(draft_text: str) -> str:
    return llm(f"Refine this draft: {draft_text}", model=route(hard=True))


def main() -> None:
    log("run_start", pipeline="demo")
    demo = pipeline(draft, refine)
    result = demo("agentic workflows")
    log("run_end", result_preview=result[:80])
    print(json.dumps(cost_report(), indent=2))


if __name__ == "__main__":
    main()
