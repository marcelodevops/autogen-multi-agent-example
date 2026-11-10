from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import ChatCompletionClient
from autogen_ext.models.replay import ReplayChatCompletionClient

DEFAULT_TASK = "Write a concise, safe release plan for a small web API."


def build_team(client: ChatCompletionClient, max_turns: int = 9) -> RoundRobinGroupChat:
    if max_turns < 1:
        raise ValueError("max_turns must be positive")

    planner = AssistantAgent(
        "planner",
        model_client=client,
        system_message=(
            "You are the planner. Break the user's task into a concise plan. "
            "On later turns, update the plan to address the reviewer's feedback. "
            "Leave writing the deliverable to the writer."
        ),
    )
    writer = AssistantAgent(
        "writer",
        model_client=client,
        system_message=(
            "You are the writer. Produce the requested deliverable using the "
            "planner's plan and the shared conversation. On later turns, revise "
            "the deliverable to address all reviewer feedback. Return the full "
            "deliverable, not just a description of your changes."
        ),
    )
    reviewer = AssistantAgent(
        "reviewer",
        model_client=client,
        system_message=(
            "You are the reviewer. Check the writer's deliverable against the "
            "user's task for completeness, accuracy, and actionable detail. "
            "If changes are needed, give concrete feedback without using the "
            "approval marker. If it is acceptable, respond with exactly APPROVED."
        ),
    )
    return RoundRobinGroupChat(
        [planner, writer, reviewer],
        termination_condition=TextMentionTermination("APPROVED", sources=["reviewer"]),
        max_turns=max_turns,
    )


def create_demo_client() -> ReplayChatCompletionClient:
    return ReplayChatCompletionClient(
        [
            "Plan: validate the build, deploy gradually, then verify service health.",
            (
                "Draft: 1. Run tests and build the release. "
                "2. Deploy to staging, then canary production. "
                "3. Monitor error rate and latency before completing the rollout."
            ),
            (
                "Please revise: add a rollback trigger, an owner, and steps to "
                "restore the previous version."
            ),
            (
                "Revised plan: retain build validation and gradual rollout; add "
                "the on-call owner, a rollback trigger, and recovery verification."
            ),
            (
                "Release plan:\n"
                "1. Release owner runs tests and records the last healthy version.\n"
                "2. On-call engineer validates staging and deploys a 5% canary.\n"
                "3. Observe for 10 minutes; expand only if health checks pass, "
                "5xx rate stays below 1%, and p95 latency stays below 500 ms.\n"
                "4. If any gate fails, the on-call engineer stops the rollout "
                "and rolls back to the recorded healthy version.\n"
                "5. Verify health checks and metrics after rollback or completion.\n"
                "Example thresholds must be adapted to the service's actual SLOs."
            ),
            "APPROVED",
        ]
    )
