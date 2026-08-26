# Authorization

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.11 — 2. API engineering

### 1. Problem

Authentication முடிஞ்சிடுச்சு. User யாருன்னு தெரியும். JWT இருக்கு, session இருக்கு.

இப்போ பிரச்சனை வேற.

ஒரு API-ல `POST /orders`, `DELETE /users/{id}`, `GET /reports/finance` எல்லாம் இருக்கு. ஒரு normal customer-க்கு order create பண்ண அனுமதி இருக்கு, ஆனா user delete பண்ண அனுமதி இல்ல. Support agent-க்கு தன்னோட assigned customers-ன் order மட்டும் பார்க்க அனுமதி. Finance team-க்கு மட்டும் report access.

Authentication இல்லாமல் எல்லாம் பிரச்சனை. Authentication இருந்தும் எல்லாம் பிரச்சனை.

> "Who are you?" சரியா கேட்டோம். "What are you allowed to do here?" கேட்கல.

இதுதான் Authorization-ன் வலி.

### 2. Mental Model

Authentication = identity prove பண்ணுறது.
Authorization = **principal-க்கு ஒரு resource-ல ஒரு action-ஐ செய்ய அனுமதி இருக்கா?** என்பதை decide பண்ணுறது.

Mental model simple:
`Decision = f(principal, action, resource, context)`

principal = user, service account, API key
action = read, write, delete, approve
resource = `/orders/123`, `tenant A`, `document type invoice`
context = time, IP, location, device

இந்த decision-ஐ எல்லா request-க்கும் consistent-ஆ apply பண்ணணும்.

### 3. How It Works

Practice-ல இது பெரும்பாலும் policy enforcement-ஆக வரும்.

Request வரும் -> API gateway / service mesh layer-ல authentication ஆகும் -> token-ல இருந்து claims / scopes எடுக்கப்படும் -> authorization check ஓடும்.

மூன்று common models:

* **RBAC - Role Based Access Control**: user-க்கு role கொடு. Role-க்கு permission set. `admin`, `support`, `customer`. Simple, ஆனா fine-grained கஷ்டம்.
* **ABAC - Attribute Based Access Control**: policy rule base. `user.department == resource.ownerDepartment AND action == read`. Flexible, ஆனா complex.
* **Scope / Permission based**: OAuth2-ல போல `orders:read`, `orders:write`. API level-ல clean.

Policy எங்க இருக்கும்?

Central policy engine இருந்து decision எடுத்து, services-க்கு propagate பண்ணலாம். அல்லது each service தன்னோட own check வச்சுக்கலாம்.

Typical flow:

```mermaid
graph LR
Client -->|JWT| API Gateway
API Gateway --> AuthN
API Gateway --> AuthZ Engine
AuthZ Engine -->|allow/deny + reason| API Gateway
API Gateway --> Resource Service
```

### 4. Architectural Reasoning

Authorization தேவைப்படும் constraints:

* Multi-tenant system. Tenant A data Tenant B பார்க்கக்கூடாது.
* Service-to-service call. Internal service-க்கு மட்டும் access.
* Regulatory / audit. Who did what, prove பண்ணணும்.

Architect எப்போ choose பண்ணுவார்?

* **Centralize** பண்ணும்போது: API gateway-ல single policy decision point. Consistency easy, latency ஒரே இடத்தில் கட்டுப்படுத்தலாம். ஆனா gateway single point of failure / bottleneck ஆகும்.
* **Distribute** பண்ணும்போது: Each service தன்னோட authorization logic வைத்துக்கொள்ளும். Local enforcement fast, service autonomous. ஆனா policy drift வரும், duplicate code, audit கஷ்டம்.

OAuth2 / OIDC போன்ற standards பயன்படுத்துவது என்பது identity provider-ஐ trust பண்ணி, service-கள் token-ல இருக்கும் claims-ஐ base-ஆக்கி decide பண்ணுவது. But token-ல எல்லா permission வைக்க முடியாது. Token பெரியதாகும், revoke கஷ்டம். அதனால் short-lived token + introspection / policy lookup.

### 5. Trade-offs

* **Performance vs Freshness**: Authorization check DB / policy store-க்கு call பண்ணினால் accurate ஆனா latency அதிகம். Cache பண்ணினால் fast ஆனா stale permission risk.
* **Coarse vs Fine-grained**: Role coarse, easy to operate. ABAC fine-grained, powerful ஆனா policy testing, debugging கடினம்.
* **Central vs Distributed**: Central easy audit, single source of truth. Distributed resilient, team autonomy. Hybrid பொதுவானது: central policy definition, distributed enforcement with local cache.
* **Fail-open vs Fail-closed**: AuthZ service down ஆனால் request-ஐ allow பண்ணலாமா deny பண்ணலாமா? Architecturally fail-closed தான் safe, ஆனா availability impact இருக்கும்.

Failure mode: Permission மாறினாலும் token-ல old scopes இருக்கும். Revocation window இருக்கும். அதனால token lifetime குறைவாக வைத்து refresh flow பயன்படுத்துவது common.

### 6. Practical Example

Enterprise SaaS billing API.

`GET /tenants/{tenantId}/invoices`

Customer user -> தன்னோட tenant invoices மட்டும் பார்க்கலாம்.
Support agent -> assigned tenants மட்டும் பார்க்கலாம்.
Finance admin -> எல்லா tenants.

Design:
API Gateway authentication செய்து JWT கொடுக்கும். JWT-ல `sub`, `roles`, `tenant_id` இருக்க
