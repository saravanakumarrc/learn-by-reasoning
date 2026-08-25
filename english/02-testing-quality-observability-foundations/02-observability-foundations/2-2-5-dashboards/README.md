# Dashboards

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 22.2.5 — Observability foundations

**22.2.5 Observability foundations — Dashboards**

### 1. The problem

You ship a distributed system. It produces metrics, logs and traces constantly. When something degrades you need to answer: *Is it happening now? Where? How bad? Is it getting better?*

Tailing logs on a single pod, running ad-hoc queries in a console, or asking an engineer to pull data is too slow for common questions. Different teams need the same answers repeatedly, and they need them without deep query knowledge.

Constraints created the need for dashboards:
* High volume, high velocity signals you cannot read manually
* Multiple teams need shared situational awareness
* Questions repeat: latency, error rate, saturation, business health
* Decision speed matters more than exploratory depth

### 2. Mental model

A dashboard is a curated, shared view of telemetry for a specific operational question.

It is not a data dump. It is a pre-joined, pre-aggregated, pre-filtered answer to: "What is the current state of system X from perspective Y?"

Think of it as a cockpit instrument panel, not a flight data recorder. Alerts tell you when something is wrong. Dashboards help you understand *what* is wrong and *why*.

### 3. How it works

Signals flow from system → observability pipeline → storage → query → visualization.

```mermaid
flowchart LR
    A[Services] --> B[Metrics / Logs / Traces]
    B --> C[Collector / Agent]
    C --> D[TSDB / Log Store / Trace Store]
    D --> E[Query Layer]
    E --> F[Dashboard UI]
    F --> G[Operator / On-call]
```

Essential mechanism: dashboards declare a small set of queries over time-series data, with dimensions and thresholds baked in. They refresh automatically and render trends, not point values. Good dashboards are built around the Golden Signals: latency, traffic, errors, saturation.

### 4. Architectural reasoning

**When it helps**
* Common operational questions asked repeatedly by multiple roles
* Need for real-time situational awareness during incidents
* Onboarding new engineers to system behavior
* Correlating signals across services: e.g., latency spike + error rate + CPU saturation

**When it doesn't help**
* Rare, deep-dive investigations → use ad-hoc exploration tools
* Single threshold violations → use alerts
* Business reporting over long historical periods → use BI, not operational dashboards

Alternatives: ad-hoc query UIs, alert-only approaches, log tailing. Dashboards win on speed of shared understanding and reduced cognitive load. They lose on flexibility.

Decision rule: if a question is asked >2 times a week by >1 team, it deserves a dashboard.

### 5. Trade-offs and failure modes

* **Signal vs noise.** More panels = slower comprehension. Architects must curate ruthlessly. The most important failure mode is dashboard blindness: a wall of green charts that no one looks at.
* **Freshness vs cost.** Real-time dashboards require high write/read throughput and short retention. Expensive. Choose granularity and retention per use case: 10s for incident response, 1m for trends, 1h for capacity planning.
* **Generality vs specificity.** Shared dashboards get too generic. Team-specific dashboards get duplicated. Solve with a layered model: platform provides golden-signal dashboards, teams add service-specific panels.
* **Staleness.** Dashboards rot. Queries break when metrics are renamed, filters become wrong, and no one owns updates. Treat dashboards as code, version them, and assign an owner.

### 6. Example

E-commerce checkout service.

Operational dashboard built around one question: *Can users complete purchase?*

Panels: request rate, p95 latency, error rate by error type, payment success rate, downstream dependency latency, CPU/memory saturation. All filtered by region and environment, time range defaults to last 1 hour.

During an incident, on-call opens the dashboard first. Rate is flat, latency up, errors up only for payment gateway. Saturation normal. Conclusion narrows to dependency in <30 seconds without writing a query.

### 7. Reasoning challenge

You have a microservice with high-cardinality request IDs and user IDs in logs. A team wants a dashboard showing p99 latency per user to find slow users.

Should you build it? What is the architectural problem, and what would you do instead?

### 8. Key takeaway

* Dashboards exist to make repeated operational questions instantly answerable and shareable
* They are curated views of metrics/logs/traces, not exploration tools
* Build them for common, high-impact questions; alert on thresholds, explore with ad-hoc tools
* Curate aggressively, own them as code, and watch for cost, staleness, and noise
