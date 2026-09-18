# Reasoning Agent

**Pipeline position:** 5 of 15 &middot; **Manifest:** [`agents/reasoning.yaml`](../../agents/reasoning.yaml) &middot; **Implementation:** [`src/kim_k3/agents/reasoning_agent.py`](../../src/kim_k3/agents/reasoning_agent.py)

## Role

Analyses complex problems and builds explicit deductive chains.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Turn evidence and constraints into premises.
2. Derive conclusions step by step, each step labelled deduction / induction / assumption.
3. Expose assumptions explicitly so the Verifier can test them.
4. Produce alternative hypotheses when evidence is thin.

## Inputs

- Plan
- Evidence[]
- problem statement

## Outputs

- ReasoningTrace: premises, steps, conclusions, assumptions, confidence

## Tools allowed

- `memory.recall`

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
from kim_k3.agents.reasoning_agent import ReasoningAgent
from kim_k3.agents.base import AgentContext

result = await ReasoningAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "reasoning"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
