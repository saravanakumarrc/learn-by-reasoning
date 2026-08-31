# Stale data

> **Learning Path:** RAG Architecture
> **Section:** 12.3.6 — RAG failure modes

### 12.3.6 — RAG failure modes: Stale data

## 1. Problem

உங்க RAG system-ல ஒரு user கேட்கிறார்: "நம்ம ப்ராடக்ட் X-ன் latest price என்ன?"

RAG retriever உங்க vector database-ல இருந்து ஒரு chunk எடுத்து LLM-க்கு கொடுக்கிறது. LLM நம்பிக்கையோடு பதில் சொல்கிறது.

ஆனால் அந்த chunk 3 வாரங்களுக்கு முன்பு எழுதப்பட்டது. Price மாறியிருக்கு. Promotion முடிந்திருக்கு.

User-க்கு தப்பான பதில் போயிருக்கு. Support ticket வந்திருக்கு. Trust போயிருக்கு.

**What goes wrong if we don't have this?** 
Source data மாறியும், vector index மாறாமல் இருக்கும். RAG hallucinate பண்ணவில்லை, அது உண்மையாக நம்பும் stale information-ஐ repeat பண்ணும்.

இது RAG-ன் classic failure mode: **stale data**.

## 2. Mental Model

RAG என்பது 3 moving parts-ன் composition:
`Source of truth → Indexing pipeline → Vector DB + LLM`

Stale data என்பது source மாறியது, ஆனால் index மாறவில்லை என்பதால் வரும் lag.

ஒரு distributed system-ல eventual consistency போல. நீங்கள் write பண்ணினீர்கள், ஆனால் read path still old version-ஐ பார்க்கிறது.

ஆனால் இங்கே cost அதிகம்: Business decision, pricing, compliance, medical info போன்றவற்றில் stale answer = wrong decision.

## 3. How It Works

Stale data எப்படி உருவாகிறது?

1. **Source changes.** DB row update ஆகிறது, webpage மாறுகிறது, product catalog refresh ஆகிறது.
2. **Change detection miss.** Crawler / CDC / webhook இல்லை. அல்லது poll interval மிகப்பெரியது.
3. **Indexing lag.** Chunking, embedding, upsert queue-ல தேங்கி நிற்கிறது.
4. **Serving reads old vectors.** LLM இன்னும் பழைய embedding-ஐ retrieve பண்ணுகிறது.

Result: Freshness gap = `t_source_update → t_index_visible`

இந்த gap நிமிடங்கள் முதல் வாரங்கள் வரை இருக்கலாம்.

## 4. Architectural Reasoning

Stale data எப்போது painful ஆகிறது?

* Low latency requirement உள்ள domains: pricing, inventory, flight status, stock quotes
* Compliance / legal: policy documents மாறும்
* High churn knowledge base: news, product specs

எப்போது குறைவாக painful?
Static knowledge, historical documents, rarely changing internal wiki.

Options architects weigh:

* **Batch re-indexing:** Nightly / weekly full crawl. Simple, cheap. Freshness மோசம்.
* **Incremental / CDC-based indexing:** Source DB change events → immediate re-embed. Freshness நல்லது, complexity அதிகம்.
* **TTL + freshness metadata:** Every chunk-க்கு `last_updated` timestamp. Retrieval-ல filter பண்ணு. Old docs-ஐ downgrade பண்ணு.
* **Hybrid retrieval:** Vector + live lookup. Retrieval செய்த பிறகு, source system-ல real-time fetch செய்து verify / override.
* **Read-time re-ranking by freshness:** Score = similarity * freshness_decay.

Decision depends on constraints: freshness SLA, cost, source accessibility, team ops capacity.

## 5. Trade-offs

**Freshness vs Cost.** Real-time CDC + immediate upsert கட்டமைப்பு விலை உயர்ந்தது. Embedding API calls, queue infra, vector DB write load. Batch cheap ஆனால் stale.

**Freshness vs Recall.** Freshness filter கடுமையாக வைத்தால், பழைய ஆனால் relevant context தவறிவிடும். நீங்கள் relevance-ஐ தியாகம் செய்கிறீர்கள்.

**Consistency vs Availability.** Strong freshness க்கு index update-ஐ synchronous ஆக்க வேண்டும். அது pipeline failure-ல் retrieval-ஐ block பண்ணும். Most teams eventual consistency-ஐ தேர்ந்தெடுக்கிறார்கள்.

**Failure modes:**
* Silent staleness: User-க்கு தெரியாது. Trust degrade slowly.
* Partial update: Document-ன் பாதி மட்டும் re-index ஆகி, chunk inconsistency உருவாகிறது.
* Version skew: Multiple sources-ன் freshness வெவ்வேறு, LLM confused context-ஐ mix பண்ணுகிறது.

## 6. Practical Example

Enterprise support RAG. Knowledge base = Confluence + Zendesk articles.

Product team price change பண்ணினார்கள். Confluence page update ஆனது.

நீங்கள் nightly batch crawler வைத்திருக்கிறீர்கள். User next morning query பண்ணினால், பழைய price-ஐ காட்டுகிறது.

Architectural fix:
* Confluence webhook → Event bus → Ingestion worker → Chunk, embed, upsert to vector DB with `updated_at`.
* Retrieval query-ல `updated_at > now - 7 days` போன்ற filter, அல்லது re-rank.
* Critical fields price/inventory-க்கு hybrid path: Vector retrieve செய்த பிறகு, product catalog API-ல live fetch செய்து LLM prompt-ல inject செய்யவும். Source citation-ல "as of timestamp" காட்டவும்.

Now freshness SLA ~ 2 minutes. Cost அதிகரித்தது, ஆனால் support tickets குறைந்தன.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG agent உள்ளது. இது financial reports-ல இருந்து answer கொடுக்கிறது. Reports quarterly மாறுகின்றன, ஆனால் அதற்கிடையில் analyst notes தினமும் update ஆகின்றன.

நீங்கள் ஒரே indexing pipeline-ஐ பயன்படுத்தினால், என்ன trade-off வரும்? Reports-க்கும் notes-க்கும் வெவ்வேறு freshness strategy வேண்டுமா? எப்படி design பண்ணுவீர்கள்?

## 8. Key Takeaways

* Stale data என்பது RAG-ல silent failure. LLM சரியாகவே பதில் சொல்லும், ஆனால் அது outdated.
* Freshness = source change detection + indexing latency + serving visibility. மூன்றும் பார்க்க வேண்டும்.
* One size fits all indexing இல்லை. Data class-ன் churn rate-க்கு ஏற்ப freshness strategy மாறும்.
* Critical facts-க்கு vector மட்டும் போதாது. Hybrid retrieval with live lookup + freshness metadata தேவை.

நீங்கள் இப்போது ஏன் stale data வருகிறது என்பதை reason பண்ண முடியும், எப்போது tolerate பண்ணலாம், எப்போது real-time update தேவை என்பதை decide பண்ண முடியும்.
