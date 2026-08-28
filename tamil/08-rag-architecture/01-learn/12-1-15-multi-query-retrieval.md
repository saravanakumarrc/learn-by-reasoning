# Multi-query retrieval

> **Learning Path:** RAG Architecture
> **Section:** 12.1.15 — Learn

## 1. Problem

ஒரு RAG system-ல user query வருகிறது. நீங்கள் அதை vector database-ல search செய்கிறீர்கள். Top-k results கிடைக்கின்றன. ஆனால் பல சமயம் answer incomplete ஆக இருக்கிறது.

ஏன்? ஒரு user question என்பது பல intentions கொண்டது. ஒரே query-ல் ஒரு concept-ஐ முழுமையாக capture செய்ய முடியாது. Embedding model-கள் query-ன் wording-க்கு sensitive.

உதாரணம்: "எங்கள் payment system-ல latency எப்படி reduce பண்ணுவது?"

இந்த query vector search-ல் "latency reduction techniques" மட்டும் கண்டுபிடிக்கும். ஆனால் பின்னால் உள்ள sub-intentions:
* latency root cause என்ன?
* database optimization options என்ன?
* caching strategy எப்படி?
* distributed system-ல network latency?

ஒரே embedding-ல் இவை எல்லாம் capture ஆகாது. ஒரு narrow retrieval ஆகி, relevant documents miss ஆகின்றன. இதுதான் painful problem.

## 2. Mental Model

Multi-query retrieval என்பது **ஒரு user question-ஐ பல different angles-ல் rephrase செய்து, ஒவ்வொரு rephrase-க்கும் தனித்தனியாக retrieve செய்து, results-ஐ merge செய்வது**.

ஒரு detective ஒரு case-ஐ ஒரு angle-ல் மட்டும் விசாரிக்காமல், multiple questions கேட்டு விசாரிப்பது போல.

Original query = ஒரு lens. Multi-query = multiple lenses.

## 3. How It Works

பொதுவாக 3 வழிகள் உள்ளன:

**1. LLM-based paraphrasing**
Original query-ஐ LLM-க்கு கொடுத்து, 3-5 semantically similar variants generate செய்யச் சொல்லுங்கள்.
`Q -> Q1, Q2, Q3... -> embed each -> retrieve -> deduplicate`

**2. Decomposition**
Complex query-ஐ sub-questions ஆக பிரிக்கிறோம்.
`Why is payment latency high? -> What is DB query latency? What is network latency? What is cache hit rate?`

**3. Query expansion with keywords**
User intent-ல் இருந்து related technical terms add செய்வது.

Practical flow:
```
User query -> LLM generates 4-6 variants -> Parallel vector search -> Candidate set union -> Re-rank by original query similarity -> Top-k to LLM
```

Implementation lightweight ஆக இருக்கும். Retrieval step மட்டும் replicate ஆகிறது. No change to vector DB.

## 4. Architectural Reasoning

இது எப்போது useful?

* Query ambiguous or broad ஆக இருக்கும்போது
* Domain-specific jargon வேறுபடும்போது: "latency" vs "response time" vs "TAT"
* High recall தேவைப்படும் RAG, பின்னர் LLM filter செய்யும்
* User question-க்கு multiple documents தேவைப்படும் synthesis

Constraint-ஐ address செய்கிறது: **single embedding-ன் limited coverage**.

Alternatives:
* **HyDE - Hypothetical Document Embedding**: Query-க்கு hypothetical answer generate செய்து அதை embed செய்வது
* **Re-ranking**: ஒரே retrieval-க்கு பிறகு cross-encoder-ல் re-rank
* **Query rewriting**: Just one better reformulation

Multi-query vs HyDE: Multi-query recall-ஐ அதிகரிக்கிறது. HyDE relevance-ஐ அதிகரிக்கிறது. பல systems இரண்டையும் combine செய்கின்றன.

Architect ஏன் தேர்வு செய்வார்? Cost vs recall trade-off accept செய்ய முடியுமா? Retrieval latency பிரச்சனை அல்லவா? என்பதை பார்ப்பார்.

## 5. Trade-offs

**Recall vs Precision vs Cost**
More queries = more candidates = better recall. ஆனால் noise increase ஆகும். Precision குறையும். LLM calls cost + latency increase ஆகும். 1 query -> 5 queries = 5x embedding + 5x vector search.

**Latency**
Parallel search செய்தாலும், network roundtrip increase. 5 queries = 5 vector DB calls. Timeout, rate limit handling தேவை.

**Deduplication complexity**
Same document 5 variants-லும் வரும். Merge logic தேவை. Score normalization important.

**Over-retrieval risk**
Too broad variants irrelevant documents pull செய்யும். LLM context window waste ஆகும்.

Failure mode: LLM generate செய்யும் variants off-topic ஆகிவிட்டால் retrieval quality drop ஆகும். Prompt quality critical.

## 6. Practical Example

Enterprise support RAG: Employee query "Production API error 503 வருகிறது, என்ன செய்ய?"

Single retrieval: "503 Service Unavailable" documents மட்டும் கிடைக்கும்.

Multi-query variants:
1. Production API 503 error troubleshooting steps
2. Service Unavailable cause and fix in Kubernetes
3. API gateway 503 error due to backend overload
4. How to check pod readiness and liveness probes failure

Retrieval-ல் troubleshooting guide, K8s docs, gateway config, monitoring playbook எல்லாம் கிடைக்கும்.

LLM இவை அனைத்தையும் பார்த்து, synthesized answer கொடுக்கிறது: check pod status, check HPA, check ingress, check backend logs.

## 7. Reasoning Challenge

உங்கள் RAG system-ல் average query latency 300ms. Vector DB call 50ms. LLM generation for query expansion 400ms. நீங்கள் 4 variants generate செய்ய விரும்புகிறீர்கள்.

Total latency எப்படி குறைப்பீர்கள்? Multi-query-ஐ எப்போது synchronous ஆக செய்வது, எப்போது async pre-compute செய்வது?

Cost budget limited. 10k queries/day. ஒவ்வொரு extra LLM call $0.001. Trade-off என்ன?

## 8. Key Takeaways

* Single query embedding limited coverage தரும். Multi-query recall-ஐ அதிகரிக்கிறது.
* Variants generate செய்வது cheap architecture trick, but cost and latency trade-off உண்டு.
* Retrieve பின் deduplicate + re-rank செய்யாமல் multi-query value குறையும்.
* Query complexity high ஆனால் recall critical ஆன RAG-ல் மட்டும் use செய்யுங்கள்.
