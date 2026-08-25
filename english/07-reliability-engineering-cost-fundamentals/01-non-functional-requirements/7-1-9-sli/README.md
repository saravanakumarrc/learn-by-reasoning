# SLI

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 23.1.9 — Non-functional requirements

**SLI — Service Level Indicator**

### 1. The problem

You ship a service. Users say it feels slow or flaky. Engineers say it's fine. Product asks "are we reliable?"

You can't argue about reliability. You need a measurable signal of whether the service is delivering the experience users need, now and over time.

Without that signal you over-react to every alert, under-invest until an outage, and make capacity decisions by gut.

### 2. Mental model

An SLI is a *user-visible* success metric you can measure from real traffic.

Think of it as a probe into the contract with the user: *Did this request meet the quality we promised?*

SLI is the measurement. SLO is the target you set on it. SLA is the business promise backed by penalties.

```
User Request --> Service --> Outcome
Outcome --> SLI = fraction of good outcomes
SLI --> SLO = target e.g., 99.9% good
SLO --> SLA = contractual promise
```

SLI is not a dashboard metric. It's a deliberately chosen indicator of user experience.

### 3. How it works

Pick one or two dimensions that actually matter to users, make them measurable, and aggregate them over a window.

The classic triad:
* **Availability:** % of requests that return a successful response
* **Latency:** % of requests that complete within a threshold
* **Correctness / Freshness:** % of results that are accurate or up-to-date

Measurement = `good requests / total requests` over a rolling window, e.g., 28 days.

Good is defined by user-facing criteria, not internal health. A 200 from a cache miss that returns stale data may be bad. A 5xx you automatically retry may be invisible.

You need instrumentation at the edge of the service, not inside the host. The SLI must be computed from the same perspective as the user.

### 4. Architectural reasoning

When does an SLI help?

* You have multiple teams sharing a platform and need a shared definition of "healthy".
* You want error budgets to drive release decisions.
* You need to prioritize reliability work against feature work.

It solves: vague reliability discussions → measurable trade-offs.

Alternatives:
* **No SLI, just alerts.** You react to symptoms, not to user impact. Noise is high.
* **Internal metrics only.** CPU, queue depth, etc. Useful for debugging, useless for user contract.
* **One giant SLI.** Leads to masking. Payment success is not the same as search latency.

Choice rule: pick SLIs that are *actionable*. If the SLI degrades, you know which system and which user flow to fix. If it degrades and you don't know why, it's the wrong SLI.

Architecture impact: you must design for observability first. Request tracing, standardized success criteria, and consistent time windows across services become requirements.

### 5. Trade-offs and failure modes

* **Granularity vs signal.** Per-endpoint SLIs are accurate but costly to maintain. Too coarse and you miss hotspots.
* **Latency threshold choice.** 200ms for a checkout API vs 800ms for a report. Wrong threshold makes SLO meaningless.
* **Good vs bad definition drift.** If "good" changes with product, SLI must be versioned. Otherwise you compare apples to oranges.
* **Sampling cost.** High-cardinality measurement is expensive. You often sample but must keep it statistically valid.
* **Gaming.** Teams can make SLI look good by redefining good, throttling traffic, or moving work out of scope.

Failure mode: SLIs that measure the system, not the user. e.g., measuring API availability while the downstream data is 5 minutes stale.

### 6. Example

Payments service.

User need: submit payment and get a definitive result fast.

Chosen SLIs:
* Availability: `successful payment responses / total attempts` over 28 days. Good = 2xx.
* Latency: `requests with p99 < 1.5s` / total. Good = under threshold.

SLO: 99.95% availability, 99% latency.

Error budget = 0.05% of requests can fail per month. When budget burns, freeze non-critical deploys. This links engineering behavior directly to user impact.

Instrumentation is at the API gateway, counting attempts and outcomes per payment flow, not per internal microservice.

### 7. Reasoning challenge

Your search service has two SLIs: overall availability 99.9% and p95 latency < 300ms. Both are green.

Product complains that "search feels broken for new users". What is missing and how would you fix the SLI set?

### 8. Key takeaway

* SLI is a user-facing success fraction, not an internal metric.
* Pick few, actionable SLIs that map directly to user pain.
* SLO is the target on the SLI; error budget is the operational consequence.
* If you can't measure good vs bad from the user's perspective, you can't reason about reliability.

You can't improve what you don't measure, and you shouldn't measure what you can't act on.
