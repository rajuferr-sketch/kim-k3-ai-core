# The 15-agent pipeline

Every request to kim-k3 activates **all fifteen agents**. There is no "simple question"
fast path that skips review: the Router may downgrade model tiers and shrink budgets,
but each agent still runs and still records its verdict in the run trace.

## Roster

| # | Agent | Key | Role | Files |
| --- | --- | --- | --- | --- |
| 1 | **Router Agent** | `router` | Decides which agents and which model tier every incoming request needs. | [manifest](../agents/router.yaml) / [doc](agents/router.md) / [code](../src/kim_k3/agents/router_agent.py) |
| 2 | **Coordinator Agent** | `coordinator` | Assigns tasks to the other agents and owns the execution flow of the run. | [manifest](../agents/coordinator.yaml) / [doc](agents/coordinator.md) / [code](../src/kim_k3/agents/coordinator_agent.py) |
| 3 | **Research Agent** | `research` | Finds information, primary sources and data relevant to the request. | [manifest](../agents/research.yaml) / [doc](agents/research.md) / [code](../src/kim_k3/agents/research_agent.py) |
| 4 | **Planner Agent** | `planner` | Decomposes the problem into objectives, ordered steps and acceptance criteria. | [manifest](../agents/planner.yaml) / [doc](agents/planner.md) / [code](../src/kim_k3/agents/planner_agent.py) |
| 5 | **Reasoning Agent** | `reasoning` | Analyses complex problems and builds explicit deductive chains. | [manifest](../agents/reasoning.yaml) / [doc](agents/reasoning.md) / [code](../src/kim_k3/agents/reasoning_agent.py) |
| 6 | **Data Agent** | `data` | Analyses datasets, computes statistics and interprets numerical results. | [manifest](../agents/data.yaml) / [doc](agents/data.md) / [code](../src/kim_k3/agents/data_agent.py) |
| 7 | **Coding Agent** | `coding` | Writes, modifies and checks code. | [manifest](../agents/coding.yaml) / [doc](agents/coding.md) / [code](../src/kim_k3/agents/coding_agent.py) |
| 8 | **Tool Agent** | `tool` | Selects and calls external tools and APIs on behalf of the other agents. | [manifest](../agents/tool.yaml) / [doc](agents/tool.md) / [code](../src/kim_k3/agents/tool_agent.py) |
| 9 | **Executor Agent** | `executor` | Carries out the planned actions that change state in the real world. | [manifest](../agents/executor.yaml) / [doc](agents/executor.md) / [code](../src/kim_k3/agents/executor_agent.py) |
| 10 | **Critic Agent** | `critic` | Looks for errors, gaps and inconsistencies in the work of the other agents. | [manifest](../agents/critic.yaml) / [doc](agents/critic.md) / [code](../src/kim_k3/agents/critic_agent.py) |
| 11 | **Verifier Agent** | `verifier` | Verifies facts, calculations and outputs independently. | [manifest](../agents/verifier.yaml) / [doc](agents/verifier.md) / [code](../src/kim_k3/agents/verifier_agent.py) |
| 12 | **Safety Agent** | `safety` | Checks risk, policy compliance and problematic requests. | [manifest](../agents/safety.yaml) / [doc](agents/safety.md) / [code](../src/kim_k3/agents/safety_agent.py) |
| 13 | **Memory Agent** | `memory` | Manages context, relevant information and the state of the work. | [manifest](../agents/memory.yaml) / [doc](agents/memory.md) / [code](../src/kim_k3/agents/memory_agent.py) |
| 14 | **Evaluator Agent** | `evaluator` | Scores the quality of the output against defined criteria. | [manifest](../agents/evaluator.yaml) / [doc](agents/evaluator.md) / [code](../src/kim_k3/agents/evaluator_agent.py) |
| 15 | **Synthesizer Agent** | `synthesizer` | Combines the results of all agents into one coherent answer. | [manifest](../agents/synthesizer.yaml) / [doc](agents/synthesizer.md) / [code](../src/kim_k3/agents/synthesizer_agent.py) |

## Flow

```text
                 request
                    |
                 [router]              choose agents, tiers, budgets
                    |
               [coordinator]           build graph, dispatch, retry
                    |
              [safety pre-flight]      refuse / constrain before spending credits
                    |
                [memory recall]        working + episodic + semantic
                    |
        +-----------+-----------+
     [research]              [planner]        (concurrent)
        +-----------+-----------+
                    |
               [reasoning]             premises -> deductions -> conclusions
                    |
        +-----------+-----------+
       [data]                [coding]         (concurrent)
        +-----------+-----------+
                    |
             [tool] -> [executor]      external calls, then real side effects
                    |
        +-----------+-----------+
      [critic]              [verifier]        (concurrent)
        +-----------+-----------+
                    |
            [safety pre-commit]
                    |
              [evaluator]  --revise--> back to [planner] (max 2 loops)
                    |
            [memory consolidate]
                    |
             [synthesizer]             one answer, with citations
                    |
                 response
```

## Shared blackboard

Agents never call each other directly. Each writes an `AgentResult` to the shared
blackboard keyed by agent name, and reads the results it depends on. This keeps the
graph inspectable, makes every run replayable from the trace, and means an agent can
be swapped or re-run in isolation.

## Budgets

Each agent has a credit ceiling in `agents/pipeline.yaml`; the run has a global ceiling
of 2000 credits. The budget guard authorises every provider call *before* it is issued.
When a ceiling is hit the agent returns a partial result flagged `budget_exhausted`,
the Evaluator lowers the completeness score, and the Synthesizer states the limitation
in the answer instead of hiding it.

## Guarantees

1. All 15 agents run on every request and appear in the run trace, even when skipped-by-policy.
2. No side effect happens without a Safety clearance and, for destructive tools, human approval.
3. Every factual claim in the final answer carries a Verifier status; unverified claims are labelled.
4. Retrieved content and tool output are data, never instructions.
5. The answer is written in the user's language by the Synthesizer only - other agents never speak to the user.

## Per-agent documentation

- [Router Agent](agents/router.md)
- [Coordinator Agent](agents/coordinator.md)
- [Research Agent](agents/research.md)
- [Planner Agent](agents/planner.md)
- [Reasoning Agent](agents/reasoning.md)
- [Data Agent](agents/data.md)
- [Coding Agent](agents/coding.md)
- [Tool Agent](agents/tool.md)
- [Executor Agent](agents/executor.md)
- [Critic Agent](agents/critic.md)
- [Verifier Agent](agents/verifier.md)
- [Safety Agent](agents/safety.md)
- [Memory Agent](agents/memory.md)
- [Evaluator Agent](agents/evaluator.md)
- [Synthesizer Agent](agents/synthesizer.md)
