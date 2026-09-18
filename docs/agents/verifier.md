# Verifier Agent

**Pipeline position:** 11 of 15 &middot; **Manifest:** [`agents/verifier.yaml`](../../agents/verifier.yaml) &middot; **Implementation:** [`src/kim_k3/agents/verifier_agent.py`](../../src/kim_k3/agents/verifier_agent.py)

## Role

Verifies facts, calculations and outputs independently.

Runs in the position defined by the pipeline; the Coordinator may run it concurrently with independent agents.

## Responsibilities

1. Re-check every factual claim against a source, independent of the Research Agent's summary.
2. Recompute every number with an independent method.
3. Execute produced code and compare the observed output with the claimed output.
4. Mark each claim verified / unverified / refuted; unverified claims must be labelled in the answer.

## Inputs

- claims[]
- numbers
- code artifacts
- sources

## Outputs

- VerificationReport: per-claim status, evidence, recomputation

## Tools allowed

- `web.fetch`
- `code.sandbox`
- `calc.eval`

Any tool outside this list is refused by the tool registry, even if the model asks for it.

## Budget

| Limit | Value |
| --- | --- |
| Max steps | 14 |
| Max credits | 160 |
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
from kim_k3.agents.verifier_agent import VerifierAgent
from kim_k3.agents.base import AgentContext

result = await VerifierAgent().run(AgentContext(request=request, blackboard=blackboard))
assert result.agent == "verifier"
```

See [the pipeline overview](../multi-agent-pipeline.md) for how this agent's output is consumed by the others.
