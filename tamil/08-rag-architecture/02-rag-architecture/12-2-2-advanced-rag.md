# Advanced RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.2.2 — RAG architecture

## 1. Problem

உனக்கு ஒரு LLM உண்டு. அது தன்னோட training data வரைக்கும் மட்டுமே பேசும். உன் company-ன் internal documents, fresh product catalog, customer tickets போன்றவை training-ல இல்லை.

Basic RAG-ல என்ன நடக்கும்? User query வந்ததும் embedding பண்ணி vector database-ல top-k documents தேடி, அதை context-ஆ LLM-க்கு கொடுத்து answer generate பண்ணுவோம்.

இப்போது pain என்ன வருகிறது?

* Query vague ஆக இருக்கும்: "இந்த quarter-ல top selling product எது?" — ஆனால் document-ல direct answer இல்லை, multiple tables இருக்கும்.
* Context too big: 20 documents கொடுத்தால் LLM confuse ஆகும், hallucinate பண்ணும்.
* Relevance low: keyword match இருக்கு ஆனால் actual intent இல்லை.
* Multi-hop reasoning தேவை: "இந்த customer last month buy பண்ணது என்ன, அதுக்கு warranty எப்போ expire ஆகும்?" இது 2 sources தேவை.
* Freshness & freshness: data real time-ல மாறுகிறது, vector DB stale ஆகும்.

இதனால் basic retrieve -> generate மட்டும் போதாது. அதுதான் Advanced RAG வர காரணம்.

## 2. Mental Model

Basic RAG = `Retrieve then Generate`

Advanced RAG = `Understand -> Plan -> Retrieve -> Rerank -> Fuse -> Generate -> Verify`

ஒரு researcher மாதிரி நினை. Query வந்ததும் நேரடியாக google பண்ணாமல், முதலில் query-ஐ clarify பண்ணுவான், என்ன தேவை என்று plan பண்ணுவான், பல source-ல தேடுவான், முடிவை cross-check பண்ணுவான்.

அதே pattern-ஐ RAG-ல கொண்டு வருவதுதான் advanced.

## 3. How It Works

Core additions basic RAG-க்கு மேல்:

**Query Understanding & Expansion**
Query-ஐ rewrite பண்ணி, intent extract பண்ணி, multiple sub-queries generate பண்ணுவோம். Hybrid search உபயோகிப்போம்: vector similarity + BM25 keyword.

**Retrieval with Routing**
எல்லா data ஒரே vector DB-ல இல்லை. Structured DB, graph DB, web search, internal tools என்று இருக்கும். Query router முடிவு செய்யும் எந்த retriever-ஐ hit பண்ண வேண்டும்.

**Reranking**
Retriever 100 candidates கொடுக்கும். Cross-encoder reranker அல்லது LLM-based reranker அதை 5-10 quality context-க்கு குறைக்கும். Relevance கூடும், latency குறையும்.

**Context Compression & Fusion**
Retrieved chunks-ஐ summarize / compress பண்ணி, duplicate remove பண்ணி, final context-ஐ build பண்ணுவோம். Multi-hop-க்கு intermediate results-ஐ chain பண்ணுவோம்.

**Generation with Guardrails**
LLM generate பண்ணிய பிறகு, citation check, fact verification பண்ணி, confidence score கொடுக்கும்.

## 4. Architectural Reasoning

இது useful ஆகும் போது?

* Domain knowledge heavy systems: finance, legal, medical.
* Multi-source data: DB + vector DB + API.
* Accuracy > speed: hallucination cost high.
* Query complex, ambiguous.

Constraint address பண்ணும்?

* Latency vs quality trade-off: Reranking cost adds latency but improves answer quality.
* Cost: LLM calls அதிகம் ஆகும்.
* Consistency: Same query-க்கு stable answer வேண்டும்.

Alternatives?
Basic RAG, fine-tuning, knowledge graph only. Advanced RAG fine-tuning-க்கு மாற்று அல்ல, complement. Fine-tuning costly & slow to update. Advanced RAG real-time update handle பண்ணும்.

## 5. Trade-offs

* **Quality vs Latency & Cost**: Query expansion, reranking, multi-hop என்று ஒவ்வொன்றும் extra LLM calls, extra latency. Production-ல budget set பண்ணி, critical queries மட்டும் advanced path.
* **Complexity vs Operability**: Pipeline பெரிதாகும். Observability, tracing, fallback தேவை. எந்த stage fail ஆனாலும் graceful degradation வேண்டும்.
* **Relevance vs Coverage**: Top-k அதிகம் எடுத்தால் context noisy. குறைவாக எடுத்தால் miss. Reranker + dynamic k இதை balance பண்ணும்.
* **Freshness vs Consistency**: Real-time retrieval வேண்டும் என்றால் cache குறைவு. Cache அதிகம் போட்டால் stale data risk.

Failure modes: Retriever bias, reranker over-filtering, context truncation, citation hallucination.

## 6. Practical Example

Enterprise support agent.

User asks: "எனக்கு last month-ல order பண்ண iPhone-க்கு warranty extend பண்ண முடியுமா?"

Advanced flow:
1. Query understanding: `customer_id` extract, `order last month`, `iPhone`, `warranty extend eligibility` identify.
2. Router decides: structured DB query for orders, vector DB for warranty policy.
3. Sub-queries: "customer orders in last 30 days", "warranty extension policy for iPhone".
4. Retrieve from Postgres via API, retrieve policy docs from vector DB.
5. Rerank policy docs for iPhone specific clause.
6. Fuse: Order date + product + policy rule -> compute eligibility.
7. Generate answer with citation: Order #12345, purchase date, policy section 4.2, eligibility Yes/No.

Basic RAG இங்கே generic policy மட்டும் கொடுத்திருக்கும்.

## 7. Reasoning Challenge

உனக்கு 3 source உண்டு: internal knowledge base vector DB, Postgres customer DB, real-time pricing API. User query: "எனக்கு பிடித்த product-ன் price compare பண்ணு, last year price உம் இப்போ price உம்".

இங்கே retrieve-ஐ எப்படி plan பண்ணுவாய்? எந்த stage-ல reranking, எந்த stage-ல LLM call செய்வாய்? Latency high ஆகாமல் இருக்க என்ன compromise பண்ணுவாய்?

## 8. Key Takeaways

* Advanced RAG என்பது retrieve-then-generate அல்ல, understand-plan-retrieve-rerank-fuse-generate verify.
* Query complexity தான் design driver. Simple FAQ-க்கு basic RAG போதும், multi-hop & multi-source-க்கு advanced தேவை.
* Reranking மற்றும் context compression quality-க்கு மிக முக்கியம்.
* Every added stage adds latency & cost. Choose stages based on query criticality, not by default.
* Observability & citations must be first-class, not afterthought.
