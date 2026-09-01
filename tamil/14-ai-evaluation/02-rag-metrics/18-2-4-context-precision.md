# Context precision

> **Learning Path:** AI Evaluation
> **Section:** 18.2.4 — RAG metrics

## 1. Problem

RAG system-ல LLM-க்கு நீங்கள் context கொடுக்கிறீர்கள். Retrieval சரியாக வேலை செய்தாலும், retrieved chunks-ல் தேவையற்ற, irrelevant, அல்லது misleading information இருந்தால் என்ன ஆகும்?

LLM அதை படித்து hallucinate பண்ணும், wrong answer தரும், அல்லது correct answer-ஐ override பண்ணும். 

நீங்கள் 10 documents retrieve பண்ணி 4k tokens context போடுகிறீர்கள். User கேள்விக்கு தேவை 2 sentences மட்டுமே. மீதி noise. 

அந்த noise-தான் context precision-ஐ குறைக்கிறது.

> What goes wrong if we don't have this? Retrieval recall high ஆக இருக்கும், ஆனால் answer quality குறையும்.

## 2. Mental Model

Context precision = Retrieved context-ல் உள்ள information எவ்வளவு உண்மையில் relevant ஆக இருக்கிறது.

ஒரு search result list-ல் top results தொடர்புடையதா இல்லையா என்பதை நீங்கள் check பண்ணுவது போல.

Precision என்பது **quality over quantity**. Recall என்பது "தேவையானதை எல்லாம் கண்டுபிடித்தோமா?" என்பது. Precision என்பது "கண்டுபிடித்ததில் எவ்வளவு தேவையற்றது?"

Mental model: Funnel.
User query → Retrieve 100 chunks → Top K → Context window → LLM answer.

Precision என்பது Top K-ல் எத்தனை chunks உண்மையில் query-க்கு useful.

## 3. How It Works

Context precision-ஐ measure பண்ண, ஒரு query-க்கு ground truth relevant documents set தேவை.

சாதாரணமாக:
1. Query கொடுக்கப்படுகிறது.
2. RAG system K chunks retrieve செய்கிறது.
3. ஒவ்வொரு retrieved chunk-உம் relevant / not relevant என human அல்லது LLM judge மூலம் label செய்யப்படுகிறது.
4. 

Precision@K = Number of relevant chunks in top K / K

எ.கா: K=10, relevant chunks=3 → Precision@10 = 0.3

முக்கியமானது: இது retrieval quality-யை மட்டும் பார்க்காது. Reranking, chunking strategy, hybrid search எல்லாம் இதில் reflect ஆகும்.

## 4. Architectural Reasoning

Context precision எப்போது முக்கியம்?

* LLM context window limited. Noise அதிகம் என்றால் good information கூட பார்க்க முடியாது.
* Agent workflows-ல் multi-step reasoning. தவறான context ஒரு step-ல் error cascade ஆகும்.
* High-stakes domains: finance, legal, medical. Irrelevant citation = trust loss.

Architect எப்போது precision-ஐ prioritize செய்வார்?

* Query specific, factual. தேவை சில exact facts.
* Context budget tight. Small window, large model cost.

Alternatives:
* **Recall focused retrieval**: K அதிகம், பிறகு LLM filter செய்யும் என்று நம்புவது. Cost அதிகம், noise அதிகம்.
* **Aggressive reranking**: Cross-encoder reranker பயன்படுத்தி top K-ஐ சுருக்குதல். Latency + compute trade-off.
* **Query decomposition**: Query-ஐ sub-queries ஆக break செய்து precise retrieval.

Decision: Precision vs Recall trade-off system requirement-ஐ பொறுத்தது.

## 5. Trade-offs

**Precision vs Recall**: Precision அதிகப்படுத்த precision-focused retrieval பயன்படுத்தினால், recall குறையலாம். முக்கியமான but hard-to-find chunk miss ஆகும்.

**Precision vs Latency**: Better precision க்கு cross-encoder reranking, query expansion, hybrid search தேவை. Latency + cost அதிகரிக்கும்.

**Precision vs Coverage**: Very strict filtering செய்தால் context too small ஆகும். LLM-க்கு reasoning-க்கு தேவையான background கிடைக்காது.

Failure mode: High precision, low recall system-ல் user "I don't know" என்று சொல்லும். User experience மோசம்.

Another failure: Precision metric-ஐ optimize செய்யும் போது chunk size-ஐ குறைக்கலாம். Precision மேலே போகும், ஆனால் chunk boundary-ல் meaning break ஆகும்.

## 6. Practical Example

Enterprise RAG for internal policy.

User query: "WFH policy-ல் laptop insurance யார் cover செய்கிறார்கள்?"

System retrieve 10 chunks:
* 3 chunks = actual IT policy about laptop insurance
* 4 chunks = general WFH policy, remote work guidelines
* 2 chunks = old 2021 policy, already deprecated
* 1 chunk = unrelated finance expense

Precision@10 = 3/10 = 0.3

Architect decision: Reranker + metadata filter by `policy_version = current`, `doc_type = official`. K=5 ஆக குறைக்கிறார்.

After rerank: Top 5-ல் 4 relevant. Precision@5 = 0.8

Cost: Reranker adds 150ms latency per query. Acceptable for internal tool.

## 7. Reasoning Challenge

உங்களிடம் customer support RAG system உள்ளது. 2 வகை queries வருகிறது:
1. "Refund policy என்ன?" - broad, multiple documents தேவை.
2. "Order #12345 refund status?" - specific, 1 document போதும்.

Precision@10 எப்போதும் 0.4 மட்டுமே. Recall@10 0.9 இருக்கிறது.

நீங்கள் system-ஐ மாற்ற வேண்டும். Precision-ஐ மேம்படுத்துவதா, அல்லது recall-ஐ தக்க வைத்து context filtering-ஐ LLM-க்கு ஒப்படைப்பதா? எந்த query type-க்கு எது சரியானது? ஏன்?

## 8. Key Takeaways

* Context precision = Retrieved set-ல் எவ்வளவு noise இருக்கிறது என்பதன் அளவீடு. Quality over quantity.
* High precision குறைந்த context window, high-stakes factual answers-க்கு முக்கியம்.
* Precision மேம்படுத்த reranking, metadata filtering, smaller K உதவும், ஆனால் recall மற்றும் latency-ஐ பாதிக்கும்.
* Recall இல்லாமல் precision-க்கு மட்டும் முக்கியத்துவம் கொடுத்தால், system "I don't know" என்று சொல்லும்.
