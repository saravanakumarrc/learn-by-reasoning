# Query rewriting

> **Learning Path:** RAG Architecture
> **Section:** 12.1.14 — Learn

## 1. Problem

உங்க RAG system-ல user கேட்கிறார்: *"நேற்று மும்பைக்கு போன ஃப்ளைட் டிலே ஆனதா?"*

Retriever-க்கு போகிற query direct-ஆ அப்படியே போனால் என்ன ஆகும்?
Vector database-ல உங்க documents இருக்கு: "Flight AI-203 delayed by 2 hours due to weather on 2025-10-18", "Mumbai arrival log", "airline status update".

User-ன் natural language query-ன் embedding, document embedding-ன் meaning-க்கு match ஆகுமா? பெரும்பாலும் partial-ஆ தான் match ஆகும். Synonyms, context missing, implicit info இருக்கு. 

Result: retriever relevant chunks-ஐ miss பண்ணும். LLM-க்கு போகும் context weak ஆகும். Answer hallucination or "I don't know" வரும்.

இதுதான் painful problem. Query-ன் intent தெளிவில்லை. Retriever-க்கு தேவையான terms இல்லை.

## 2. Mental Model

Query rewriting என்பது user-ன் original query-ஐ, retrieval-க்கு சிறப்பாக வேலை செய்யும் வடிவத்திற்கு மாற்றுவது.

ஒரு translator போல. User speaks colloquial Tamil/English. Retriever speaks document language.

Rewriter ஒரு intermediate layer. It expands, clarifies, decomposes user intent into retrieval-friendly queries.

உதாரணமாக: *"நேற்று மும்பை ஃப்ளைட் டிலே?"* → 
1. "Mumbai flight delay 2025-10-19"
2. "Flight arrival delay Mumbai yesterday"
3. "AI-203 Mumbai delay status"

ஒரே user intent, பல retrieval queries.

## 3. How It Works

Simple flow:

**User Query → Query Rewriter [LLM] → Multiple rewritten queries → Retriever → Merge results → LLM answer**

Rewriter-ன் job:

* **Clarify implicit info**: "நேற்று" → 2025-10-19. "ஃப்ளைட்" → flight number, airline?
* **Expand synonyms**: delay = late, postponed, rescheduled
* **Decompose complex query**: "மும்பைக்கு போன ஃப்ளைட் டிலே ஆனதா, காரணம் என்ன?" → Query A: delay fact. Query B: delay reason.
* **Add domain terms**: user "பணம்" சொன்னால், documents-ல "refund, chargeback" இருக்கலாம்.

Implementation-ல mostly LLM with prompt:

> Rewrite the user query to be more specific for retrieval. Keep intent same. Return 3-5 variations.

Some systems use hybrid: LLM rewrite + keyword expansion via embeddings.

## 4. Architectural Reasoning

Query rewriting useful ஆகும் when:

* User queries are short, vague, conversational
* Domain vocabulary mismatch உள்ளது. User says "ஃப்ளைட் லேட்", docs say "flight delay"
* Multi-intent queries: user ஒரே தடவையில் 2-3 விஷயம் கேட்கிறார்
* Retrieval recall low ஆக இருக்கிறது. Metrics show good relevant docs exist but not retrieved

Alternatives:

* **Query expansion without LLM**: synonyms from thesaurus. Cheap but dumb.
* **Hybrid retrieval**: BM25 + vector. Helps but doesn't fix intent ambiguity.
* **Better embeddings**: Helps but can't fix missing context like date.

ஏன் architect choose பண்ணுவார்? Because retrieval recall improve ஆகும், with minimal change to index. It's a pre-retrieval technique.

Cost: extra LLM call per query.

## 5. Trade-offs

* **Recall vs Precision vs Latency**: Rewriting improves recall, but you get more noisy results. Merge/dedupe தேவை. Latency increase ஆகும், because 1 LLM call + N retrievals.
* **Cost**: Every query needs rewriter LLM call. High traffic system-ல cost add ஆகும். Caching rewritten patterns helps.
* **Over-rewriting risk**: LLM hallucinate new info. "நேற்று" ஐ தப்பா date மாற்றி விடலாம். Rewriter should not invent constraints.
* **Complexity**: Need to handle failure mode. Rewriter fails → fallback to original query.

Failure mode: Rewriter creates overly specific queries that miss broader relevant docs. Or generates 5 queries, retriever returns duplicate chunks, context window overflow ஆகும்.

## 6. Practical Example

Enterprise support RAG. User asks: *"கடந்த வாரம் என் ஆர்டர் ஏன் வரல?"*

Original query retrieval poor. Rewriter produces:

1. "order not delivered last week status"
2. "order delivery delay reason 2025-10-10 to 2025-10-16"
3. "order tracking status pending delivery"

Retriever now hits delivery logs, support tickets, SLA docs. LLM gets proper context and answers: "Your order #4521 was delayed due to courier strike in Chennai, now rescheduled to 2025-10-21."

Without rewrite, system would return generic order FAQs.

## 7. Reasoning Challenge

உங்களிடம் RAG chatbot உள்ளது. Financial documents corpus. User கேட்கிறார்: *"Q2-ல் revenue குறைந்ததற்கு காரணம்?"*

Rewriter 3 queries generate பண்ணும். ஒரு query-ல "Q2" ஐ 2024 Q2 ஆக assume பண்ணிடும், உண்மையில் user 2025 Q2 பற்றி கேட்கிறார்.

இந்த scenario-ல நீங்கள் என்ன safeguard போடுவீர்கள்? Rewrite-ஐ எப்படி control பண்ணுவீர்கள்? Original query-ஐ preserve பண்ண வேண்டுமா?

## 8. Key Takeaways

* Query rewriting solves vocabulary gap and intent ambiguity, not embedding quality problem.
* It improves recall by generating retrieval-friendly variants before search.
* Trade-off is latency, cost, and risk of hallucination in rewritten queries.
* Use it when queries are vague/conversational and retrieval metrics show recall gap.
* Always keep original query as fallback, and validate rewritten queries don't invent facts.
