# Maintainability

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 23.1.5 — Non-functional requirements

### The problem

You ship v1. It works. Six months later the business needs a new tax rule, a new payment provider, and GDPR deletion. The change touches 12 files, breaks an unrelated report, and takes two engineers three days to test safely.

The problem isn't the change. It's the *cost and risk of change*. Every system must evolve — requirements shift, bugs appear, teams turn over. If modifying the system is expensive, slow, and dangerous, the system stops evolving or evolves through workarounds.

Maintainability is the non-functional requirement that controls that cost over the lifetime of the system.

### Mental model

Think of maintainability as the rate at which you can absorb change per unit of cost and risk.

A maintainable system lets a small, well-scoped change stay small. A non-maintainable system makes every change radiate.

The core mental model is **change containment**. Can you reason about what a change will affect, can you test that impact, and can you deploy it with confidence?

```mermaid
flowchart LR
    C[Change Request] --> A[Impact Boundary]
    A -->|small| T[Fast test & deploy]
    A -->|large| R[Risk, delay, regressions]
    R --> D[Workarounds & tech debt]
```

### How it works

Maintainability isn't a feature you add. It's an emergent property of design choices that make intent visible and side-effects bounded.

The essential mechanisms are:

* **Clear boundaries and contracts.** Modules/services have explicit interfaces. Internal structure is hidden. You can change inside a boundary without renegotiating the outside.
* **Local reasoning.** A developer can understand a change by reading a small amount of code, not the whole system. Names, types, and tests encode intent.
* **Observability and testability.** You can prove a change works. Automated tests, contracts, and production signals give fast feedback.
* **Explicit dependencies.** Dependencies are visible and acyclic where possible. No hidden global state or surprise coupling.
* **Operational simplicity.** Deployments are reversible, changes are small, and runbooks exist.

These mechanisms don't make code pretty. They make change cheap.

### Architectural reasoning

When it helps:
* Systems with a long lifetime and frequent change — core domains, platforms, AI services with evolving prompts/models.
* Large teams where ownership is split. Boundaries reduce coordination.
* Regulated or high-reliability domains where a bad change is expensive.

What it solves:
* Reduces mean time to change and defect escape rate.
* Makes onboarding and team churn survivable.

Alternatives and why you might choose them:
* Optimize for first-time speed: throwaway prototype, tightly coupled scripts. Accept high change cost because lifetime is short.
* Optimize for performance: tightly coupled, highly optimized code. Accept higher change cost because change is rare and performance is critical.

Decision is economic: expected number of future changes × cost per change vs upfront cost of better boundaries, tests, and abstraction.

### Trade-offs and failure modes

* **Maintainability vs time-to-market.** Good boundaries and tests slow the first build. The payoff is later.
* **Maintainability vs performance.** Indirection, abstraction, and safety checks add overhead. Choose where the bottleneck actually is.
* **Over-abstraction.** Boundaries that are too granular create churn in coordination. The cost of change moves from code to process.
* **False maintainability.** Code is clean but behavior is undocumented. Without tests and observability, clean code is still risky to change.
* **Team coupling.** Even perfect code is unmaintainable if only one person understands it. Maintainability requires shared ownership and documentation of *why*, not just *what*.

Common failure mode: a system that is locally clean but globally tangled. Each service is tidy, but they share databases, implicit event ordering, and undocumented assumptions. Change still radiates.

### Example

Enterprise payments platform. Two services: `Pricing` and `Billing`.

Poor design: `Billing` imports pricing logic directly and reads `Pricing` tables. A tax rule change requires edits in both services and a coordinated deploy.

Maintainable design: `Pricing` exposes a versioned contract `calculate(order) -> price`. `Billing` only depends on the contract and a test double. Tax rule changes are contained in `Pricing`, verified by contract tests, and released independently behind a feature flag.

Cost: extra network hop and contract test suite. Benefit: Pricing team can ship daily without involving Billing, and a bug in pricing is isolated and observable.

This is the same reasoning that applies to AI systems: prompt/model versioning, feature stores, and evaluation suites are maintainability mechanisms for non-deterministic components.

### Reasoning challenge

You inherit a monolith with 200k LOC, no tests, and shared DB. Business demands two new features per quarter. Team is 8 engineers, high churn.

Option A: spend 3 months adding tests and extracting two bounded contexts, then deliver features slower initially.
Option B: keep shipping features in the monolith with hotfixes, accepting increasing regression risk.

What signals would you need to decide, and where would you draw the first boundary if you choose A?

### Key takeaway

* Maintainability is about the cost and risk of future change, not code aesthetics.
* It is created by clear boundaries, explicit contracts, testability, and observability.
* It trades upfront design and slower initial delivery for cheaper, safer change over time.
* Unmaintainable systems don't stop changing; they accumulate workarounds until change becomes impossible.
