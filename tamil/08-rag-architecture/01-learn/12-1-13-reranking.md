# Reranking

> **Learning Path:** RAG Architecture
> **Section:** 12.1.13 — Learn

## 1. Problem

RAG pipeline-ல் உங்களுக்கு ஒரு user query வருகிறது. `embedding` போட்டு `vector database`-ல் top-K documents எடுக்கிறீர்கள். 

அந்த top-K-ல் பல documents relevant அல்ல. ஏன்? `embedding similarity` என்பது semantic closeness-ஐ பிடிக்கும், ஆனால் query intent-ஐ துல்லியமாக புரிந்து கொள்ளாது.

உதாரணமாக, user கேட்கிறார்: "UPI payment fail ஆனால் refund எப்போது வரும்?" 
Vector search தரும் முதல் 10 results-ல் 3-4 results UPI basics, 2 results general payment failure, 1 result refund policy, ஆனால் தேவையான specific SLA document கீழே இருக்கும்.

LLM-க்கு நீங்கள் 10-15 low quality chunks கொடுத்தால், hallucination ஏற்படும், latency அதிகரிக்கும், context window waste ஆகும்.

**What goes wrong if we don't have this?** Relevant doc கிடைக்காமல் போகும். LLM bad answer தரும். User trust குறையும்.

## 2. Mental Model

Reranking என்பது **first pass recall → second pass precision** என்ற இரண்டு stage filter.

First stage: `vector search` = fast, recall oriented. Wide net வீசி பல candidates எடு.
Second stage: `reranker` = slow, precision oriented. Query + document pair-ஐ பார்த்து உண்மையில் relevant ஆனதை மேலே கொண்டு வா.

அது ஒரு smart filter. Embedding cosine similarity-க்கு பதிலாக, cross-attention மூலம் query intent vs document content-ஐ ஆழமாக ஒப்பிடுகிறது.

## 3. How It Works

1. **Retrieve**: Vector DB-ல் top-K' எடு. K' = 50-200. இது cheap.
2. **Rerank**: Cross-encoder model ஒன்று ஒவ்வொரு query-doc pair-க்கும் relevance score கொடுக்கும்.
   `score = reranker(query, document)`
3. **Select**: Top-K ஐ வைத்து LLM-க்கு கொடு. K = 5-10.

இங்கே cross-encoder என்பது query மற்றும் document-ஐ ஒன்றாக input-ஆக வாங்கி attention பண்ணும். Bi-encoder போல தனித்தனியாக encode செய்யாது. அதனால் துல்லியம் அதிகம், ஆனால் latency அதிகம்.

பெரிய scale-க்கு `late interaction` models like ColBERT பயன்படுத்தப்படுகிறது.

## 4. Architectural Reasoning

**When useful?**
* Query specific ஆக இருக்கும், documents long ஆக இருக்கும்.
* Hallucination cost high ஆன domain: finance, legal, healthcare.
* Recall-ல் தொலைந்து போன good documents இருக்கும் சூழல்.

**What constraint it addresses?** Precision at top. First stage recall-ஐ தக்க வைத்துக் கொண்டு, precision-ஐ உயர்த்த வேண்டும்.

**Alternatives:**
* Hybrid search: BM25 + Vector. Keyword match improve ஆகும், ஆனால் intent understanding limited.
* Larger K to LLM: LLM-ஐயே rerank செய்ய சொல்லலாம். Cost மற்றும் latency அதிகம்.
* Better embeddings: Fine-tune embeddings. Helpful, ஆனால் reranking-ஐ முழுவதும் replace செய்யாது.

Architect-ஆக நீங்கள் தேர்வு செய்யும் போது கேட்க வேண்டியது: Recall என்பது போதுமானதா? Top 5 precision தான் business impact-ஐ தீர்மானிக்கிறது.

## 5. Trade-offs

**Latency vs Quality:** Reranker ஒவ்வொரு pair-க்கும் inference பண்ண வேண்டும். 100 docs × 50ms = 5s. Batching, GPU, caching தேவை.

**Cost vs Accuracy:** Cross-encoder heavy. Per query cost அதிகரிக்கும். Production-ல் `small reranker` முதல் stage-ல் பயன்படுத்தி top 20 filter, பின்னர் large reranker.

**Freshness:** Reranker model static. New domain jargon வந்தால் performance drop ஆகும். Regular evaluation தேவை.

**Failure mode:** Reranker overfits to training distribution. Query-document length mismatch ஆனால் score skewed ஆகும். மேலும் reranker ஒரு black box. ஏன் doc ஐ தேர்ந்தெடுத்தது என்பதை explain செய்ய முடியாது.

## 6. Practical Example

Enterprise RAG for internal support KB.

Query: "Production-ல் payment service timeout ஆனால் retry policy என்ன?"

Vector search top 50-ல்: retry policy doc, timeout config doc, general resilience doc, incident postmortem, API spec.

Reranker query intent-ஐ பார்த்து "retry policy" + "payment service" + "timeout" keywords-ஐ document-ல் context-உடன் படிக்கும். உண்மையான retry policy doc-ஐ top 1-க்கு கொண்டு வரும், incident postmortem-ஐ கீழே தள்ளும்.

LLM இப்போது 8 high quality chunks மட்டும் பார்க்கிறது. Answer accurate ஆகும், latency கட்டுப்பாட்டில் இருக்கும்.

## 7. Reasoning Challenge

உங்களிடம் customer support RAG உள்ளது. 1000 RPS traffic. Vector search 30ms எடுக்கும். Cross-encoder reranker 40ms per doc.

உங்களால் top 100-ல் rerank செய்ய முடியாது. Latency budget 300ms.

இந்த constraint-ல் நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? K' எவ்வளவு வைப்பீர்கள்? Reranker size எப்படி choose பண்ணுவீர்கள்? ஏன்?

## 8. Key Takeaways

* Reranking = recall கெடுக்காமல் precision improve செய்யும் second stage.
* Embedding similarity fast ஆனால் shallow. Cross-attention deep ஆனால் slow.
* Top-K' wide retrieve, Top-K tight select என்பது standard pattern.
* Latency, cost, precision trade-off தான் architect-ஐ drive செய்கிறது, model accuracy அல்ல.
