# Coding Agent

**Pipeline position:** 7 of 15 &middot; **Manifest:** [`agents/coding.yaml`](../../agents/coding.yaml) &middot; **Implementation:** [`src/kim_k3/agents/coding_agent.py`](../../src/kim_k3/agents/coding_agent.py)

## Role

Writes, modifies and checks code.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Read the relevant files before editing them.
2. Write minimal, typed, tested changes that match repository conventions.
3. Run lint, type-check and tests on the produced diff.
4. Return a unified diff plus the command output that proves it works.

## Inputs

- Plan step
- repository context
- failing test or spec

## Outputs

- CodeChange: diff, touched files, test evidence

## Tools allowed

- `repo.read`
- `repo.write`
- `shell.run`
- `code.sandbox`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 20 |
| Max credits | 250 |
| Timeout | 300s |
| Delegation depth | 1 |

The budget guard authorises every provider call before it is issued. When the cap is reached the agent returns a partial result flagged `budget_exhausted` instead of silently stopping.

## Failure modes

- **Empty output** - the Coordinator retries once with the previous output attached; a second empty output fails the agent.
- **Malformed schema** - the result is rejected, the Critic is notified and the agent is re-run with the schema error appended.
- **Policy hit** - control transfers to the Safety Agent, which decides between constraints, approval or refusal.
- **Budget exhausted** - the run continues with a partial result and the Evaluator lowers the completeness score.

## Contract

```python
from kim_k3.agents.coding_agent import CodingAgent
from kim_k3.agents.base import AgentContext

result = await CodingAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "coding"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
