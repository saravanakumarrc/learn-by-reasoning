# Capacity planning

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 23.1.10 — Non-functional requirements

**Capacity planning**

### The problem

You ship a service that works fine today. Then traffic grows 3x, a product launch creates a spike, a downstream dependency slows, or a zone fails. Latency climbs, queues back up, errors rise, and you either overpay for idle capacity or lose availability.

Capacity planning is not about buying big servers. It is about deciding *how much supply of compute, memory, storage, network, and human ops* you need, *when*, under uncertainty, while meeting non-functional requirements: latency SLOs, availability targets, and cost constraints.

Without it, you react. With it, you manage risk proactively.

### Mental model

Capacity = demand + headroom for variance + headroom for failure + headroom for growth.

Think of it as a buffer problem. Utilization is a liability. At 95% utilization you have no room for a spike, a slowdown, or a node loss. The architect's job is to pick the right buffer size for each constraint.

```
flowchart LR
  Metrics[Demand metrics: RPS, tokens/s, queue depth] --> Forecast[Forecast: baseline, seasonality, growth]
  Forecast --> Model[Capacity model: per-request cost, SLOs]
  Model --> Decision[Provision / Autoscale policy / Backpressure]
  Decision --> System[System]
  System --> Metrics
```

The loop is measurement → forecast → model → provision → validate.

### How it works

Essentially four steps, repeated.

**Measure demand in business terms.** Not just CPU. Requests per second, p95 latency, concurrent sessions, tokens per second for inference, writes per second. Correlate to business events.

**Forecast.** Baseline + trend + seasonality + known events. Good enough beats perfect. Use historical data and simple growth assumptions, then add explicit uncertainty.

**Model capacity.** Translate demand to resources. A request costs X ms CPU, Y MB RAM, Z network. Model includes:
* Efficiency: per-instance throughput
* SLO headroom: you need p99 < 200ms, so you need spare capacity for tail latency
* Failure domain: N+1 or N+2 per AZ, not per cluster
* Growth window: how long until next change

**Decide and validate.** Choose static provisioning, autoscaling, or both. Define triggers, cooldowns, and backpressure. Validate with load tests and chaos experiments, not just dashboards.

### Architectural reasoning

When it helps:
* You have hard SLOs on latency or availability
* Demand is variable and costly to miss
* Failure of a unit removes significant capacity
* Cost is a first-class requirement

What it solves:
* Prevents outage from under-provisioning
* Prevents waste from over-provisioning
* Gives a defensible trade-off between cost and reliability

Alternatives:
* Overprovision heavily and accept cost. Simple, reliable, expensive.
* Reactive autoscaling only. Cheap, but cold start and scale-up lag can violate SLOs.
* Queue and shed load. Accepts degraded experience to protect system.

Capacity planning lets you pick a deliberate point on that spectrum.

### Trade-offs and failure modes

* **Cost vs headroom.** More headroom = higher availability, higher bill. The right amount depends on SLO and blast radius.
* **Utilization vs tail latency.** Average utilization looks fine; p99 latency degrades under contention. Model tails, not averages.
* **Precision vs agility.** Complex models are brittle. Simple models with explicit safety margins are often more robust.
* **Static vs dynamic.** Autoscaling saves cost but adds failure modes: thrashing, scaling lag, noisy neighbors in shared pools.

Common failures:
* Planning on averages, not peaks and failure scenarios
* Ignoring dependency capacity. Your service is fine, the database is not
* Forgetting operational capacity. On-call engineers, deployment windows, incident response
* Planning for steady state only, not the recovery burst after an outage

### Example

Enterprise checkout during Black Friday.

Baseline: 2k RPS, p95 120ms, 60% CPU utilization.
Forecast: 8x peak for 3 hours, 20% week-over-week growth.
Model: Each request needs ~15ms CPU. Peak needs 8k RPS → 120s CPU/s. With 4 cores per instance at 70% safe utilization → ~43 instances baseline, ~172 peak.
Decision: Base fleet 50 instances, autoscale up to 220 with 2-minute scale-up, pre-warm before event. Database read replicas +N+1, queue orders with backpressure to avoid DB overload.
Result: Peak handled within SLO, cost limited to event window, failure of one AZ covered by replica.

Without planning, you'd either over-provision 220 instances all month or hit errors at peak.

### Reasoning challenge

You are launching a new LLM chat feature. Current inference demand is 100 req/s, p95 latency 800ms on 8 GPUs. Marketing plans a campaign that could add 400 req/s for 2 hours, with unknown spike shape. GPUs cost $3/hr and take 4 minutes to warm.

Do you pre-provision, rely on autoscaling, add a queue with backpressure, or shed load? What metrics would you track to decide, and what is your failure mode?

### Key takeaway

* Capacity planning is risk management for supply vs demand under uncertainty
* Model for peaks, tails, and failures, not averages
* Headroom is a deliberate design choice balancing cost, latency, and availability
* Validate plans with load tests and chaos, not assumptions
