# Vector databases

> **Learning Path:** Data Architecture
> **Section:** 4.3.2 — AI-specific data

## 1. Problem

உங்கிட்ட ஒரு LLM இருக்கு. RAG பண்ணணும். User கேள்வி கேட்டதும், அவன் company-க்கு உள்ள கோடிக்கணக்கான documents, tickets, product specs-ல இருந்து பொருத்தமான context-ஐ கொண்டு வந்து answer generate பண்ணணும்.

என்ன painful? 

Traditional database-ல `WHERE title LIKE '%...%'` போட்டு text match பண்ணலாம். ஆனா semantic similarity வேண்டும். "refund policy for premium user" என்று கேட்டால், "premium customer return rules" என்ற document-ம் relevant ஆக வேண்டும்.

Embedding model வச்சு query-ஐ vector-ஆ மாற்றி, collection-ல உள்ள மில்லியன் vectors-ல மிக்க similar ஆனவற்றை கண்டுபிடிக்கணும். Brute force cosine similarity பண்ணினால் 10M vectors x 1536 dims = every query-க்கு ஒரு full scan. Latency seconds ஆகும், cost பெருகும்.

இங்கே வரும் பிரச்சனை: **scale-ல similarity search வேகமாகவும் சரியாகவும் வேண்டும்.**

## 2. Mental Model

Vector database என்பது relational database இல்லை. இது **Approximate Nearest Neighbor index** க்கான storage + query engine.

நினைத்துக்கொள்ள: ஒரு library-ல புத்தகங்கள் topic-ன் படி shelf-ல அடுக்கப்பட்டிருக்கின்றன. நீ ஒரு topic-ஐ கொடுத்தால், அதுக்கு அருகில் உள்ள shelf-களை மட்டும் பார்த்து relevant புத்தகத்தை எடுக்கிறாய். முழு library-யும் தேடுவதில்லை.

அதே போல vector database, embedding space-ல உள்ள vectors-ஐ graph அல்லது partitioned index-ல வைத்து, query vector-க்கு நெருக்கமானவற்றை fast-ஆ கண்டுபிடிக்கிறது.

Exact match இல்லை, **nearest neighbors** தான்.

## 3. How It Works

Core flow:

1. Document / image / audio → embedding model → 768/1536 dim vector
2. Vector + metadata → vector database-க்கு ingest
3. Query time → query-ஐ embed பண்ணு → ANN index-ல search
4. Top-K results + metadata திரும்ப வரும் → LLM-க்கு context-ஆக போகும்

Index types பொதுவாக:
* **HNSW** - graph based, low latency, high recall. Memory heavy.
* **IVF + PQ** - inverted file + product quantization, disk friendly, good for large scale.

முக்கிய metric-கள்: **recall@K**, **latency p95**, **QPS**. Exact nearest neighbor தேவையில்லை. RAG-க்கு top 10-ல 7-8 சரியாக இருந்தால் போதும்.

## 4. Architectural Reasoning

Vector database useful ஆகும் போது:

* Similarity search தேவை: semantic search, recommendation, duplicate detection, image search
* Data volume large: lakhs to crores vectors
* Latency SLA < 100-200ms
* Replay / incremental updates தேவை

Alternatives:

* **Postgres + pgvector**: small scale, < few million vectors, metadata filtering வேண்டும், team already Postgres-ல இருக்கிறது. Simplicity > scale.
* **In-memory FAISS / ScaNN**: training / batch inference-க்கு நல்லது. Production serving, persistence, replication இல்லை.
* **Dedicated vector DB**: Pinecone, Weaviate, Qdrant, Milvus, Chroma. Managed ANN, scaling, hybrid search.

Architect எப்போது தேர்வு செய்கிறான்? Team-க்கு operational complexity கையாள தெரியும், traffic high, recall tuning தேவை என்றால் dedicated. Prototype, internal tool என்றால் Postgres போதும்.

## 5. Trade-offs

* **Recall vs Latency vs Cost**: HNSW-ல recall அதிகம் ஆனால் memory + compute அதிகம். ANN என்பதால் exact இல்லை. `ef_search` அதிகப்படுத்தினால் recall ஏறும், latency ஏறும்.
* **Filtering + Vector**: metadata filter போட்டு தேடுவது மெதுவாகும். Pre-filter vs post-filter trade-off. Hybrid search-க்கு vector DB + relational
