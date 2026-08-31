# Wrong ranking

> **Learning Path:** RAG Architecture
> **Section:** 12.3.4 — RAG failure modes

### 12.3.4 — RAG failure modes: Wrong ranking

## 1. Problem

உங்க RAG system-ல் user கேள்வி: *"நாங்கள் கடந்த quarter-ல் தயாரித்த highest margin product எது?"*

Retriever 10 chunks திரும்பி கொடுத்தது. அதில் 3 chunks சரியாக relevant. ஆனால் LLM-க்கு கிடைத்த top 3 chunks எல்லாம் generic product description, financial summary மாதிரி irrelevant ஆனது.

Result: LLM சரியான context இல்லாமல் hallucinate பண்ணுது அல்லது generic பதில் தருது. User-க்கு தப்பான ranking தெரியுது.

What goes wrong? Retriever தேடினான், ஆனால் **relevant-ஆனவற்றை முதலில் வைக்கவில்லை**. Wrong ranking = right information உள்ளே இருக்கு, ஆனால் LLM-ன் attention-க்கு வராமல் போய்விட்டது.

## 2. Mental Model

RAG-ல் ranking என்பது **relevance ordering** மட்டுமல்ல, **decision power** கொடுப்பது.

LLM-க்கு context window limited. முதல் few chunks தான் strong influence கொடுக்கும். Retriever ஒரு relevance score கொடுக்கும். அந்த score தவறாக இருந்தால், சரியான chunk deep-ல் புதைந்து விடும்.

Think of it like search results: Page 1-ல் சரியான link இல்லை என்றால் user page 2-க்கு போக மாட்டார்.

## 3. How It Works

Typical flow:

`Query → Embedding → Vector DB similarity search → Top-K → Reranker? → LLM`

Wrong ranking usually happens இங்கே:

* **Embedding similarity mismatch**: Query embedding "highest margin product" vs chunk embedding "Q2 sales report". Semantic similarity low ஆனால் conceptually related. Embedding model surface words-க்கு மட்டும் match பண்ணும்.
* **Chunking artifact**: Important info 2 chunks-க்கு split ஆகி இருக்கும். Each chunk alone incomplete. Score low.
* **No reranking**: Vector DB cosine similarity மட்டும் பயன்படுத்தினால், lexical nuance miss ஆகும். Cross-encoder reranker இல்லாமல் ranking noisy ஆகும்.
* **Query misunderstanding**: User implicit context இருக்கும். "நாங்கள்" என்றால் company X. Retriever அதை capture பண்ணவில்லை.

## 4. Architectural Reasoning

Wrong ranking எப்போது painful ஆகும்?

* **High precision needed**: Finance, legal, medical RAG-ல் ஒரு wrong chunk முதலில் வந்தால் decision தவறும்.
* **Long corpus**: Millions of chunks-ல் signal-to-noise low.
* **Ambiguous queries**: Same words, different intent.

Options:

1. **Better chunking**: Smaller, semantically coherent chunks with metadata. Problem solve ஆகும்? Partial.
2. **Hybrid retrieval**: Vector + BM25 keyword. Query has rare terms "margin" -> BM25 boost.
3. **Reranker**: Cross-encoder with query+chunk. Computational cost அதிகம் ஆனால் ranking quality கணிசமாக improve ஆகும்.
4. **Query expansion / rewrite**: LLM-ஆல் query-ஐ expand பண்ணி multiple queries generate செய்யலாம்.
5. **Contextual reranking with LLM**: First pass top-50 → LLM judge relevance → top-5.

Architect choose பண்ணுவது constraint பொறுத்து: latency vs accuracy, cost vs quality.

## 5. Trade-offs

* **Recall vs Precision in top-K**: K அதிகமாக்கினால் relevant chunk கண்டிப்பாக வரும், ஆனால் LLM context window fill ஆகி noise அதிகம். K சிறியதாக இருந்தால் noise குறைவு, ஆனால் relevant miss ஆகும்.
* **Reranker latency**: Cross-encoder ~50-200ms per query. Real-time chat-க்கு painful. Trade-off: async rerank or only for critical queries.
* **Embedding model choice**: General embedding cheap & fast. Domain-specific embedding தேவைப்படும் ஆனால் retraining cost உண்டு.
* **Ranking stability**: Same query, different runs different ranking if vector DB approximate search ANNS பயன்படுத்தினால். Determinism vs speed.

Failure mode: Reranker overfits to query wording, மறைமுக related chunk-ஐ reject பண்ணும்.

## 6. Practical Example

Enterprise support RAG: User asks "Production API timeout எப்படி fix பண்ணுறது?" 

Retriever top results:
1. "API timeout general overview" – generic
2. "How to increase timeout in dev environment" – dev only
3. "Production incident postmortem: 2024-06" – contains exact fix, but chunk title is "Postmortem summary"

Embedding score low because words mismatch. Wrong ranking.

Fix applied: Hybrid retrieval + metadata filter `env=production`. Reranker with instruction: "Prefer chunks with remediation steps". Now correct postmortem chunk #1-ல் வருகிறது.

Result: LLM correct runbook தருகிறது.

## 7. Reasoning Challenge

உங்க RAG system-ல் 100K chunks உள்ளது. User query: "எந்த customer-க்கு refund approve பண்ண வேண்டும்?"

Retriever top-10-ல் 2 relevant chunks உள்ளன, ஆனால் rank 8 மற்றும் 9-ல் உள்ளன. LLM தவறான பதில் தருகிறது. Latency budget 800ms.

நீங்கள் reranker add பண்ணலாம், K அதிகமாக்கலாம், அல்லது hybrid retrieval பயன்படுத்தலாம். என்ன செய்வீர்கள்? ஏன்? Trade-off என்ன?

## 8. Key Takeaways

* Wrong ranking என்பது retrieval failure அல்ல, **ordering failure**. Relevant info உள்ளே இருந்தும் LLM-க்கு தெரியாமல் போகும்.
* Embedding similarity மட்டும் போதாது. Hybrid + reranker பல real systems-ல் must.
* Top-K choice, chunking strategy, metadata filtering எல்லாம் ranking quality-ஐ நேரடியாக மாற்றும்.
* Ranking improve பண்ணினால் latency, cost, complexity அதிகரிக்கும். Architect அதை tradeoff பண்ணி தான் decide செய்ய வேண்டும்.
