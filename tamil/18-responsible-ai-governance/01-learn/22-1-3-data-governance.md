# Data governance

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.3 — Learn

## 1. Problem

உங்க company-ல 200+ tables இருக்கு, 15 teams data-வை produce பண்ணுது, 40 teams consume பண்ணுது. 

ஒரு data scientist churn prediction model-க்கு `customer_age` column use பண்ணார். மாதம் ஒரு team அதே column-ஐ வேறு definition-ல calculate பண்ணி இருக்காங்க. மாடல் production-ல போன பிறகு bias வந்து தெரியுது.

ஒரு compliance audit வந்துது. "இந்த PII data எங்க இருக்கு? யார் access பண்ணாங்க? retention policy என்ன?" என்று கேட்டாங்க. யாருக்கும் சரியாக தெரியல. 

Data governance இல்லாமல் என்ன ஆகும்? 
Inconsistency, duplication, compliance risk, trust loss, rework. 

Problem painful ஆகும்போது தான் governance வரும்.

## 2. Mental Model

Data governance என்பது **data-விற்கான operating model** . 

அது technology அல்ல, அது rules + roles + processes + tooling.

Simple analogy: ஒரு library. Books இருக்கு. யார் எந்த book-ஐ எழுதலாம், எப்படி catalog பண்ணணும், யார் borrow பண்ணலாம், எப்போ remove பண்ணணும் என்பதற்கு policy இருக்கு. Librarian, catalog system, fines இருக்கு.

Data governance = data-விற்கான librarian system.

## 3. How It Works

Core pillars 4 இருக்கு:

**1. Metadata & Catalog**
Data என்ன, எங்க இருக்கு, யார் owner, definition என்ன, lineage என்ன. 
Data catalog + business glossary இங்கே வரும்.

**2. Policies & Standards**
Naming convention, PII classification, retention, quality thresholds, access control. 
Policy as code ஆக இருக்கலாம்.

**3. Roles**
Data Owner - business meaning own பண்ணுவார்.
Data Steward - day-to-day quality, policy enforce பண்ணுவார்.
Data Consumer - use பண்ணுவார்.

**4. Enforcement**
Automated checks in pipeline, access review, data quality monitoring, audit logs.

Governance work flow: Discover → Classify → Define → Monitor → Audit.

## 4. Architectural Reasoning

எப்போது தேவை?

* Multiple teams same data-வை use பண்ணும்போது
* Regulated data இருக்கும்போது - PII, PHI, financial
* AI/ML systems data lineage தேவைப்படும்போது
* Data product scale ஆகும்போது

Alternatives?

**Centralized governance**: One central team controls everything. Strong consistency, slow, bottleneck.

**Federated governance**: Domain teams own their data, central provides standards. Scalable, but consistency குறையலாம்.

Architect choice: Start federated with strong central policy framework. 
Domain Data Owner-ஐ empower பண்ணு, central stewardship provide tooling.

Data governance AI system-ல எப்படி relevant? 
RAG / LLM agent-க்கு training data, retrieval data source-க்கு provenance தெரியணும். Hallucination risk, bias risk, compliance risk எல்லாம் data governance-ல இருந்து தான் வரும்.

## 5. Trade-offs

**Control vs Speed**: Strict approval slow down development. Too loose → chaos.

**Centralization vs Autonomy**: Central control consistency கொடுக்கும், but teams frustrated. Federated fast, but standards drift ஆகும்.

**Automation vs Manual**: Automated policy enforcement costly to build, but manual reviews don't scale.

**Completeness vs Pragmatism**: Perfect metadata impossible. 80% coverage with good ownership beats 100% theoretical catalog.

Failure modes:
* Governance as checkbox: policy document எழுதி வைத்து, enforce பண்ணாமல் இருப்பது.
* Tool-first: catalog tool வாங்கி, ownership இல்லாமல் data quality drop ஆகும்.
* Shadow data: teams governance-ஐ bypass பண்ணி own lake பண்ணுவார்கள்.

## 6. Practical Example

Enterprise bank-ல loan approval model இருக்கு.

Problem: `income` field 3 sources-ல வருது: core banking, CRM, external bureau. Definition வேறுபடுது.

Governance design:
* Business glossary-ல `income` = net monthly income after tax, source of truth = core banking.
* Data Owner = Risk domain head.
* Data Steward = data engineer + risk analyst.
* Data catalog-ல lineage track: core banking → ingestion → feature store → model.
* PII classification tag, access policy: only models with audit log.
* Data quality check: null rate < 0.1%, freshness < 24h.
* Retention policy: raw PII 7 years, then mask.

Result: Audit-க்கு lineage prove பண்ண முடியும். Model drift வந்தால் source change தெரியும்.

## 7. Reasoning Challenge

உங்களிடம் Responsible AI & Governance path-ல RAG system இருக்கு. 
Internal docs, customer support tickets, public web data எல்லாம் knowledge base-ல mix ஆகி இருக்கு. 
Compliance team கேட்கிறார்: "PII எங்க இருக்கு? Model training data-ல bias உள்ளதா? Source-ஐ trace பண்ண முடியுமா?"

இந்த scenario-ல data governance-ல முதல் 3 steps என்ன வைப்பீர்கள்? 
Classification, ownership, lineage இதில் எது priority? ஏன்?

## 8. Key Takeaways

* Data governance = trust, risk, quality க்கான operating model. Tool அல்ல.
* Ownership clear இல்லாமல் governance fail ஆகும்.
* Federated model + central standards real world-ல scale ஆகும்.
* AI systems-க்கு governance இல்லாமல் compliance, bias, hallucination risk hidden ஆக இருக்கும்.
