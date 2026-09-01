# Context relevance

> **Learning Path:** AI Evaluation
> **Section:** 18.2.3 — RAG metrics

## 1. Problem

உங்களுக்கு ஒரு RAG system இருக்கு. LLM + vector database + retrieval pipeline. Demo-ல நல்லா வேலை செய்யுது. Production-க்கு போனதும் user கேள்வி கேட்டா தேவையில்லாத document-ஐ திருப்பி கொடுக்குது. சில சமயம் சரியான doc-ஐயும் கொண்டு வருது, ஆனால் LLM அதை புரிஞ்சுக்காம ஹாலூசினேட் பண்ணுது.

இப்போ கேள்வி: System நல்லா இருக்கா, மோசமா இருக்கா என்பதை எப்படி தெரிஞ்சுக்கறது?

Accuracy மட்டும் பார்த்தா போதாது. Retrieval சரியா இருக்கா? Generation grounded-ஆ இருக்கா? Latency எவ்ளோ? Cost எவ்ளோ? 

இந்த pain தான் RAG metrics-ஐ உருவாக்கியது. System-ஐ measure பண்ணி, improve பண்ணி, regress ஆகாம பார்க்க.

## 2. Mental Model

RAG-ல மூன்று layer இருக்கு:

1. **Retrieval** - சரியான chunks-ஐ கண்டுபிடிச்சதா?
2. **Generation** - LLM அந்த chunks-ஐ use பண்ணி சரியான, grounded answer கொடுத்ததா?
3. **End-to-end UX** - User-க்கு useful, fast, safe answer கிடைச்சதா?

ஒவ்வொரு layer-க்கும் வெவ்வேறு metric வேணும். ஒரே metric-ஆல் முழு system-ஐ மதிப்பிட முடியாது.

## 3. How It Works

Metrics-ஐ இரண்டு வகையா பிரிக்கலாம்.

**Offline, reference-based metrics**: உங்களுக்கு ground truth answer தெரியும்.
- Retrieval: Recall@k, Precision@k, MRR
  உதாரணமா, user query-க்கு 5 relevant documents இருக்கு. நீங்க top-5-ல 3-ஐ கொண்டு வந்தா Recall@5 = 3/5.
- Generation: Faithfulness, Answer Relevancy
  LLM answer-ல சொன்னது retrieved context-ல இருக்கா? Context-ல இருக்காததை சேர்த்துட்டதா?

**Online, reference-free metrics**: Real user queries-க்கு ground truth இல்லை.
- Retrieval latency, retrieval recall proxy
- Generation latency, tokens per query, cost per query
- User signals: click, follow-up question, thumbs up/down, conversation abandonment

Practically, நீங்க இரண்டையும் கலந்து use பண்ணுவீங்க.

## 4. Architectural Reasoning

எப்போ இந்த metrics தேவை?

- **Retrieval tuning** பண்ணும்போது: embedding model மாற்றினீங்க, chunk size மாற்றினீங்க, reranker add பண்ணினீங்க. Recall@k மாறுதா?
- **Prompt change** பண்ணும்போது: Faithfulness குறையுதா?
- **Production monitor** பண்ணும்போது: Latency spike ஆகுதா? Hallucination rate அதிகரிக்குதா?

Alternatives: Blind A/B testing only. அது slow, expensive. Metrics கொடுக்கும் early signal.

அரசியல் முடிவு: நீங்க business goal-ஐ align பண்ணி metrics-ஐ தேர்வு பண்ணணும்.

Financial RAG system-க்கு faithfulness > latency. Consumer chatbot-க்கு latency + relevancy > perfect recall.

## 5. Trade-offs

**Recall vs Precision vs Latency**
Top-k அதிகரித்தா recall ஏறும், ஆனால் LLM context window நிரம்பும், latency & cost ஏறும். Precision குறையும்.

**Reference-based vs Reference-free**
Reference-based metrics accurate ஆனா, உருவாக்க expensive. Real user queries-க்கு ground truth இல்லை. Reference-free cheap ஆனா noisy.

**Faithfulness vs Answer Relevancy**
Faithfulness = answer context-ஐ follow பண்ணுதா. Answer Relevancy = user question-க்கு பதில் பொருத்தமா இருக்கா. ஒன்னு மட்டும் high ஆனால் போதாது. Context-ல இருக்கும் முக்கியமில்லாத info-ஐ நகல் பண்ணி faithfulness high வரும், ஆனால் relevancy low இருக்கும்.

Failure mode: Metrics gaming. System metrics-ஐ மேம்படுத்த, real quality குறையலாம். எடுத்துக்காட்டு: Reranker-ஐ மட்டும் overfit பண்ணி Recall@10 அதிகரிக்க, but end-to-end response slower and less useful.

## 6. Practical Example

Enterprise support RAG. Knowledge base = 200k support articles.

Goal: First response helpful, no hallucination.

Metrics setup:
- Offline: 500 real tickets with human-annotated relevant chunks. Track Recall@5, Recall@10. Target Recall@5 > 0.7.
- Faithfulness via LLM-as-judge: Generated answer-ல உள்ள ஒவ்வொரு claim-ஐ context-ல verify பண்ணு. Target > 0.85.
- Online: p95 retrieval latency < 200ms, p95 end-to-end < 2s. Cost per query < $0.02. Thumbs up rate > 40%.

Deploy reranker. Recall@5 0.65-ல இருந்து 0.78-க்கு ஏறும். ஆனால் latency 150ms -> 420ms. Cost +18%. Thumbs up rate மாறாமல் இருக்கு.

Decision: Reranker-ஐ async-ஆ run பண்ணி top-10-ல இருந்து top-5 தேர்வு செய், or cheaper reranker model use பண்ணு. Trade-off clear.

## 7. Reasoning Challenge

உங்களிடம் RAG system இருக்கு. Retrieval Recall@10 0.9. ஆனால் production-ல users keep asking follow-up questions for clarification, thumbs down rate high.

இங்கே என்ன metric missing? Retrieval மட்டும் போதாது. Generation-ல என்ன பார்க்கணும்? Retrieval quality-ஐ improve பண்ணினாலும் user satisfaction ஏறாதா? ஏன்?

## 8. Key Takeaways

* RAG-ஐ மூன்று layer-ஆ பிரித்து மதிப்பிடு: Retrieval, Generation, End-to-end UX.
* Offline reference metrics வேகமான iteration-க்கு, online user signals உண்மையான quality-க்கு.
* ஒரே metric-ஆல் optimize பண்ணாதே. Recall, faithfulness, latency, cost ஒன்னுக்கொன்னு trade-off.
* Metrics என்பது architectural decision-ஐ justify பண்ணும் tool. System-ஐ build பண்ணும் guide.
