# Semantic search

> **Learning Path:** RAG Architecture
> **Section:** 12.1.21 — Learn

## 1. Problem

உங்களிடம் ஒரு enterprise document system இருக்கு. 10,000+ support tickets, product manuals, policy docs. User கேட்கிறார்: "என்னோட refund எப்போ வரும்?"

Keyword search-ல் என்ன ஆகும்? User exact phrase "refund" தேடினால் match ஆகும். ஆனால் "money back", "return credit", "paisa wapas" என்று கேட்டால்? Zero results.

அடுத்து synonym, typo, paraphrase, different language mix எல்லாம் வரும். Boolean search-ல் போய் query-யை expand பண்ணினாலும், human intent-ஐ பிடிக்க முடியாது.

இதுதான் pain point. Engineer-க்கு தேவை: **meaning-ஐ பிடிக்கணும், word-ஐ இல்லை.**

## 2. Mental Model

Semantic search என்பது keyword matching அல்ல. Meaning matching.

ஒரு document-ஐயும் user query-யையும் ஒரு high-dimensional vector space-ல் போட்டு, அவைகள் எவ்வளவு close இருக்கின்றன என்று பார்க்கிறோம். Cosine similarity நெருக்கமாக இருந்தால், அது relevant.

Analogy: ஒரு library-ல் books-ஐ subject-ஆல் categorize பண்ணினால் போதாது. Books-ஐ ஒரு map-ல் point ஆக வைக்கிறோம். User கேட்கும் topic-க்கு நெருக்கமான point-களை திரும்ப கொடுக்கிறோம்.

## 3. How It Works

1. **Embedding**: Text-ஐ LLM / embedding model-ல் போட்டு vector-ஆக மாற்றுகிறோம். `refund process` மற்றும் `money back timeline` இரண்டும் similar vector-ல் வரும்.
2. **Index**: எல்லா documents-ன் vectors-ஐ vector database-ல் store செய்கிறோம். Pinecone, Weaviate, Qdrant, pgvector போன்றவை.
3. **Query**: User query-யையும் embed பண்ணி, nearest neighbors-ஐ தேடுகிறோம். Top-K results வரும்.
4. **RAG pipeline-ல்**: Retrieved chunks-ஐ LLM-க்கு context ஆக கொடுத்து answer generate செய்கிறோம்.

Keyword search-ல் inverted index. Semantic search-ல் vector index. அவ்வளவுதான்.

## 4. Architectural Reasoning

எப்போது semantic search தேவை?

* User intent vague / natural language.
* Synonyms, paraphrases, multilingual queries common.
* Large unstructured corpus.
* You need relevance, not exact match.

Alternatives:

* **Keyword search + BM25**: Exact match strong, deterministic, cheap. Legal clause retrieval போன்ற precise search-க்கு நல்லது.
* **Hybrid search**: Vector similarity + keyword score combine பண்ணுவது. இப்போது production default. Recall-ஐ improve பண்ணும்.

Architect decision: தூய semantic மட்டும் போதுமா? இல்லை. RAG system-ல் semantic retrieval base layer. Filtering, reranking அதற்கு மேல்.

Constraints consider பண்ணணும்:
* Latency: vector search 20-100ms
* Cost: embedding compute + vector DB
* Freshness: documents update ஆனால் re-embed வேண்டும்
* Multilingual: Tamil + English mix queries

## 5. Trade-offs

**Relevance vs Precision**
Semantic search recall நல்லது, ஆனால் sometimes irrelevant but conceptually close results வரும். Reranker மூலம் fix செய்யலாம்.

**Cost vs Quality**
Bigger embedding model = better meaning capture, ஆனால் latency & cost அதிகம். Small model + reranker என்பது common trade-off.

**Index size & update**
Document எண்ணிக்கை அதிகரிக்கும்போது vector DB sharding தேவை. Real-time ingestion-க்கு embedding pipeline lag வரும்.

**Failure mode**
Embedding drift: model version மாற்றினால் পুরানো vectors stale ஆகும். Re-embed pipeline தேவை. Also, semantic search meaning-ஐ பிடிக்கும், ஆனால் exact ID / number search-க்கு தோல்வி அடையும். Hybrid தேவை.

## 6. Practical Example

Banking RAG system. User கேட்கிறார்: "என்னோட credit card bill late ஆனா என்ன penalty?"

Keyword search-ல் "penalty" இருக்கும் docs மட்டுமே வரும். "late fee", "fine", "charge" என்று இருந்தால் miss.

Semantic pipeline:
1. Query embed → vector
2. Vector DB-ல் top 5 policy chunks retrieve
3. Hybrid boost: "credit card" keyword filter apply
4. Reranker cross-encoder use பண்ணி best 3 pick
5. LLM answer generate with citations

Result: user intent-ஐ catch பண்ணி relevant penalty clause கொண்டு வருகிறது.

## 7. Reasoning Challenge

உங்களிடம் 5M support tickets உள்ளன. Daily 10K new tickets வருகின்றன. Users Tamil, English, Hinglish-ல் கேட்கிறார்கள். Latency budget 300ms.

Pure semantic search, hybrid search, அல்லது keyword + semantic two-stage? எதை தேர்வு செய்வீர்கள்? Embedding model size எப்படி decide செய்வீர்கள்? Re-indexing frequency என்ன?

இதில் cost, latency, recall எப்படி trade-off ஆகும்?

## 8. Key Takeaways

* Semantic search = meaning matching, not keyword matching.
* Embed documents and queries into vector space, find nearest neighbors.
* Production-ல் hybrid search + reranking தான் practical default.
* Trade-off: relevance & recall vs latency, cost, operational complexity.
* Semantic search alone exact facts-க்கு போதாது, architecture-ல் filtering & reranking தேவை.

இது ஏன் தேவைன்னு புரிஞ்சுது. எப்போ use பண்ணணும்னு தெரியும்.
