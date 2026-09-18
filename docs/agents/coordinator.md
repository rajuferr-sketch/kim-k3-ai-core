# Coordinator Agent

**Pipeline position:** 2 of 15 &middot; **Manifest:** [`agents/coordinator.yaml`](../../agents/coordinator.yaml) &middot; **Implementation:** [`src/kim_k3/agents/coordinator_agent.py`](../../src/kim_k3/agents/coordinator_agent.py)

## Role

Assigns tasks to the other agents and owns the execution flow of the run.

Always second. Never skipped.

## Responsibilities

1. Build the execution graph from the routing decision.
2. Dispatch tasks, honour dependencies, run independent agents concurrently.
3. Re-dispatch on agent failure, escalate when the budget guard refuses a call.
4. Own the run state machine and emit the run trace.

## Inputs

- RoutingDecision
- agent registry
- run context

## Outputs

- RunPlan and ordered AgentResult list

## Tools allowed

- `registry.read`
- `run.state`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 24 |
| Max credits | 120 |
| Timeout | 360s |
| Delegation depth | 1 |

The budget guard authorises every provider call before it is issued. When the cap is reached the agent returns a partial result flagged `budget_exhausted` instead of silently stopping.

## Failure modes

- **Empty output** - the Coordinator retries once with the previous output attached; a second empty output fails the agent.
- **Malformed schema** - the result is rejected, the Critic is notified and the agent is re-run with the schema error appended.
- **Policy hit** - control transfers to the Safety Agent, which decides between constraints, approval or refusal.
- **Budget exhausted** - the run continues with a partial result and the Evaluator lowers the completeness score.

## Contract

```python
from kim_k3.agents.coordinator_agent import CoordinatorAgent
from kim_k3.agents.base import AgentContext

result = await CoordinatorAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "coordinator"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
