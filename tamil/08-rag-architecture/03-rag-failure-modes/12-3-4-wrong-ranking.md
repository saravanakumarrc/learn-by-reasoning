# Wrong ranking

> **Learning Path:** RAG Architecture
> **Section:** 12.3.4 — RAG failure modes

## 1. Problem

RAG system-ல user கேள்வி கேட்டா, LLM-க்கு relevant context கொடுத்து பதில் generate பண்றோம். ஆனா சில சமயம் பதில் technically correct-ஆ இருக்கும், ஆனா context-ல இருந்து தப்பா ரேங்க் ஆன documents வந்துடும்.

உதாரணமா, user கேட்கிறார்: *"நம்ம subscription plan-ல free tier-க்கு API rate limit என்ன?"*

Retriever 3 documents திரும்ப கொடுத்தது:
1. Free tier rate limit = 100/day
2. Pro tier pricing page
3. Free tier rate limit = 1000/day

இதுல 3-ம் document பழையது. ஆனா embedding similarity அதிகமா இருந்ததால அது top-1-ல வந்துடுச்சு. LLM அதை நம்பி பதில் கொடுத்துடும்.

Wrong ranking என்பது இது தான்: **relevant ஆன document கிடைக்காம போகல, தவறான document முதல்ல வந்துடுச்சு.**

இதனால என்ன ஆகும்? Hallucination இல்ல, ஆனா **grounding failure**. User-க்கு தப்பான தகவல் போகும். Business impact ஆகும். Trust போகும்.

## 2. Mental Model

Retriever-ன் வேலை = query-க்கு பொருத்தமான chunks-ஐ கண்டுபிடித்து, **சரியான order-ல** LLM-க்கு கொடுப்பது.

Ranking தப்பு ஆனால், LLM ரொம்ப smart ஆனாலும் அதுக்கு கொடுத்த context தான் உண்மை. Garbage in, garbage out.

Vector similarity மட்டும் போதாது. Semantic similarity ≠ relevance.

## 3. How It Works

RAG pipeline-ல ranking எப்படி நடக்குது?

`Query embedding → Vector DB similarity search → Top-K chunks → Re-rank / Filter → LLM`

Wrong ranking பெரும்பாலும் இங்கே நடக்கும்:

* **Embedding limitation:** query "rate limit free tier" என்பதற்கு, பழைய document-ல "free tier" மற்றும் "rate limit" words இருக்கு, அதனால cosine similarity high. ஆனா அது deprecated.
* **Chunking artifact:** ஒரு document-ல முக்கியமான sentence தனியா chunk ஆகி, context இல்லாம போயிடும். அந்த chunk standalone-ஆ query-க்கு match ஆகும்.
* **No recency / authority signal:** Vector DB similarity மட்டும் பார்க்கும். Created date, source trust, version எல்லாம் பார்க்காது.
* **Duplicate/conflicting info:** Same topic-ல பல versions இருக்கும். Retriever அதை differentiate பண்ண மாட்டும்.

## 4. Architectural Reasoning

Wrong ranking எப்போ painful ஆகும்?

* **Enterprise knowledge base:** Policies மாறிக்கொண்டே இருக்கும். Old version இன்னும் index-ல இருக்கும்.
* **Financial / compliance data:** தப்பான எண் கொடுத்தால் சட்ட பிரச்சனை.
* **Multi-source RAG:** Wiki, docs, support tickets எல்லாம் ஒன்னா இருக்கும். Source authority வேறுபடும்.

Alternatives / Mitigations:

* **Hybrid search:** Vector similarity + BM25 keyword search. Keyword exact match ranking-ஐ சரி பண்ணும்.
* **Re-ranker model:** Cross-encoder போன்ற model query vs chunk ஐ பார்த்து fine-grained relevance score கொடுக்கும். Cost அதிகம், latency அதிகம்.
* **Metadata filtering:** Recency, source type, document version, region filter போடுவது. Query time-ல filter.
* **Contextual compression & deduplication:** Same topic-ல conflicting chunks-ஐ கண்டுபிடித்து merge / prefer latest.

Architect ஆக நீங்கள் தேர்வு செய்ய வேண்டியது: **Accuracy vs latency vs cost**.

## 5. Trade-offs

* **Vector only vs Hybrid:** Vector மட்டும் fast ஆனா semantic drift வரும். Hybrid accurate ஆனா pipeline complex.
* **Re-ranker:** Ranking quality கணிசமா மேம்படும். ஆனா per query 100-200ms கூடும், cost per query அதிகரிக்கும்.
* **Metadata filtering:** Recency signal சேர்ப்பது easy, ஆனா filter too strict ஆனால் recall குறையும். Relevant document விட்டுபோகும்.
* **More context vs less context:** Top-K அதிகமா கொடுத்தால் wrong ranked document-ன் தாக்கம் குறையும், ஆனா LLM context window, noise அதிகரிக்கும்.

Failure mode: Re-ranker இல்லாமல் vector மட்டும் பயன்படுத்தி, production-ல user கேள்விக்கு outdated pricing திரும்பி வந்தது. Customer support team-க்கு escalate ஆனது.

## 6. Practical Example

Enterprise SaaS company-க்கு internal RAG chatbot.

Problem: "Refund policy 2024" என்று கேட்டால், 2022 policy document top-1-ல வந்தது. 2024 update document second page-ல இருந்தது.

Architectural fix:

1. Metadata-ல `effective_from`, `effective_to`, `source_tier` சேர்த்தோம்.
2. Retriever query time-ல `effective_to IS NULL OR effective_to >= now()` filter போட்டோம்.
3. Hybrid search: vector + BM25.
4. Top 20 chunks எடுத்து cross-encoder re-ranker-ல top 5 filter.

Result: Wrong ranking 60% குறைந்தது. Latency 180ms → 340ms ஆனது. Team அதை accept பண்ணது ஏனெனில் refund தவறு cost அதிகம்.

## 7. Reasoning Challenge

உங்கள் RAG system-ல 2 types of queries வருகின்றன:

A. Real-time product pricing, B. General conceptual docs like architecture principles.

Pricing query-க்கு recency மிக முக்கியம். Conceptual query-க்கு recency குறைவான முக்கியம்.

ஒரே pipeline உங்களுக்கு இருக்கு. Wrong ranking-ஐ குறைக்க நீங்கள் என்ன architectural decision எடுப்பீர்கள்? Re-ranker எல்லா query-க்கும் போடுவீர்களா? ஏன் / ஏன் இல்லை?

## 8. Key Takeaways

* Wrong ranking = relevant document இல்லாமல் போகாமல், தவறான document முதலில் வருவது.
* Vector similarity மட்டும் relevance-ஐ guarantee செய்யாது. Recency, authority, conflict signals தேவை.
* Hybrid search + metadata filtering + selective re-ranking = practical balance between accuracy and latency.
* Ranking தப்பு ஆனால் LLM-ஐ குறை சொல்ல முடியாது. Retriever-ன் responsibility.
