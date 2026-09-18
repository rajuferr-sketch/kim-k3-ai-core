# Memory Agent

**Pipeline position:** 13 of 15 &middot; **Manifest:** [`agents/memory.yaml`](../../agents/memory.yaml) &middot; **Implementation:** [`src/kim_k3/agents/memory_agent.py`](../../src/kim_k3/agents/memory_agent.py)

## Role

Manages context, relevant information and the state of the work.

Runs at the start (recall) and at the end (consolidate).

## Responsibilities

1. Recall working, episodic and semantic memory relevant to the request.
2. Keep the shared blackboard compact: summarise, never truncate blindly.
3. Promote durable facts to semantic memory deliberately, with provenance.
4. Expose run state so a resumed run does not repeat finished work.

## Inputs

- request
- run trace
- agent outputs

## Outputs

- MemoryBundle: recalled items, working summary, promotions

## Tools allowed

- `memory.recall`
- `memory.write`
- `memory.promote`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 12 |
| Max credits | 120 |
| Timeout | 180s |
| Delegation depth | 1 |

The budget guard authorises every provider call before it is issued. When the cap is reached the agent returns a partial result flagged `budget_exhausted` instead of silently stopping.

## Failure modes

- **Empty output** - the Coordinator retries once with the previous output attached; a second empty output fails the agent.
- **Malformed schema** - the result is rejected, the Critic is notified and the agent is re-run with the schema error appended.
- **Policy hit** - control transfers to the Safety Agent, which decides between constraints, approval or refusal.
- **Budget exhausted** - the run continues with a partial result and the Evaluator lowers the completeness score.

## Contract

```python
from kim_k3.agents.memory_agent import MemoryAgent
from kim_k3.agents.base import AgentContext

result = await MemoryAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "memory"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
