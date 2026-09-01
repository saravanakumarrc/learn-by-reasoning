# Agent identity

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.16 — Learn

## 1. Problem

ஒரு multi-agent system-ல் 5-10 agents வேலை செய்யுது. ஒரு user request வருது. இதை Agent A ஆரம்பிக்குது, Agent B க்கு delegate பண்ணுது, Agent C data fetch பண்ணுது.

இப்போது கேள்வி வருது: இந்த response உண்மையில் யார் கொடுத்தது? யார் authorize பண்ணினது? யார் இந்த action-க்கு responsible?

Log-ல் `agent_id = ?` என்று பார்த்தால் ஒன்றும் புரியவில்லை. Audit ஆக வேண்டும், billing ஆக வேண்டும், security policy enforce ஆக வேண்டும். ஆனால் identity தெளிவில்லை.

ஒரு agent மற்றொரு agent-ஐ impersonate செய்தால் என்ன ஆகும்? ஒரு compromised agent முழு system-ஐ access பண்ணலாம்.

**Identity இல்லாமல் trust இல்லை.**

## 2. Mental Model

Agent identity என்பது ஒரு agent-க்கு stable, verifiable, scoped அடையாளம் கொடுப்பது.

மனிதனுக்கு ஆதார் / employee ID போல.

ஒரு agent என்பது:

* **Who it is** - stable ID
* **Who it can act for** - principal / delegation chain
* **What it can do** - permissions / scope
* **Proof it is who it claims** - cryptographic proof

இது authentication + authorization + provenance ஆகியவற்றை ஒன்றாக இணைக்கிறது.

## 3. How It Works

ஒரு agent start ஆகும்போது அது ஒரு identity credential பெறுகிறது. அது typically:

* **Agent ID**: `agent:payments-v1:prod:7f3a`
* **Signing key**: agent-க்கு தனிப்பட்ட private key
* **Claims**: role, tenant, capabilities, expiry

ஒவ்வொரு message / action-க்கும் agent தனது identity-யை sign செய்கிறது. Receiver அதை verify செய்கிறது.

Delegation நடக்கும்போது chain காப்பாற்றப்படுகிறது. Agent A Agent B-க்கு task கொடுக்கும்போது:

`A -> B` என்ற delegation token உருவாக்கப்படும். B அதை காட்டி செயல்படும். Audit trail-ல் `initiated_by=A, delegated_by=A, executed_by=B` தெரியும்.

## 4. Architectural Reasoning

எப்போது identity தேவை?

* **Cross-service trust**: Service A ஒரு agent-ஐ நம்ப வேண்டும்.
* **Audit & compliance**: யார் என்ன செய்தது என்பது prove ஆக வேண்டும்.
* **Delegation**: ஒரு agent மற்றொரு agent-க்கு power கொடுக்கும்போது.
* **Multi-tenant**: வெவ்வேறு customer-க்கு வெவ்வேறு agents.

Alternatives:

* **No identity**: அனைவரும் அனோனிமஸ். Simple ஆனால் audit, security இல்லை.
* **API key per service**: Static. Rotation கடினம், least privilege கிடையாது.
* **Central identity provider**: OIDC / SPIFFE for agents. Manageable ஆனால் latency + dependency.

ஆர்கிடெக்ட் ஏன் choose பண்ணுவார்? System boundary கடக்கும்போது identity mandatory. Internal-only agents என்றால் lightweight ID போதும். Public-facing / financial agents என்றால் strong crypto identity.

## 5. Trade-offs

**Strong identity vs latency**: Sign/verify ஒவ்வொரு call-க்கும் overhead. Caching, short-lived tokens உதவும்.

**Centralized vs decentralized**: Central issuer ஒன்று இருந்தால் control எளிது, ஆனால் single point of failure. Decentralized ஆனால் coordination கடினம்.

**Granularity**: Fine-grained permissions secure ஆனால் policy management complex. Coarse permissions simple ஆனால் over-privilege risk.

**Failure modes**:
* Key leak -> impersonation. Rotation strategy தேவை.
* Clock skew -> token expiry validate fail.
* Delegation chain too long -> trust dilution, verification cost.

## 6. Practical Example

Enterprise RAG agent system.

`User -> Gateway -> Router Agent -> Research Agent -> Database Agent`

User query: "Q3 revenue for customer X".

Gateway agent authenticate user, create `request_id` and `user_principal`.

Router Agent identity: `agent:router:prod`. அது Research Agent-க்கு delegate பண்ணும்போது delegation token கொடுக்கும்:

```
{
  "delegated_by": "agent:router:prod",
  "for": "user:acme-corp:u123",
  "scope": ["read:documents", "read:customer:X"],
  "expires": "now+5m"
}
```

Research Agent இந்த token-ஐ verify செய்து, தனது சொந்த signature சேர்த்து DB Agent-க்கு forward செய்யும்.

Final log:

`initiator=user:acme-corp:u123, chain=[router, research], executor=db-agent, action=read`

Billing, audit, revoke ஆகியவை இப்போது possible.

## 7. Reasoning Challenge

உங்களிடம் 3 agents உள்ளன: `Planner`, `Coder`, `Executor`. Planner user request-ஐ புரிந்து Coder-க்கு பணி கொடுக்கிறது. Coder code எழுதி Executor-க்கு கொடுக்கிறது. Executor production database-ஐ தொடுகிறது.

ஒரு bug-ல் Executor தவறான table-ஐ drop செய்துவிட்டது. Audit-ல் யார் approve செய்தது தெரிய வேண்டும்.

இங்கே agent identity எப்படி design செய்வீர்கள்? Delegation chain-ஐ எப்படி காப்பாற்றுவீர்கள்? Executor-க்கு எந்த scope கொடுக்க வேண்டும்?

## 8. Key Takeaways

* Agent identity என்பது ID + proof + scope + audit trail ஆகும், வெறும் name அல்ல.
* Multi-agent system-ல் trust அடிப்படையில் identity இருக்க வேண்டும், இல்லையெனில் impersonation மற்றும் audit failure நடக்கும்.
* Delegation chain-ஐ preserve செய்தால் accountability maintain ஆகும்.
* Strong identity cost கொடுக்கும் - latency, key management, operational complexity. அதை use case-க்கு ஏற்ப balance செய்யுங்கள்.
