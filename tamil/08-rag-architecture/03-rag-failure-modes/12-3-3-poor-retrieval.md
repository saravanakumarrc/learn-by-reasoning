# Poor retrieval

> **Learning Path:** RAG Architecture
> **Section:** 12.3.3 — RAG failure modes

## 12.3.3 — RAG failure modes: Poor retrieval

### 1. Problem

உங்கள் RAG system-ல் LLM சரியாகத் தான் respond பண்ணுது. Prompt, grounding, formatting எல்லாம் சரி. ஆனால் answer தவறாக இருக்கிறது, hallucinate பண்ணுகிறது, அல்லது outdated information கொடுக்கிறது.

ஏன்?

LLM-க்கு கொடுத்த context தான் தவறு.

> "User கேட்டதுக்கு சரியான document தேவை. ஆனால் retriever திரும்பியது irrelevant document."

இது தான் **poor retrieval**. Generator எவ்வளவு நல்லது இருந்தாலும், கொடுத்த input தவறாக இருந்தால் output தவறாகத்தான் வரும்.

Garbage in, garbage out. RAG-ல் garbage என்பது பெரும்பாலும் wrong retrieval.

### 2. Mental Model

RAG என்பது இரண்டு step:

**Retrieve → Generate**

Generate step தவறாக இருந்தால், LLM-ஐ tune பண்ணலாம், prompt மாற்றலாம்.

Retrieve step தவறாக இருந்தால், LLM செய்வது ஒன்றும் இல்லை. அது தப்பான தகவலை திடமாக நம்பி தரும்.

Retrieval என்பது user query-க்கு **relevant, accurate, fresh** chunks-ஐ கொண்டு வருவது. அதில் ஒன்று கூட தவறினால் answer quality விழும்.

### 3. How It Works

Poor retrieval வருவதற்கு மூன்று root causes:

**a. Representation mismatch**
Query embedding vs document embedding சரியாக align ஆகவில்லை. User natural language-ல் கேட்கிறார், document formal technical language-ல் உள்ளது. அல்லது query vague. Embedding model அந்த semantic gap-ஐ பிடிக்கவில்லை.

**b. Chunking problem**
Information பிரிந்து போய் விட்டது. ஒரு fact இரண்டு chunk-களுக்கு இடையில் பிரிந்து உள்ளது. Chunk too small → context lost. Chunk too big → noise அதிகம், signal dilute ஆகிறது. Vector DB cosine similarity குறைந்து விடுகிறது.

**c. Index quality problem**
Index stale. Document update ஆனது, ஆனால் embedding re-index ஆகவில்லை. Duplicate content. Metadata filter தவறாக configure ஆகியுள்ளது. User role-க்கு relevant section filter ஆகாமல் இருக்கிறது.

Retriever top-k திருப்பும் போது, relevant item ranking-ல் கீழே இருக்கிறது அல்லது top-k-க்குள் வரவில்லை.

### 4. Architectural Reasoning

Poor retrieval எப்போது தெரியும்?

Latency குறைவு, cost குறைவு, ஆனால் answer hallucination அதிகம். User trust குறையும்.

இதற்கு solution என்ன?

**Retrieval quality-ஐ improve செய்ய வேண்டும், generator-ஐ மட்டும் பெரிதாக்காதீர்கள்.**

Options:

* Better embedding model. Domain-specific fine-tuned embedding vs generic. Tamil-English mix content-க்கு multilingual embedding தேவை.
* Hybrid retrieval. Vector similarity + BM25 keyword search. Keyword exact match தேவைப்படும் technical terms-க்கு உதவும்.
* Re-ranker. First retrieval broad, then cross-encoder re-ranker-ல் top 20-ல் இருந்து top 5-ஐ select.
* Query expansion / query rewriting. LLM-ஐ use செய்து user query-ஐ rewrite செய்து multiple queries generate செய்யலாம்.
* Metadata filtering. User, tenant, date range, document type போன்ற filters apply செய்து search space குறைக்கலாம்.
* Chunking strategy re-evaluate. Semantic chunking, overlap, metadata-aware chunking.

Architect-ஆக நீங்கள் தேர்வு செய்ய வேண்டியது: **quality vs latency vs cost trade-off.**

Re-ranker சேர்ப்பது latency அதிகப்படுத்தும். Hybrid search infrastructure சிக்கலாகும்.

### 5. Trade-offs

* **Precision vs Recall.** Top-k-ஐ அதிகப்படுத்தினால் recall அதிகம், ஆனால் generator-க்கு noise அதிகம். குறைத்தால் relevant doc miss ஆகலாம்.
* **Latency vs Quality.** Re-ranker, query expansion, multi-query improve quality ஆனால் round trip அதிகம்.
* **Index freshness vs Cost.** Real-time re-indexing செய்தால் retrieval accurate ஆகும், ஆனால் embedding compute cost, vector DB write load அதிகம்.
* **Generic embedding vs Domain embedding.** Domain embedding better retrieval, ஆனால் maintain, retrain செய்ய வேண்டும்.

Failure mode: Retrieval poor என்பதை உணராமல், LLM-ஐ larger model-க்கு upgrade செய்து விடுவது. அது cost-ஐ மட்டும் அதிகப்படுத்தும்.

### 6. Practical Example

Enterprise RAG: Internal knowledge base-ல் 10,000 policy documents உள்ளன.

User query: "Leave encashment for resigning employees in Tamil Nadu"

Retriever vector search-ல் திருப்பியது: "General leave policy" document, "HR onboarding FAQ". Relevant "Resignation & Exit Policy - TN" document top-5-ல் இல்லை.

காரணம்: Query-ல் "encashment" என்ற word document-ல் "leave payout" என்று இருக்கிறது. Synonym mismatch. Document chunked per page, payout info 2 pages-க்கு பரவி உள்ளது, single chunk-ல் full context இல்லை.

Fix: Hybrid search add செய்து "resigning" keyword exact match பெற, chunk overlap 150 tokens வைக்க, metadata filter "state = Tamil Nadu", re-ranker add செய்ய.

இப்போது correct doc top-3-ல் வருகிறது.

### 7. Reasoning Challenge

உங்கள் RAG system-ல் user query-க்கு answer சரியாக வருகிறது, ஆனால் 30% queries-க்கு retriever top-10-ல் relevant doc இல்லை. Embedding model generic, chunk size 512 tokens fixed, no metadata filter.

நீங்கள் budget-ல் மூன்று மாற்றம் மட்டுமே செய்ய முடியும்.

எந்த மூன்று தேர்வு செய்வீர்கள்: hybrid search, re-ranker, query expansion, metadata filtering, chunking strategy change, domain embedding? ஏன்?

### 8. Key Takeaways

* Poor retrieval என்பது RAG-ல் மிகப் பெரிய failure mode. Generator நன்றாக இருந்தாலும் பயனில்லை.
* Problem representation mismatch, chunking, index freshness ஆகியவற்றால் வருகிறது.
* Fix என்பது LLM-ஐ பெரிதாக்குவது அல்ல. Retrieval pipeline-ஐ improve செய்வது.
* Precision vs Recall, latency vs quality trade-off-ஐ மனதில் வைத்து hybrid retrieval, re-ranking, metadata filtering போன்றவற்றை தேர்வு செய்யுங்கள்.
