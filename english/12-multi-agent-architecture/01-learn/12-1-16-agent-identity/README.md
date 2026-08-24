# Agent identity

> **Learning Path:** Multi-Agent Architecture
> **Section:** 12.1.16 — Learn

**Agent identity**

### 1. The problem

In a single agent, identity is trivial: one user, one session, one model. In multi-agent, agents call agents, share tools, and hand off work.

Who made that decision? Who is authorized to call that tool? Can we audit it later? If Agent A spawns Agent B for a sub-task, does B inherit A's permissions or get its own?

Without explicit identity you get confused deputy, loss of auditability, and memory bleed. An ephemeral process ID is not enough.

### 2. Mental model

Agent identity is not a name. It is three layers that must be kept consistent:

* **Instance identity:** a cryptographically verifiable ID for a running agent execution. `agent:finance-reviewer:run_42b9`. It is short-lived and signed.
* **Persona / Role identity:** what the agent is allowed to be. `role=claims-specialist`, `team=finance`. This defines capabilities, policies, and trust boundaries.
* **Provenance chain:** who created it, who delegated to it, with what claims. Identity propagates like a call stack, not just a label.

Think of it as a passport + role badge + chain of custody.

### 3. How it works

An identity provider issues identities at agent start. The runtime holds a private key for signing outbound messages and verifies inbound signatures.

Messages are not just `content`. They are `content + sender_id + role_claims + signature + parent_id`.

```
mermaid
flowchart LR
    IDP[Identity Provider] -->|issues key + claims| A[Agent A<br/>instance + role]
    A -->|signed request with parent_id| B[Agent B]
    B -->|signed response with provenance| A
    A -->|writes| Audit[Audit Log]
    IDP -. revokes -> A
```

The orchestrator does not trust a string. It verifies the signature, checks role claims against the policy for the requested action, and records the provenance chain.

Memory and tool access are scoped to instance identity, not shared globally.

### 4. Architectural reasoning

Use explicit agent identity when:

* Agents delegate to other agents. You need non-repudiation for the handoff.
* Agents use privileged tools. Authorization must be per-instance, not per-human-user.
* You need audit and compliance. Regulators ask "which autonomous system acted?"
* You have long-running memory. Identity provides a stable anchor for continuity without conflating users.

Alternatives:
* **Session-scoped anonymous IDs.** Simpler, but no cross-session accountability and no delegation trust.
* **Human-user identity only.** Treats agents as extensions of the user. Breaks down when agents act autonomously or in parallel.

Choose explicit agent identity when autonomy and delegation exist. Keep it lightweight when agents are stateless functions.

### 5. Trade-offs and failure modes

* **Identity proliferation vs. granularity.** Too fine-grained IDs create management overhead. Too coarse and you lose isolation.
* **Propagation risk.** If an agent forwards its parent claims verbatim, you get privilege escalation. Claims must be attenuated on delegation.
* **Identity drift.** Long-lived agents with mutable roles can accumulate stale permissions. Require re-attestation.
* **Confused deputy.** Agent B trusts A's signature but does not verify that A was actually authorized to delegate that specific task.

Operational cost is real: key management, revocation, and audit storage. The benefit is security and debuggability.

### 6. Example

Enterprise support triage:

`User -> Triage Agent -> Specialist Agent -> Tool:Refund API`

Triage has role `triage` with claim `can_delegate_to:specialist`. It signs a sub-task to Specialist with parent_id and limited claims `can_call:refund_api, max_amount:500`. Specialist verifies signature, checks its own role `specialist`, and checks the attenuated claim. The refund is logged as `initiated_by=user, delegated_by=triage:run_9f1, executed_by=specialist:run_3a2`.

If the refund is disputed, the chain is reconstructible. If Triage is compromised, revoking Triage's signing key stops new delegations without killing all specialists.

### 7. Reasoning challenge

You are designing a multi-agent code review system. Reviewer agents can spawn Linter agents and Security agents. Should the Linter inherit the Reviewer's permissions to read all repos, or should it get a minimal, repo-scoped identity per invocation?

Consider audit, least privilege, and blast radius if a Linter is compromised.

### 8. Key takeaway

* Identity in multi-agent systems is about verifiable provenance, not naming.
* Separate instance identity, role claims, and delegation chain.
* Sign messages and attenuate claims on delegation; never trust labels.
* Design identity for auditability and least privilege first, convenience second.
