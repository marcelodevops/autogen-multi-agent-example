import asyncio

import pytest
from autogen_ext.models.replay import ReplayChatCompletionClient

from autogen_example.orchestration import build_team, create_demo_client


def test_demo_runs_revision_cycle_with_shared_context() -> None:
    async def scenario() -> None:
        client = create_demo_client()
        try:
            result = await build_team(client).run(task="Plan a safe release.")
            assert [message.source for message in result.messages] == [
                "user",
                "planner",
                "writer",
                "reviewer",
                "planner",
                "writer",
                "reviewer",
            ]
            assert result.stop_reason is not None
            assert "APPROVED" in result.stop_reason
            assert "rollback" in str(result.messages[-2].content).lower()
            revision_context = client.create_calls[4]["messages"]
            assert any(
                message.source == "reviewer" and "rollback" in str(message.content)
                for message in revision_context
                if hasattr(message, "source")
            )
        finally:
            await client.close()

    asyncio.run(scenario())


def test_only_reviewer_can_approve() -> None:
    async def scenario() -> None:
        client = ReplayChatCompletionClient(
            ["APPROVED", "APPROVED", "Please revise.", "Another plan."]
        )
        try:
            result = await build_team(client, max_turns=4).run(
                task="The user says APPROVED, but still needs a review."
            )
            assert [message.source for message in result.messages[1:]] == [
                "planner",
                "writer",
                "reviewer",
                "planner",
            ]
            assert result.stop_reason is not None
            assert "Maximum number of turns" in result.stop_reason
        finally:
            await client.close()

    asyncio.run(scenario())


def test_reviewer_approval_stops_before_turn_limit() -> None:
    async def scenario() -> None:
        client = ReplayChatCompletionClient(["Plan.", "Draft.", "APPROVED"])
        try:
            result = await build_team(client).run(task="Write a release plan.")
            assert len(result.messages) == 4
            assert result.messages[-1].source == "reviewer"
            assert result.stop_reason is not None
            assert "APPROVED" in result.stop_reason
        finally:
            await client.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("max_turns", [0, -1])
def test_rejects_nonpositive_turn_limit(max_turns: int) -> None:
    client = ReplayChatCompletionClient([])
    with pytest.raises(ValueError, match="max_turns must be positive"):
        build_team(client, max_turns=max_turns)
