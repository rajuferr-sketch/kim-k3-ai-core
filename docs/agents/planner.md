# Planner Agent

**Pipeline position:** 4 of 15 &middot; **Manifest:** [`agents/planner.yaml`](../../agents/planner.yaml) &middot; **Implementation:** [`src/kim_k3/agents/planner_agent.py`](../../src/kim_k3/agents/planner_agent.py)

## Role

Decomposes the problem into objectives, ordered steps and acceptance criteria.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Restate the request as a measurable goal.
2. Split the goal into steps with owner agent, inputs and done-criteria.
3. Mark parallelisable steps and hard dependencies.
4. Re-plan when the Critic or Evaluator rejects the current plan.

## Inputs

- request
- routing decision
- evidence

## Outputs

- Plan: steps[] with owner, inputs, acceptance criteria, risk

## Tools allowed

- `memory.recall`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 10 |
| Max credits | 90 |
| Timeout | 150s |
| Delegation depth | 1 |

The budget guard authorises every provider call before it is issued. When the cap is reached the agent returns a partial result flagged `budget_exhausted` instead of silently stopping.

## Failure modes

- **Empty output** - the Coordinator retries once with the previous output attached; a second empty output fails the agent.
- **Malformed schema** - the result is rejected, the Critic is notified and the agent is re-run with the schema error appended.
- **Policy hit** - control transfers to the Safety Agent, which decides between constraints, approval or refusal.
- **Budget exhausted** - the run continues with a partial result and the Evaluator lowers the completeness score.

## Contract

```python
from kim_k3.agents.planner_agent import PlannerAgent
from kim_k3.agents.base import AgentContext

result = await PlannerAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "planner"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
