# Semantic search

> **Learning Path:** Data Architecture
> **Section:** 4.3.7 — AI-specific data

## 1. Problem

உங்கள் company-ல் ஒரு knowledge base இருக்கு. 10,000 support articles, FAQs, internal docs.

User தேடுகிறார்: *"my order is stuck, where is my delivery"*.

Keyword search-ல் "order stuck" என்ற exact phrase இருக்கும் article மட்டும் வரும். 
*"delivery delayed"*, *"shipment not moving"*, *"tracking shows no update"* போன்ற அதே meaning உள்ள article வராது.

இன்னொரு case: *"cheap flights to chennai"* vs *"low cost tickets to maamallapuram"*.

Keyword matching-க்கு synonym, paraphrase, context எல்லாம் தெரியாது. Engineer-க்கு painful ஆகும் போது:
- Users relevant result கிடைக்காமல் churn ஆகிறார்கள்
- Support team same question-ஐ திரும்ப திரும்ப பதில் சொல்கிறது
- Keyword list-ஐ கைமுறையாக expand செய்வது scale ஆகாது

இந்த pain தான் semantic search-ஐ உருவாக்கியது.

## 2. Mental Model

Keyword search = exact match.

Semantic search = meaning match.

Idea simple: text-ஐ ஒரு vector-ஆக மாற்று. அதே meaning உள்ள text-கள் vector space-ல் பக்கத்தில் இருக்கும்.

Query-ஐ embed செய், documents-ஐ embed செய்து வைத்துக்கொள். Similarity எது அதிகம் என்று பார்த்து Top-K எடு.

அதாவது: *எழுத்துக்களை பொருத்து பார்க்காமல், அர்த்தத்தை பொருத்து பார்க்கிறோம்.*

## 3. How It Works

1. **Embed**: ஒரு embedding model உதாரணமாக `text-embedding-3-small` ஒரு paragraph-ஐ 1536 dimension vector-ஆக மாற்றும்.
2. **Store**: இந்த vectors-ஐ vector database-ல் index செய்து வைக்கிறோம். `pgvector`, `Milvus`, `Weaviate`, `Qdrant`, `Pinecone` போன்றவை.
3. **Query**: User query வந்ததும் அதையும் embed செய்து, vector DB-ல் cosine similarity / dot product search பண்ணி மிக நெருக்கமான vectors-ஐ திருப்பி தருகிறோம்.
4. **Rerank**: Optional. Top-K vectors-ஐ LLM அல்லது cross-encoder model-ல் rerank செய்து quality உயர்த்தலாம்.

```
User Query -> Embedding -> Vector DB ANN Search -> Top-K Docs -> Rerank -> LLM / UI
```

Implementation-ல் கவனிக்க வேண்டியது: embeddings ஒரு முறை உருவாக்கி store செய்தால் போதும். Query time-ல் ஒரு embed மட்டும் போதும்.

## 4. Architectural Reasoning

Semantic search useful ஆகும் போது:
- Text corpus பெரியது, user language மாறுபடும்
- Synonym, paraphrase, intent matching தேவை
- RAG pipeline-ல் retrieval stage-க்கு தேவை

Constraint it addresses: meaning, not keywords.

Alternatives:
- **Keyword search + synonym expansion**: Cheap, but manual maintenance, incomplete.
- **BM25 / Elasticsearch**: Exact match + ranking நன்றாக இருக்கும், ஆனால் semantic gap இருக்கும்.
- **Hybrid search**: Keyword + semantic இரண்டையும் combine செய்யலாம். Production-ல் இது common.

Architect எப்போது தேர்வு செய்வார்?
Latency முக்கியம் இல்லாத internal search, customer support, document Q&A, product recommendation என்றால் semantic search first choice. Real-time e-commerce search-ல் hybrid பயன்படுத்துவார்கள்.

## 5. Trade-offs

**Embedding model quality vs cost**: Bigger model = better semantics, ஆனால் latency மற்றும் cost அதிகம். Production-ல் small model for retrieval, large model for rerank என்ற two-stage common.

**Approximate Nearest Neighbor vs Exact**: Vector DB-கள் ANN பயன்படுத்தும். Recall தியாகம் செய்து latency குறைக்கிறோம். `nprobe`, `ef_search` போன்ற tuning தேவை.

**Dimensionality & storage**: 1M docs * 1536 dim * 4 bytes ≈ 6 GB. Index, replication சேர்த்தால் cost வரும்.

**Drift & freshness**: Content update ஆனால் re-embed செய்ய வேண்டும். Embedding model புதுப்பித்தால் full re-index தேவை. Versioning முக்கியம்.

**Failure mode**: Embedding model garbage input-ஐ vector-ஆக மாற்றும். No relevance guard. Hallucination risk in RAG. Filter, metadata, rerank இல்லாமல் மோசமான results வரும்.

## 6. Practical Example

Enterprise support chatbot.

Docs: 50k tickets, product manuals, release notes.

Flow:
- Offline: docs-ஐ chunks-ஆக பிரித்து embed செய்து vector DB-ல் store. Metadata: product, version, language.
- Online: user query "refund not credited after cancellation" -> embed -> vector DB search with metadata filter product = 'X' -> top 10 chunks -> rerank -> LLM-க்கு context-ஆக அனுப்பு.

Result: keyword-ல் "refund credited" இல்லாத ticket கூட "money returned after cancel" என்ற meaning-ல் வந்துவிடும்.

Cost control: 80% queries-க்கு embedding model small, rerank optional. Peak load-ல் cache frequent queries.

## 7. Reasoning Challenge

உங்களிடம் 20M product descriptions இருக்கு. Users daily 2M queries செய்கிறார்கள். 
Requirement: p95 latency < 150ms, recall > 90%.

இப்போது plain semantic search போதுமா? Hybrid search தேவைய
