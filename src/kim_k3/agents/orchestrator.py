"""Orchestrator: activates all 15 agents for every request.

Flow (see docs/multi-agent-pipeline.md):

    router -> coordinator -> safety(pre-flight) -> memory(recall)
      -> research | planner -> reasoning -> data -> coding -> tool -> executor
      -> critic -> verifier -> safety(pre-commit) -> evaluator
      -> [revision loop, max 2] -> memory(consolidate) -> synthesizer
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from kim_k3.agents.base import AgentContext, AgentResult
from kim_k3.agents import registry

MAX_REVISIONS = 2

#: Agents that may run concurrently once their inputs exist.
CONCURRENT_GROUPS: tuple[tuple[str, ...], ...] = (
    ("research", "planner"),
    ("data", "coding"),
    ("critic", "verifier"),
)


@dataclass(slots=True)
class DictBlackboard:
    _items: dict[str, AgentResult] = field(default_factory=dict)

    def put(self, agent: str, result: AgentResult) -> None:
        self._items[agent] = result

    def get(self, agent: str) -> AgentResult | None:
        return self._items.get(agent)

    def snapshot(self) -> dict[str, AgentResult]:
        return dict(self._items)


class Orchestrator:
    """Runs the full 15-agent pipeline for one request."""

    def __init__(self, **services: Any) -> None:
        self.services = services

    async def run(self, request: str, locale: str = "en") -> AgentResult:
        board = DictBlackboard()
        ctx = AgentContext(request=request, blackboard=board, locale=locale, **self.services)

        await registry.get("router").run(ctx)
        await registry.get("coordinator").run(ctx)

        safety = await registry.get("safety").run(ctx)
        if safety.payload.get("decision") == "refuse":
            return await registry.get("synthesizer").run(ctx)

        await registry.get("memory").run(ctx)

        for group in CONCURRENT_GROUPS[:1]:
            await asyncio.gather(*(registry.get(n).run(ctx) for n in group))
        await registry.get("reasoning").run(ctx)
        for group in CONCURRENT_GROUPS[1:2]:
            await asyncio.gather(*(registry.get(n).run(ctx) for n in group))
        await registry.get("tool").run(ctx)
        await registry.get("executor").run(ctx)

        for _ in range(MAX_REVISIONS + 1):
            await asyncio.gather(*(registry.get(n).run(ctx) for n in CONCURRENT_GROUPS[2]))
            await registry.get("safety").run(ctx)
            evaluation = await registry.get("evaluator").run(ctx)
            if evaluation.payload.get("verdict") in ("pass", "fail"):
                break
            await registry.get("planner").run(ctx)  # re-plan, then loop

        await registry.get("memory").run(ctx)
        return await registry.get("synthesizer").run(ctx)
