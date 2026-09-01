# Tenant-specific memory

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.2.3 — Multi-tenancy

## 1. Problem

Enterprise AI system-ல ஒரு LLM agent அல்லது RAG pipeline பல customers-க்கு பகிர்ந்து பயன்படுத்தப்படும்போது என்ன நடக்கும்?

Customer A-க்கான conversation history, preferences, past decisions, domain data Customer B-க்கு தெரியக்கூடாது. ஒரே model, ஒரே vector database, ஒரே memory store என்றால் leakage ஆகும்.

மறுபுறம், ஒவ்வொரு tenant-க்கும் தனித்தனி infrastructure போடுவது cost-லும் ops complexity-லும் பெரிய பிரச்சனை.

பிரச்சனை clear: **shared compute, isolated memory.**

What goes wrong if we don't have tenant-specific memory?
- Data leakage between tenants
- Personalization இல்லாமல் போகும்
- Compliance violation, GDPR / HIPAA breach
- One tenant-ன் noisy data மற்ற tenant-ன் retrieval quality-ஐ கெடுக்கும்

## 2. Mental Model

Tenant-specific memory என்பது **identity + context boundary**.

ஒரு request வரும்போது, அது எந்த tenant-க்கு சொந்தம் என்பதை அடையாளம் கண்டு, அந்த tenant-க்கு மட்டும் relevant memory, embeddings, conversation history, tools access என்பதை திறக்க வேண்டும்.

Shared brain, but separate notebooks.

Mental model: `request → tenant_id → isolated memory slice → retrieve → generate → store back to same slice`.

## 3. How It Works

Practically மூன்று layers-ல் இது implement ஆகும்.

**1. Routing Layer**
API gateway அல்லது auth service tenant_id-ஐ extract பண்ணும். Header, JWT claim, subdomain மூலம். இது ஒவ்வொரு request-க்கும் first gate.

**2. Storage Isolation**
Options:
* **Physical isolation:** ஒவ்வொரு tenant-க்கும் தனி vector database, தனி Postgres schema. Strong isolation, high cost.
* **Logical isolation:** ஒரே vector DB-ல் ஒவ்வொரு vector-ம் `tenant_id` column உடன் store. Query time-ல் `WHERE tenant_id = X` filter.
* **Hybrid:** Hot tenants-க்கு physical, மற்றவற்றுக்கு logical.

**3. Memory lifecycle**
Short-term session memory: Redis per tenant, TTL உடன்.
Long-term memory: tenant-scoped vector DB + relational store.
Retrieval: query + tenant filter → rerank → context window-க்கு pass.

Access control: tenant இன் users, roles, data classification-ஐ மதித்து memory read/write permission check.

## 4. Architectural Reasoning

எப்போது தேவை?

Multi-tenant SaaS AI platform இருக்கும்போது, ஒவ்வொரு enterprise customer-க்கும் தனித்தனி knowledge base, branding, conversation tone, compliance boundary வேண்டும்.

Constraint என்ன?
* **Security & Compliance:** Tenant data mix ஆகக்கூடாது.
* **Personalization:** Tenant context-ஐ remember பண்ணி quality improve ஆக வேண்டும்.
* **Cost & Operability:** Thousands of tenants-க்கு thousands of DBs manage பண்ண முடியாது.

Options:
* Shared DB + tenant_id filter
* Schema per tenant
* Database per tenant

Architect choose பண்ணும்போது trade-off பார்க்க வேண்டும்: isolation strength vs operational cost.

## 5. Trade-offs

**Isolation vs Cost**
Physical isolation gives strongest guarantee, but storage, backup, scaling cost அதிகம். Logical isolation cheap but filter miss ஆனால் leakage risk.

**Query performance**
`tenant_id` filter எல்லா query-லும் வரும். Vector DB-ல் tenant படி partition செய்யாவிட்டால் large tenant data சிறிய tenant query-ஐ slow ஆக்கும்.

**Memory freshness & retention**
Tenant A wants 2 year retention, Tenant B wants 30 days. Unified retention policy கடினம். Per-tenant policy தேவை.

**Failure modes**
Tenant_id extraction fail ஆனால் request default tenant-க்கு போகும். அது silent data leak.
Also, embedding model upgrade பண்ணும்போது ஒரு tenant-ன் embeddings மட்டும் rebuild பண்ண வேண்டுமா? Versioning தேவை.

**Operability**
Backups, restore, migration ஒரு tenant-க்கு மட்டும் செய்ய முடியுமா? Logical isolation-ல் கடினம்.

## 6. Practical Example

Enterprise support AI.

Acme Bank, RetailCo ரெண்டும் ஒரே platform-ல் உள்ளன.

Flow:
1. User logs in → JWT-ல் `tenant_id: acme_bank` வரும்.
2. Gateway request-ஐ route பண்ணி, tenant context set பண்ணும்.
3. Agent ஒரு question கேட்கும்போது:
   - Retrieval: `vector_db.search(query, tenant_id='acme_bank', top_k=5)`
   - Conversation history: `redis.get(session:{tenant_id}:{user_id})`
   - Tools: Acme-க்கு மட்டும் allowed tools list
4. Answer generate ஆகி, அதே tenant-ன் memory-க்கு store ஆகும்.

RetailCo-ன் pricing data Acme-க்கு retrieve ஆகாது.

Cost குறைக்க, ஒரே managed vector DB, ஆனால் collection-ல் tenant_id metadata mandatory, index filter enable செய்யப்பட்டது.

## 7. Reasoning Challenge

உங்களிடம் 10,000 tenants இருக்கு. 95% small, 5% large enterprise.

Large enterprises GDPR-க்கு physical isolation கேட்கிறார்கள். Small tenants-க்கு cost அதிகமாகக்கூடாது.

நீங்கள் எப்படி architecture design பண்ணுவீர்கள்? Isolation எங்கே physical, எங்கே logical என்பதை எப்படி decide பண்ணுவீர்கள்? Migration path என்ன?

## 8. Key Takeaways

* Tenant-specific memory என்பது data isolation + personalization boundary.
* `tenant_id` என்பது ஒவ்வொரு memory read/write operation-ன் முதல் filter.
* Physical isolation = strong security, high cost. Logical isolation = cost efficient, filter discipline தேவை.
* Memory design-ல் compliance, performance, operability மூன்றும் சமமாக முக்கியம்.
* Architecture decision-ல் tenant size, regulatory need, team ops capacity-ஐ balance பண்ணுவது முக்கியம்.
