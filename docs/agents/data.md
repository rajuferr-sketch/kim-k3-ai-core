# Data Agent

**Pipeline position:** 6 of 15 &middot; **Manifest:** [`agents/data.yaml`](../../agents/data.yaml) &middot; **Implementation:** [`src/kim_k3/agents/data_agent.py`](../../src/kim_k3/agents/data_agent.py)

## Role

Analyses datasets, computes statistics and interprets numerical results.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Load and profile the dataset (schema, nulls, ranges, outliers).
2. Run the requested aggregations, tests or models.
3. Report effect sizes and uncertainty, never a bare point estimate.
4. Return reproducible code alongside every number produced.

## Inputs

- dataset reference or inline data
- analysis question

## Outputs

- DataFindings: metrics, tables, caveats, reproduction snippet

## Tools allowed

- `data.load`
- `data.query`
- `code.sandbox`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 14 |
| Max credits | 180 |
| Timeout | 210s |
| Delegation depth | 1 |

The budget guard authorises every provider call before it is issued. When the cap is reached the agent returns a partial result flagged `budget_exhausted` instead of silently stopping.

## Failure modes

- **Empty output** - the Coordinator retries once with the previous output attached; a second empty output fails the agent.
- **Malformed schema** - the result is rejected, the Critic is notified and the agent is re-run with the schema error appended.
- **Policy hit** - control transfers to the Safety Agent, which decides between constraints, approval or refusal.
- **Budget exhausted** - the run continues with a partial result and the Evaluator lowers the completeness score.

## Contract

```python
from kim_k3.agents.data_agent import DataAgent
from kim_k3.agents.base import AgentContext

result = await DataAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "data"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
