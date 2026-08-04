import asyncio
from pathlib import Path
from unittest import mock

from gateway.config import GatewayConfig
from gateway.run import GatewayRunner


def test_routed_turn_discovers_mcp_inside_selected_profile(monkeypatch, tmp_path):
    runner = GatewayRunner.__new__(GatewayRunner)
    runner.config = GatewayConfig(multiplex_profiles=True)
    runner._run_agent_inner = mock.AsyncMock(return_value={"completed": True})
    source = mock.MagicMock(profile="project-a")
    profile_home = tmp_path / "project-a"
    profile_home.mkdir()
    seen_homes = []

    def discover():
        from hermes_constants import get_hermes_home

        seen_homes.append(Path(get_hermes_home()))
        return []

    monkeypatch.setattr(
        runner, "_resolve_profile_home_for_source", lambda _source: profile_home
    )
    monkeypatch.setattr("tools.mcp_tool.discover_mcp_tools", discover)

    asyncio.run(
        runner._run_agent(
            "hello", "", [], source, "session-a"
        )
    )

    assert seen_homes == [profile_home]
    runner._run_agent_inner.assert_awaited_once()
