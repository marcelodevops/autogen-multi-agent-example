import argparse
import asyncio
import os

from autogen_agentchat.ui import Console
from autogen_core.models import ChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient

from autogen_example.orchestration import (
    DEFAULT_TASK,
    build_team,
    create_demo_client,
)


async def run(*, live: bool, model: str, task: str, max_turns: int) -> None:
    client: ChatCompletionClient
    if live:
        print(f"Live mode: {model} (OpenAI API usage charges apply).")
        client = OpenAIChatCompletionClient(model=model, timeout=60, max_retries=2)
    else:
        print("Offline demo: scripted responses, real AutoGen orchestration.")
        client = create_demo_client()

    try:
        team = build_team(client, max_turns=max_turns)
        result = await Console(team.run_stream(task=task))
        print(f"\nStop reason: {result.stop_reason}")
    finally:
        await client.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an AutoGen planner/writer/reviewer team (offline by default)."
    )
    parser.add_argument(
        "--live", action="store_true", help="Use OpenAI instead of scripted replay."
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
        help="OpenAI model for live mode (default: OPENAI_MODEL or gpt-4o-mini).",
    )
    parser.add_argument(
        "--task",
        default=DEFAULT_TASK,
        help="Task for the team; replay responses remain fixed in offline mode.",
    )
    parser.add_argument(
        "--max-turns", type=int, default=9, help="Positive agent-turn cap (default: 9)."
    )
    args = parser.parse_args()
    if args.max_turns < 1:
        parser.error("--max-turns must be positive")
    if not args.task.strip():
        parser.error("--task must not be blank")
    if not args.model.strip():
        parser.error("--model must not be blank")
    if args.live and not os.getenv("OPENAI_API_KEY", "").strip():
        parser.error("Live mode requires OPENAI_API_KEY to be exported in your shell")

    asyncio.run(
        run(
            live=args.live,
            model=args.model,
            task=args.task,
            max_turns=args.max_turns,
        )
    )


if __name__ == "__main__":
    main()
