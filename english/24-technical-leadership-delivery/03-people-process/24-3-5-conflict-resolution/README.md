# Conflict resolution

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 24.3.5 — People & process

**Conflict resolution**

### 1. The problem

Conflict appears when two people want different things from the same system, and both have legitimate reasons.

On a delivery team this is not a personality flaw. It is a constraint collision:
- Engineering wants reliability and low technical debt
- Product wants speed to market
- Security wants controls
- Data science wants model flexibility
- Finance wants cost control

When constraints are made explicit, they conflict. If you suppress the conflict, it goes underground and becomes delays, passive-aggressive PRs, rework, and attrition.

The need for conflict resolution is not to make everyone happy. It is to make the trade-off visible and decidable.

### 2. Mental model

Think of conflict as a signal, not a bug.

A disagreement is data that the current system of decisions is underspecified. The underlying structure is:

```
Goal A needs X
Goal B needs Y
X and Y cannot both be fully satisfied with current constraints
```

Resolution is the process of making the constraints explicit, and choosing which constraint to relax, which to accept, and how to design around it.

### 3. How it works

Effective resolution is not mediation, it is structured decision making.

```mermaid
flowchart LR
    A[Disagreement surfaced] --> B[Name the conflict]
    B --> C[Map constraints & goals]
    C --> D[Separate people from data]
    D --> E[Generate options]
    E --> F[Choose with criteria]
    F --> G[Close loop]
```

Name it explicitly. "We disagree on whether to build a real-time feature flag service vs extend the existing config service."

Map constraints: latency budget, team capacity, risk tolerance, compliance, reversibility.

Separate people from data. The goal is not to win the argument, it is to test hypotheses. Ask: What evidence would change your mind?

Generate 2-3 options, not a binary. Option A: build new service. Option B: extend existing. Option C: defer with a temporary workaround with explicit sunset criteria.

Choose with decision criteria agreed upfront: risk, cost, time to value, reversibility. Document the decision and the trade-offs accepted.

### 4. Architectural reasoning

When does this matter architecturally?

* Cross-team dependencies. Two services need the same data model but different SLAs.
* Technical direction forks. Monolith vs services, sync vs async, build vs buy.
* Priority conflicts. Roadmap items compete for the same engineers.

Conflict resolution enables an architecture decision record to exist. Without it you get "we tried both" and hidden work.

Alternatives:
* Escalate to manager = removes context, creates hierarchy dependency
* Vote = optimizes for popularity, not constraints
* Delay = lets entropy win

You choose structured resolution when the decision is reversible at low cost, you can test assumptions, or when the cost of misalignment > cost of discussion.

### 5. Trade-offs and failure modes

**Speed vs quality of decision.** A fast decision preserves momentum but may miss a constraint. A slow decision erodes trust. Use time-boxed resolution: 30-90 min for tactical, 1-2 meetings for strategic.

**Transparency vs psychological safety.** Naming conflict openly can feel risky. If the culture punishes dissent, people will hide disagreement until production incidents.

**Decision authority vs buy-in.** An architect can decide, but if the team does not understand why, implementation will be half-hearted. The trade-off is decision velocity vs adoption.

Failure modes:
* Reframing as personal: "You are being difficult" → stalls progress
* Premature compromise: splitting the difference on architectural qualities
* No closure: agreement to disagree without recording the trade-off

### 6. Example

Platform team wants to enforce a single event bus for all AI feature telemetry to enable replay and governance. Data science team needs low-latency point-to-point writes to a feature store for online inference.

Conflict: governance vs latency.

Mapping constraints:
- Platform: auditability, replay, schema evolution
- Data Science: p99 < 50ms, no extra hop

Options:
A. Event bus for all telemetry, async mirror to feature store
B. Dual write: direct to feature store + async to bus
C. Feature store writes first, bus ingestion with 5 min lag acceptable

Criteria: latency budget is non-negotiable for online path. Auditability is required but can be eventually consistent.

Decision: B with contract. Direct write to feature store for hot path, async to bus for governance. Add monitoring for drift between stores and explicit owner for reconciliation.

The conflict is resolved because constraints are explicit, not because one side won.

### 7. Reasoning challenge

Two teams own a customer profile service. Team A wants to add a new field `risk_score` computed synchronously on read. Team B owns the read path and says it will add 120ms p99 latency and violates the service's read SLA.

You have 45 minutes. What do you surface first: the technical disagreement, the SLA definition, or the business value of the field? What criteria do you set before generating options?

### 8. Key takeaway

* Conflict is a signal of competing constraints, not bad people.
* Name the conflict explicitly and map the underlying goals and constraints before debating solutions.
* Resolution is a decision process with criteria, options, and recorded trade-offs, not consensus.
* Close the loop: document decision, rationale, and what would trigger revisiting.

You will know it worked when the team can disagree quickly and still move forward with a shared understanding of what was sacrificed.
