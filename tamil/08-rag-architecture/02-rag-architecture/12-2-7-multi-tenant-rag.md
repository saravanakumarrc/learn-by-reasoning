# Multi-tenant RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.2.7 — RAG architecture

## 1. Problem

ஒரு RAG system build பண்ணியாச்சு. உங்கள் product-ல இப்போ 1 tenant. அதன் documents, embeddings, vector database எல்லாம் ஒரே pool-ல.

இப்போ business சொல்லுது: "We need to onboard 10 customers, then 100."

What goes wrong?

* Customer A-ன் confidential data Customer B-க்கு leak ஆகக்கூடாது.
* Tenant A-க்கு 1M documents, Tenant B-க்கு 10k documents. Same vector DB-ல இருந்தா query performance, cost எல்லாம் எப்படி manage பண்ணுவீங்க?
* One tenant ஒரு bad query-ல் அனைவருக்கும் latency spike கொடுக்குது.
* Compliance: EU tenant data EU-ல மட்டும் இருக்கணும், US tenant data US-ல.
* Billing, quotas, feature flags tenant-wise வேணும்.

Single-tenant RAG-ல இந்த constraints எல்லாம் painful ஆகுது. அதனால் Multi-tenant RAG தேவைப்படுது.

## 2. Mental Model

Multi-tenant RAG என்பது **same RAG infrastructure-ஐ பல customers share பண்ணுவது, ஆனால் data, access, behavior தனித்தனியாக isolate செய்வது**.

Core mental model: **Isolation vs Sharing**.

* Share பண்ணுவது: vector DB cluster, embedding model, LLM, orchestration code, infra cost.
* Isolate பண்ணுவது: data, index, access control, tenant config, usage limits.

இதை நீங்கள் எப்படி isolate பண்றீங்க என்பதுதான் architecture decision.

## 3. How It Works

Query வரும்போது flow இது:

User query → API Gateway → Tenant identification → Tenant routing → Retrieval with tenant filter → LLM generation with tenant context → Response

Key components:

* **Tenant ID**: API key, subdomain, JWT claim மூலம் extract பண்ணுவீங்க.
* **Retrieval isolation**: Vector DB-ல ஒவ்வொரு vector-க்கும் `tenant_id` field இருக்கும். Query-ல எப்போதும் `WHERE tenant_id = X` filter.
* **Embedding + Storage**: Same embedding model பயன்படுத்தலாம், ஆனால் index தனி அல்லது shared.
* **Prompt isolation**: System prompt-ல tenant-specific instructions, brand voice, allowed tools inject பண்ணுவீங்க.
* **Access control**: Document level permissions, user roles tenant context-ல enforce.

## 4. Architectural Reasoning

Multi-tenancy-ல மூன்று main strategies உண்டு:

### A. Shared Database, Shared Schema + Tenant ID filter
ஒரே vector DB, ஒரே collection/table. ஒவ்வொரு row-க்கும் tenant_id.

* When useful: Small to medium scale, cost save வேணும், operational simplicity வேணும்.
* Constraint address: Fast to build, low infra cost.
* Trade: Noisy neighbor problem, one tenant-ன் huge data எல்லாரையும் slow பண்ணும். Security risk அதிகம் if filter miss ஆகும்.

### B. Shared Database, Separate Schema / Collection per Tenant
ஒவ்வொரு tenant-க்கும் தனி collection / index. Same DB cluster.

* When useful: Strong logical isolation வேணும், per-tenant performance control வேணும்.
* Trade: Metadata management சிக்கல், 1000 tenants = 1000 collections. DB limits வரும்.

### C. Separate Database / Cluster per Tenant
ஒவ்வொரு tenant-க்கும் dedicated vector DB, even separate region.

* When useful: Enterprise customers, compliance, strict isolation, custom models.
* Trade: Cost அதிகம், operational complexity அதிகம்.

Architect ஆக நீங்கள் choose பண்ணும்போது பார்க்க வேண்டியது:

* Data isolation requirement - GDPR, HIPAA?
* Scale per tenant - data size, QPS வேறுபடுமா?
* Team size & operability - நீங்கள் எத்தனை clusters manage பண்ண முடியும்?
* Cost model - per-tenant pricing சாத்தியமா?

## 5. Trade-offs

**Isolation vs Cost**
Strong isolation = higher cost, more infra. Shared = cheaper but risk.

**Performance vs Simplicity**
Per-tenant index = predictable latency. Shared index = noisy neighbor, need query routing & rate limiting.

**Security vs Developer velocity**
Filter-based isolation fast to build. But one bug in filter = data leak. Defense in depth தேவை: DB filter + application level check + audit logs.

**Flexibility vs Standardization**
Some tenants want custom embedding model, custom retriever, custom LLM. Multi-tenant platform-ல அதை எப்படி allow பண்ணுவது? If you allow too much customization, you lose sharing benefits.

Failure modes கவனிக்க வேண்டியது:

* Missing tenant filter in retrieval → cross-tenant data leak. This is catastrophic.
* Embedding model drift across tenants if you update model without re-embedding.
* Cold start: new tenant-க்கு index build time.

## 6. Practical Example

Enterprise knowledge base product.

Tenant A = Bank, 5M documents, needs EU region, PII filtering, dedicated LLM fine-tune.
Tenant B = Startup, 50k documents, US region, standard model.

Architecture decision:

* Shared API gateway + auth service.
* Routing layer tenant config-ல இருந்து reads.
* Tenant A: Separate vector DB cluster in EU, dedicated collection, separate embedding pipeline.
* Tenant B: Shared vector DB cluster in US, shared collection with tenant_id filter, shared embedding pipeline.
* Retrieval service always injects tenant_id filter + row-level security policy.
* LLM call-ல tenant-specific system prompt + guardrails.

Result: Cost optimized for small tenants, isolation guaranteed for enterprise tenant, compliance satisfied.

## 7. Reasoning Challenge

உங்களிடம் 200 tenants இருக்கு. 180 tenants சிறியவை, 20 tenants பெரியவை. எல்லாரும் same embedding model use பண்ணுறாங்க. ஒரு tenant திடீரென 10x traffic spike பண்ணும்போது மற்ற tenants-க்கு latency increase ஆகுது.

Shared collection with tenant_id filter vs per-tenant collection என்றால் எதை தேர்வு செய்வீர்கள்? அல்லது hybrid approach? எந்த failure mode-ஐ நீங்கள் முதலில் mitigate பண்ணுவீர்கள்?

## 8. Key Takeaways

* Multi-tenant RAG-ன் core problem isolation + cost sharing balance.
* Tenant ID filter எப்போதும் mandatory, ஆனால் filter மட்டும் போதாது, defense in depth வேணும்.
* Architecture choice depends on tenant size, compliance, and operational capacity, not just technology.
* Every isolation decision creates cost and complexity trade-off.
