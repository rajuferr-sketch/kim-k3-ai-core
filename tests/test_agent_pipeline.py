"""The 15-agent contract is enforced by tests, not by convention."""

from __future__ import annotations

import pathlib

import pytest
import yaml

from kim_k3.agents import registry

REPO = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = ['coding', 'coordinator', 'critic', 'data', 'evaluator', 'executor', 'memory', 'planner', 'reasoning', 'research', 'router', 'safety', 'synthesizer', 'tool', 'verifier']


def test_all_fifteen_agents_are_registered() -> None:
    assert sorted(registry.AGENT_CLASSES) == EXPECTED
    assert len(registry.PIPELINE_ORDER) == 15


def test_pipeline_order_is_unique_and_dense() -> None:
    orders = [registry.AGENT_CLASSES[n].order for n in registry.PIPELINE_ORDER]
    assert orders == sorted(orders)
    assert len(set(orders)) == 15


@pytest.mark.parametrize("name", EXPECTED)
def test_each_agent_has_manifest_and_doc(name: str) -> None:
    assert (REPO / "agents" / f"{name}.yaml").is_file()
    assert (REPO / "docs" / "agents" / f"{name}.md").is_file()
    assert (REPO / "src" / "kim_k3" / "agents" / f"{name}_agent.py").is_file()


@pytest.mark.parametrize("name", EXPECTED)
def test_manifest_matches_implementation(name: str) -> None:
    manifest = yaml.safe_load((REPO / "agents" / f"{name}.yaml").read_text())
    agent = registry.get(name)
    assert manifest["name"] == agent.name
    assert manifest["order"] == agent.order
    assert manifest["always_activate"] is True
    assert manifest["limits"]["max_steps"] == agent.max_steps
    assert manifest["limits"]["max_credits"] == agent.max_credits
    assert tuple(manifest["tools"]) == agent.allowed_tools


def test_pipeline_yaml_covers_every_agent() -> None:
    pipeline = yaml.safe_load((REPO / "agents" / "pipeline.yaml").read_text())
    staged = {a for stage in pipeline["stages"] for a in stage["agents"]}
    assert staged == set(EXPECTED)
    assert set(pipeline["budgets"]) == set(EXPECTED)
    assert pipeline["activation"] == "all"


@pytest.mark.parametrize("name", EXPECTED)
def test_agents_refuse_unlisted_tools(name: str) -> None:
    agent = registry.get(name)
    with pytest.raises(PermissionError):
        agent.assert_tool_allowed("definitely.not.allowed")
