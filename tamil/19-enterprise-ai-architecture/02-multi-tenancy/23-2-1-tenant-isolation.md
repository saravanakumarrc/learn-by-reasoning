# Tenant isolation

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.2.1 — Multi-tenancy

## 1. Problem

ஒரு Enterprise AI platform-ல 50 customers இருக்காங்க. எல்லாரும் ஒரே SaaS system-ஐ use பண்ணுறாங்க. 

Customer A-ன் data, Customer B பார்க்கக்கூடாது. Customer A-ன் prompt, embeddings, RAG knowledge base, logs எல்லாம் A-க்கு மட்டும். ஆனால் infrastructure ஒன்னு தான்.

இதை செய்யாம விட்டால் என்ன ஆகும்?

* ஒரு tenant-ன் traffic spike மற்ற tenant-ன் latency-ஐ உயர்த்தும்.
* ஒரு tenant-ன் bad data மற்றவர்களை பாதிக்கும்.
* Compliance audit-ல fail ஆகும். GDPR, SOC2-ல data leakage.
* ஒரு tenant-க்கு custom model, custom retention வேண்டும் என்றால் கையாள முடியாது.

இதுதான் tenant isolation-ன் root problem. **Shared system, separate concerns.**

## 2. Mental Model

Tenant isolation என்பது ஒரு building-ல apartments மாதிரி.

அனைவருக்கும் ஒரே building, ஒரே lift, ஒரே power supply. ஆனால் ஒவ்வொரு flat-க்கும் தனி lock, தனி key, தனி bill.

Architecture-ல அதுதான் isolation: logical separation with shared infrastructure, physical separation when needed.

## 3. How It Works

Isolation-ஐ மூன்று layers-ல பார்க்கலாம்:

**Identity & Routing:** Request வரும்போது tenant ID எப்படி கண்டுபிடிக்கிறோம்? API key, JWT claim `tenant_id`, subdomain `acme.app.com`.

**Data isolation:** ஒரே database-ல இருந்தாலும் `tenant_id` column-ஆல் filter செய்யணும். அல்லது ஒவ்வொரு tenant-க்கும் தனி schema / database.

**Compute & Resource isolation:** ஒரு tenant-ன் LLM inference, vector search, background jobs மற்றவரை affect பண்ணக்கூடாது. Rate limit, queue per tenant, resource quotas.

Isolation என்பது all-or-nothing அல்ல. **Levels இருக்கு.**

## 4. Architectural Reasoning

**When isolation becomes painful:**

* Multi-tenant SaaS with sensitive data
* Enterprise AI where each customer wants private RAG index
* Compliance requirement: data residency

**Options:**

* **Shared database, shared schema + tenant_id column:** Cheapest. Horizontal scale easy. One query, one index. ஆனால் tenant_id filter மறக்கும் bug = data leak. Noisy neighbor problem.
* **Shared database, separate schema per tenant:** Better isolation. Schema migration complex. Postgres-ல 1000 schemas manage பண்ண முடியும்.
* **Separate database per tenant:** Strongest isolation, backup/restore independent, per-tenant performance. Cost high, operational overhead high. 1000 tenants = 1000 DBs.
* **Physical isolation:** Separate Kubernetes namespace / cluster per tenant. Extreme isolation, expensive.

**Decision driver:** Data sensitivity > cost > operational complexity.

AI systems-ல RAG க்கு இது critical. Customer A-ன் documents-ன் embeddings Customer B-ன் query-ல தோன்றக்கூடாது. அதனால் vector database-ல isolation மிக முக்கியம்.

## 5. Trade-offs

* **Cost vs Isolation:** Separate DB = safe, expensive. Shared DB = cheap, risk.
* **Operational complexity vs Safety:** More isolation = more DBs to backup, monitor, upgrade.
* **Performance vs Fairness:** Shared compute = noisy neighbor. One tenant burst -> everyone slow. Per-tenant rate limit + priority queue தேவை.
* **Developer velocity vs Correctness:** tenant_id-ஐ எல்லா query-லும் add செய்வது மறந்துவிடும். Row Level Security, middleware enforcement போன்ற guardrails வேண்டும்.

Failure modes:

* Missing tenant filter in one repository method -> cross-tenant leak.
* Cache key without tenant prefix -> A-ன் result B-க்கு போகும்.
* Logs aggregate ஆகி PII leak.

## 6. Practical Example

Enterprise AI assistant platform.

Architecture:
`API Gateway -> Auth service -> Tenant resolver -> Service layer -> Postgres + Qdrant`

* Auth service JWT-ல `tenant_id` set செய்கிறது.
* Middleware request context-ல tenant_id inject செய்கிறது.
* Postgres-ல Row Level Security policy: `USING tenant_id = current_setting('app.tenant_id')::uuid`
* Qdrant-ல collection naming: `tenant_{id}_docs`. அல்லது shared collection + payload filter `tenant_id`.
* Redis cache key: `tenant:{id}:user:{uid}:search:{hash}`
* Rate limiter: token bucket per tenant in Redis.

இதனால் one tenant-ன் 10k documents index ஆனாலும் மற்ற tenant-ன் search latency மாறாது.

## 7. Reasoning Challenge

உங்களிடம் SaaS AI platform இருக்கு. 200 small tenants + 5 large enterprise tenants.

Small tenants: shared infra ok.
Enterprise tenants: demand data residency in EU, dedicated model fine-tuning data, SLA 99.95%.

நீங்கள் isolation-ஐ எப்படி design செய்வீர்கள்? எந்த tenants-க்கு எந்த isolation level? Database, vector store, compute எப்படி separate செய்வீர்கள்? Cost-ஐ எப்படி justify செய்வீர்கள்?

## 8. Key Takeaways

* Tenant isolation என்பது security + performance + compliance-ன் கலவை.
* Isolation level-ஐ tenant tier, data sensitivity, compliance-ஆல் தேர்ந்தெடு.
* Shared schema easy ஆனால் bug-prone. Separate DB safe ஆனால் costly.
* Isolation-ஐ enforce செய்ய middleware, RLS, cache key design, tenant-aware routing மூலம் செய்ய வேண்டும்.
* Every isolation decision creates operational overhead. Choose deliberately.
