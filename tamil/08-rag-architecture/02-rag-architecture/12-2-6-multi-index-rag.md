# Multi-index RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.2.6 — RAG architecture

## 1. Problem

உங்க RAG system ஒன்னு இருக்கு. User கேட்குறது: "Q3-ல் ஏற்றுமதி செய்யப்பட்ட ஏர்லைன்களின் சராசரி profit margin என்ன?"

இதுக்கு தேவை:
* invoice data
* product catalog
* financial report

ஒரே vector database-ல எல்லாவற்றையும் dump பண்ணினீங்க. Embedding-கள் எல்லாம் ஒன்னா mix ஆகிடும்.

இப்போ query வந்தால்:
* invoice-ல இருந்து irrelevant invoices வந்து context-ஐ pollute பண்ணும்
* catalog description-ல generic terms மாட்டிக்கொள்ளும்
* financial table-ஐ retrieve பண்ண retrieval recall குறையும்

ஒரே index-ல heterogeneous data types, different access patterns, different freshness requirements எல்லாம் சேரும்போது, precision குறையும். Latency அதிகரிக்கும். Re-ranking கடினமாகும்.

**Pain point:** One-size-fits-all index-ல எல்லா data-யும் போட்டால், retrieval quality degrade ஆகும்.

## 2. Mental Model

Multi-index RAG = ஒரே user query-க்கு, பல specialized indexes-ல retrieve பண்ணி, அதை combine பண்ணுவது.

அனலாகி: Library-ல general books, reference books, newspapers என்று sections இருக்கு. ஒரு researcher கேள்விக்கு மூன்று section-களுக்கும் போய் பார்க்கிறார். எல்லாவற்றையும் ஒரே room-ல குவித்தால் கண்டுபிடிக்க கஷ்டம்.

ஒவ்வொரு index-ம் ஒரு **data type / access pattern / freshness** க்கு optimized.

## 3. How It Works

Query வரும்போது:

1. **Query Router / Classifier**: Query-ஐ புரிந்து எந்த index-கள் தேவை என்று decide பண்ணும். Simple rule-based or lightweight LLM classifier.
2. **Parallel Retrieval**: தேர்ந்தெடுத்த indexes-ல vector search + optional keyword / hybrid search.
3. **Fusion**: Results-ஐ merge பண்ணுவது. Reciprocal Rank Fusion, weighted scoring, or LLM re-ranker.
4. **Context Assembly**: Selected chunks-ஐ prompt-ல் போடுவது.

உதாரணம்: user query -> classifier says `financial` + `invoice` indexes தேவை -> இரண்டிலும் top-k retrieve -> fuse -> LLM-க்கு கொடு.

## 4. Architectural Reasoning

Multi-index எப்போது useful?

* **Heterogeneous data**: unstructured docs, structured tables, time-series, code.
* **Different freshness**: Product catalog அடிக்கடி மாறாது, invoices நாள்தோறும் வரும். Different update frequency-க்கு different index.
* **Different retrieval semantics**: Semantic search for docs, keyword / BM25 for precise IDs, vector for embeddings.
* **Access control**: Tenant A data, Tenant B data தனி index-ல isolate பண்ண security சுலபம்.
* **Cost / scale**: Hot data ஒரு fast vector DB-ல, cold data மற்றொரு cheaper store-ல.

Alternative என்ன?
* **Single monolithic index**: Simple, low latency, less operational overhead. ஆனால் precision, freshness, scale-ல compromise.
* **Hybrid search in single index**: BM25 + vector ஒன்றாக. ஆனால் data heterogeneity-ஐ solve பண்ணாது.

Architect ஏன் choose பண்ணுவார்? Recall மற்றும் precision வேண்டும், மற்றும் data boundaries clear-ஆக இருக்கும்போது.

## 5. Trade-offs

**Complexity increases**
Router logic, fusion logic, consistency across indexes maintain பண்ண வேண்டும். Observability கஷ்டம்.

**Latency**
Parallel retrieve செய்தாலும், slowest index overall latency-ஐ drive பண்ணும். Timeout / fallback தேவை.

**Cost**
Multiple vector databases, embeddings, storage. Operational cost அதிகம்.

**Fusion risk**
Wrong weights-ல தவறான context prioritize ஆகும். Hallucination risk increase ஆகலாம்.

Failure mode: Router தவறாக classify பண்ணினால், critical index skip ஆகும். அதனால் router-க்கு fallback = all indexes retrieve.

## 6. Practical Example

Enterprise sales RAG:

* Index A: `knowledge_base` - product docs, blog. Embedding model: `text-embedding-3-large`. Update: monthly. Vector DB: Pinecone.
* Index B: `invoices` - last 12 months invoices. Embedding + metadata filter by date/tenant. Update: daily. Vector DB: Qdrant with TTL.
* Index C: `financial_tables` - structured tables, hybrid BM25+vector. Update: quarterly. Vector DB: Weaviate.

Query: "எங்கள் top 3 customers-க்கு கடந்த quarter-ல return rate என்ன?"

Router detects `invoices` + `financial_tables`. Retrieve top 20 from each. Fusion with weight 0.7 for invoices, 0.3 for tables. LLM re-ranker removes duplicates. Final answer with citations.

## 7. Reasoning Challenge

உங்களிடம் 3 indexes இருக்கு: `legal_contracts`, `support_tickets`, `product_specs`. ஒரு user கேட்கிறார்: "நியூ டெல்லி customer-க்கு warranty claim reject செய்த contract clause எது?"

எந்த indexes-ஐ retrieve பண்ணுவீர்கள்? Query router-ஐ எப்படி design பண்ணுவீர்கள்? Fusion-ல என்ன weight கொடுப்பீர்கள்? ஏன்?

## 8. Key Takeaways

* Multi-index RAG என்பது data heterogeneity மற்றும் access pattern-ஐ handle பண்ண retrieval quality-ஐ improve பண்ணுவது.
* Router + Parallel retrieve + Fusion என்பது core flow.
* Trade-off: Precision / scalability கிடைக்கும், ஆனால் complexity, cost, latency அதிகரிக்கும்.
* Index design-ஐ data boundary, freshness, security constraint-இன் படி செய்ய வேண்டும்.

இது ஏன் தேவைன்னு புரிஞ்சுது. எப்போ use பண்ணணும்னு தெரியும்.
