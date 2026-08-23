# Sequential agents

> **Learning Path:** Multi-Agent Architecture
> **Section:** 12.1.7 — Learn

### 1. The problem

A single agent can reason, call tools, and summarize. It struggles when a task is:
* multi-step with hard dependencies
* requires different skills, tools, and validation criteria per step
* must be auditable and recoverable

One monolithic prompt leads to hallucinated steps, context bloat, and unrecoverable errors. Parallel agents solve breadth but not ordering. You need ordered specialization.

### 2. Mental model

Sequential agents = an assembly line for reasoning.

Each agent owns one transformation of state. Input in, validated output out. The output becomes the next agent's input. No agent needs to know the whole job, only its contract with neighbors.

Think pipeline, not committee.

```mermaid
flowchart LR
    In[Task + Context] --> A1[Agent 1<br/>Extract & Normalize]
    A1 --> S1[(State v1)]
    S1 --> A2[Agent 2<br/>Validate & Enrich]
    A2 --> S2[(State v2)]
    S2 --> A3[Agent 3<br/>Decide & Summarize]
    A3 --> Out[Final Output]
    
    Orchestrator{{Orchestrator}} -.controls flow, retries, checkpoints-. A1 & A2 & A3
```

### 3. How it works

* **State object:** A canonical schema passed between agents. Contains data, metadata, and provenance. Not raw chat history.
* **Contract:** Each agent has a narrow input/output schema and a success criterion. e.g., `extract → normalized fields with confidence`.
* **Orchestrator:** Lightweight controller that routes state, enforces order, handles retries, and checkpoints. It does not do the work.
* **Handoff validation:** Before passing forward, the agent or orchestrator validates schema, completeness, and confidence thresholds. Fail fast, don't propagate garbage.

Implementation is just message passing with typed state. The hard part is defining the contracts.

### 4. Architectural reasoning

Use sequential agents when:

* Steps have a natural order and dependencies. Risk scoring must come after validation.
* You need quality gates. Each step can be tested, monitored, and versioned independently.
* Different capabilities are needed per step. Extraction needs vision, decision needs policy rules.
* You need auditability. State checkpoints give you a replayable trail.

Alternatives:
* **Single agent with chain-of-thought:** Simpler, lower latency, but brittle on complex tasks and hard to debug.
* **Parallel agents:** Good for independent sub-tasks, bad for dependent steps. Requires merge logic.
* **Router / dynamic workflow:** More flexible but higher complexity. Sequential is the baseline.

Choose sequential when correctness and traceability outweigh raw latency.

### 5. Trade-offs and failure modes

* **Latency accumulates.** Three agents = three LLM calls + validation. You trade speed for reliability.
* **Error propagation.** A bad handoff poisons downstream. Mitigate with schema validation and confidence gates, not with bigger prompts.
* **Coupling via state schema.** Changing Agent 2's output breaks Agent 3. Version state schemas explicitly.
* **Bottleneck and head-of-line blocking.** One slow agent stalls the pipeline. Add timeouts, retries with backoff, and dead-letter queues for poisoned state.
* **Observability cost.** You need per-step metrics: latency, success rate, hallucination rate, state drift. Without it you only see end-to-end failures.

The most common failure is treating agents as black boxes and passing raw conversation. Pass structured state.

### 6. Example

Enterprise loan intake:

* Agent 1 - Intake & Extraction: parses application PDF, extracts fields into JSON with confidence scores.
* Agent 2 - Validation & Enrichment: validates fields against schema, calls KYC/credit APIs, enriches state.
* Agent 3 - Policy Decision: applies business rules, produces approve/deny/referral with rationale.

If validation fails, the orchestrator halts and returns a structured error to the user instead of letting a downstream agent hallucinate a decision. Each agent is independently testable and can be retrained without touching the others.

### 7. Reasoning challenge

You are designing a medical triage assistant. Step A extracts symptoms from free text. Step B classifies urgency. Step C drafts a clinician note.

Latency SLA is 2 seconds end-to-end. Agent B needs the full original transcript for safety, but Agent A already summarizes it.

Do you keep the full transcript in state for all agents, or pass only the summary? What trade-off are you making?

### 8. Key takeaway

* Sequential agents decompose complex tasks into ordered, testable transformations with explicit state contracts.
* The orchestrator enforces order, validation, and retries; agents stay focused on one skill.
* Use them when steps depend on each other and auditability matters more than minimal latency.
* Guard against error propagation with schema validation, confidence thresholds, and per-step observability.
