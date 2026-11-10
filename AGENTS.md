# Contributor guidance

Use the `graphify` skill when exploring this repository.
When `graphify-out/graph.json` exists, start codebase questions with
`graphify query "<question>"`. After code changes run `graphify update .`.
Use the existing Python Graphify installation; do not replace or reinstall it.

Keep the example focused on AutoGen AgentChat round-robin orchestration.
Offline demo and tests must not make model API calls.
Never commit credentials or `.env` files.

Before committing, run:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
