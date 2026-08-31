# Poor retrieval

> **Learning Path:** RAG Architecture
> **Section:** 12.3.3 — RAG failure modes

## 1. Problem

உங்க RAG system-ல LLM சரியா பதில் சொல்லுது, ஆனா சில கேள்விகளுக்கு பதில் தப்பா இருக்கு, அல்லது hallucination போல இருக்கு. 

Query: "நம்ம product return policy என்ன?"
LLM answer: "30 நாளுக்குள் return செய்யலாம்"

ஆனால் உண்மையான policy 15 நாள். ஏன்? LLM திறமையானது. Embeddings-ம் okay. ஆனா retrieve ஆன chunks-ல policy பற்றிய correct information இல்லை. தவறான chunk வந்திருக்கு, அல்லது relevant chunk வரவே இல்லை.

Poor retrieval என்பது: **User query-க்கு தேவையான தகவல் இருக்கும் corpus-ல இருக்கு, ஆனா retriever அதை கண்டுபிடிக்க தவறுகிறது.**

What goes wrong if we don't have this? LLM தான் தகவலை உருவாக்க ஆரம்பிக்கும். Trust முறிவு. Production-ல business risk.

## 2. Mental Model

Retrieval என்பது ஒரு search problem. Query embedding vs document embedding space-ல similarity கணக்கிடுவது.

Poor retrieval என்றால், query intent-ம் document content-ம் match ஆகவில்லை. இது 3 இடத்தில் நடக்கும்:

1. **Query misunderstanding** - user என்ன கேட்கிறான் என்பதை retriever புரிந்து கொள்ளவில்லை
2. **Representation gap** - document chunk எப்படி cut ஆகியிருக்கு, அதன் embedding query-க்கு தூரமாக இருக்கு
3. **Index gap** - தேவையான தகவலே corpus-ல சரியாக இல்லை, அல்லது outdated

## 3. How It Works

RAG pipeline: Query → Embed → Vector DB Search → Top-K chunks → LLM Context → Answer

Poor retrieval இங்கே search step-ல break ஆகும்.

ஒரு தவறான உதாரணம்:
Query: "GST rate for SaaS export"
Chunk A: "SaaS export services are zero-rated under GST"
Chunk B: "Our product pricing includes 18% GST"

Retriever Chunk B-ஐ திரும்ப கொடுக்கிறது ஏனென்றால் "GST" token match strong. ஆனால் intent mismatch.

இது ஏன் நடக்கும்?
- Chunk too small: context இழக்கப்படுகிறது
- Chunk too large: signal dilute ஆகிறது
- Embedding model domain mismatch
- Synonym / paraphrase problem: user "return window" என்கிறான், doc "refund period" என்கிறது

## 4. Architectural Reasoning

Poor retrieval எப்போது வரும்?

- **Ambiguous queries**: user குறைவாக எழுதுகிறான். "policy" என்றால் என்ன policy?
- **Multi-hop need**: ஒரு chunk-ல முழு பதில் இல்லை. இரண்டு docs ஒன்றாக link செய்ய வேண்டும்
- **Freshness**: corpus-ல பழைய version இருக்கு. New policy embed ஆகவில்லை
- **Chunking strategy**: paragraph boundary, fixed size, semantic chunk எது என்பது தவறு

Alternatives:
- Better retriever: hybrid search BM25 + vector
- Query expansion / re-ranking
- Larger context window + more chunks
- Reranker model

Architect தேர்வு செய்யும் போது constraint பார்க்கணும்:
Latency constraint இருந்தால் reranker add பண்ணுவது கடினம். Cost constraint இருந்தால் larger K அதிக token cost.

## 5. Trade-offs

**Relevance vs Recall**
Top-3 மட்டும் கொடுத்தால் latency குறைவு, ஆனா recall குறையும். Top-20 கொடுத்தால் recall நன்றாக இருக்கும் ஆனால் LLM context window fill ஆகி, noise அதிகரிக்கும்.

**Chunk size**
சிறிய chunk = precise retrieval, ஆனால் context loss. பெரிய chunk = context retain, ஆனால் embedding diluted, irrelevant info வரும்.

**Hybrid vs Pure vector**
Hybrid search BM25 + vector accuracy improve ஆகும். ஆனால் operational complexity அதிகரிக்கும். Two indexes maintain செய்ய வேண்டும்.

**Failure mode**: Poor retrieval-ஐ debug செய்வது கடினம். LLM output தவறு என்றால் அது retrieval தவறா, generation தவறா என்று தெரியாது. Observability வேண்டும்: query, retrieved chunks, scores log செய்ய வேண்டும்.

## 6. Practical Example

Enterprise support RAG. Customer எழுதுகிறார்: "எனது order cancel செய்தேன் ஆனால் refund வரவில்லை"

Corpus-ல 2 docs உள்ளன:
Doc1: Cancellation policy - refund 7-10 working days
Doc2: Refund process steps

Poor retrieval scenario:
Chunker fixed 500 tokens-ல cut செய்தது. Doc1-ன் cancellation policy chunk-ல refund timeline இல்லை, அது அடுத்த chunk-ல இருக்கு. Retriever முதல் chunk-ஐ மட்டும் கொண்டு வருகிறது. LLM-க்கு timeline தெரியாது. அது generic answer கொடுக்கிறது.

Fix: semantic chunking by section header. "Refund timeline" என்ற section தனியாக chunk ஆகும். அல்லது query expansion: "refund not received" → "refund timeline", "refund delay".

## 7. Reasoning Challenge

உங்க RAG system-ல 80% queries-க்கு good answer வருகிறது. ஆனால் "pricing" related queries-க்கு மட்டும் தவறான தகவல் வருகிறது. Vector DB-ல 10,000 pricing docs உள்ளன. Queries short and ambiguous. 

இங்கே poor retrieval-ன் root cause என்னவாக இருக்கலாம்? Query, chunking, அல்லது index? நீங்கள் முதலில் என்ன diagnostic செய்வீர்கள், மற்றும் architecture-ல என்ன மாற்றம் செய்வீர்கள்? ஏன்?

## 8. Key Takeaways

- Poor retrieval = correct info corpus-ல இருக்கு, ஆனால் retriever அதை கண்டுபிடிக்கவில்லை. இது RAG-ன் மிகப்பெரிய failure mode.
- Chunking strategy, embedding quality, query understanding மூன்றும் retrieval-ஐ நிர்ணயிக்கின்றன.
- Top-K அதிகரிப்பது recall கொடுக்கும் ஆனால் noise மற்றும் cost உருவாக்கும். Reranker உதவும்.
- Retrieval quality-ஐ மதிப்பிட, ground truth queries-க்கு recall@K மற்றும் relevant chunk presence track செய்ய வேண்டும்.
