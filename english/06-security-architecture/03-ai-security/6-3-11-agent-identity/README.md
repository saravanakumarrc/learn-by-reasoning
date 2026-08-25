# Agent identity

> **Learning Path:** Security Architecture
> **Section:** 5.3.11 — AI security

### The problem

Traditional security assumes a human user authenticates to a service, and the service trusts the request. 

With autonomous agents the chain becomes: User → Agent → Service. The agent makes tool calls, writes data, and calls other agents on the user's behalf, often without real-time human supervision.

That creates three architectural gaps:
* **Who is acting?** The service sees a request from an agent, not a user. Is it the right agent, for the right tenant, with the right version and permissions?
* **On whose behalf?** The agent must carry user context for authorization and audit, but must not be able to lie about it.
* **Can we audit it?** When an agent autonomously causes damage, you need non-repudiable proof of which identity, with which policy, performed the action.

Without a verifiable agent identity you get confused deputy attacks, prompt injection that escalates privileges, and unauditable cross-tenant actions.

### Mental model

Think of agent identity as a passport + badge + audit log.

* Passport: cryptographically verifiable identity of the agent itself — who it is, who issued it, when it expires.
* Badge: scoped permissions granted to that agent for a specific tenant/workload.
* Audit log: the identity is propagated with every action so downstream systems can attribute behavior.

User identity is still required, but it is *propagated* inside the agent's identity, not replaced.

### How it works

The essential mechanism is issuance, attestation, and propagation.

**Issuance.** Each agent instance or deployment gets a distinct cryptographic identity, typically a key pair issued by a central identity provider. The identity includes agent ID, tenant ID, deployment metadata, and model/version. It is issued as a short-lived JWT or mTLS certificate.

**Attestation.** The identity is bound to a trusted runtime. In production this means the agent proves it is running in a known environment — e.g., via workload identity, SPIFFE/SPIRE, or platform attestation — so a stolen key cannot be used off-platform.

**Propagation.** Every outbound call from the agent carries two identities:
1. Agent identity — who is calling
2. User/tenant context — on whose behalf

Downstream services verify both, enforce policy, and log both.

```mermaid
flowchart LR
U[User Identity] -->|delegates to| A[Agent Platform]
A -->|creates| I[Agent Identity + Attestation]
I -->|presents JWT with user context| S[Service/Tool]
S -->|verifies agent & user, enforces policy| Log[Audit]
```

The agent never creates its own identity; it receives it and must present it on every call.

### Architectural reasoning

Agent identity helps when agents have autonomous write access.

* **Least privilege:** You can scope an agent to read-only CRM for support, and deny write to billing, even if the user could write to billing.
* **Isolation in multi-tenant systems:** Tenant A’s agent cannot impersonate Tenant B because the tenant claim is cryptographically bound in the token.
* **Audit and non-repudiation:** You can trace an action to agent `support-agent-v3` running in `us-east-1` for tenant `acme`, acting on behalf of user `jane@acme`.
* **Revocation:** If a model version is compromised, you revoke that agent identity class without revoking all users.

Alternatives are worse: using a shared service account gives no attribution; using the user’s token directly lets a compromised agent impersonate the user; using static API keys cannot be scoped to runtime.

Choose agent identity when agents call sensitive tools, act across tenants, or need to be audited. Skip it for fully sandboxed, read-only assistants with no external actions.

### Trade-offs and failure modes

* **Centralized vs decentralized issuance.** Centralized is simpler to audit and revoke, but creates a trust bottleneck. Decentralized DIDs enable cross-org agents but complicate policy enforcement.
* **Ephemeral vs long-lived credentials.** Ephemeral per-instance keys limit blast radius but increase issuance load. Long-lived keys are simpler but risk leakage.
* **Identity propagation complexity.** Carrying user context through chains of agents multiplies token size and privacy risk. You must decide what to propagate and for how long.
* **Prompt injection stealing identity.** If the agent builds requests from untrusted input without validation, an attacker can trick it into reusing its own credentials for unauthorized calls. The identity is correct, the intent is not.

Common failure modes: confused deputy where service trusts agent identity but not user context; token leakage via logs; missing attestation allowing a local copy of the agent to use stolen credentials; over-privileged agents because identity was issued too broadly.

### Example

Enterprise support copilot.

The agent is issued an identity `agent://support/v3/tenant=acme`. It is attested to run only in the managed agent platform. When Jane from Acme chats, the platform issues a request-scoped token containing:

* `agent_id`, `tenant=acme`, `model=v3`, `attestation_ok`
* `on_behalf_of=user:jane@acme`, `session_id`

The agent calls Salesforce. Salesforce verifies the agent identity, checks policy “support agents can read Cases, cannot delete”, and verifies the user belongs to tenant acme. The action is logged as `agent support/v3 → user jane@acme`.

If the agent is compromised, you revoke `support/v3` for tenant acme only. Jane’s personal credentials are untouched.

### Reasoning challenge

You are designing a multi-tenant SaaS where each customer can deploy their own custom agents in their own VPC, but those agents also need to call your central knowledge API.

Do you issue a single global agent identity per customer, or a unique identity per agent deployment? What do you propagate from the end user to the API, and how do you prevent a customer’s agent from impersonating another customer’s user?

### Key takeaway

* Agents need their own verifiable identity, separate from and in addition to user identity.
* Identity must be issued, attested, and short-lived, then propagated with user context for every action.
* The architectural win is auditable least privilege and safe delegation, not just authentication.
* The risks are confused deputy, credential leakage, and prompt-injection-driven misuse of a valid identity.
