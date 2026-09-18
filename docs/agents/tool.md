# Tool Agent

**Pipeline position:** 8 of 15 &middot; **Manifest:** [`agents/tool.yaml`](../../agents/tool.yaml) &middot; **Implementation:** [`src/kim_k3/agents/tool_agent.py`](../../src/kim_k3/agents/tool_agent.py)

## Role

Selects and calls external tools and APIs on behalf of the other agents.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Resolve an intent to a concrete tool in the registry.
2. Validate arguments against the tool schema before calling.
3. Enforce the allow-list; destructive tools require human approval.
4. Normalise tool responses and errors into ToolResult.

## Inputs

- tool intent
- arguments
- caller agent identity

## Outputs

- ToolResult: ok, payload, error, latency, credits

## Tools allowed

- `registry.tools`
- `http.request`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 12 |
| Max credits | 140 |
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
from kim_k3.agents.tool_agent import ToolAgent
from kim_k3.agents.base import AgentContext

result = await ToolAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "tool"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
