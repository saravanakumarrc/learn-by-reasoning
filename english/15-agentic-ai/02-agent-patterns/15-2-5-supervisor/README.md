# Supervisor

> **Learning Path:** Agentic AI
> **Section:** 11.2.5 — Agent patterns

**Supervisor Agent Pattern**

### The problem

A single LLM agent gets worse as the task gets broader. One model has to hold the whole domain in context, know which tools to use, and keep reasoning consistent across steps.

In practice this creates three constraints:
* **Capability sprawl.** One agent needs retrieval, code execution, web search, summarization, and compliance checks. Tool selection becomes noisy and error-prone.
* **Context limits.** Long conversations dilute the signal. The agent forgets goals, repeats work, or hallucinates facts.
* **Quality variance.** A generalist is mediocre at everything. Specialization is needed for accuracy, but a single agent can't specialize.

You need decomposition without losing coherence.

### Mental model

A foreman with a crew.

The Supervisor does not do the work. It understands the overall goal, decomposes it, routes sub-tasks to specialist workers, validates outputs, and synthesizes a final answer. Workers are narrow, stateless, and reusable.

### How it works

```
flowchart TD
    User --> S[Supervisor]
    S --> D{Decompose & Route}
    D --> A1[Specialist A]
    D --> A2[Specialist B]
    D --> A3[Specialist C]
    A1 --> S
    A2 --> S
    A3 --> S
    S --> Synthesize[Aggregate & Validate]
    Synthesize --> User
```

Essential mechanism:
1. **Intent classification & planning.** Supervisor extracts goal, constraints, and success criteria.
2. **Decomposition.** Break into independent or ordered sub-tasks with clear inputs/outputs.
3. **Delegation.** Route each sub-task to the right specialist agent with a bounded prompt and tools.
4. **Orchestration.** Handle dependencies, retries, and timeouts. Parallel where possible, sequential where required.
5. **Aggregation.** Merge results, detect conflicts, enforce policies, and produce final output.

The Supervisor owns state and coherence. Specialists own depth.

### Architectural reasoning

When it helps:
* Multi-step workflows requiring different skills: research → analysis → code → review.
* Need for auditability and policy enforcement at a single point.
* Teams want to swap specialists without changing the overall flow.

Alternatives:
* **Router:** single decision point, no iterative oversight. Cheaper, faster, but no validation or synthesis.
* **Monolithic agent:** simplest to deploy, fails on complexity and tool noise.
* **Hierarchical multi-agent:** supervisor can itself be supervised for large systems.

Choose Supervisor when correctness and decomposition matter more than raw latency, and when sub-tasks are stable enough to specialize.

### Trade-offs and failure modes

* **Latency adds up.** Round trips to specialists multiply. Mitigate with parallel fan-out and strict contracts.
* **Supervisor bottleneck.** All reasoning and failure handling flows through one agent. Prompt injection or hallucination here corrupts everything.
* **Coordination overhead.** Defining clear interfaces between sub-tasks is hard. Ambiguous handoffs cause drift.
* **Error propagation.** A bad specialist output is often accepted. You need validation, schema checks, and fallback strategies.
* **Cost.** More tokens per request. You pay for specialization.

Failure modes architects hit first: supervisor over-delegating trivial work, specialists returning over-confident garbage, and no rollback when a dependency fails.

### Example

Enterprise support triage.

User: "My invoice is wrong and I need a refund for last quarter."

Supervisor plans:
1. Retrieve account and invoices → Finance Specialist
2. Validate refund policy → Policy Specialist
3. Draft response with options → Communications Specialist

Supervisor validates that invoice dates match policy window before allowing refund suggestion, then synthesizes a single coherent reply with citations. Specialists never see the full conversation, only bounded context.

### Reasoning challenge

You have a real-time chatbot that needs to answer product questions, check inventory, and place orders. Latency budget is 800ms p95.

Do you use a Supervisor with specialist agents, a single tool-augmented agent, or a Router that fans out in parallel? What changes if the policy requires human approval for refunds over $1k?

### Key takeaway

* Supervisor exists to decompose complex goals into specialized, verifiable sub-tasks while preserving coherence.
* It trades latency and cost for quality, consistency, and auditability.
* Design the contracts between supervisor and specialists first; the agents are secondary.
* Centralize policy and validation in the supervisor, decentralize depth to specialists.
* If you cannot define clear inputs/outputs for sub-tasks, a supervisor will add complexity without value.
