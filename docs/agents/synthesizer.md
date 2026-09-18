# Synthesizer Agent

**Pipeline position:** 15 of 15 &middot; **Manifest:** [`agents/synthesizer.yaml`](../../agents/synthesizer.yaml) &middot; **Implementation:** [`src/kim_k3/agents/synthesizer_agent.py`](../../src/kim_k3/agents/synthesizer_agent.py)

## Role

Combines the results of all agents into one coherent answer.

Always last before delivery.

## Responsibilities

1. Merge agent outputs, resolving conflicts in favour of verified claims.
2. Write one answer in the user's language and register, without agent jargon.
3. Attach citations for every non-obvious factual claim.
4. State open questions and unverified points explicitly at the end.

## Inputs

- all AgentResults
- Evaluation
- SafetyVerdict

## Outputs

- FinalAnswer: text, citations, confidence, open questions

## Tools allowed

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
from kim_k3.agents.synthesizer_agent import SynthesizerAgent
from kim_k3.agents.base import AgentContext

result = await SynthesizerAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "synthesizer"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
