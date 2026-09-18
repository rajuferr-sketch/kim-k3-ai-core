"""Shared contract every one of the 15 agents implements."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

Status = Literal["ok", "error", "partial", "budget_exhausted", "refused", "skipped"]


@dataclass(slots=True)
class AgentResult:
    agent: str
    status: Status
    payload: dict[str, Any] = field(default_factory=dict)
    steps: int = 0
    credits: float = 0.0
    error: str | None = None
    citations: list[str] = field(default_factory=list)


class Blackboard(Protocol):
    """Shared, append-only workspace all agents read from and write to."""

    def put(self, agent: str, result: AgentResult) -> None: ...
    def get(self, agent: str) -> AgentResult | None: ...
    def snapshot(self) -> dict[str, AgentResult]: ...


@dataclass(slots=True)
class AgentContext:
    request: str
    blackboard: Blackboard
    provider: Any
    tools: Any
    memory: Any
    budget: Any
    trace: Any
    policy: Any
    locale: str = "en"


class Agent:
    """Base class. Subclasses set name/order/allowed_tools/limits and implement run()."""

    name: str = "agent"
    order: int = 99
    allowed_tools: tuple[str, ...] = ()
    max_steps: int = 10
    max_credits: float = 100.0
    model_tier: str = "balanced"
    step_cost: float = 5.0

    def system_prompt(self, ctx: AgentContext) -> str:  # pragma: no cover - overridden
        raise NotImplementedError

    async def run(self, ctx: AgentContext) -> AgentResult:  # pragma: no cover
        raise NotImplementedError

    def assert_tool_allowed(self, tool: str) -> None:
        if tool not in self.allowed_tools:
            raise PermissionError(f"{self.name} may not call tool {tool!r}")

    def partial(self, ctx: AgentContext, payload: dict[str, Any], reason: str) -> AgentResult:
        return AgentResult(agent=self.name, status="budget_exhausted", payload=payload, error=reason)

    # The following helpers are thin seams so tests can stub provider behaviour.
    def build_messages(self, ctx: AgentContext, payload: dict[str, Any]) -> list[dict[str, str]]:
        return [{"role": "user", "content": ctx.request}]

    def tool_schemas(self, ctx: AgentContext) -> list[dict[str, Any]]:
        return ctx.tools.schemas_for(self.allowed_tools)

    def parse(self, completion: Any) -> Any:
        return completion.parsed

    def merge(self, payload: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
        return {**payload, **output}

    def merge_tool_result(self, payload: dict[str, Any], tool_result: Any) -> dict[str, Any]:
        calls = list(payload.get("tool_calls", []))
        calls.append({"tool": tool_result.tool, "ok": tool_result.ok, "payload": tool_result.payload})
        return {**payload, "tool_calls": calls}
