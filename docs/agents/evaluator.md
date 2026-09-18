# Evaluator Agent

**Pipeline position:** 14 of 15 &middot; **Manifest:** [`agents/evaluator.yaml`](../../agents/evaluator.yaml) &middot; **Implementation:** [`src/kim_k3/agents/evaluator_agent.py`](../../src/kim_k3/agents/evaluator_agent.py)

## Role

Scores the quality of the output against defined criteria.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Score correctness, completeness, grounding, clarity and cost on a 0-1 scale.
2. Compare against the acceptance criteria written by the Planner.
3. Return pass / revise / fail with the weakest dimension named.
4. Trigger at most two revision loops, then hand over with known limitations.

## Inputs

- draft answer
- Plan acceptance criteria
- Critique
- VerificationReport

## Outputs

- Evaluation: scores, verdict, required revisions

## Tools allowed

- `memory.recall`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 10 |
| Max credits | 110 |
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
from kim_k3.agents.evaluator_agent import EvaluatorAgent
from kim_k3.agents.base import AgentContext

result = await EvaluatorAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "evaluator"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
