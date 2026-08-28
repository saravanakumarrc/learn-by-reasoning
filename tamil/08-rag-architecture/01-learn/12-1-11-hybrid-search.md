# Hybrid search

> **Learning Path:** RAG Architecture
> **Section:** 12.1.11 — Learn

## 1. Problem

உங்களுக்கு ஒரு RAG system இருக்கு. User query: "என்னுடைய refund policy எப்படி work ஆகும்?"

Pure vector search பண்ணினா, embedding similarity-க்கு பொருத்தமான chunks கிடைக்கும். ஆனா "refund policy" என்ற exact phrase இருக்கும் document கூட miss ஆகலாம். ஏன்னா embedding semantic meaning-ஐ பார்க்கும், exact keyword-ஐ guarantee பண்ணாது.

மாறாக pure keyword search, BM25 போன்றது, "refund policy" exact match-ஐ கண்டுபிடிக்கும். ஆனா "return request எப்படி செய்யறது" என்று user கேட்டால், அதே document-ஐ கொண்டு வராது.

உண்மையில் user என்ன வேண்டும் என்பது **both** : semantic intent + exact term match.

இந்த gap தான் hybrid search வந்த காரணம்.

> What goes wrong if we don't have this? Relevant docs miss ஆகும், hallucination அதிகரிக்கும், user experience மோசமாகும்.

## 2. Mental Model

Hybrid search = **vector search + keyword search ஒன்றாக**.

இரண்டு signals-ஐயும் generate பண்ணி, combine பண்ணி rank பண்ணுவது.

உதாரணமாக ஒரு document-க்கு:
- Vector score = 0.82
- BM25 score = 1.4

இதை ஒரு common scale-க்கு normalize பண்ணி, weight கொடுத்து final score கணக்கிடுவது.

Mental model: இரண்டு கண்கள். ஒன்று meaning-ஐ பார்க்கும், இன்னொன்று exact words-ஐ பார்க்கும். இரண்டும் சேர்ந்தால் தான் முழு படம்.

## 3. How It Works

Flow simple:

1. Query வரும்.
2. Parallel-ஆ இரண்டு paths:
   - **Vector path**: query-ஐ embedding-ஆ convert பண்ணி vector database-ல ANN search.
   - **Keyword path**: query-ஐ BM25 / inverted index-ல run பண்ணி lexical match.
3. இரண்டு results set-ஐ combine பண்ணி re-rank.

Combine எப்படி?

**Reciprocal Rank Fusion - RRF**: மிகவும் பிரபலம், no training தேவை.
`score = 1 / (k + rank_vector) + 1 / (k + rank_keyword)`

k ~ 60.

Weight-based linear combination-ம் உண்டு: `final = alpha * norm_vector + (1-alpha) * norm_keyword`

Some systems do **first retrieve broad, then re-rank**: vector + keyword-ல top 100 எடுத்து, cross-encoder போன்ற re-ranker-க்கு கொடுத்து final top 10 தேர்வு.

## 4. Architectural Reasoning

எப்போது hybrid useful?

- Domain-ல exact terms முக்கியம்: product codes, error codes, law clauses, medical terms, SKU, policy names.
- User queries short and keyword heavy.
- Corpus-ல paraphrase அதிகம் இருக்கும்.

Alternatives:
- **Vector only**: semantic strong, but keyword precision இல்லை. Synonym match ஆகும், but exact match guarantee இல்லை.
- **Keyword only**: precise for exact terms, semantic drift இல்லை, but "how to cancel subscription" vs "subscription cancellation process" miss ஆகும்.
- **Vector + re-ranker only**: quality better, ஆனால் recall குறைவு.

Hybrid choose பண்ணுவது ஏனெனில்: recall-ஐ maximize பண்ணலாம், precision-ஐ keyword-ஆல் protect பண்ணலாம்.

## 5. Trade-offs

**1. Complexity and cost**
இரண்டு index maintain பண்ண வேண்டும். Vector DB + keyword index. Query latency double ஆகும், though parallel run பண்ணலாம். Operational overhead உண்டு.

**2. Tuning burden**
Alpha weight, RRF k, normalization method — இதை data-க்கு ஏற்ப tune பண்ண வேண்டும். Query type-க்கு ஏற்ப dynamic weight கூட வேண்டும். இது architect-ன் decision.

**3. Storage**
Embedding vectors + inverted index. Corpus பெரிதாக இருந்தால் cost அதிகரிக்கும்.

Failure modes:
- Keyword index stale ஆனால் vector fresh என்றால் mismatch.
- Normalization தவறாக இருந்தால் ஒரு signal dominate ஆகி இன்னொன்று மறைந்து விடும்.

## 6. Practical Example

Enterprise support RAG.

Corpus: 200k support articles. User asks: "Order #A12345 refund status"

Vector search: "refund status" semantic-ஆல் பொருத்தமான articles கொண்டு வரும், ஆனால் order number தேவை.

Keyword search: order number exact match-ஐ கண்டுபிடிக்கும்.

Hybrid: RRF-ஆல் combine பண்ணினால், order number கொண்ட article-ம் semantic related policy article-ம் இரண்டும் top-ல் வரும்.

Architecture:
`API Gateway -> Hybrid Retriever -> [Vector DB: pgvector, Keyword: Elasticsearch] -> RRF combiner -> Re-ranker -> LLM`

Production-ல, Elasticsearch-ல் hybrid search native support இருக்கு, OpenSearch கூட. Pinecone, Weaviate hybrid mode கொடுக்கின்றன.

## 7. Reasoning Challenge

உங்களிடம் 2M documents உள்ளன. 70% queries product codes / error codes கொண்டவை. 30% natural language questions. Latency budget 200ms.

இங்கே hybrid search-ஐ எப்படி design செய்வீர்கள்? Weight எப்படி set செய்வீர்கள்? Keyword vs vector-க்கு priority எது?

யோசித்து பாருங்கள்: query pattern பார்த்து dynamic weighting பயன்படுத்தலாமா? எல்லா query-க்கும் same weight போதுமா?

## 8. Key Takeaways

- Hybrid search solves **recall + precision** gap between semantic and exact match.
- Vector = meaning, Keyword = exact terms. இரண்டும் தேவை.
- RRF is simple, effective, training free combination method.
- Trade-off என்பது complexity, cost, tuning. Every architectural gain has operational price.
- Architect-ஆக நீங்கள் தேர்வு செய்வது எப்போது hybrid தேவை, எந்த weight, எந்த combiner என்பதுதான்.

இதை புரிந்து கொண்டால், RAG retrieval quality-ஐ production level-க்கு கொண்டு வர முடியும்.
