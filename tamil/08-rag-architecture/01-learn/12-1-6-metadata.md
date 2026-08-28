# Metadata

> **Learning Path:** RAG Architecture
> **Section:** 12.1.6 — Learn

### 12.1.6 — Metadata: RAG-ல் context-ஐ filter பண்ணும் காரணி

## 1. Problem

RAG system-ல் vector database-ல் நீங்கள் ஆயிரக்கணக்கான documents-ஐ embed பண்ணி store பண்ணிருக்கீங்க. User query வந்ததும் top-k similar chunks-ஐ retrieve பண்ணி LLM-க்கு கொடுக்கிறீங்க.

இங்கே பிரச்சனை என்ன?

Query: "Q3 2025-ல் Chennai office-க்கு budget approval என்ன ஆச்சு?"

Retriever semantic similarity மட்டும் பார்த்து, Chennai office-க்கு பழைய 2023 blog post, HR policy, random budget doc எல்லாம் கொண்டு வந்துடும். Relevant ஆனால் **wrong time, wrong department, wrong doc type**.

Embedding மட்டும் போதாது. Similarity இருந்தாலும் context தப்பா இருந்தால் LLM hallucinate பண்ணும், அல்லது noise-ஐ read பண்ணி மெதுவாகும்.

> **What goes wrong if we don't have metadata?** Retrieve செய்யும் data-ல் signal-to-noise ratio மோசமாகும். Filter பண்ண முடியாது.

## 2. Mental Model

Metadata என்பது vector embedding-க்கு கூடவே ஒட்டிக்கொண்டிருக்கும் **structured labels**.

Embeddings = *what the chunk means*.
Metadata = *when, where, who, what type, how reliable*.

உதாரணமா ஒரு chunk-க்கு:
- `doc_type: "budget_approval"`
- `office: "Chennai"`
- `quarter: "Q3_2025"`
- `source_system: "SAP"`
- `classification: "internal"`
- `last_updated: "2025-10-01"`

Embedding semantic search-ஐ கவனிக்கும், metadata structured filter-ஐ கவனிக்கும். இரண்டும் சேர்ந்தால் தான் precision வரும்.

## 3. How It Works

RAG pipeline-ல் ingestion time-ல் ஒவ்வொரு chunk-உம் create ஆகும்போது, நீங்கள் metadata fields-ஐ extract / generate பண்ணி vector DB-ல் store பண்ணுறீங்க.

Retrieval time-ல்:

1. Query-ஐ புரிஞ்சிக்கோங்க, filters என்ன தேவைன்னு identify பண்ணுங்க.
2. Vector search + metadata filter ஒன்னா apply பண்ணுங்க.
3. Hybrid ranking பண்ணுங்க.

Pseudo:

```
filters = {
  office: "Chennai",
  quarter: "Q3_2025",
  doc_type: in ["budget_approval","budget_report"]
}
results = vector_db.search(query_embedding, filters=filters, top_k=10)
```

Vector DB-கள் Pinecone, Weaviate, Qdrant, Milvus எல்லாம் metadata filter-ஐ native-ஆ support பண்ணும். Filter பிறகு similarity ranking நடக்கும்.

## 4. Architectural Reasoning

Metadata தேவைப்படும் போது?

- **Multi-tenant system**: tenant_id மூலம் data isolation வேணும். Customer A-வோட data Customer B-க்கு போகக்கூடாது.
- **Time-sensitive queries**: quarter, year, effective_date மூலம் stale data-ஐ தவிர்க்க.
- **Access control**: classification = public/internal/confidential. User role-க்கு ஏற்றபடி filter.
- **Source quality**: source_system reliability, author, review_status.
- **Routing**: doc_type-க்கு ஏற்ப different retrieval strategy.

Alternatives?

- Embed everything into text: "This is Chennai office Q3 2025 budget approval..." னு chunk-ல் hardcode பண்ணலாம். ஆனால் embedding noise ஆகும், filter exact ஆகாது, மாற்றம் வந்தால் re-embed வேண்டும்.
- Post-retrieval filter: 100 results எடுத்து Python-ல் filter பண்ணலாம். ஆனால் cost, latency, less accurate.

Architect ஏன் metadata choose பண்ணுவார்? Because it gives **deterministic control** on top of fuzzy semantic search.

## 5. Trade-offs

**Precision vs Recall**
Filter strict ஆக்கினால் precision அதிகம், ஆனால் relevant docs miss ஆகலாம். Too loose filter என்றால் noise வரும்.

**Metadata maintenance cost**
Metadata schema evolve ஆகும். office name மாறும், new fields வரும். Ingestion pipeline-ல் extraction logic maintain பண்ண வேண்டும்.

**Filter performance**
Vector DB-ல் metadata filter index இல்லாமல் scan ஆகலாம். High cardinality fields-ல் performance degrade ஆகும்.

**Consistency risk**
Metadata wrong ஆக extract ஆனால் correct doc கூட retrieve ஆகாது. Garbage in, garbage out. Validation, normalization முக்கியம்.

**Security**
Metadata filter மட்டும் போதாது. Defense in depth வேண்டும். DB level row-level security + app level filter இரண்டும்.

## 6. Practical Example

Enterprise RAG for internal knowledge base.

Documents: Confluence, Jira, SAP reports, emails.

Ingestion-ல் chunk-க்கு metadata:

```
{
  "chunk_id": "...",
  "doc_id": "SAP_BUD_2025Q3",
  "title": "Q3 Budget Approval",
  "office": "Chennai",
  "department": "Sales",
  "quarter": "Q3_2025",
  "doc_type": "budget_approval",
  "source": "SAP",
  "classification": "internal",
  "owner_team": "finance",
  "created_at": "2025-09-15",
  "updated_at": "2025-10-01"
}
```

User query: "Show me approved budget for Chennai sales Q3 2025"

Retrieval flow:
- Embed query
- Vector search with filters: `office = Chennai AND department = Sales AND quarter = Q3_2025 AND doc_type in [budget_approval,budget_report] AND classification in [public,internal]`
- Top 5 results to LLM with metadata citations.

Result: Noise குறையும், latency குறையும், compliance maintain ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் 3 product lines உள்ளன: `mobile`, `laptop`, `server`. ஒவ்வொன்றுக்கும் separate support docs உள்ளன. User role `customer` மற்றும் `internal_engineer`. Internal docs-ல் sensitive debug info உள்ளது.

Query: "server firmware bug fix"

நீங்கள் metadata-ஐ எப்படி design செய்வீர்கள்? Filter-ஐ எங்கே apply செய்வீர்கள் - retrieval time-லா, post-retrieval-லா? Role based access-க்கு என்ன trade-off இருக்கு?

## 8. Key Takeaways

- Metadata = semantic search-க்கு deterministic guardrails.
- Embedding tells *what it means*, metadata tells *when/where/who*.
- Filter at retrieval time for performance, precision, and cost.
- Schema design முக்கியம்: consistent, normalized, low cardinality where possible.
- Every filter adds precision but risks missing relevant data; balance with recall.

இப்போது metadata இல்லாமல் RAG வேலை செய்யும், ஆனால் production-grade, multi-tenant, compliant system-க்கு metadata தான் difference create பண்ணும்.
