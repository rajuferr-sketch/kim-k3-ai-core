# Router Agent

**Pipeline position:** 1 of 15 &middot; **Manifest:** [`agents/router.yaml`](../../agents/router.yaml) &middot; **Implementation:** [`src/kim_k3/agents/router_agent.py`](../../src/kim_k3/agents/router_agent.py)

## Role

Decides which agents and which model tier every incoming request needs.

Always first. Never skipped.

## Responsibilities

1. Classify the request (intent, domain, risk, complexity).
2. Select the model tier (fast / balanced / deep) per downstream agent.
3. Produce the activation plan: which of the 15 agents run, in which order, with which budget share.
4. Short-circuit trivial requests to a minimal path while still recording the decision.

## Inputs

- raw user request
- tenant policy
- credit budget for the run

## Outputs

- RoutingDecision: activated agents, model tiers, per-agent credit caps

## Tools allowed

- `policy.read`
- `catalog.models`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 6 |
| Max credits | 40 |
| Timeout | 90s |
| Delegation depth | 1 |

The budget guard authorises every provider call before it is issued. When the cap is reached the agent returns a partial result flagged `budget_exhausted` instead of silently stopping.

## Failure modes

- **Empty output** - the Coordinator retries once with the previous output attached; a second empty output fails the agent.
- **Malformed schema** - the result is rejected, the Critic is notified and the agent is re-run with the schema error appended.
- **Policy hit** - control transfers to the Safety Agent, which decides between constraints, approval or refusal.
- **Budget exhausted** - the run continues with a partial result and the Evaluator lowers the completeness score.

## Contract

```python
from kim_k3.agents.router_agent import RouterAgent
from kim_k3.agents.base import AgentContext

result = await RouterAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "router"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
