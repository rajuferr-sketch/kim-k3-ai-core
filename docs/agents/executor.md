# Executor Agent

**Pipeline position:** 9 of 15 &middot; **Manifest:** [`agents/executor.yaml`](../../agents/executor.yaml) &middot; **Implementation:** [`src/kim_k3/agents/executor_agent.py`](../../src/kim_k3/agents/executor_agent.py)

## Role

Carries out the planned actions that change state in the real world.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Execute only steps the Plan marked as actionable and the Safety Agent cleared.
2. Run inside a transaction or with a compensating action defined up front.
3. Stop at the first irreversible step lacking approval.
4. Record every side effect in the run trace.

## Inputs

- approved Plan steps
- ToolResults
- approval tokens

## Outputs

- ExecutionReport: performed actions, side effects, rollback notes

## Tools allowed

- `tool.invoke`
- `repo.write`
- `shell.run`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 16 |
| Max credits | 200 |
| Timeout | 240s |
| Delegation depth | 1 |

The budget guard authorises every provider call before it is issued. When the cap is reached the agent returns a partial result flagged `budget_exhausted` instead of silently stopping.

## Failure modes

- **Empty output** - the Coordinator retries once with the previous output attached; a second empty output fails the agent.
- **Malformed schema** - the result is rejected, the Critic is notified and the agent is re-run with the schema error appended.
- **Policy hit** - control transfers to the Safety Agent, which decides between constraints, approval or refusal.
- **Budget exhausted** - the run continues with a partial result and the Evaluator lowers the completeness score.

## Contract

```python
from kim_k3.agents.executor_agent import ExecutorAgent
from kim_k3.agents.base import AgentContext

result = await ExecutorAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "executor"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
