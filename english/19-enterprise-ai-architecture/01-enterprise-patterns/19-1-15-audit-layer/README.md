# Audit layer

> **Learning Path:** Enterprise AI Architecture
> **Section:** 19.1.15 — Enterprise patterns

**Audit layer**

### 1. The problem

In enterprise AI, a decision is not just code. It is: who asked, what prompt was sent, which model version ran, what data was in context, what output was returned, and who acted on it.

Without a dedicated record, you cannot prove what happened. You cannot debug a bad output, defend a decision to a regulator, or reproduce a failure. Logging is for operators. Auditing is for accountability.

The problem gets worse with AI: non-determinism, prompt injection, RAG context, and model updates make a single output impossible to explain from application logs alone. Compliance requirements like GDPR, SOC2, HIPAA and emerging AI acts require immutable, attributable trails of automated decisions.

### 2. Mental model

Think of the audit layer as a witness, not a participant.

It sits beside the business flow and observes every decision-relevant event, then writes an append-only, tamper-evident record. Business logic never reads the audit store; the audit store never blocks business logic.

It captures *what* happened, *who* caused it, *with what inputs*, and *under what policy* at the time.

### 3. How it works

Events are emitted at trust boundaries: API ingress, policy check, model call, tool use, human approval, final action.

Each audit event contains:
* Identity and auth context
* Request fingerprint: prompt, parameters, model id, version, temperature, tools
* Data lineage: retrieval sources, vector IDs, training cutoff
* Decision output and confidence
* Policy snapshot: guardrails active, allowlist version
* Timestamp and correlation id

Emission is asynchronous via outbox pattern or event bus. The event is signed and written to an immutable store optimized for append and verification, not fast OLAP. Retention and PII handling are enforced at the store level.

```mermaid
flowchart LR
User[User Request] --> App[Application Layer]
App --> AI[AI Service]
App --> Outbox[Audit Outbox]
AI --> Outbox
Outbox --> Store[(Immutable Audit Store)]
Store --> Query[Compliance / Forensics Query]
```

### 4. Architectural reasoning

**When it helps**
* High-stakes decisions: credit, hiring, medical triage, legal advice
* Regulated domains requiring non-repudiation and reconstruction
* Multi-agent systems where responsibility is distributed
* Production AI where model drift and prompt changes must be traceable

**Alternatives**
* Inline logging: cheap, but logs are mutable, incomplete, and mixed with debug noise
* Observability traces: great for latency, poor for legal attestation
* Application-level audit tables: couples audit to app schema and risks tampering

Audit layer decouples *compliance durability* from *operational speed*.

### 5. Trade-offs and failure modes

* **Completeness vs latency.** Synchronous audit guarantees delivery but adds tail latency. Async is normal, with at-least-once delivery and reconciliation.
* **Storage cost vs queryability.** Immutable raw events are cheap to write, expensive to query. Keep hot index for recent audits, cold archive for long retention.
* **Privacy vs fidelity.** Full prompt capture aids forensics but contains PII. Apply field-level redaction and encryption at rest; keep audit keys separate from app keys.
* **Failure modes to design for:** audit emitter drops events under load, clock skew breaks ordering, model version not recorded, partial context capture makes reconstruction impossible, and audit store becomes a target for tampering.

If audit is best-effort, it is not audit.

### 6. Example

Loan approval assistant.

User request → Authenticated user ID and session → Policy engine checks allowlist version v3.2 → RAG retrieves 3 credit bureau docs with IDs → Model `gpt-4.1-2025-06` with temp 0.2 → Output: approve with reason.

The audit layer records one immutable event with correlation ID `req-abc123`, capturing user, policy version, retrieved doc IDs, prompt template hash, model version, output hash, and approver. Six months later, a regulator asks why this loan was approved. The decision is reconstructed exactly, without trusting the current application code.

### 7. Reasoning challenge

Your AI customer support agent auto-refunds users under $50 without human review. Latency SLA is <800ms p95. Compliance requires an immutable record of every auto-refund with the exact prompt and model version used at decision time.

Do you emit audit synchronously before refund, or asynchronously after? What do you do if the audit emitter is down?

### 8. Key takeaway

* Audit is an architectural boundary for accountability, not a logging feature.
* Capture decision-relevant facts at trust boundaries, emit asynchronously, store immutably.
* Design for tamper evidence, completeness, and reconstruction, not just observability.
* Accept the cost in storage and complexity because the alternative is unprovable AI behavior in production.
