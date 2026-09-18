"""Registry of the 15 mandatory agents.

Every incoming request activates all agents listed here, in ``order``.
Disabling an agent is a deliberate configuration change in ``agents/pipeline.yaml``,
never an implicit runtime decision.
"""

from __future__ import annotations

from kim_k3.agents.base import Agent
from kim_k3.agents.router_agent import RouterAgent
from kim_k3.agents.coordinator_agent import CoordinatorAgent
from kim_k3.agents.research_agent import ResearchAgent
from kim_k3.agents.planner_agent import PlannerAgent
from kim_k3.agents.reasoning_agent import ReasoningAgent
from kim_k3.agents.data_agent import DataAgent
from kim_k3.agents.coding_agent import CodingAgent
from kim_k3.agents.tool_agent import ToolAgent
from kim_k3.agents.executor_agent import ExecutorAgent
from kim_k3.agents.critic_agent import CriticAgent
from kim_k3.agents.verifier_agent import VerifierAgent
from kim_k3.agents.safety_agent import SafetyAgent
from kim_k3.agents.memory_agent import MemoryAgent
from kim_k3.agents.evaluator_agent import EvaluatorAgent
from kim_k3.agents.synthesizer_agent import SynthesizerAgent

AGENT_CLASSES: dict[str, type[Agent]] = {
    "router": RouterAgent,
    "coordinator": CoordinatorAgent,
    "research": ResearchAgent,
    "planner": PlannerAgent,
    "reasoning": ReasoningAgent,
    "data": DataAgent,
    "coding": CodingAgent,
    "tool": ToolAgent,
    "executor": ExecutorAgent,
    "critic": CriticAgent,
    "verifier": VerifierAgent,
    "safety": SafetyAgent,
    "memory": MemoryAgent,
    "evaluator": EvaluatorAgent,
    "synthesizer": SynthesizerAgent,
}

#: Canonical activation order for a full run.
PIPELINE_ORDER: tuple[str, ...] = tuple(
    name for name, _ in sorted(
        ((n, c.order) for n, c in AGENT_CLASSES.items()), key=lambda kv: kv[1]
    )
)


def build_all() -> list[Agent]:
    """Instantiate all 15 agents in pipeline order."""
    return [AGENT_CLASSES[name]() for name in PIPELINE_ORDER]


def get(name: str) -> Agent:
    try:
        return AGENT_CLASSES[name]()
    except KeyError as exc:  # pragma: no cover - defensive
        raise KeyError(f"unknown agent {name!r}; known: {sorted(AGENT_CLASSES)}") from exc
