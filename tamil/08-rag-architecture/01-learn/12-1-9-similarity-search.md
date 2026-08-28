# Similarity search

> **Learning Path:** RAG Architecture
> **Section:** 12.1.9 — Learn

## 1. Problem

உங்க RAG system-ல user கேட்ட கேள்விக்கு relevant documents கண்டுபிடிக்கணும்.

பழைய முறை: keyword search. `Elasticsearch` -ல `match` பண்ணுவோம். User "credit card late fee"ன்னு கேட்டா, அதே exact words இருக்குற doc மட்டும் வரும்.

இப்போ user "என் கார்டுக்கு தாமதமாக கட்டினா என்ன fine வரும்?"ன்னு தமிழ்-English mix-ல கேக்குறார். Exact match இல்லை. Synonym இருக்கு. Intent ஒன்னுதான்.

இதுல என்ன பிரச்சனை? 
- Semantic meaning புரியாது.
- Paraphrase பண்ணினாலும் miss ஆகும்.
- Large corpus-ல manual keyword tuning செய்ய முடியாது.

இந்த pain தான் similarity search-ஐ உருவாக்கியது.

## 2. Mental Model

Similarity search என்பது **meaning-ஐ compare பண்ணுவது, words-ஐ compare பண்ணுவதல்ல**.

ஒவ்வொரு document / text chunk-ஐயும் ஒரு vector-ஆ மாற்றி விடுறோம். இது embedding.

அதே query-ஐயும் vector-ஆ மாற்றுறோம். இப்போ இரண்டு vectors-க்கும் இடையேயான distance பார்த்து "இது எவ்ளோ close"ன்னு decide பண்ணுறோம்.

உதாரணம்: "late fee" vector-க்கும் "தாமத கட்டணம்" vector-க்கும் cosine similarity high.

Mental model: ஒரு high-dimensional space-ல meaning-ஐ point-ஆ plot பண்ணி, nearest neighbours கண்டுபிடிக்கிறோம்.

## 3. How It Works

1. **Chunking**: Document-ஐ 200-500 tokens-க்கு split பண்ணுறோம். Context retain பண்ண.
2. **Embedding**: `text-embedding-3-small` / `bge-small` மாதிரி model use பண்ணி ஒவ்வொரு chunk-க்கும் 768/1536 dim vector generate பண்ணுறோம்.
3. **Index**: Vector-ஐ vector database-ல store பண்ணுறோம். `pgvector`, `Milvus`, `Qdrant`, `Weaviate`, `Pinecone`.
4. **Query**: User query-க்கும் embedding உருவாக்கி, index-ல ANN search பண்ணி top-K nearest vectors எடுக்குறோம்.
5. **Rerank**: Optional. First retrieval-ல semantic match வந்ததும், cross-encoder-ஆல final relevance score மேம்படுத்துறோம்.

ANN = Approximate Nearest Neighbour. Exact search செய்ய முடியாது scale-ல, அதனால approximate பண்ணுறோம்.

## 4. Architectural Reasoning

எப்போ similarity search தேவை?

- User query paraphrase ஆகும், synonym use பண்ணும்.
- Large unstructured corpus: PDFs, support tickets, product catalog.
- LLM-க்கு context provide பண்ணணும், but relevant context மட்டும்.

Constraints address பண்ணும்:
- **Latency**: ANN index + HNSW graph -> 10-50ms-ல top 10 results.
- **Scale**: Millions of chunks. Brute force cosine compare impossible.
- **Recall**: Semantic match வேண்டும், keyword மட்டும் போதாது.

Alternatives:
- Keyword search + BM25: exact term match, fast, cheap. Semantic இல்லை.
- Hybrid search: keyword + vector combine. Best of both. Production RAG-ல common.
- Full LLM re-rank all docs: accurate ஆனா expensive, slow.

Architect choose பண்ணுவது ஏன்? 
User intent-ஐ capture பண்ணணும், மற்றும் corpus grow ஆகும் போது maintainable-ஆ இருக்கணும்.

## 5. Trade-offs

**Accuracy vs Speed**: HNSW high recall, but memory heavy. IVF PQ compression save memory but recall drop.

**Embedding model quality vs cost**: Bigger model = better semantic, but latency & cost அதிகம். Query time embedding generate பண்ணும்போது cold start.

**Index freshness**: Document update ஆனா re-embed + re-index வேண்டும். Real-time ingestion pipeline வேண்டும்.

**Dimensionality curse**: High dim-ல distance meaningless ஆகும். Normalization, good embedding model தேவை.

Failure modes:
- Chunk too big -> context loss, too small -> fragmentation.
- Poor chunking strategy -> meaning break.
- Embedding drift: model version change பண்ணினா old vectors inconsistent ஆகும்.
- ANN recall miss: approximate search சில relevant docs-ஐ miss பண்ணலாம்.

## 6. Practical Example

Enterprise support RAG.

Corpus: 200k support articles, 5 years tickets.

Architecture:
`User Query` -> `Embedding Service` -> `Qdrant` vector DB -> Top 10 chunks -> `Reranker` -> LLM context.

Producer side: Document ingestion pipeline daily run ஆகும். PDF -> text -> chunk -> embed -> upsert to Qdrant with metadata: article_id, category, language.

Query time: User கேட்ட "என் UPI payment fail ஆச்சு refund எப்போ வரும்?" -> embedding -> Qdrant search with filter: `category = payments`. Top 5 results get.

Trade-off handle: Hybrid search use பண்ணி query-ல keyword "refund" exact match weight கொடுக்கிறோம். Cost control: first retrieval vector மட்டும், rerank 10 docs மட்டும்.

## 7. Reasoning Challenge

உங்க system-ல 10M chunks இருக்கு. Query latency p95 < 100ms வேண்டும். Daily 50k new documents add ஆகும்.

நீங்கள் pure vector search வைப்பீர்களா? Hybrid வைப்பீர்களா? HNSW vs IVF PQ எதை தேர்வு செய்வீர்கள்? Embedding model change ஆனா existing vectors-ஐ என்ன செய்வீர்கள்?

## 8. Key Takeaways

- Similarity search என்பது words இல்லை, meaning-ஐ compare பண்ணும்.
- Embedding + vector DB + ANN தான் core. Reranker தரத்தை lift பண்ணும்.
- Chunking quality, embedding model choice, index config ஆகியவை retrieval quality-ஐ decide பண்ணும்.
- Production-ல hybrid search, filters, freshness pipeline முக்கியம். Vector alone போதாது.
- Every choice is trade-off: recall vs latency, quality vs cost, freshness vs complexity.
