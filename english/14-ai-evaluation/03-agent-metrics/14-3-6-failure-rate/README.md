# Failure rate

> **Learning Path:** AI Evaluation
> **Section:** 14.3.6 — Agent metrics

**Failure Rate - AI Evaluation / Agent Metrics**

### 1. The problem

You ship an agent to production. It works in tests, but in the wild it sometimes returns a wrong answer, times out on a tool call, or loops forever. Success rate looks okay on the dashboard, but you have no sense of how often it *breaks* and whether that is getting worse.

For deterministic services you monitor error rate. For agents you have non-determinism, multi-step plans, and multiple failure modes. You need a single, time-based signal for reliability that you can alert on, compare between versions, and use for SLOs.

Failure rate gives you that signal: how often agent executions fail, not just whether the last one succeeded.

### 2. Mental model

Failure rate = failures / total attempts in a window.

It is a rate, not a count. It forces you to define two things up front:

* What counts as an attempt? A user request, a task, or a step?
* What counts as a failure? Hard error, timeout, tool failure, or user-abandoned?

Think of it as reliability exposure. A 2% failure rate means 2 in 100 users hit a broken experience. That is an architectural constraint, not just a model quality metric.

### 3. How it works

```mermaid
flowchart LR
    User[User Request] --> Agent[Agent Orchestrator]
    Agent --> Plan[Plan / Tool Calls]
    Plan --> Outcome{Outcome}
    Outcome -->|Success| S[Success Counter]
    Outcome -->|Failure| F[Failure Counter]
    S & F --> Metrics[Failure Rate = F / (S+F) over window]
```

At each execution boundary you classify the outcome. Common classifications:

* **Hard failure:** exception, unrecoverable tool error, timeout
* **Logical failure:** task completed but result is incorrect per judge/ground truth
* **Partial failure:** task completed with degraded quality

The denominator must be stable. Most teams track failure rate per *task* for user-facing SLOs, and per *step* for debugging. The window is typically 5m/1h/1d with an exponential moving average to avoid alert noise.

### 4. Architectural reasoning

Failure rate solves the problem of knowing if your agent is degrading in production.

When it helps:
* **SLO / alerting.** You can set a target like <1% task failure rate and page on breach.
* **Version comparison.** A/B two prompts or tool sets and compare failure rate, not just average latency.
* **Capacity and fallback decisions.** High failure rate on a tool triggers circuit breaking or fallback to a simpler agent.

Alternatives:
* **Success rate = 1 - failure rate.** Same information, different framing. Use success rate for user-facing reporting, failure rate for ops.
* **Error rate per step.** More granular, needed for root cause.
* **Task completion rate.** Often confounded with user abandonment.

Choose failure rate when you need a simple, comparable reliability signal across agents and deployments. Choose step-level metrics when you need to fix it.

### 5. Trade-offs and failure modes

* **Definition drift kills comparability.** If one team counts timeouts as failures and another does not, rates are meaningless. Define failure taxonomy once.
* **Coarse metric hides root cause.** A flat 3% failure rate can be 100% tool failures on one tool and zero elsewhere. Always pair rate with failure type breakdown.
* **Non-stationarity.** Agent failure rate spikes with prompt changes, model updates, or downstream API degradation. Without tagging by model version and tool, you cannot attribute.
* **Partial success ambiguity.** Is a refund agent that partially processed a refund a failure? Your classification policy determines the rate. Inconsistent policy leads to gaming.

Failure mode to watch: silent logical failures. The agent returns a confident answer that is wrong. Those are invisible to infrastructure metrics. You need a judge or human review sample to capture them.

### 6. Example

Enterprise customer support agent with tools: KB search, ticket create, refund.

You track task-level failure rate over 1 hour.

* Total attempts: 10,000
* Hard failures: 120 timeouts on KB search
* Logical failures: 80 refunds with wrong amount per post-hoc judge
* Failure rate = 200 / 10,000 = 2%

Rate rises to 4% after a model upgrade. Breakdown shows logical failures doubled, hard failures flat. Decision: rollback model, not scale tools. Without classification you would have chased infra.

### 7. Reasoning challenge

Your agent has a steady 1.5% failure rate for a month. Last week you added retry with exponential backoff for tool calls. The failure rate dropped to 0.8%, but p95 latency increased 40% and user abandonment rose slightly.

Do you keep the retry policy? What metric would you add to decide?

### 8. Key takeaway

* Failure rate is a reliability SLO for agents, not a model accuracy score. Define attempt and failure explicitly.
* Track it at task level for users, step level for engineers, and always by failure type.
* A stable definition enables safe rollout, alerting, and fallback decisions.
* Pair rate with latency and quality signals; retries can hide failures while harming experience.
