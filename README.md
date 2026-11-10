# AutoGen multi-agent orchestration

A small Python example using Microsoft's **AutoGen AgentChat**, not the legacy
`pyautogen` API. Three agents collaborate on a release plan, sharing conversation
history and revising the draft until the reviewer approves or the turn limit
is reached.

```text
User task -> Planner -> Writer -> Reviewer
                ^                    |
                |--- revise ---------|
                                     +-> APPROVED -> stop
```

The team uses `RoundRobinGroupChat`: agents speak sequentially, not in parallel.
The same team works with a scripted replay client or a live OpenAI model.

## Run offline

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/marcelodevops/autogen-multi-agent-example.git
cd autogen-multi-agent-example
uv sync --frozen
uv run autogen-example
```

No API key or model requests are needed for the default demo. Initial dependency
installation needs network access. The six scripted responses show a plan, draft,
review requesting rollback details, revised plan, revised draft, and approval.
Replay illustrates orchestration; it does **not** generate an answer to arbitrary
tasks. Use live mode for that.

## Run with a live model

```bash
export OPENAI_API_KEY='your-key'
export OPENAI_MODEL='gpt-4o-mini'  # optional
uv run autogen-example --live \
  --task "Write a safe deployment checklist for a small web API." \
  --max-turns 9
```

`--model` overrides `OPENAI_MODEL`. `.env.example` documents the variables;
`.env` files are not loaded automatically. Never commit your API key.
Live mode sends your task and conversation to OpenAI and incurs API usage charges.
No live model calls are made by tests or CI.

## How it works

| Component | Responsibility |
| --- | --- |
| `planner` | Break the task down and incorporate review feedback |
| `writer` | Produce or revise the deliverable using the shared conversation |
| `reviewer` | Request concrete changes or emit `APPROVED` |
| `RoundRobinGroupChat` | Select the next speaker in fixed order |
| `TextMentionTermination` | Stop on `APPROVED` from the reviewer only |
| `max_turns` | Bound agent turns even when approval never arrives |

The default cap is nine **agent turns**, not nine rounds. Approval is
case-sensitive substring matching in a reviewer message; it is a teaching
convention, not a reliable structured validation or human approval mechanism.
The Console output includes the stop reason: reaching the cap is not approval.
There is no code execution, shell access, browsing, or infrastructure access.
The model client is closed even when a run fails; API/network failures surface
instead of silently switching to replay.

The core implementation is in `src/autogen_example/orchestration.py`; the CLI
is in `src/autogen_example/__main__.py`. Run `uv run python -m autogen_example`
as an alternative entry point.

## Development

```bash
uv sync --frozen
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

Tests exercise the actual AutoGen team with replayed model responses: speaker
order, shared review context, early approval, ignored non-reviewer approval,
turn limits, and CLI validation.

## Graphify

This repository uses the `graphify` skill for code exploration. With the Python
Graphify CLI installed, generate a local AST-only graph without API calls:

```bash
graphify update .
graphify query "How does the reviewer stop the team?"
```

Generated graph artifacts stay local and are ignored by Git.

## References

- [AutoGen team tutorial](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
- [Replay model client](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.models.replay.html)
- [Termination conditions](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html)
