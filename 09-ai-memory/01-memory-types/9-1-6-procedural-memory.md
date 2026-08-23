# Procedural memory

> **Learning Path:** AI Memory
> **Section:** 9.1.6 — Memory types

**The problem**

An LLM agent can recall facts. It cannot reliably *do* things the same way every time.

Give it a loan approval workflow today and it will reconstruct the steps from its training data and prompt context. Tomorrow it will reconstruct a slightly different version. Cost rises with context, latency rises with reasoning, and compliance drifts.

You need repeatable skill, not re-derivation. Procedural memory is the architectural answer to: how do we make an agent perform a learned procedure consistently, quickly, and safely without re-prompting the whole reasoning chain each time?

**Mental model**

Procedural memory is muscle memory for agents: how to do, not what is known.

* Declarative memory = what / when: facts, entities, events.
* Procedural memory = how: conditioned sequences of actions, tool calls, policies.

It is implicit. You don’t recall the steps; you execute them.

**How it works**

Procedural memory can be implicit or explicit.

Implicit: skill encoded in weights via fine-tuning, RLHF, or reinforcement learning. The model internalizes a policy: `state -> action`. Fast at inference, hard to inspect, update, or audit.

Explicit: a versioned skill library the agent can retrieve and follow. Stored as structured procedures, action templates, or state machines. The planner retrieves the relevant procedure and binds current context to it.

In practice you get a hybrid:

```mermaid
flowchart LR
    Intent --> Planner
    Planner --> PM[Procedural Memory]
    PM --> Skill[Skill / Policy]
    Skill --> Executor[Tool Executor]
    Executor --> Feedback[Outcome Feedback]
    Feedback --> PM
```

The procedural store is updated from feedback, not just new facts. Success reinforces the procedure; failure triggers revision.

**Architectural reasoning**

Use procedural memory when the task is repetitive, multi-step, and constrained.

When it helps:
* Tool use patterns that must be identical every time, e.g., KYC verification, refund issuance.
* Compliance workflows with hard steps and audit requirements.
* Latency-sensitive execution where re-planning is wasteful.

Alternatives:
* Prompt the steps every time. Cheap to change, expensive at runtime, inconsistent.
* RAG over documentation. Gives declarative instructions but no execution policy.
* Fine-tune the model. Gives implicit skill but poor traceability and slow to update.

Decision: make the procedure explicit and versioned if you need auditability, governance, and fast updates. Keep it implicit in weights if the skill is broad, fuzzy, and benefits from generalization.

**Trade-offs and failure modes**

* Stability vs plasticity. A frozen procedure is safe but stale. A constantly learning procedure drifts. You need explicit versioning and canary rollout for procedural updates.
* Implicit vs explicit cost. Implicit is cheap at inference, expensive to train and opaque. Explicit is inspectable and governable, adds retrieval and binding latency.
* Generalization vs brittleness. Learned policies generalize well to novel inputs. Retrieved procedures are brittle to out-of-scope inputs unless you have good guardrails and fallback to planning.
* Procedural drift. Feedback loops can reinforce bad shortcuts. You must log actual executions and compare against the canonical procedure.

**Example**

Enterprise support agent for returns.

Declarative memory holds product catalog, return policy text, customer history.

Procedural memory holds the *Return Authorization Procedure v3.2*:

1. Verify purchase in last 90 days
2. Check warranty flag
3. If high value >$500, require manager approval tool call
4. Generate label, log audit event

The planner retrieves the procedure by intent classification, binds customer ID and order ID, and the executor runs the steps deterministically. When compliance changes the approval threshold, you update the procedure artifact, not the model. Execution stays identical across agents and is auditable.

**Reasoning challenge**

You are building a medical triage chatbot that must follow a safety-critical escalation script. New clinical guidelines arrive quarterly. Do you encode the script as an explicit procedural memory with versioned retrieval, or bake it into model weights via fine-tuning? What breaks first if you choose wrong?

**Key takeaway**

* Procedural memory stores how to act, not what to know. Separate it from declarative knowledge.
* Make procedures explicit and versioned when you need auditability, compliance, and rapid updates.
* Implicit procedural skill lives in weights; explicit procedural skill lives in a retrievable, executable library.
* Guard against drift: version procedures, log executions, and test updates before rollout.
