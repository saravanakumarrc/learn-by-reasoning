# Retrieval degradation

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.2.3 — AI-specific monitoring

## 1. Problem

உங்கள் RAG system production-ல் நல்லா run ஆகுது. LLM answers correct ஆக இருந்தது. ஒரு வாரம் கழித்து, users சொல்றாங்க: "answers vague ஆகுது, hallucination அதிகமாகுது".

Model-ஐ மாற்றவில்லை. Prompt-ஐ மாற்றவில்லை. அப்புறம் என்ன?

Retrieval degrade ஆகி இருக்கும்.

Vector database-ல் data stale ஆகி இருக்கலாம். Embedding model drift ஆகி இருக்கலாம். Chunking strategy மோசமாகி இருக்கலாம். Index corruption. Query rewriting fail ஆகி இருக்கலாம்.

Classic monitoring-ல் API latency, error rate, throughput எல்லாம் green. ஆனால் AI quality கெட்டு போயிருக்கு. அதுதான் retrieval degradation.

> What goes wrong if we don't have this? Good retrieval இருந்தால்தான் LLM context-ல் சரியான information இருக்கும். Retrieval மோசமானால், LLM-க்கு தவறான context போகும். அது hallucination-ஐ உருவாக்கும்.

## 2. Mental Model

Retrieval degradation என்பது **retrieval quality silently குறைவது**. Latency spike போல் alert வராது.

ஒரு mental model:

`Query → Retrieval → Context → LLM → Answer`

நாம் பொதுவாக LLM மட்டும் monitor பண்ணுவோம். ஆனால் root cause பெரும்பாலும் Retrieval layer-ல் இருக்கும்.

Retrieval quality = relevance + freshness + coverage

இது காலப்போக்கில் மாறும். Data grows, distribution shifts, embeddings drift.

## 3. How It Works

Retrieval degrade ஆவதற்கு common reasons:

**1. Data freshness gap**
New documents add ஆகுது, ஆனால் vector index update fail ஆகி இருக்கு. அல்லது batch ingestion delay ஆகுது. User latest policy-க்கு கேட்டாலும் system old version-ஐ திருப்பி கொடுக்கும்.

**2. Embedding drift / model version mismatch**
Query embedding model-ஐ மாற்றினீங்க, ஆனால் index-ல் இருக்கும் vectors old model-ல் உருவாக்கப்பட்டது. அப்போ cosine similarity meaningless ஆகும்.

**3. Chunking / metadata drift**
Chunk size, overlap, metadata filters மாறினால் retrieval recall drop ஆகும். உதாரணமாக, filter by `tenant_id` சரியாக apply ஆகாமல் cross-tenant leakage வரும்.

**4. Query understanding degradation**
Query rewriting, reranker model performance degrade ஆகும். Prompt changes காரணமாக query vector poor quality.

**5. Index health**
Vector DB fragmentation, stale segments, corrupted shards. Recall மெதுவாக குறையும்.

இவை எல்லாம் traditional SLO-க்களை பாதிக்காது. P95 latency 80ms தான். Success rate 99.9% தான்.

## 4. Architectural Reasoning

Retrieval degradation-ஐ catch பண்ண, நாம் application metrics மட்டும் போதாது. AI-specific signals வேண்டும்.

**When useful:**
- RAG, agents, semantic search, recommendation systems
- Data frequently changes
- Multi-tenant, multi-dataset environment

**What to monitor:**
* Retrieval metrics: recall@k, precision@k, MRR. Offline golden queries set வைத்து daily run பண்ணுவது.
* Relevance score distribution: reranker scores, embedding similarity distribution drift.
* Freshness: last indexed timestamp per collection, lag between source DB and vector DB.
* Coverage: query vs no-result rate, fallback rate.
* Context quality: context-faithfulness proxy, citation presence.

Alternatives:
- Only log user complaints → too late
- Only monitor latency → misses quality
- Only A/B test LLM → blames model for retrieval problem

## 5. Trade-offs

**1. Offline golden set vs live evaluation**
Golden queries stable benchmark கொடுக்கும், ஆனால் real query distribution-ஐ capture பண்ணாது. Live evaluation real but noisy.

**2. Human annotation vs automatic metrics**
Human rating accurate ஆனால் expensive. Automatic metrics cheap ஆனால் proxy மட்டுமே.

**3. Monitoring cost vs signal quality**
Every query-க்கு embedding similarity, rerank scores store பண்ணுவது storage cost. Sampling பண்ணலாம், ஆனால் rare degradation miss ஆகும்.

**4. Alert sensitivity**
Too sensitive → alert fatigue. Too relaxed → degradation silent.

Failure mode: Retrieval degrade ஆனதை தெரிந்து கொண்டு, reindex பண்ணும்போது downtime / cost spike வரும். Blue-green index switch வேண்டும்.

## 6. Practical Example

Enterprise support RAG. Knowledge base daily update ஆகிறது.

நீங்கள் கண்காணிக்கிறீர்கள்:
- Golden 200 queries daily run. Recall@5 0.82 → 0.61 ஆக drop.
- Similarity score distribution mean 0.71 → 0.58 ஆக shift.
- No-result rate 3% → 18% ஆக increase.
- Last index timestamp 36 hours old.

இதுவும் API latency 70ms, error rate 0.1%.

Root cause: ingestion pipeline fail ஆனது, vector DB update நிறுத்தப்பட்டது. Fresh articles missing.

Decision: Index rebuild trigger, alert on freshness lag >4h.

## 7. Reasoning Challenge

உங்கள் system-ல் query volume 10x increase ஆகிறது. New tenant onboard ஆகிறது. Reranker latency spike ஆகிறது, அதனால் team reranker-ஐ bypass செய்து, direct embedding similarity மட்டும் use பண்ணுகிறது.

இரண்டு வாரம் கழித்து answer quality குறைகிறது. 

இது retrieval degradation-வா? இல்லையா? எந்த metric-ஐ முதலில் பார்ப்பீர்கள்? Trade-off என்ன?

## 8. Key Takeaways

* Retrieval quality degrade ஆகும், latency degrade ஆகாது. AI observability-க்கு quality signals தேவை.
* Monitor freshness, relevance distribution, recall on golden set, coverage.
* Embedding model version consistency between index and query time மிக முக்கியம்.
* Every retrieval change creates a trade-off between relevance, latency, cost, freshness.
