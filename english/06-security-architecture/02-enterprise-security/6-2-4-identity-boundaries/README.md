# Identity boundaries

> **Learning Path:** Security Architecture
> **Section:** 5.2.4 — Enterprise security

**Identity boundaries**

### 1. The problem

A large enterprise does not have one identity. It has many: employees, contractors, customers, partners, service accounts, AI agents. Each lives in a different system with different lifecycle, risk profile, compliance rules and trust assumptions.

When you treat all identities as one flat namespace you get:
* **Blast radius.** Compromise of the central IdP compromises everything.
* **Policy collision.** One business unit needs immediate deprovisioning, another needs 90-day audit retention. One region needs data residency, another needs global SSO.
* **Trust leakage.** A low-trust identity from a partner portal gets implicitly trusted inside core finance because the token was issued by the same IdP.

The problem is not authentication. It is deciding *where one authority ends and another begins*, and what is allowed to cross.

### 2. Mental model

An identity boundary is a customs border for identity.

Inside the border you have a single source of truth for who someone is, what attributes they have, and how long a token is valid. Crossing the border requires explicit verification, translation of attributes, and a limited trust contract.

Think: passport at a national border, not a building access card.

### 3. How it works

A boundary is defined by three things:

* **Authority.** Which IdP is authoritative for identity lifecycle: create, update, delete, sign tokens.
* **Trust model.** How crossing is proven: direct federation, token exchange, or brokered trust. Typically OIDC/SAML federation with signed assertions, not shared user stores.
* **Attribute mapping.** Identities are rarely 1:1 across boundaries. You map claims, scope, and roles at the border and you never let the foreign attribute set leak unchanged inward.

```
flowchart LR
    User --> IdP_A[Boundary A: Corp HR IdP]
    IdP_A -- signed token --> API_Gateway_A
    Partner --> IdP_B[Boundary B: Partner IdP]
    IdP_B -- federated assertion --> TrustBroker
    TrustBroker -- mapped claims --> API_Gateway_A
    API_Gateway_A -- deny by default --> CoreService
```

Tokens do not cross blindly. They are validated, mapped, and re-issued inside the target boundary with a reduced claim set.

### 4. Architectural reasoning

Use a boundary when:

* **Regulatory or data residency** requires identity data to stay in a region.
* **Risk separation** is needed: e.g., customer identities must not be able to reach internal admin APIs even if the IdP is compromised.
* **Lifecycle ownership** differs: employees managed by HR, customers by CRM, service principals by platform team.
* **Blast radius containment** is a priority: compromise of partner IdP does not give access to crown-jewel systems.

Alternatives:
* **Centralized IdP** - one tenant, one policy. Simple to operate, terrible blast radius, policy lowest common denominator.
* **Full isolation** - each system owns its own users. Zero trust leakage, impossible to operate at scale.
* **Boundaries with federation** - central where sensible, explicit edges where risk/compliance demands it.

Decision rule: centralize identity *management* where you can, but enforce boundaries at the trust and data planes where risk diverges.

### 5. Trade-offs and failure modes

* **Operational overhead vs blast radius.** More boundaries = more IdPs, more federation configs, more key rotation. Fewer boundaries = easier ops, larger blast radius.
* **User experience vs security.** Each boundary adds latency and a possible auth hop. Design for silent token exchange, not multiple logins.
* **Mapping drift.** Attributes get stale or over-permissive at the border. If mapping is manual, it becomes security debt.
* **Failure modes to watch:** token replay across boundaries, over-privileged service accounts with cross-boundary trust, federation loops that create circular trust, and identity sprawl where the same person has 5 principal IDs with no linkage.

### 6. Example

A global bank has Retail Banking and Investment Banking.

Retail uses Azure AD B2C for 20M customers, tokens short-lived, data in EU/US. Investment Banking uses on-prem IdP with HSM-backed keys, stricter MFA, data must stay in EU.

Architectural choice: two identity boundaries with a trust broker.

Customer login never reaches investment systems. Employee login to investment systems is issued by the corporate IdP boundary, which federates to the Investment IdP via SAML with attribute mapping: corporate `employeeId` -> investment `traderId`, and only if `department = Investment` and `mfa = hardware`.

A partner fintech can access a read-only reporting API via a third boundary. Its IdP federates in, but the broker strips all claims except `partner_id` and `scope=reports.read`. No employee attributes are exposed.

### 7. Reasoning challenge

You are architecting SaaS for multi-tenant customers in EU and US. Each tenant wants SSO via their own IdP, and you must guarantee that a tenant admin cannot access another tenant's data even if your platform is compromised.

Do you put all tenants in one IdP tenant with tenant claims in tokens, or create a per-tenant identity boundary? What controls the boundary crossing for your internal services?

### 8. Key takeaway

* Identity boundaries exist to limit blast radius and enforce different trust, compliance and lifecycle rules.
* Define boundaries by authority, trust model, and attribute mapping, not by network perimeter.
* Centralize where you can operate safely; federate explicitly where risk diverges.
* Every cross-boundary hop is a place where claims must be validated, mapped, and minimized.
