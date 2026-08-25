# Trade-off analysis

> **Learning Path:** Non-AI System Design Practice
> **Section:** 25.1.7 — System design practice

**Trade-off analysis**

### The problem

You have two good options, both will work. Picking one is not about finding the "best" design. It's about choosing which constraints to satisfy and which to relax.

In system design, every decision moves you along competing axes: latency vs cost, consistency vs availability, flexibility vs simplicity, speed to market vs maintainability. If you don't make the trade-offs explicit, you get accidental architecture: a system that is fast in dev, expensive in prod, and impossible to change.

Trade-off analysis is the practice of making those tensions explicit before you commit.

### Mental model

Think of design as a constrained optimization problem, not a search for perfection.

You have:
* **Hard constraints** - non-negotiable: compliance, SLA, budget cap
* **Soft preferences** - negotiable: low latency, high throughput, easy ops
* **Levers** - architectural choices that move you along axes

A good trade-off is not a compromise. It is a deliberate allocation of scarce resources.

### How it works

1. **Name the dimensions that matter.** Pick 3-5 that actually constrain the business. For most systems: latency, throughput, consistency, availability, cost, operational complexity, time to market.
2. **Quantify the constraints.** Convert requirements to numbers. "Fast" -> p95 < 200ms. "Cheap" -> <$0.01 per request. Without numbers you compare feelings.
3. **Enumerate options, not solutions.** Two or three distinct architectural strategies, not ten minor variations.
4. **Score each option per dimension.** What does it improve? What does it cost?
5. **Choose with context.** The right choice depends on the phase, scale, and risk profile.

```mermaid
flowchart LR
    Req[Requirements] --> Constraints[Hard vs Soft Constraints]
    Constraints --> Options[2-3 Architectural Options]
    Options --> Matrix[Score: Latency | Cost | Consistency | Ops]
    Matrix --> Decision[Deliberate Choice + Assumptions]
    Decision --> Monitor[Re-evaluate when assumptions break]
```

### Architectural reasoning

Trade-off analysis helps when requirements conflict and you must commit.

**When it helps:** New service boundary, scaling bottleneck, reliability incident postmortem, AI inference serving design.

**What it solves:** Prevents local optimization. Example: choosing a strongly consistent DB improves correctness but adds latency and cost. If you never state that you value correctness over latency, a developer will later "fix" latency by adding caching and silently break correctness.

**Alternatives:** You can defer the decision with abstraction, or you can accept a default. Both are valid trade-offs. Deferral buys optionality at the cost of complexity. Defaults buy speed at the cost of future rework.

### Trade-offs and failure modes

The architect needs to remember these four:

* **Latency vs Cost.** Lower latency requires over-provisioning, faster storage, more replicas, smaller batch sizes. You pay for it continuously. For AI systems, smaller batch = lower latency but worse GPU utilization and higher cost per token.
* **Consistency vs Availability.** Strong consistency simplifies reasoning but reduces availability during partitions. Eventual consistency improves availability but forces you to design for reconciliation and out-of-order events.
* **Simplicity vs Flexibility.** A simple monolith ships fast and is easy to reason about. A modular service mesh is flexible but increases operational surface area. Complexity compounds.
* **Speed to market vs Maintainability.** Hacks and shortcuts get you to launch. They become architectural debt when the system scales.

Failure modes:
* **False dichotomy.** You assume two options are mutually exclusive when a third exists. Example: you think you must choose between expensive managed service vs build in-house. Often a hybrid with managed core + custom edge works.
* **Static analysis.** Trade-offs change with scale. A design that is optimal at 1k RPS is wrong at 1M RPS.
* **Optimizing the wrong dimension.** You make the system faster when the real constraint is cost or data correctness.

### Example

AI inference serving for a recommendation model.

Options:
A. Synchronous online serving on GPU autoscaling pods. p95 latency 80ms, cost $12k/mo at current load, simple ops.
B. Async batch inference with queue + pre-computed embeddings. p95 latency 800ms, cost $3k/mo, requires staleness tolerance.

Constraints: Product requires <200ms for user-facing feed. Budget is capped.

Analysis: Latency is hard, cost is soft. Option A wins despite cost. However, the team notes that 70% of requests are for cold users where 1s latency is acceptable. Decision: split traffic. Hot path uses A, cold path uses B. You explicitly trade a small increase in system complexity for 40% cost reduction while keeping SLA.

This is trade-off analysis in practice: you didn't pick A or B, you partitioned the problem.

### Reasoning challenge

You are designing a RAG system for internal knowledge search.

Option 1: Store embeddings in a vector DB with strong consistency and synchronous updates. Guarantees fresh data, higher write latency, higher cost.
Option 2: Write-through to object storage, async index update via stream. Eventual consistency ~30s lag, lower cost, higher availability.

Business says "answers must be accurate" but also "search must be available during incidents". What dimensions do you quantify first, and what question do you ask the product owner to make the trade-off explicit?

### Key takeaway

* Trade-offs are inevitable. The goal is to make them explicit, not eliminate them.
* Quantify constraints before comparing options. Vague requirements produce vague architecture.
* Record the assumptions that justify your choice. Re-evaluate when they change.
* Good architecture is a set of deliberate compromises, documented and monitored.
