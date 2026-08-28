# Embeddings

> **Learning Path:** RAG Architecture
> **Section:** 12.1.7 — Learn

## 1. Problem

உங்க RAG system-ல user ஒரு question கேட்கிறார்: *"Q3-ல் நமது churn ஏன் அதிகரித்தது?"*

உங்க knowledge base-ல 10,000 documents இருக்கு. 10,000 documents-ஐ ஒவ்வொன்றாக படித்து, LLM-க்கு கொடுத்து, *"இது relevant ஆ?"* என்று கேட்க முடியுமா?

முடியாது. Too slow, too expensive. 

உங்களுக்கு தேவை: **query-வுக்கு பொருத்தமான documents-ஐ வேகமாக கண்டுபிடிக்க வேண்டும்.**

Keyword search வைத்தால் என்ன ஆகும்? User "churn" என்று கேட்டால், "churn" என்ற வார்த்தை இருக்கும் documents மட்டுமே வரும். Paraphrase, synonyms, context எல்லாம் miss ஆகும்.

*What problem became painful?* Text-ஐ machine-க்கு புரியும் வடிவில், meaning-ஐ preserve செய்து, compare செய்யக்கூடிய வடிவில் மாற்ற வேண்டும்.

அதற்கான தீர்வு தான் embeddings.

## 2. Mental Model

Embedding என்பது ஒரு text-ஐ high-dimensional vector ஆக மாற்றுவது.

ஒரு sentence-க்கு 768, 1024 அல்லது 1536 dimensions உள்ள ஒரு number array கிடைக்கும்.

Mental model: **Meaning-ஐ geometry-ஆக மாற்றுவது.**

பொருள் ஒத்த வாக்கியங்கள் vector space-ல் ஒன்றுக்கொன்று அருகில் இருக்கும். வெவ்வேறு பொருள், தூரத்தில் இருக்கும்.

Cosine similarity என்பது இரண்டு vectors எவ்வளவு நெருக்கமாக உள்ளன என்பதை அளவிடும்.

## 3. How It Works

Embedding model என்பது neural network. அது text-ஐ input ஆக எடுத்து, ஒரு fixed-size vector output செய்யும்.

RAG pipeline-ல இது இப்படி work ஆகும்:

1. **Indexing time:** Knowledge base-ல உள்ள ஒவ்வொரு chunk-ஐயும் embedding model வழியாக அனுப்பி vector ஆக்கி, vector database-ல store செய்யுங்கள்.
2. **Query time:** User question-ஐயும் அதே model வழியாக vector ஆக்குங்கள்.
3. Nearest neighbor search செய்யுங்கள். Query vector-க்கு அருகில் உள்ள top-k chunks-ஐ தேர்ந்தெடுங்கள்.
4. அந்த chunks-ஐ LLM context-க்கு கொடுங்கள்.

முக்கியம்: **Same model**-ஐ indexing-க்கும் querying-க்கும் use செய்ய வேண்டும். இல்லை என்றால் space align ஆகாது.

## 4. Architectural Reasoning

Embeddings எப்போது useful?

* Semantic search வேண்டும். Keyword match போதாது.
* Large corpus-ல relevant passages-ஐ retrieve செய்ய வேண்டும்.
* LLM hallucination-ஐ குறைக்க, grounding வேண்டும்.

Constraints it addresses:
* **Latency:** Vector similarity search milliseconds-ல முடியும்.
* **Scalability:** 10M chunks-ஐயும் search செய்யலாம்.
* **Recall:** Paraphrase-ஐயும் catch செய்யும்.

Alternatives:
* Keyword search + BM25. Fast, deterministic, but semantics miss.
* Hybrid search: BM25 + embeddings. பெரும்பாலும் production-ல இது தான்.
* Full LLM re-ranking. Accurate ஆனால் expensive.

Architect ஏன் embeddings-ஐ choose பண்ணுவார்? Because meaning-based retrieval தேவை, மற்றும் cost-ல balance செய்ய முடியும்.

## 5. Trade-offs

**Embedding model quality vs cost.** Bigger models give better semantic capture, but inference slow and expensive. Production-ல small, fast models போதும். Domain-specific fine-tune செய்தால் quality jump ஆகும்.

**Chunk size & overlap.** Chunk too small → context loss. Too large → noise, vector diluted. 200-500 tokens பொதுவாக நல்லது. Overlap 10-20% வைத்தால் boundary cut issues குறையும்.

**Vector database choice.** Pinecone, Weaviate, Qdrant, pgvector. Trade-off: managed vs self-hosted, filtering support, hybrid search, cost.

**Failure modes:**
* Semantic drift: model புரிந்துகொள்ளாத domain jargon.
* Retrieval without grounding: similar ஆனால் factually wrong chunks வரலாம். Reranker தேவை.
* Embedding staleness: knowledge base update ஆனால் embeddings regenerate செய்ய வேண்டும்.

**Every solution creates trade-off:** Embeddings retrieval speed கொடுக்கும், ஆனால் exact keyword match கிடைக்காது. அதனால் hybrid தேவை.

## 6. Practical Example

Enterprise support RAG.

Knowledge base: 50,000 support tickets, product docs, release notes.

Architecture:
* Chunking: 400 tokens, 50 token overlap.
* Embedding model: `text-embedding-3-small` for cost.
* Vector DB: Qdrant, metadata filter: product = "Payments", date > 2024-01.
* Query flow:
  1. User query → embed.
  2. Qdrant-ல cosine similarity search, top 20.
  3. Cross-encoder reranker → top 5.
  4. LLM-க்கு context + query கொடு.

இதனால் "refund process slow" என்று கேட்டால், "payment reversal takes time" என்ற ticket-கூட retrieve ஆகும்.

Cost control: Embeddings offline batch-ல generate செய், query time-ல மட்டும் embed. Vector DB-ல HNSW index வைத்தால் recall vs latency tune செய்யலாம்.

## 7. Reasoning Challenge

உங்களிடம் medical RAG system இருக்கு. Doctors "myocardial infarction" என்றும், patients "heart attack" என்றும் கேட்கிறார்கள். ஒரே concept-க்கு இரண்டு வார்த்தைகள்.

உங்க corpus-ல technical articles மட்டும் இருக்கு. Keyword search-ல patient queries miss ஆகின்றன.

நீங்கள் embeddings use செய்யலாம். ஆனால் general model medical jargon-ஐ சரியாக capture செய்யவில்லை.

இங்கே என்ன செய்வீர்கள்? General embeddings vs domain fine-tune? Hybrid search வேண்டுமா? Chunking strategy மாற்றுமா? ஏன்?

## 8. Key Takeaways

* Embeddings = text-ஐ meaning-preserving vector ஆக மாற்றுவது. Geometry-ல similarity = semantic similarity.
* RAG-ல retrieval-ன் முதுகெலும்பு embeddings தான். Model, chunking, vector DB மூன்றும் சேர்ந்து recall-ஐ decide செய்யும்.
* Keyword search-க்கு semantic search, hybrid search, fine-tuned domain model ஆகியவை realistic options.
* Trade-off எப்போதும் உண்டு: quality vs latency vs cost vs operational complexity.

இது ஏன் தேவைன்னு புரிஞ்சுது. எப்போ embeddings use பண்ணணும்னு தெரியும்.
