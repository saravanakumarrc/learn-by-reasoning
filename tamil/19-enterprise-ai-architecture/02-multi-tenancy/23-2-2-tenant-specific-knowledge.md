# Tenant-specific knowledge

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.2.2 — Multi-tenancy

## 1. Problem

Enterprise AI system-ல ஒரு platform-ஐ 100+ customers use பண்ணுறாங்க. ஒவ்வொரு customer-க்கும் தனித்தனி internal docs, policies, product catalog இருக்கு.

ஒரே LLM, ஒரே vector database-ஐ எல்லாரும் share பண்ணினா என்ன ஆகும்?

Customer A கேட்ட கேள்விக்கு Customer B-ன் confidential pricing data வந்து விடும். அதாவது data leakage.

மாறாக ஒவ்வொரு tenant-க்கும் தனி model, தனி vector DB வைத்தால் cost எகிறும், operations nightmare ஆகும்.

இதுதான் multi-tenancy-ல tenant-specific knowledge பிரச்சனை. **Isolation vs sharing** balance பண்ண வேண்டும்.

## 2. Mental Model

Tenant-specific knowledge = ஒவ்வொரு tenant-க்கும் சொந்தமான knowledge graph, embeddings, retrieval context.

Think of it like bank locker room. Common hall, common staff, ஆனால் ஒவ்வொரு customer-க்கும் தனி locker. Locker-ன் key தவறாமல் வேறு யாருக்கும் தெரியக்கூடாது.

AI system-ல locker = tenant id + isolated retrieval namespace.

## 3. How It Works

RAG pipeline-ல tenant isolation 3 level-ல வரும்:

**a. Data ingestion level**
Document ingest பண்ணும் போதே tenant_id tag செய். 
`{ tenant_id: "acme_corp", doc_id: "...", embedding: [...] }`
Embedding generate பண்ணும் போது tenant context-ஐ preserve பண்ணு.

**b. Retrieval level**
User query வரும்போது:
1. Authenticate → tenant_id extract
2. Retrieval query-ஐ filter பண்ணு: `WHERE tenant_id = ?`
3. Only that tenant-ன் embeddings-ல search.

Vector database-ல இது row-level security / collection per tenant மூலம் implement ஆகும்.

**c. Generation level**
LLM prompt-ல system instruction + tenant-specific context inject பண்ணு. 
`You are assistant for Acme Corp. Use only Acme's approved docs.`

Tenant-specific knowledge base என்பது tenant_id scoped embeddings + metadata filters + access control policy combination.

## 4. Architectural Reasoning

இது எப்போது useful?

- SaaS AI platform, enterprise customers with confidential data
- Compliance தேவை: GDPR, HIPAA, data residency
- Customer A-ன் data Customer B-க்கு leak ஆகக்கூடாது

Options:

1. **Separate infrastructure per tenant** - Full isolation. Cost high, operational complexity high. Good for 5-10 big enterprise tenants.
2. **Shared infrastructure, logical isolation** - Single vector DB, tenant_id filter. Cost effective, scale easy. Good for 100s-1000s tenants.
3. **Hybrid** - Tier based. Free tier = shared, Enterprise tier = dedicated collection / DB.

Architect choose பண்ணுறது constraint-ஐ பார்த்து:
- Compliance requirement strong → Option 1 or 2 with strict filtering + audit
- Team size small → Option 2
- Query latency requirement low → collection per tenant may be faster than filter scan

## 5. Trade-offs

**Isolation vs Cost**
Separate DB per tenant = perfect isolation, but storage, compute cost multiply ஆகும். Shared DB = cost save, but filter bug = leak risk.

**Query performance vs Simplicity**
Tenant_id filter on shared index = query slow ஆகலாம். Per-tenant collection = fast, ஆனால் 10k collections manage பண்ணுவது painful.

**Operational complexity**
Tenant-specific knowledge update பண்ணும்போது stale embeddings, orphan docs வரும். Garbage collection, tenant offboarding process தேவை.

**Failure mode**
Filter miss ஆனால் data leak. So retrieval layer-ல tenant_id filter-ஐ hard code பண்ணி, DB level-ல row-level security enforce பண்ணு. Defense in depth.

## 6. Practical Example

Enterprise support chatbot.

3 tenants: BankA, BankB, InsureCo.

Common LLM: GPT-4. Shared vector DB: Pinecone.

Ingestion pipeline:
BankA-ன் internal policy PDFs → chunk → embed → upsert with metadata `tenant_id=banka, access_level=internal`
Same for others.

User query வரும்போது:
User JWT-ல tenant_id = banka extract.
Retrieval query: `vector search where tenant_id = banka AND access_level <= user_role`

Result only BankA docs return ஆகும். LLM answer BankA context-ல மட்டும் generate ஆகும்.

Offboarding: tenant delete ஆனால் `DELETE WHERE tenant_id = ?` + audit log.

## 7. Reasoning Challenge

உங்களிடம் 2000 SMB tenants இருக்கு, ஒவ்வொருவருக்கும் சராசரி 500 docs. 5 enterprise tenants இருக்கு, ஒவ்வொருவருக்கும் 2M docs.

ஒரே vector database use பண்ண வேண்டும். Retrieval latency < 200ms வேண்டும்.

எப்படி tenant-specific knowledge-ஐ organize செய்வீர்கள்? Shared index with filter போதுமா? Dedicated collections எப்போது create செய்வீர்கள்? ஏன்?

## 8. Key Takeaways

- Tenant-specific knowledge என்பது data isolation + retrieval isolation இரண்டும் சேர்ந்தது
- Tenant_id-ஐ ingestion, retrieval, generation முழுவதும் propagate பண்ணு
- Shared infra + logical isolation cost effective, ஆனால் filter correctness = security
- Multi-tenancy design decision எப்போதும் cost, compliance, ops complexity trade-off-ல வரும்
