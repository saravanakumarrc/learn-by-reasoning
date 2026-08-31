# Multi-tenant RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.2.7 — RAG architecture

## 1. Problem

ஒரு SaaS product-ல் 100+ customers இருக்காங்க. ஒவ்வொருத்தருக்கும் தனித்தனி documents, knowledge base, chat history இருக்கு.

Single-tenant RAG பண்ணினா? ஒவ்வொரு customer-க்கும் தனி vector database, தனி index, தனி pipeline வச்சா cost, ops complexity எகிறும்.

ஒரே RAG system-ல் எல்லாரையும் வச்சா என்ன ஆகும்?

Customer A-ன் data Customer B-க்கு leak ஆகும். Prompt injection-ல ஒருத்தர் இன்னொருத்தர் document-ஐ பார்க்க முடியும். Billing, rate limiting, retention policy எல்லாம் customer-specific ஆக இருக்கணும்.

Multi-tenant RAG-ன் problem இதுதான்: **Same infrastructure, isolated data, isolated behavior, per-tenant control**.

## 2. Mental Model

Multi-tenant RAG = One shared retrieval + generation pipeline, but tenant boundary எப்போதும் enforce ஆகணும்.

நினைச்சுக்கோ: ஒரு apartment building. Common elevator, plumbing இருக்கு. ஆனா ஒவ்வொரு flat-க்கும் தனி lock, தனி meter.

அதே மாதிரி RAG-ல் embedding model, LLM, API gateway common. Data access, index, policies tenant-specific.

## 3. How It Works

Core flow மாறாது: Query → Tenant Resolve → Filtered Retrieval → Generation → Response.

வித்தியாசம் tenant context எங்கே inject ஆகிறது.

**Tenant Resolution:** API key, JWT claim, subdomain இல்லை header-ல tenant_id வரும். Auth layer-ல இதை extract பண்ணி request context-ல் வை.

**Isolated Retrieval:** Vector DB query-ல tenant_id filter எப்போதும் add ஆகணும்.

```
vector_search(query_embedding, where: tenant_id = 't_123')
```

Index-level isolation வேண்டாம் என்றாலும் logical isolation must.

**Per-tenant config:** Embedding model, chunk size, top-k, reranker, prompt template, guardrails ஒவ்வொரு tenant-க்கும் வேறு வேறு இருக்கலாம்.

**Metadata enrichment:** Chunk-ஐ ingest பண்ணும்போது tenant_id, document_id, permissions, retention_date என metadata-வுடன் store பண்ணு.

## 4. Architectural Reasoning

எப்போது multi-tenant வேண்டும்?

* SaaS RAG product, multiple customers share same service.
* Cost efficiency முக்கியம். Separate infra per tenant cost அதிகம்.
* Operational overhead குறைக்கணும்.

Alternatives:

* **Single-tenant:** ஒவ்வொரு customer-க்கும் dedicated vector DB + LLM. Strong isolation, high cost, ops nightmare.
* **Shared DB + No tenant filter:** Cheapest, but data leak guarantee.
* **Multi-tenant with physical isolation:** Tenant per database / collection. Middle ground.

Decision point: Compliance requirement.

GDPR, HIPAA போன்ற strict isolation வேண்டும் என்றால் physical isolation or at least collection-per-tenant வேண்டும். Startups-க்கு logical isolation + strict filtering போதும், scale-க்கு மேலே physical isolation-க்கு migrate.

## 5. Trade-offs

**Isolation vs Cost**
Logical isolation cheap. Physical isolation safe. Trade-off is ops complexity and storage.

**Performance vs Correctness**
Tenant filter every query add latency. Cache per tenant வேண்டும். Cross-tenant cache hit கூடாது.

**Query complexity**
Where filter-ல் tenant_id always mandatory. Developer mistake ஆனால் data leak. Defense in depth வேண்டும்: DB level Row Level Security, application level filter, audit logs.

**Embedding drift**
ஒரு tenant தனியாக embedding model upgrade செய்ய விரும்பலாம். Shared model-ல் versioning தேவை. அல்லது tenant-specific embedding store.

Failure modes: Tenant ID missing → query fail closed, never return data. Tenant ID spoof → strict auth + validation. Index rebuild-ல் tenant metadata drop ஆனால் data leak.

## 6. Practical Example

Enterprise support assistant.

Tenant A = Bank. Tenant B = E-commerce.

Both use same RAG API: `POST /rag/chat`

Request header: `X-Tenant-ID: bank_01` + JWT.

Ingestion pipeline: Documents upload ஆகும்போது tenant_id tag ஆகி chunks create ஆகும். Vector DB-ல Pinecone / Weaviate-ல collection shared, metadata-ல tenant_id இருக்கு.

Retrieval: Query embedding → `where tenant_id = 'bank_01' AND permissions IN ('public','agent')` → top-k 5 → rerank → LLM context.

Prompt template tenant-specific: Bank-க்கு tone formal, PII redaction strict. E-commerce-க்கு casual, product catalog bias.

Billing: Token usage, retrieval count per tenant track பண்ணி meter.

Ops: One Kubernetes deployment, horizontal scale. Vector DB shared but tenant filtered.

## 7. Reasoning Challenge

உங்களுக்கு 200 tenants இருக்கு. 10 tenants மட்டும் enterprise, அவங்களுக்கு 99.99% SLA, data residency EU. மீதி 190 tenants standard, global.

Shared vector DB, single LLM endpoint use பண்ணுறீங்க.

**Question:** Enterprise tenants-க்கு isolation எப்படி ensure பண்ணுவீங்க? Physical collection per tenant வேண்டுமா? Logical filter போதுமா? Cost, latency, ops என்ன trade-off வரும்? Decision எப்படி justify பண்ணுவீங்க?

## 8. Key Takeaways

* Multi-tenant RAG-ன் core problem data isolation, not retrieval accuracy.
* Tenant ID must be part of every retrieval path, never optional.
* Logical isolation cost-effective to start, physical isolation for compliance heavy tenants.
* Per-tenant config for prompt, top-k, guardrails முக்கியம், one size fits all work ஆகாது.
* Every architectural choice creates new ops burden; design for fail-closed, audit everything.
