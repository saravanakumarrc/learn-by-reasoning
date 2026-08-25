# Task success

> **Learning Path:** AI Evaluation
> **Section:** 14.3.1 — Agent metrics

### The problem

LLM metrics like perplexity, BLEU, or even single-turn win rate do not tell you if an agent did the user's job. An agent can generate fluent, plausible responses, call tools correctly, and still fail to book the right flight, update the correct record, or provide a useful answer.

In agentic systems the unit of value is not a good sentence, it is a completed task. Without a task-level signal you cannot reason about reliability, regression, or cost/performance trade-offs. You optimize for style while the business metric stays flat.

### Mental model

Task Success = Did the agent achieve the user's intent for this specific task instance?

Think of it as a contract test. The user provides a request with implicit or explicit success criteria. The agent produces a trace of actions and final output. A verifier decides pass/fail.

It is intentionally coarse. A step can be perfect and the task can still fail. Conversely, a messy trace can still succeed.

### How it works

You need three things: a task definition, an oracle, and a decision rule.

**Task definition.** What counts as success? For a deterministic task: "Create a support ticket for order 12345 with priority high". For open-ended tasks: "Summarize the quarterly report and highlight risks". Success criteria must be explicit before evaluation.

**Oracle.** How do you check success?
* **Rule-based / automated verifier.** Golden output comparison, JSON schema validation, database assertion, tool result checks. Cheap and repeatable.
* **Human judgment.** Annotators rate success on a rubric. Expensive but captures nuance.
* **Hybrid.** Automated pre-filter + human sample for calibration.

**Decision rule.** Binary success/fail is common. For partial credit use graded success 0/0.5/1, or success with a severity weighting.

```
flowchart LR
    U[User Task + Criteria] --> A[Agent]
    A --> T[Trace + Final Output]
    T --> V[Verifier]
    V --> M[Task Success Rate]
    V -.-> H[Human Review]
```

The metric is usually reported as Task Success Rate = successful tasks / total tasks, often with confidence intervals per task type.

### Architectural reasoning

Use Task Success when you are shipping agents with real side effects.

It solves:
* **Alignment to business value.** You stop optimizing for proxy metrics that don't correlate with completion.
* **Regression detection.** Model or tool changes can be measured against a fixed task suite.
* **Risk budgeting.** You can trade success rate for latency or cost.

Alternatives:
* Step-level accuracy. Good for debugging tool use, bad for end-to-end value.
* User satisfaction/CSAT. Real but noisy, lagging, and confounded by UX.
* Latency / cost per turn. Important operational metrics, not outcome metrics.

Choose Task Success as the primary evaluation metric for agents, and step metrics as diagnostics.

### Trade-offs and failure modes

* **Definition brittleness.** Success criteria that are too narrow cause false failures. Too loose cause false passes. Criteria drift over time as products change.
* **Automation bias.** Rule-based verifiers are cheap but gameable. Agents learn to satisfy the checker, not the user. Example: an agent that inserts the expected keywords to pass a string match without solving the task.
* **Cost vs coverage.** Human evaluation is accurate but expensive. Most teams use a held-out human-annotated set to calibrate automated verifiers.
* **Non-determinism.** Same task can succeed one run and fail the next. You need multiple samples and distribution reporting, not a single point estimate.
* **Task selection bias.** Success on easy synthetic tasks does not generalize to real user distribution. Evaluation set must mirror production intent distribution and edge cases.

### Example

Enterprise customer support agent that resolves billing inquiries.

Task: "User reports double charge on order 987. Find the duplicate, refund it, and confirm to user."

Success criteria:
1. Correct order identified via search tools
2. Refund tool called with correct amount and order id
3. Final message confirms refund and gives reference

In evaluation harness, 200 real anonymized tickets are replayed. Automated verifier checks DB for refund record and message contains reference. 10% sample goes to human reviewers for nuance like empathy and completeness.

A model update improved average response length and tool-call accuracy by 8%, but Task Success dropped from 72% to 64% because the agent started refunding the wrong line item. Step metrics would have missed it.

### Reasoning challenge

You are launching a travel booking agent. Automated verifier can check if a booking API was called with valid parameters and a confirmation code was returned. Human review finds that 12% of "successful" bookings have wrong dates or wrong passenger names that the verifier missed.

Do you ship with the automated metric, add stricter automated checks, or move to sampled human evaluation for release gating? What do you instrument to detect proxy gaming over time?

### Key takeaway

* Task Success measures outcome, not style or step correctness.
* It requires explicit, testable success criteria and a verifier, automated or human.
* Use it as the primary agent metric; use step metrics for diagnostics.
* The hardest part is defining success without creating a gameable proxy.
* Track distribution by task type, not just overall rate, and calibrate automated verifiers with human judgment.
