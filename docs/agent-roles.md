# Agent Roles

The system runs six specialised agents. Each has a narrow, well-defined
responsibility. No agent does another agent's job.

---

## Planner

**Responsibility:** Strategic decomposition

The Planner receives a high-level goal and breaks it into an ordered graph
of sub-tasks. It does not execute tasks — it only defines them and
maintains the dependency structure.

- Input: Goal or objective from the human or orchestrator
- Output: Ordered task list with dependencies and agent assignments
- Risk profile: Low (does not touch external systems)
- Typical confidence range: 75–95%
- Gates triggered by: Major plan changes affecting live systems

---

## Researcher

**Responsibility:** Web and knowledge retrieval

The Researcher fetches external information — web pages, APIs, databases,
internal knowledge stores — and structures it for use by other agents.

- Input: Research queries from Planner or Critic
- Output: Structured data, summaries, source citations
- Risk profile: Low (reads only, no writes)
- Typical confidence range: 60–85%
- Gates triggered by: Never (read-only agent)

---

## Coder

**Responsibility:** Code generation and review

The Coder writes, modifies, or reviews code. It works within a sandboxed
environment and does not deploy or merge without an approval gate.

- Input: Specification from Planner, context from Researcher
- Output: Code diffs, pull requests, review comments
- Risk profile: Medium–High (code changes affect production if merged)
- Typical confidence range: 55–80%
- Gates triggered by: Any merge or deployment action

---

## Critic

**Responsibility:** Output validation and quality assurance

The Critic reviews outputs from other agents before they proceed. It acts
as an internal QA layer, scoring outputs and flagging issues.

- Input: Any agent output flagged for validation
- Output: Quality score (0–100), list of issues, pass/fail verdict
- Risk profile: Low (read-only evaluator)
- Typical confidence range: 85–99%
- Gates triggered by: Never (evaluation agent only)

---

## Executor

**Responsibility:** Safe action execution

The Executor performs real-world actions: API calls, deployments, file
writes, external service triggers. It is the only agent that takes
irreversible actions, and it requires the highest approval threshold.

- Input: Approved action plan from Planner, verified by Critic
- Output: Execution result, logs, status report
- Risk profile: High–Critical (all actions are potentially irreversible)
- Typical confidence range: 50–75%
- Gates triggered by: Every action above a defined risk score

---

## Memory

**Responsibility:** Context and knowledge storage

The Memory agent manages the shared context window across all agents.
It compacts long conversations, stores key decisions for recall, and
retrieves relevant history when agents need it.

- Input: Agent outputs, conversation state, decision records
- Output: Compacted context, retrieved memories, indexed knowledge
- Risk profile: Very Low (internal state management only)
- Typical confidence range: 95–99%
- Gates triggered by: Never

---

## Agent Interaction Map

```
           ┌─────────────┐
           │   Planner   │  ← sets direction
           └──────┬──────┘
         ┌────────┼────────┐
         ▼        ▼        ▼
   Researcher   Coder   Executor
         │        │        │
         └────────┼────────┘
                  ▼
              Critic  ←  validates all outputs
                  │
                  ▼
              Memory  ←  stores context for all
```

Nicholas Core routes communication between all agents and decides
which paths activate based on current task state.
