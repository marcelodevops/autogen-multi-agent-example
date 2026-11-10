import os
import subprocess
import sys

import pytest


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("OPENAI_API_KEY", None)
    return subprocess.run(
        [sys.executable, "-m", "autogen_example", *args],
        capture_output=True,
        text=True,
        env=environment,
        timeout=30,
    )


def test_default_demo_needs_no_api_key() -> None:
    result = run_cli()
    assert result.returncode == 0, result.stderr
    for role in ("planner", "writer", "reviewer"):
        assert role in result.stdout
    assert "APPROVED" in result.stdout
    assert "scripted" in result.stdout


def test_live_mode_requires_api_key() -> None:
    result = run_cli("--live")
    assert result.returncode == 2
    assert "OPENAI_API_KEY" in result.stderr


@pytest.mark.parametrize("arguments", [("--max-turns", "0"), ("--task", " ")])
def test_invalid_arguments_are_reported(arguments: tuple[str, str]) -> None:
    result = run_cli(*arguments)
    assert result.returncode == 2
    assert "error:" in result.stderr
