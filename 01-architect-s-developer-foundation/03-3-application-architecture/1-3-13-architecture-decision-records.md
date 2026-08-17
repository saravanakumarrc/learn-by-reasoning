# Architecture Decision Records

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.3.13 — 3. Application architecture

**The problem**

You ship a system. Six months later a new engineer asks: "Why did we pick Kafka over SQS for events?" The answer lives in a Slack thread, a design doc no one links to, or in someone's head. The team re-debates the same choice, or worse, undoes it without understanding the constraints that shaped it.

As systems grow, decisions compound. Requirements change, people leave, code drifts from intent. Without a durable record of *why* an architecture looks the way it does, you lose accountability, repeat mistakes, and spend time reconstructing history instead of reasoning about the future.

**Mental model**

An Architecture Decision Record is a time-stamped, lightweight log of a significant architectural choice and the reasoning behind it. It is not documentation of what you built. It is a decision audit trail.

Think of it as a commit message for architecture: context at the time, options considered, decision made, and consequences accepted. The value is not the record itself, it is that the record forces explicit reasoning now, and makes that reasoning inspectable later.

**How it works**

An ADR is a small markdown file, usually in `/docs/adr/`, named by date and title. The essential fields are:

* Context: what problem are we solving, what constraints exist now
* Options considered: what was evaluated and why
* Decision: what was chosen
* Consequences: what we gain, what we give up, what we must monitor

Status tracks lifecycle: Proposed → Accepted → Superseded → Deprecated. When a decision is revisited, you do not edit the old ADR. You create a new ADR that supersedes it and links back. History stays intact.

```mermaid
flowchart LR
    Context[Context + Constraints] --> Options[Options]
    Options --> Decision[Decision]
    Decision --> Consequences[Consequences]
    Consequences --> ADR[ADR Accepted]
    ADR -->|time passes| Review[Review / New Context]
    Review -->|changed| NewADR[New ADR Supersedes]
```

**Architectural reasoning**

ADRs help when decisions are irreversible or expensive to reverse, made under ambiguity, and will be questioned later.

They solve:
* **Memory loss.** New team members can understand rationale without oral history.
* **Re-debate prevention.** The record shows what was known then, not what seems obvious now.
* **Risk visibility.** Consequences make trade-offs explicit and reviewable.

Alternatives are informal notes, wikis, or PR comments. Those capture *what* was done, but not the bounded context in which it made sense. ADRs are chosen when you need traceability for compliance, audits, or large distributed teams where alignment costs are high.

You would *not* ADR every dependency bump. You would ADR when the choice shapes the system: data model, service boundaries, consistency model, deployment topology, external integration pattern.

**Trade-offs and failure modes**

* **ADR rot.** Records are written and never updated. Accepted ADRs become fiction. Mitigate by linking ADRs to architecture reviews and requiring a superseding ADR for reversals.
* **Over-documentation.** Writing ADRs for trivial choices creates noise and is abandoned. Use a threshold: is this decision hard to reverse in >1 sprint? Will others need to understand it?
* **False certainty.** ADRs can fossilize a bad decision if consequences are not monitored. Treat them as hypotheses, not contracts. The record should include what would prove the decision wrong.
* **Process overhead.** If writing an ADR is heavy, teams skip it. Keep template minimal and time-box writing to ~20 minutes.

**Example**

Team needs a new order service. Options: PostgreSQL with read replicas vs DynamoDB.

Context: 10k orders/day now, projected 10x in 18 months. Strong consistency needed for payment state. Team has deep Postgres expertise, limited DynamoDB experience. Multi-region active-active is not required in year one.

Decision: PostgreSQL.

Consequences: Accept operational overhead of replicas and backups. Gain strong transactional guarantees and team velocity. Revisit if write throughput exceeds ~5k/s or multi-region becomes mandatory. Metric to watch: p95 write latency and replication lag.

Two years later, latency degrades. A new ADR supersedes the old one, referencing the original metrics and the changed constraint, choosing Aurora Global Database. The history explains why the first choice was rational then and why it no longer is.

**Reasoning challenge**

Your team wants to upgrade a logging library from v2 to v3. The change is backward compatible, no API changes, just better performance. Do you write an ADR? What information would make you decide yes or no? What would you put in the ADR if you wrote one?

**Key takeaway**

* ADRs capture *why* a decision was made under specific constraints, not just what was built.
* They are valuable for irreversible, high-impact choices where future understanding matters.
* Keep them small, time-stamped, and supersedable. An ADR is a record of reasoning, not a guarantee of correctness.
* The real benefit is the discipline of making trade-offs explicit now, so you can learn from them later.
