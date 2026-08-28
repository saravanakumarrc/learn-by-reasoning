# Agent identity

> **Learning Path:** Security Architecture
> **Section:** 6.3.11 — AI security

## 1. Problem

ஒரு AI agent banking service-ஐ call பண்ணி payment initiate பண்ணுது. API log-ல "agent-123 called /payments" என்று இருக்கு. 

இப்போது கேள்வி: இந்த agent யாருடையது? எந்த tenant-க்கு சேர்ந்தது? எந்த model version ஓடுது? எந்த human user இதை trigger பண்ணினார்? Agent தன்னுடைய decision-ஐ ஏன் எடுத்தது என்பதற்கு provenance இருக்கா?

Traditional service-க்கு ஒரு static identity போதும். Agent அப்படி இல்லை. Agents dynamically spawn ஆகும், delegate பண்ணும், tools-ஐ தொடர்ந்து மாற்றும். ஒரு agent compromise ஆனால் அதன் blast radius எவ்வளவு? Audit-க்கு யார் responsible?

இந்த confusion தான் agent identity தேவையை உருவாக்கியது.

## 2. Mental Model

Agent identity என்பது ஒரு API key அல்ல. அது ஒரு **chain of trust**.

`Human / Tenant → Agent Runtime → Agent Instance → Tool Call`

ஒவ்வொரு step-க்கும் who, what, why என்று தெரிய வேண்டும். Identity-ல் இருக்க வேண்டியது:

* **Who**: agent_id, tenant_id, creator
* **What**: capabilities, allowed tools, policy version
* **When**: short-lived, issuance time
* **Provenance**: parent agent, prompt hash, model version

இது basically non-repudiation + least privilege-க்கான foundation.

## 3. How It Works

Architecture-ல் மூன்று விஷயங்கள் தேவை.

**Issuance.** Agent runtime start ஆகும்போது Identity Issuer-இடம் authenticate ஆகி short-lived token வாங்கும். JWT / OAuth2 access token போல, claims-ல் agent metadata இருக்கும்.

**Binding.** Token-ஐ workload-க்கு bind பண்ண வேண்டும். mTLS, SPIFFE/SPIRE போன்ற workload identity, அல்லது runtime attestation. Token-ஐ copy பண்ணி வேறு process-ல் use பண்ண முடியாமல் பார்த்துக்கொள்ள வேண்டும்.

**Propagation.** Agent ஒரு tool-ஐ call பண்ணும்போது, அதே identity context-ஐ propagate பண்ண வேண்டும். Parent agent → child agent என்று chain வைத்திருப்பது audit-க்கு முக்கியம்.

```
User → Agent Runtime
Agent Runtime --authenticate--> Identity Issuer
Identity Issuer --issue--> short-lived JWT with agent claims
Agent Runtime --propagate token--> Tool/Service
Tool/Service --verify--> Authorization decision + audit log
```

## 4. Architectural Reasoning

Agent identity useful ஆகும் போது:

* Multi-tenant AI platform-ல் ஒரே runtime-ல் பல customers agents ஓடும் போது.
* Agents தன்னிச்சையாக external APIs, database, internal services-ஐ அணுகும் போது.
* Compliance தேவைப்படும் domain-ல் finance, healthcare, enterprise support.

Alternatives:

* Static API keys per agent: scale ஆகாது, rotate செய்ய கஷ்டம்.
* No identity, only runtime trust: blast radius பெரியது, audit இல்லை.
* Human user identity மட்டும் propagate: agent-ன் autonomous action-ஐ differentiate செய்ய முடியாது.

Architect தேர்வு செய்யும் போது கேட்க வேண்டியது: identity எவ்வளவு granular ஆக வேண்டும்? Per agent instance, per session, per tool call?

## 5. Trade-offs

* **Granularity vs overhead.** Per invocation identity கொடுத்தால் audit சரியாக இருக்கும், ஆனால் token issuance latency, signing cost வரும்.
* **Centralized identity vs distributed.** Central issuer simple ஆனால் single point of failure / latency. Distributed trust சிக்கலானது.
* **Static capability vs dynamic policy.** Static scopes easy ஆனால் agent behavior மாறும் போது policy update slow. Dynamic policy evaluation flexible ஆனால் decision latency அதிகம்.
* **Revocation.** Short-lived tokens revocation-ஐ எளிதாக்கும். Long-lived credentials compromise ஆனால் impact நீண்ட நாள்.

Failure mode:
