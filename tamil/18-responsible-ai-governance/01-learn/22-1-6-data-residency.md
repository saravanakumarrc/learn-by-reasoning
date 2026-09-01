# Data residency

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.6 — Learn

## 1. Problem

உங்கள் company ஒரு global SaaS product பண்ணுது. ஒரு EU customer sign up பண்ணும்போது, அவரோட personal data, payment info, chat logs எல்லாம் எங்க store ஆகுது? 

அந்த data US data center-ல store ஆனா, GDPR சொல்றது: EU citizen-ன் personal data-வை EU-க்கு வெளியே process பண்ணக்கூடாது. அல்லது explicit legal mechanism இருக்கணும்.

இப்போ திடீரென்று auditor கேட்கிறார்: "Show me where customer data physically resides." நீங்கள் சொல்ல முடியலை. Compliance fine வரும், contract-ல penalty வரும், customer trust போகும்.

**What goes wrong if we don't have this?** Data location unknown = legal risk, data sovereignty violation, cross-border transfer ban.

Data residency என்பது legal + technical requirement, வெறும் storage preference அல்ல.

## 2. Mental Model

Data residency = **data-ன் physical/legal location-ன் guarantee**.

இது "data எங்கே process ஆகிறது, எங்கே persist ஆகிறது" என்பதை control செய்வது.

ஒரு country boundary ஒரு firewall போல. Data அந்த boundary தாண்டக்கூடாது என்று law சொல்லும்போது, நீங்கள் architecture-ஐ அதற்கு ஏற்ப design செய்ய வேண்டும்.

Key distinction:
* **Data residency**: Data physically stays in country/region.
* **Data sovereignty**: Who has legal control/jurisdiction over data.
* **Data localization**: Strict version, data must never leave.

அடிப்படையில், region pinning + data isolation.

## 3. How It Works

Architecturally, residency என்பது data placement policy ஆக implement ஆகிறது.

* **Region-aware routing**: User-ன் location / tenant-ன் residency requirement படி request-ஐ correct region-க்கு route பண்ண வேண்டும்.
* **Data partitioning by geography**: Database, object storage, backups எல்லாம் region-specific. EU tenant data = EU region bucket / EU DB.
* **Replication control**: Cross-region replication disable அல்லது allowlist செய்ய வேண்டும். EU data US-க்கு replicate ஆகக்கூடாது.
* **Metadata tagging**: Every record/tenant-க்கு residency tag இருக்கும். "residency=EU".
* **Network boundary**: Inter-region traffic block, egress control.

Example flow: API gateway reads `tenant_id` -> lookup residency config -> route to `eu-west-1` service. Write goes only to EU DB. Read replica also EU-ல மட்டும்.

## 4. Architectural Reasoning

**When does this become useful?**
* GDPR, India DPDP Act, China PIPL, Russia data law போன்ற regulations உள்ள markets-ல.
* Healthcare, finance, government customers.

**What constraint it addresses?** Legal compliance + customer trust.

**Alternatives:**
1. **Single global region + legal safeguards**: Standard contracts, SCCs. Cheaper but risky when laws change.
2. **Multi-region with residency pinning**: Data stays in region, higher cost.
3. **Customer-managed keys + region selection**: Customer chooses.

Architect ஏன் choose பண்ணுவார்? 
Business requires EU customers. Cost of non-compliance > cost of multi-region infra.

Data residency என்பது feature flag அல்ல. Architecture decision from day one. Later migrate பண்ணுவது painful.

## 5. Trade-offs

* **Cost vs Compliance**: Multi-region infra, duplicate services, data transfer cost அதிகம். Operational overhead double.
* **Latency vs Residency**: User-க்கு nearest region சிறந்தது. Residency requirement அந்த nearest region-ஐ restrict செய்யும். EU user Australia region-ல இருந்தாலும் EU DB-க்குதான் request போக வேண்டும்.
* **Consistency vs Isolation**: Global consistency கொடுக்க cross-region replication தேவை. Residency அதை தடுக்கிறது. Eventual consistency or regional isolation தேவைப்படும்.
* **Operability**: Backup, disaster recovery, monitoring எல்லாம் region scoped. Team needs region-aware runbooks.

Failure mode: Misrouted write. ஒரு EU user-ன் data accidentally US DB-ல write ஆனால், அது compliance breach. அதனால் residency enforcement code path-ல bug ஆனால் impact huge.

## 6. Practical Example

Enterprise RAG system with Responsible AI.

You build an AI assistant for banks. Customer documents, chat history, embeddings store ஆகின்றன.

Requirement: German bank data must stay in Germany.

Architecture:
* Tenant onboarding-ல `residency=de` tag.
* API gateway -> routing layer checks tag -> route to `eu-central-1` cluster.
* Vector database, object storage, PostgreSQL எல்லாம் Germany region-ல மட்டும் deploy.
* Cross-region replication off. Backup also Germany region.
* LLM inference? If using external LLM provider, data leaves your infra. அதனால் either on-prem LLM in Germany அல்லது DPA signed provider with residency guarantee.

If new customer from India joins, new region `ap-south-1` infra spin up, same code base but isolated data plane.

## 7. Reasoning Challenge

உங்களிடம் multi-tenant SaaS app உள்ளது. 90% users US-ல. 10% users Germany-ல. Germany users require strict data residency.

Options:
A. All data in US, rely on SCCs.
B. Germany users-க்கு separate region, separate DB, same app code.
C. Global DB with residency tag, but allow cross-region reads for performance.

எந்த option தேர்வு செய்வீர்கள்? Cost, compliance, complexity எப்படி balance பண்ணுவீர்கள்? Replication and DR எப்படி handle பண்ணுவீர்கள்?

## 8. Key Takeaways

* Data residency என்பது legal requirement-ல இருந்து வரும் architectural constraint, விருப்பம் அல்ல.
* Data placement, routing, replication control என்பது core design decisions.
* Residency-க்கு trade-off: cost, latency, complexity அதிகரிக்கும்.
* Early decision தேவை; retrofitting கடினம்.
* Auditability முக்கியம்: எந்த data எங்கே உள்ளது என்பதை prove செய்ய முடிய வேண்டும்.
