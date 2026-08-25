# Agent registry

> **Learning Path:** Enterprise AI Architecture
> **Section:** 19.1.6 — Enterprise patterns

**Agent registry**

### 1. The problem

What problem appears when you move from 3 prototype agents to 300 production agents?

You can no longer hard-code who does what. Agents are created, versioned, scaled, and retired continuously. An orchestrator needs to know *which* agent can handle a task *right now*, with the right capabilities, policies, and SLAs.

Without a source of truth, you get:
* Routing brittleness: orchestrators break when an agent moves or a new version deploys
* Capability drift: the system doesn't know an agent can now do summarization + classification, or can't do PII
* Operational blindness: no inventory of who is running, healthy, costing, or compliant

The problem is not "find a service". It's discoverable, governable capability matching in a dynamic multi-agent system.

### 2. Mental model

Think of it as a phonebook + resume board for autonomous agents, not just a service registry.

A service registry tracks *where* a service is. An agent registry tracks *what it can do, under what constraints, and whether it's allowed to do it for this request*.

### 3. How it works

Essentially three operations:

**Register:** On startup an agent publishes a card: id, version, endpoint, capabilities, input/output schemas, cost model, policies, owner team.

**Discover:** An orchestrator queries `find(agent, constraints)` e.g., `intent=loan_risk, region=EU, pii_allowed=false, latency<500ms`.

**Heartbeat & lifecycle:** Health, load, and version are refreshed. Deregistration on failure triggers failover.

```mermaid
flowchart LR
    Orchestrator -->|find(capability, constraints)| Registry
    Registry -->|candidate set| Orchestrator
    Orchestrator -->|invoke| Agent[Agent Instance]
    Agent -->|register/heartbeat| Registry
    PolicyEngine -->|approve/deny| Registry
```

The registry is read-heavy, write-light, and must be strongly consistent for metadata, eventually consistent for health.

### 4. Architectural reasoning

**When it helps**
* Many agents with overlapping capabilities and you need routing by capability, not just name
* Agents are ephemeral and versioned frequently
* You need governance: cost controls, compliance tags, data residency, audit trails
* You want dynamic orchestration: planner can compose agents at runtime

**Alternatives**
* Hard-coded routing table: works for <10 static agents, fails at scale
* Service mesh / Consul only: gives location and health, not semantic capability
* Central orchestrator with embedded knowledge: becomes a bottleneck and single source of truth for logic

Choose an agent registry when discovery needs to be *semantic and policy-aware*, not just network-aware.

### 5. Trade-offs and failure modes

* **Centralization risk.** Registry is a critical dependency. Mitigate with read replicas, cache in orchestrators, and local fallback to last-known-good.
* **Stale metadata.** Capability cards drift from reality. Require versioned schemas and automated validation on register.
* **Latency.** An extra lookup per request. Acceptable if cached; problematic for tight loops. Common pattern: registry seeds a local capability index in the orchestrator, refreshed every seconds.
* **Governance vs speed.** Rich policy checks improve safety but add complexity. Decide what is enforced in-registry vs at invoke-time.
* **Schema sprawl.** If capability description is free-form, discovery fails. You need a controlled vocabulary and contract tests.

### 6. Example

A bank runs agents for loan processing: `DocumentExtractor`, `RiskScorerEU`, `RiskScorerUS`, `FraudChecker`, `ExplainabilitySummarizer`.

An intake orchestrator receives a request: `document_type=pdf, region=EU, pii=true`.

It queries the registry with constraints `{pii_allowed=true, region=EU}` and gets the current healthy `DocumentExtractor v2.3` and `RiskScorerEU v1.8`. The registry also returns cost per call and the owning team for audit.

When `RiskScorerEU v1.9` deploys with lower latency, it registers itself. The orchestrator automatically starts routing new traffic without a config change. When the EU data residency policy changes, the PolicyEngine revokes the card for non-EU instances instantly.

### 7. Reasoning challenge

You have 200 agents with 10% churn per hour and strict latency SLOs <100ms for routing decisions. Do you query the registry on every request, or cache it locally in the orchestrator? What consistency guarantees do you need for capability vs health?

### 8. Key takeaway

* An agent registry solves dynamic, semantic discovery and governance, not just service location
* It enables runtime routing by capability + policy, which hard-coding cannot
* Keep metadata authoritative and versioned; health can be eventually consistent
* Centralization buys consistency and auditability; cache it to avoid becoming a bottleneck
* The real value is architectural: it decouples *who exists* from *who is chosen*
