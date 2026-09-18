# Research Agent

**Pipeline position:** 3 of 15 &middot; **Manifest:** [`agents/research.yaml`](../../agents/research.yaml) &middot; **Implementation:** [`src/kim_k3/agents/research_agent.py`](../../src/kim_k3/agents/research_agent.py)

## Role

Finds information, primary sources and data relevant to the request.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Derive search queries from the objective.
2. Retrieve and deduplicate sources, keep provenance (url, title, retrieved_at).
3. Summarise each source into evidence items with confidence and quote spans.
4. Flag contradictions between sources instead of silently picking one.

## Inputs

- objective
- known constraints
- memory recall bundle

## Outputs

- Evidence[] with provenance and confidence

## Tools allowed

- `web.search`
- `web.fetch`
- `memory.recall`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 12 |
| Max credits | 150 |
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
from kim_k3.agents.research_agent import ResearchAgent
from kim_k3.agents.base import AgentContext

result = await ResearchAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "research"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
