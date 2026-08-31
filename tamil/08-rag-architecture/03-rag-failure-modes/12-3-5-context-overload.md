# Context overload

> **Learning Path:** RAG Architecture
> **Section:** 12.3.5 — RAG failure modes

## 1. Problem

உங்கள் RAG system ரொம்ப நல்லா work பண்ணுது. Query வருது, retriever சரியா chunks-ஐ கொண்டு வருது, LLM answer கொடுக்குது.

பிறகு ஒரு நாள் user கேட்கிறார்: "எங்கள் கடந்த 2 வருட sales report, அதுல வந்த top 10 customers, அவர்களோட recent support tickets, product returns pattern எல்லாம் சொல்லு."

Retriever 40 chunks திருப்பி கொடுக்குது. ஒவ்வொன்றும் 800-1200 tokens. Total 35k tokens.

LLM-க்கு prompt-ல system instruction + query + 35k context = 37k tokens. Model limit 128k என்றாலும், இங்கே என்ன நடக்கும்?

Answer generic ஆகிவிடும். Hallucination அதிகரிக்கும். Relevant facts miss ஆகும். Latency 8 sec → 30 sec ஆகும். Cost 3x ஆகும்.

இது தான் **context overload**.

What goes wrong if we don't have this? Retriever "more is better" என்று நினைக்கும். LLM-ன் attention spread ஆகும். Signal-ல noise கலந்துவிடும்.

## 2. Mental Model

LLM ஒரு reader மாதிரி. அவனுக்கு ஒரே நேரத்தில் 100 பக்கங்களை கொடுத்து "இதுல முக்கியமானது சொல்லு" என்றால், அவன் confuse ஆகுவான்.

Context window என்பது capacity, attention budget. Token அதிகமானால், important facts-ன் weight குறையும்.

Context overload = **Too much retrieved information, too little focus**.

## 3. How It Works

RAG-ல் overload வரும் 3 இடங்களில்:

**Retriever greediness:** Top-K = 20 என்று வைத்துவிட்டால், relevance 0.4 இருக்கும் chunk கூட வந்துவிடும்.

**Chunk size too big:** 2000 token chunk-ஐ retrieve செய்தால், ஒரே chunk-ல் query-க்கு தேவையில்லாத 1800 tokens வந்துவிடும்.

**Multi-hop accumulation:** Agent 3 steps போகும். Step 1-ல் 10 chunks, Step 2-ல் 10 chunks, Step 3-ல் 10 chunks. அனைத்தையும் history-யுடன் அனுப்பினால் context snowball ஆகும்.

Result: LLM prompt-ல் முக்கியமான sentence-கள் dilute ஆகும். Model "summary mode"-க்கு போகும். Precision குறையும்.

## 4. Architectural Reasoning

Context overload-ஐ தடுக்க வேண்டும் என்றால், retrieve செய்வதை குறைக்க வேண்டும் என்று அர்த்தமில்லை. **Focus செய்ய வேண்டும்**.

Options:

* **Re-ranking:** BM25/embedding cosine score மட்டும் போதாது. Cross-encoder-ஆல் top-K-ல் இருந்து top-5 தேர்வு. Query relevance-க்கு படி.

* **Compression / Summarization:** Retrieved chunks-ஐ LLM-ஆல் compress செய். 800 token chunk → 120 token summary. Rerun with condensed context.

* **Context window budgeting:** Max tokens per query set செய். Example: 8k for context. Retriever 12k retrieve செய்தாலும், budget-க்கு fit ஆக trim செய்.

* **Query decomposition:** Complex query-ஐ sub-queries-ஆக split செய். "sales report + top customers" என்பது 2 independent retrieval. Results merge செய்.

* **Hybrid retrieval with filters:** Metadata filters போட்டு irrelevant domain-ஐ கழி. Time range, document type filter செய்.

Architect எப்போது choose பண்ணுவார்? 
Retrieval latency முக்கியம், cost குறைவாக வேண்டும், answer precision > recall என்றால் compression + rerank.

## 5. Trade-offs

* **Recall vs Precision:** K குறைத்தால் precision அதிகரிக்கும், ஆனால் நீங்கள் தேவையான fact-ஐ miss செய்யலாம். Trade-off தெளிவாக தெரிய வேண்டும்.

* **Compression quality:** Summarizer தவறாக compress செய்தால் nuance, numbers போய்விடும். Financial data-க்கு risky.

* **Latency vs Quality:** Rerank + compression = extra LLM calls. P99 latency 2x ஆகலாம்.

* **Operability:** Context size dynamic. Monitoring வேண்டும்: tokens per query, retrieved chunks count, compression ratio, answer faithfulness score.

Failure mode: Over-aggressive filtering. User "summarize everything" என்று கேட்டால், நீங்கள் top-3 மட்டும் கொடுத்தால் answer incomplete.

## 6. Practical Example

Enterprise support RAG. Knowledge base = 500k support tickets.

User query: "Order #12345 delay ஆக காரணம் என்ன? Similar orders-க்கு என்ன resolution?"

Naive flow: Retriever top-30 chunks. 30 x 1000 = 30k tokens. LLM confused, returns generic shipping policy.

Better flow:
1. Metadata filter: order_id = 12345, created_at last 90 days.
2. Retrieve top 10, rerank cross-encoder → top 5.
3. If query contains "similar", do second retrieval with vector similarity on issue type.
4. Budget: 5 chunks * 1000 = 5k + 1k summary of similar = 6k.
5. Prompt-ல்: <context> limited, explicit instruction: "Only use provided facts, cite chunk id".

Result: Latency 3s, cost 40% down, answer accurate with citation.

## 7. Reasoning Challenge

உங்கள் RAG system-ல் average query 15 chunks retrieve செய்கிறது. 70% queries-க்கு 3 chunks மட்டும் போதும். ஆனால் 10% queries complex multi-hop. 

நீங்கள் ஒரே context budget எல்லா queries-க்கும் பயன்படுத்த வேண்டுமா? அல்லது dynamic budget வைக்கலாமா? Dynamic என்றால் எப்படி detect செய்வீர்கள்? Trade-off என்ன?

## 8. Key Takeaways

* More context ≠ better answer. Attention dilutes.
* Context overload ஆனது retrieve greediness + large chunks + multi-hop accumulation-ல் வரும்.
* Solution is focus, not just reduce: rerank, compress, budget, decompose.
* Monitor tokens per query, precision-recall curve, faithfulness.
* Every reduction in context introduces risk of missing critical fact.
