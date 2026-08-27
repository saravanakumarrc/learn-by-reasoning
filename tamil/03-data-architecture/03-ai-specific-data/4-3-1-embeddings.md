# Embeddings

> **Learning Path:** Data Architecture
> **Section:** 4.3.1 — AI-specific data

## 1. Problem

உங்க e-commerce site-ல user "நீர்ப்புகா ரன்னிங் ஷூ, மென்மையான sole"னு தேடுகிறார். Database-ல product title-ல "waterproof running shoes with soft cushioning" இருக்கு. Keyword search-க்கு match இல்லை.

இன்னொரு case: Support chat bot-க்கு user கேள்வி கேட்கிறார். Relevant FAQ-வை கண்டுபிடிக்க வேண்டும். Exact keyword match போதாது. Paraphrase, synonym, context எல்லாம் வேண்டும்.

இங்கே problem என்ன? Text-ஐ machine-க்கு compare செய்யக்கூடிய ஒரு form-க்கு மாற்ற வேண்டும். String comparison வேலை செய்யாது.

## 2. Mental Model

Embedding என்பது **meaning-ஐ number vector-ஆ மாற்றுவது**.

ஒரு sentence / document / product description-ஐ 768 அல்லது 1536 dimension உள்ள vector-ஆக encode செய்கிறோம். பொருள் ஒத்த விஷயங்கள் vector space-ல் ஒன்றுக்கொன்று அருகில் இருக்கும்.

"cheap running shoes" மற்றும் "affordable jogging footwear" vector-கள் அருகில் இருக்கும். "laptop stand" தொலைவில் இருக்கும்.

Distance = semantic similarity.

## 3. How It Works

1. **Encode**: Pre-trained embedding model e.g., `text-embedding-3-small`, `BAAI/bge-small-en` எடுத்து text-ஐ vector-ஆக மாற்றுகிறது.
2. **Store**: அந்த vector-ஐ vector database-ல் சேமிக்கிறோம். `Postgres + pgvector`, `Milvus`, `Weaviate`, `Qdrant`, `Pinecone` போன்றவை.
3. **Query**: User query-க்கும் embedding உருவாக்கி, vector DB-ல் cosine similarity / dot product மூலம் nearest neighbours-ஐ தேடுகிறோம்.
4. **Use**: Top-k results-ஐ downstream system-க்கு கொடுக்கிறோம். RAG-ல் LLM-க்கு context-ஆக.

இதுவே core loop.

## 4. Architectural Reasoning

Embeddings useful ஆகும் போது:

* Semantic search வேண்டும், keyword search போதாது
* Recommendation, clustering, deduplication போன்ற similarity tasks
* RAG pipeline-ல் retrieval stage

Constraints இது தீர்க்கிறது:
* **Latency**: Approximate Nearest Neighbour ANN மூலம் மில்லியன் vectors-ல் ms-ல் search
* **Scale**: 100M documents handle பண்ண வேண்டும்

Alternatives:
* BM25 / keyword search: exact match, cheap, interpretable. Semantic தெரியாது
* Hand-crafted features: maintenance கனமானது

Decision: Precision vs recall trade-off. Legal / finance போன்ற exactness முக்கியமான domain-ல் hybrid search: keyword + vector combine செய்வது common.

## 5. Trade-offs

* **Model quality vs cost & latency**. Bigger embedding model = better semantic capture ஆனால் inference cost அதிகம், latency அதிகம். Offline batch embedding-க்கு ஒரு model, online query-க்கு இன்னொரு lightweight model என பிரிப்பார்கள்.
* **Storage & indexing**. 1M documents × 1536 dim × 4 bytes = ~6 GB raw. HNSW index அதை 2-3x increase பண்ணும். Sharding, replication வேண்டும்.
* **Drift & versioning**. Embedding model மாற்றினால் பழைய vectors invalid ஆகும். Re-embedding pipeline, version pinning தேவை.
* **Semantic vs exact**. Embedding திரும்ப கொண்டு வரும் "relevant" ஆனால் hallucination அல்லது wrong context கொடுக்கலாம். RAG-ல் retrieval quality முழு system quality-ஐ தீர்மானிக்கும்.

Failure mode: Bad chunking. 5000 token document-ஐ ஒரே vector-ஆக encode செய்தால் முக்கிய தகவல் dilute ஆகும். Chunk size, overlap, metadata filtering முக்கியம்.

## 6. Practical Example

E-commerce + Support RAG.

Product catalog-ல் 200k descriptions உள்ளன. ஒவ்வொரு product-ஐ 512 tokens chunk-ஆக பிரித்து `bge-small` model-ல் embed செய்து Qdrant-ல் சேமிக்கிறோம். Metadata-ல் category, price, brand filter.

User search "பனிக்காலத்திற்கு ஏற்ற லேசான ஜாக்கெட்". Query-ஐ embed செய்து top-10 results எடுக்கிறோம். Metadata filter: price < 3000, in_stock = true. Results UI-ல் காட்டுகிறோம்.

Support RAG-ல் FAQ + policy docs-ஐ chunk செய்து embed செய்து Pinecone-ல் வைத்திருக்கிறோம். User question வந்ததும் embed → retrieve top-k → LLM-க்கு context-ஆக கொடுக்கிறோம்.

```mermaid
graph LR
A[Document] --> B[Chunk + Embed Model]
B --> C[Vector DB]
D[User Query] --> E[Embed Model]
E --> C
C --> F[Top-k chunks]
F --> G[LLM]
