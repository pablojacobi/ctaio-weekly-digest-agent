# Working rules — 40-min agentic test

- Respond to me in Spanish; code, identifiers, and code-facing text in English.
- Hard timebox: ~40 minutes total. Speed over polish; a working partial slice beats a
  complete design. Never gold-plate, never refactor what already works.
- I drive: propose in 2-3 lines max, then build. Never block waiting for approval on
  small calls — make them and note them. I review everything before it ships.
- Build ON TOP of the existing `agentkit.py` (llm/route/pipeline/log/cost_report).
  Everything must run offline with mocked tools (named stub functions, no API keys).
- Code quality: self-documenting names, small functions, no inline `#` comments.
- Commit small and conventional as we go — the history tells the story.
- Tests only where they're cheap and prove core decision logic; skip plumbing. `python
  main.py` must always run end to end.
- PASTE-READY OUTPUT (key): the deliverable gets pasted into a browser form. When asked,
  consolidate the final code into one self-contained, ordered block (single file view,
  run instructions in the README/docstring), ready to copy.
- Never fabricate domain facts or fake results; mocks must be obviously mocks.
