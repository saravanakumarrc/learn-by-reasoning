# Identity layer

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.14 — Enterprise patterns

## 1. Problem

உங்களுக்கு ஒரு Enterprise AI Architecture இருக்கு. அதில் 10+ services இருக்கு: API gateway, user service, billing service, RAG service, agent orchestrator, vector database, LLM gateway.

ஒவ்வொரு service-ம் "யார் இந்த request-ஐ அனுப்பினான்?" என்று கேட்கணும்.

User login பண்ணார். அவருக்கு JWT token கொடுத்தோம். இப்போ அந்த token-ஐ எல்லா service-லயும் validate பண்ணனும். Token expired ஆனால்? Role மாறினால்? User disable ஆனால்? Revoke பண்ணணும்னா?

இதை ஒவ்வொரு service-லயும் தனியா implement பண்ணினால் என்ன ஆகும்?

> Code duplication, security bug, inconsistent policy, token validation latency, revocation impossible.

இதுதான் Identity layer தேவைப்படும் இடம்.

## 2. Mental Model

Identity layer என்பது **who you are, what you can do, and can you access this** என்பதை முடிவு செய்யும் ஒரு centralised boundary.

அது authentication + authorization + context propagation-ஐ handle பண்ணும்.

உங்கள் system-க்கு ஒரு security guard போல. அவர் ID card check பண்ணி, access list பார்த்து, அனுமதி கொடுப்பார். Service-கள் gate-க்கு அப்புறம் business logic மட்டும் பார்க்கும்.

## 3. How It Works

Typical flow:

1. **Authentication**: User login -> Identity Provider ல் verify -> short-lived access token + refresh token கொடுக்கப்படும். Standard: OAuth2 / OIDC.
2. **Token issuance**: Access token-ல் claims இருக்கும்: `sub`, `roles`, `tenant_id`, `permissions`. Token signature verified by public key.
3. **Introspection / Validation**: Service ஒவ்வொன்றும் token-ஐ validate பண்ணும். Public key cache பண்ணி, local validation செய்யலாம். அல்லது central introspection endpoint-க்கு call பண்ணலாம்.
4. **Authorization**: Token valid ஆனாலும், resource-level check தேவை. "இந்த user இந்த document-ஐ பார்க்கலாமா?" என்பது Policy Engine / PDP பார்க்கும்.
5. **Context propagation**: Service-to-service call-ல் token அல்லது `x-request-id`, `tenant_id` propagate ஆகும். mTLS + token.

Enterprise AI-ல் கூடுதல் layer: **Agent identity, tool identity**. ஒரு agent ஒரு user-க்கு behalf-ல் act பண்ணும்போது, அந்த delegation-ஐ track பண்ணணும்.

## 4. Architectural Reasoning

Identity layer தனியா வரும்போது எப்போ?

* Multiple services, multiple clients, mobile/web/api.
* Centralised audit, compliance, revocation தேவை.
* Role-based / attribute-based access control தேவை.
* Multi-tenant system.

Alternatives:

* **Local DB per service**: simple ஆனால் scale ஆகாது.
* **API Gateway only auth**: gateway-ல் மட்டும் check, downstream blind trust. Service mesh பயன்படுத்தினால் okay, ஆனால் fine-grained policy கடினம்.
* **Central Identity layer**: Auth service + Policy decision point.

Enterprise AI-ல் ஏன் முக்கியம்? RAG service-ல் user-க்கு என்ன data accessible என்பது முக்கியம். Agent tool call பண்ணும்போது, அது user permissions-ஐ respect பண்ணணும். LLM prompt-ல் PII leak ஆகாமல் guardrail வேணும்.

## 5. Trade-offs

**Centralization vs Latency**: Central validation ஒவ்வொரு request-க்கும் network call = latency. Local JWT validation fast ஆனால் revocation delay.

**Stateless token vs Revocation**: JWT stateless, scale easy. ஆனால் revoke பண்ண முடியாது. Solution: short TTL + refresh token rotation + revocation list cache.

**Coarse vs Fine-grained**: Role-based simple ஆனால் insufficient. Attribute-based / policy-based flexible ஆனால் complexity அதிகம். Policy evaluation latency வரும்.

**Security surface**: Identity layer single point of failure / attack. High availability, key rotation, secret management தேவை.

**Operational complexity**: Team-க்கு identity standards enforce பண்ண வேணும். Developer friction: "token இல்லைனா service வேலை செய்யாது".

## 6. Practical Example

Enterprise AI platform: 3 tenants, 5000 users.

Login via OIDC provider. Access token 5 min TTL. Refresh token 7 days, httpOnly cookie.

API Gateway token-ஐ validate பண்ணி, `tenant_id`, `user_id`, `roles` header-ல் downstream-க்கு propagate பண்ணும்.

RAG service-ல் user query வரும்போது, Policy Engine check: `user.tenant_id == document.tenant_id` and `role in [analyst, admin]`. Fail ஆனால் empty results.

Agent orchestrator ஒரு tool call பண்ணும்போது, tool identity-யும் check பண்ணும். User-ன் permission மீறி agent external API call பண்ணக்கூடாது.

Audit log centralised: யார் எந்த document access பண்ணார் என்பது immutable log-ல்.

## 7. Reasoning Challenge

உங்களிடம் internal AI agent service இருக்கு. Agents user behalf-ல் vector DB-ல் search பண்ணும். Users 10,000+. Token revocation immediate-ஆக வேணும். Service-to-service latency < 20ms வேணும்.

நீங்கள் JWT use பண்ணுவீர்களா? Introspection use பண்ணுவீர்களா? Revocation எப்படி handle பண்ணுவீர்கள்? Identity layer-ஐ எங்கே வைப்பீர்கள்? ஏன்?

## 8. Key Takeaways

* Identity layer என்பது authentication + authorization + audit-ஐ centralise பண்ணும் architectural boundary.
* JWT stateless scaling-க்கு நல்லது, ஆனால் revocation-க்கு short TTL + refresh + revocation cache தேவை.
* Enterprise AI-ல் identity என்பது user மட்டுமல்ல, agent, tool, tenant context-ம்.
* Every service should not do auth logic; trust but verify via propagated identity context.
* Identity decision = availability, security, compliance trade-off.
