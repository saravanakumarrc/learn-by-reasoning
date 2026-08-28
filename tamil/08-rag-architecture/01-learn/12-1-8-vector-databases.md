# Vector databases

> **Learning Path:** RAG Architecture
> **Section:** 12.1.8 — Learn

## 1. Problem

RAG system-ல LLM-க்கு relevant context கொடுக்கணும். 
User query: "எங்க company-ல return policy என்ன?" 

இதுக்கு நீங்க 10,000 support articles-ல இருந்து சரியான paragraph எடுக்கணும்.

பழைய வழி: keyword search - `LIKE '%return%'` அல்லது Elasticsearch. 
ஆனா problem என்ன? 
"return policy" என்பதை user "refund rules", "money back", "நான் பொருளை திருப்பி கொடுக்கணும்" என்று கேட்கலாம்.

Meaning மாறாமல் வார்த்தை மாறும். Keyword match fail ஆகும்.
அதனால் வேண்டியது: **semantic similarity**.

இங்கே தான் pain point வருகிறது. Millions of documents இருக்கும் போது, ஒரு query vector-க்கு ஒத்த documents-ஐ millisecond-ல கண்டுபிடிக்கணும்.

Database-ல full text search போதாது. Brute force cosine similarity பண்ணினால் 10M vectors-க்கு scan பண்ணி latency போகும்.

**What problem became painful?** Scale + semantic similarity + low latency.

## 2. Mental Model

Vector database = ஒரு smart index for meaning.

Document ஒன்றை embedding model வைத்து 1536-dimensional vector-ஆக மாற்றுகிறோம்.
Query-யும் vector-ஆக மாற்றுகிறோம்.

பிரச்சனை: "இதே மாதிரி meaning உள்ள vector எது?" என்று கண்டுபிடிப்பது.

Vector DB அதை approximate nearest neighbor search-ஆக செய்கிறது. 
Think of it as library-ல புத்தகங்களை subject-ஆல அடுக்கியது போல. நீங்கள் "machine learning in finance" என்று கேட்டால், அதே shelf-ல உள்ள books தான் வரும்.

## 3. How It Works

Basic flow RAG-ல:

1. **Ingestion:** Document -> chunk -> embedding -> store vector + metadata
2. **Query:** User query -> embedding -> ANN search -> top-K vectors -> fetch metadata -> LLM context

Key capabilities:

* **Vector index:** HNSW, IVF, PQ போன்ற structures பயன்படுத்தி scan-ஐ தவிர்க்கிறது.
* **Metadata filtering:** `where category = 'policy' and lang = 'ta'`. Similarity + filter.
* **Hybrid search:** Vector similarity + keyword BM25 combine பண்ணலாம்.

நீங்கள் தனியாக vector file வைத்து FAISS-ல search செய்யலாம். Production-ல வேண்டியது durability, replication, scaling, API.

## 4. Architectural Reasoning

Vector DB தேவைப்படும் போது:

* **Retrieval based on meaning, not exact match.** 
* **Large corpus, real-time query.**
* **Replay / incremental updates தேவை.**

Alternatives என்ன?

* **Brute force in memory:** சிறிய dataset-க்கு ஓகே. 100K வரை.
* **Elasticsearch with dense_vector:** Hybrid பண்ணலாம், ஆனால் scale மற்றும் recall குறையும்.
* **Managed Pinecone / Weaviate / Qdrant / pgvector:** Production ready.

Architect ஆக நீங்கள் கேட்க வேண்டியது:

Query QPS எவ்வளவு? Latency SLA என்ன? 
Vector size 768 vs 3072? 
Filtering கடுமையா? 
Consistency வேண்டுமா, eventual ஓகேவா?

Small team, low volume -> pgvector + Postgres போதும்.
High QPS, multi-tenant, strict latency -> dedicated vector DB.

## 5. Trade-offs

**Recall vs Latency vs Cost**
HNSW high recall, low latency ஆனால் memory அதிகம். IVF cheaper. 
Parameters tweak பண்ணி trade-off மாற்றலாம்.

**Index freshness vs write cost**
Real-time ingestion வேண்டுமென்றால் index rebuild cost வரும். 
Batch update பண்ணுவது cheaper.

**Exact vs Approximate**
ANN என்பது approximate. 100% exact வேண்டுமென்றால் brute force தான். Production-ல 95% recall போதும்.

**Operational complexity**
Vector DB ஒன்று சேர்க்கிறீர்கள் என்றால் new service, monitoring, backup, scaling. 
pgvector தேர்ந்தால் existing Postgres team-க்கு simple.

Failure mode: Bad embedding model -> vector DB perfect-ஆக இருந்தாலும் irrelevant results வரும். 
Retrieval quality = embedding quality + chunking strategy + filter logic.

## 6. Practical Example

E-commerce support RAG.

10 lakh support articles, Tamil + English.

Architecture:
`S3 -> Chunking pipeline -> Embedding API -> Vector DB` 
Metadata: `article_id, category, language, last_updated`.

User query "நான் order cancel பண்ணினால் refund எப்போ வரும்?"
Query embedding -> vector DB-ல top 5 hits with filter `language = 'ta' and category in ['refund','cancellation']` -> LLM-க்கு context.

Operational decision: 
Daily new articles வரும். Incremental upsert பண்ணி HNSW-ஐ update செய்ய வேண்டும். 
QPS 200. Latency < 150ms.

இங்கே Pinecone அல்லது Qdrant தேர்ந்தெடுக்கலாம். 
Cost மட்டும் குறைக்க வேண்டும் என்றால் self-hosted Qdrant + autoscaling.

## 7. Reasoning Challenge

உங்களிடம் 20M product descriptions உள்ளன. 
Users product search பண்ணும்போது visual similarity மற்றும் text similarity இரண்டும் வேண்டும். 
Query volume 5k QPS, p95 latency < 100ms வேண்டும். 
Daily 500k new products add ஆகும்.

இங்கே vector DB தேர்வு எப்படி இருக்கும்? 
Separate indexes for image vector and text vector வைப்பீர்களா? Hybrid search எப்படி செய்வீர்கள்? 
Write throughput vs read latency trade-off எப்படி handle பண்ணுவீர்கள்?

## 8. Key Takeaways

* Vector database-ன் core job semantic nearest neighbor search at scale, not storage.
* Retrieval quality depends on embedding model + chunking + metadata filtering, not just index.
* ANN என்பது trade-off: recall, latency, memory. Architect இதை tune பண்ண வேண்டும்.
* Small scale-க்கு pgvector/FAISS, production scale-க்கு managed vector DB. Choice வருகிறது constraints-ல இருந்து.
