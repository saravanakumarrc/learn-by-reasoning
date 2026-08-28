# Filtering

> **Learning Path:** RAG Architecture
> **Section:** 12.1.20 — Learn

## 1. Problem

நீங்க ஒரு RAG system build பண்ணியிருக்கீங்க. LLM-க்கு relevant context கொடுக்கணும். Vector database-ல 10M chunks இருக்கு. User query வந்ததும் `similarity search` பண்ணி top-k chunks எடுக்கிறீங்க.

ஆனா பெரும்பாலும் அந்த top-k results-ல பாதி use-less ஆ இருக்கு. Example: user "Q4 2025 revenue for Chennai branch" என்று கேட்டாலும், vector search உங்களுக்கு தருவது:

* Q4 2024 revenue
* Bangalore branch
* Revenue policy doc
* Generic finance FAQ

ஏன்? Because semantic similarity மட்டும் போதாது. It matches meaning, but not constraints.

இது உங்களுக்கு என்ன problem கொடுக்கும்?
* LLM hallucinate பண்ணும் அல்லது wrong answer தரும்
* Context window waste ஆகும், cost அதிகம்
* Relevance குறையும், user trust குறையும்

அப்போ question: similarity score மட்டும் போதாமல், ஏன் extra filter வேண்டும்?

## 2. Mental Model

Filtering என்பது retrieval-க்கு முன் அல்லது பின் வைக்கும் **guard rails**.

Vector search = "என்ன பற்றி பேசுகிறது" என்பதை கண்டுபிடிக்கும்.
Filter = "எந்த constraints-க்குள் இருக்க வேண்டும்" என்பதை enforce செய்யும்.

ஒரு analogy: Library-ல search பண்ணும்போது topic-க்கு match ஆகும் books எடுக்கிறீங்க. ஆனா நீங்க language = Tamil, publication year > 2020, author verified மட்டும் வேண்டும் என்று சொன்னால், அது filter.

RAG-ல filtering என்பது metadata மூலம் தேவையில்லாததை முன்னதாகவே கழிப்பது.

## 3. How It Works

இரண்டு முக்கிய வகை:

**1. Pre-filtering - Retrieval முன்**
Vector DB query-வுடன் metadata filter கொடுத்து தேடுவது.
Example: `WHERE branch = 'Chennai' AND quarter = 'Q4-2025' AND doc_type = 'report'`
இது search space-ஐ குறைக்கும். Faster, cheaper. ஆனா over-filter பண்ணினால் relevant result-ஐயும் விட்டுவிடலாம்.

**2. Post-filtering - Retrieval பின்**
முதலில் broad similarity search பண்ணி top-N எடுக்கவும். பின் metadata / rules மூலம் prune பண்ணவும்.
Example: similarity top-100 எடுத்து, பின் freshness > 90 days, access_level <= user_role என filter பண்ணி top-10 கொடுக்கவும்.
Flexible ஆனா expensive.

மற்ற filters:
* **Metadata filter**: source, date, author, department, region, sensitivity, language
* **Content filter**: PII, profanity, policy violation - retrieval பின் reject
* **Hybrid filter**: reranker score + metadata score combine பண்ணி re-rank

## 4. Architectural Reasoning

Filtering எப்போது critical?

* Multi-tenant system: Tenant A data Tenant B-க்கு leak ஆகக்கூடாது. `tenant_id` filter mandatory.
* Time-sensitive data: News, prices, medical. Old doc-ஐ கொடுத்தால் wrong. `created_at` filter.
* Access control: Confidential HR data, internal only docs. `access_level` filter.
* Domain constraints: User Chennai branch-க்கு மட்டும் கேட்கிறார். Location filter.

Alternative என்ன?
* Prompt-level filtering: "Only use Chennai data" என்று LLM-க்கு சொல்வது. இது unreliable, LLM still sees all context.
* Reranker only: Relevance improve ஆகும் ஆனா constraints enforce ஆகாது.
* No filter: Simple ஆனா production-ல fail ஆகும்.

Architect decision: **Constraints-ஐ enforce செய்ய வேண்டுமா?** If yes, filter must be outside LLM trust boundary.

## 5. Trade-offs

**Relevance vs Recall**
Strict filter போட்டால் precision அதிகம், ஆனா recall குறையும். Too loose filter போட்டால் noise அதிகம்.

**Latency vs Cost**
Pre-filtering = faster, less vectors scan. Post-filtering = more candidates scan, then filter. Latency vs safety trade-off.

**Freshness vs Completeness**
Date filter போட்டால் recent data மட்டும் வரும். ஆனா long-form knowledge தேவைப்படும் query-க்கு பிரச்சனை.

**Operational complexity**
Filters எல்லாம் metadata quality-ஐ depend பண்ணும். Metadata missing / wrong ஆனால் filter fail ஆகும். So ingestion pipeline-ல metadata extraction reliable ஆக இருக்கணும்.

Failure mode: Filter bug = data leakage. Example tenant_id filter missing ஆனால் cross-tenant data expose ஆகும். அதனால் filter logic-க்கு tests, audit logs முக்கியம்.

## 6. Practical Example

Enterprise RAG for internal knowledge base.

User query: "Show me Q4 2025 hiring plan for engineering, Chennai."

Architecture:
1. Query parsing: extract intent + entities - department=engineering, location=Chennai, quarter=Q4-2025
2. Vector search with pre-filter:
   `metadata: {doc_type: 'hiring_plan', department: 'engineering', location: 'Chennai', quarter: 'Q4-2025', sensitivity <= user_clearance}`
3. Retrieve top 20 chunks
4. Post-filter: Remove chunks where `created_at < 2025-01-01` OR `source = 'draft'`
5. Rerank remaining with cross-encoder
6. Pass top 5 to LLM

Result: Only relevant, authorized, fresh docs reach LLM. Cost குறையும், hallucination குறையும்.

## 7. Reasoning Challenge

உங்களிடம் customer support RAG system இருக்கு. 3 tiers உள்ளன: Free, Pro, Enterprise.

User Pro tier-ல இருக்கார். Query: "Refund policy for annual plan".

Vector search top-10 results-ல Free plan policy, Pro plan policy, Enterprise policy எல்லாம் வருகிறது. Metadata-ல tier tag இருக்கு.

நீங்கள் என்ன செய்வீர்கள்? Pre-filter பண்ணுவீர்களா? Post-filter பண்ணுவீர்களா? ஏன்? User Pro tier-க்கு மட்டும் தான் policy காட்ட வேண்டும், ஆனா general refund principles உள்ள docs Free tier-ல இருந்தாலும் useful ஆக இருக்கலாம்.

நீங்கள் எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* Vector similarity = what about, Filter = under what constraints. இரண்டும் தேவை.
* Pre-filter for hard constraints like tenant, access, location. Post-filter for soft constraints like freshness, quality.
* Filter quality depends on metadata quality at ingestion time.
* Every filter is a trade-off between precision and recall. Architect should decide which failure is more expensive.
