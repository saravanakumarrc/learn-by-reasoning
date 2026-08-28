# RAG fundamentals

> **Learning Path:** RAG Architecture
> **Section:** 12.1.1 — Learn

## 1. Problem

LLM தனியாக இருந்தால் என்ன problem?

Model training data-க்கு அப்புறம் உலகம் மாறுது. உங்கள் company data, internal docs, customer tickets, product catalog — இது எல்லாம் LLM-க்கு தெரியாது.

"எங்க company-க்கு இந்த quarter-ல எந்த deal close ஆச்சு?" என்று கேட்டால் LLM hallucinate பண்ணும். Generic knowledge மட்டுமே தரும்.

Problem painful ஆகிறது என்றால்: **LLM-க்கு real, up-to-date, private knowledge வேண்டும், ஆனால் அதை model-ல fine-tune பண்ண முடியாது** — cost அதிகம், data மாறும், latency வேண்டாம்.

அதனால் engineers கண்டுபிடித்த solution: Retrieval-Augmented Generation, RAG.

## 2. Mental Model

RAG என்பது LLM-ஐ ஒரு smart reader ஆக்குவது.

நீங்கள் ஒரு கேள்வி கேட்கிறீர்கள். System முதலில் உங்கள் knowledge base-ல் relevant chunks-ஐ retrieve பண்ணும். அதை context-ஆக LLM-க்கு கொடுக்கும். அப்புறம் LLM அந்த context-ஐ பார்த்து answer generate பண்ணும்.

Mental model: **Retrieve → Augment → Generate**

LLM தனியாக think பண்ணாமல், external memory-யை பார்த்து பதில் சொல்லும்.

## 3. How It Works

இது 3 core steps.

**Indexing:** உங்கள் documents-ஐ chunk பண்ணுவீர்கள். ஒவ்வொரு chunk-க்கும் embedding create பண்ணி vector database-ல் store பண்ணுவீர்கள். Metadata-ம் வைப்பீர்கள்.

**Retrieval:** User query வந்ததும், அதற்கும் embedding create பண்ணி vector DB-ல் similarity search செய்வீர்கள். Top K chunks எடுப்பீர்கள். இது semantic search.

**Augmentation:** Retrieved chunks + original query ஆகி LLM-க்கு prompt-ல் சேர்க்கப்படும். LLM அதை படித்து grounded answer தரும்.

இதுதான் loop. No training, just retrieval at inference time.

## 4. Architectural Reasoning

இது எப்போ useful?

* Knowledge frequently changes, but model retrain செய்ய முடியாது.
* Private / proprietary data, internet-க்கு கொண்டு போக முடியாது.
* Citation வேண்டும், source தெரிய வேண்டும்.

Alternatives என்ன?

* Fine-tuning: Data static ஆக இருந்தால், small domain-க்கு work ஆகும். ஆனால் cost அதிகம், update slow.
* Prompt engineering with few-shot: சிறிய context-க்கு மட்டும்.
* LLM with browsing: Public info-க்கு மட்டும்.

RAG choose பண்ணுவது ஏன்? **You want up-to-date, private knowledge without retraining.**

Constraint address பண்ணுவது: accuracy, hallucination reduction, freshness.

## 5. Trade-offs

**Retrieval quality vs. latency.** Better embeddings, larger chunks, reranking — quality கூடும், ஆனால் latency கூடும்.

**Context length vs. noise.** K அதிகமாக எடுத்தால் context overflow ஆகும். Relevant இல்லாத chunk வந்தால் LLM confuse ஆகும்.

**Chunking strategy.** Small chunks = precise retrieval. Large chunks = context preserve. ஒன்றை தேர்வு செய்யணும்.

**Failure modes.** Vector DB-ல் stale index இருந்தால் outdated answer. Retrieval fail ஆனால் LLM hallucinate பண்ணும். No results-க்கு fallback strategy வேண்டும்.

Cost: embedding, vector DB storage, retrieval per query.

## 6. Practical Example

Enterprise support chatbot.

Company-க்கு 10,000 internal KB articles உள்ளன. Customer support agent LLM-ஐ use பண்ணி answer தர வேண்டும்.

Architecture:
User query → query embedding → vector DB search on KB chunks → top 5 chunks retrieve → chunks + query → LLM → answer with citations.

Operability: KB update ஆனால் nightly indexing job run பண்ணி vector DB refresh. Metadata-ல் article version, owner வைத்து filter பண்ணலாம்.

இங்கே RAG இல்லாமல் LLM alone பயன்படுத்தினால் outdated policies சொல்லும். Fine-tune பண்ணினால் every KB change-க்கு retrain செய்ய வேண்டும்.

## 7. Reasoning Challenge

உங்களிடம் financial reports இருக்கு. ஒவ்வொரு quarter-லும் PDF upload ஆகும். User கேட்கிறார்: "Q2-ல revenue எவ்வளவு?"

உங்களிடம் embedding search மட்டும் உள்ளது. Retrieval செய்தால் சில chunks-ல் table data fragment ஆகி வருகிறது. LLM numbers-ஐ misinterpret பண்ணுகிறது.

இங்கே என்ன செய்வீர்கள்? Chunking strategy-ஐ மாற்றுவீர்களா? Reranker add பண்ணுவீர்களா? Structured extraction step add பண்ணுவீர்களா? ஏன்?

## 8. Key Takeaways

* RAG என்பது LLM-க்கு external memory கொடுக்கும் pattern, retrieval-ஐ inference-க்கு கொண்டு வருவது.
* Problem solve பண்ணுவது: private, dynamic knowledge-க்கு hallucination குறைப்பது.
* Quality depends on embedding quality, chunking strategy, retrieval relevance, மற்றும் context design.
* Every gain in accuracy costs latency and complexity. Trade-off-ஐ conscious-ஆக choose பண்ணுங்கள்.
