# Tenant isolation

> **Learning Path:** Security Architecture
> **Section:** 6.3.13 — AI security

### 1. Problem

நீங்கள் ஒரு multi-tenant AI SaaS பண்ணுகிறீர்கள். 50+ enterprise customers ஒரே platform-ல இருந்து chatbot, RAG, agent services-ஐ use பண்ணுகிறார்கள்.

ஒரு customer-ன் private documents, conversation history, fine-tuned model weights, API usage — எல்லாம் மற்ற customer-க்கு தெரியக்கூடாது.

இல்லைன்னா என்ன ஆகும்?
* Tenant A-ன் confidential contract PDF, Tenant B-ன் query-க்கு RAG retrieval-ல வந்துடும்.
* Shared prompt context-ல cross-tenant data leak ஆகும்.
* Logs, monitoring, embeddings எல்லாம் mix ஆகி compliance breach ஆகும்.
* ஒரு tenant-ன் runaway usage மற்ற tenant-ன் latency-ஐ உயர்த்தும்.

AI security-ல tenant isolation என்பது **data, compute, control plane** மூன்றையும் தனிமைப்படுத்துவது தான்.

### 2. Mental Model

Tenant isolation = **ஒவ்வொரு tenant-க்கும் தனி boundary**.

அது physical boundary இருக்கலாம், logical boundary இருக்கலாம்.

முக்கியமான கேள்வி: *ஒரு tenant fail ஆனாலோ compromise ஆனாலோ, மற்ற tenant-க்கு impact வருமா?*

இல்லை என்றால் isolation உண்டு.

### 3. How It Works

Isolation-க்கு 3 layer-கள் பார்க்க வேண்டும்.

**Data isolation**
* RAG-க்கு: ஒவ்வொரு tenant-க்கும் தனி vector collection / namespace / database schema. `tenant_id` எல்லா query-லும் filter.
* LLM context: System prompt-ல tenant-specific guardrails, knowledge base reference.
* Embeddings: Shared embedding model okay, ஆனால் vector store isolation must.

**Compute isolation**
* Shared LLM inference pool okay for cost, ஆனால் request-ல tenant_id tag பண்ணி rate limit, quota enforce பண்ணணும்.
* Fine-tuned models / LoRA adapters-ஐ tenant level-ல separate பண்ணலாம்.

**Control & Observability isolation**
* API keys, roles, audit logs எல்லாம் tenant scoped.
* Logs-ல PII mask பண்ணும்போது tenant boundary cross ஆகாம பார்க்கணும்.

Implementation pattern:
Request -> Auth -> Tenant Resolution -> Router -> Isolated Data Access -> Inference -> Audit

```mermaid
graph LR
  Client --> API Gateway
  API Gateway --> Auth Service
  Auth Service --> Tenant Context
  Tenant Context --> Router
  Router -->|tenant_id filter| Vector DB
  Router -->|tenant_id tag| LLM Service
  Router -->|tenant_id| Audit Log
```

### 4. Architectural Reasoning

**When to choose what level?**

* **Physical isolation**: ஒவ்வொரு tenant-க்கும் தனி DB, தனி vector DB, தனி inference cluster. Max security, worst cost and ops.
* **Logical isolation**: Shared infrastructure, tenant_id based row-level security + namespace. பெரும்பாலான SaaS-க்கு இது sweet spot.
* **Hybrid**: Sensitive tenants-க்கு dedicated, மற்றவர்களுக்கு shared pool.

AI-க்கு தனி சிக்கல்: LLM-ன் context window shared ஆகும். Prompt injection மூலம் Tenant A ஒரு prompt-ல Tenant B-ன் data-ஐ கேட்க முயற்சிக்கலாம். அதனால் retrieval layer-ல strict tenant filter + output filtering must.

Decision driver: compliance requirement, data sensitivity, team size, cost.

### 5. Trade-offs

* **Security vs Cost**: Physical isolation safe ஆனால் idle resources waste. Logical isolation cheap ஆனால் misconfiguration-ல leak risk.
* **Performance vs Isolation**: Separate vector collections = faster filtering, ஆனால் cross-tenant search இல்லை. Shared collection + filter = cheaper ஆனால் query latency அதிகம்.
* **Operational complexity**: ஒவ்வொரு tenant-க்கும் backup, migration, scaling தனியாக handle பண்ணணும்.
* **Failure blast radius**: Shared LLM service crash ஆனால் எல்லா tenant-மும் பாதிக்கும். Circuit breaker + tenant-level rate limiting-ஆல் damage limit பண்ணலாம்.

முக்கிய failure mode: *tenant_id missing filter*. ஒரு developer query-ல tenant_id-ஐ மறந்தால், எல்லா tenant data-யும் leak ஆகும். அதனால் policy enforcement database level-லயே இருக்கணும், app level மட்டும் இல்லை.

### 6. Practical Example

Enterprise RAG platform.

Tenant A = Bank, Tenant B = Hospital.

இருவரும் ஒரே embedding model, ஒரே vector DB cluster use பண்ணுகிறார்கள்.

Design:
* Vector DB-ல collection name = `rag_<tenant_id>`.
* API Gateway request வரும்போது JWT-ல இருந்து tenant_id extract பண்ணி context-ல set.
* Retrieval service எப்போதும் `WHERE tenant_id = ?` enforce பண்ணும். DB role-க்கு row-level security enable.
* LLM call-ல system prompt: "You are assistant for Tenant A. Use only their knowledge base."
* Audit log-ல tenant_id immutable tag.

Result: Bank query hospital documents-ஐ retrieve பண்ண முடியாது. Cost share ஆகும், isolation உண்டு.

### 7. Reasoning Challenge

உங்களிடம் 200 tenants உள்ளனர். 10 tenants HIPAA compliant ஆக வேண்டும், மற்றவை normal SaaS.

ஒரே vector database use பண்ணுகிறீர்கள். Shared embedding model, shared LLM inference.

நீங்கள் என்ன isolation strategy தேர்வு செய்வீர்கள்? Data layer, compute layer, network layer-ல என்ன வித்தியாசம் வைப்பீர்கள்? ஏன்?

### 8. Key Takeaways
