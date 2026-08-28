# Contextual retrieval

> **Learning Path:** RAG Architecture
> **Section:** 12.1.17 — Learn

## 1. Problem

நீங்கள் ஒரு RAG system பண்ணிக்கொண்டிருக்கிறீர்கள். User கேட்கிறார்: *"நம்ம கடந்த கால Q4 செலவுகளை விளக்கு"*.

உங்கள் vector database-ல் ஆயிரக்கணக்கான chunks இருக்கு. Embedding similarity மூலம் top-k chunks எடுத்தீர்கள். அவை generic ஆக இருக்கு. "Q4" என்ற context-ஐ அது புரிந்துகொள்ளவில்லை. User-ன் conversation history, current session, user role, previous query எல்லாம் இல்லாமல் தனியாக chunk-ஐ தேடினால் relevance தப்பும்.

இதுதான் பிரச்சனை: **embedding மட்டும் பார்த்தால் semantic similarity கிடைக்கும், ஆனால் context கிடைக்காது.**

ஒரு document-ன் meaning முழுமையாக புரிய வேண்டுமெனில் அது எந்த conversation-ல் வருகிறது, எந்த user-க்கு, எந்த time range-க்கு, எந்த prior facts கொடுக்கப்பட்டுள்ளன என்பது தேவை.

What goes wrong if we don't have this? Hallucination, irrelevant retrieval, wrong grounding, user-க்கு வேண்டியதை கொடுக்க முடியாமல் போகும்.

## 2. Mental Model

Contextual retrieval என்பது: **query-ஐ மட்டும் தேடாமல், query + surrounding context-ஐ ஒன்றாக தேடுவது.**

எளிய analogy: ஒரு புத்தகத்தில் ஒரு வார்த்தையின் அர்த்தம் அந்த paragraph-ல் இருந்து தெரியும். அந்த paragraph-ஐ தனியாக எடுத்து அர்த்தம் புரிந்துகொள்ளலாம். ஆனால் அந்த paragraph எந்த chapter-ல் இருக்கிறது, முந்தைய chapter என்ன சொன்னது என்பது தெரிந்தால் தான் உண்மையான meaning தெரியும்.

RAG-ல் contextual retrieval என்பது query-க்கு context window-ஐ attach செய்து retrieval-ஐ enrich செய்வது.

## 3. How It Works

Basic RAG flow: `Query -> Embed -> Vector Search -> Top-k chunks -> LLM`

Contextual retrieval flow: `Query + Context -> Embed / Re-rank -> Top-k chunks -> LLM`

Context எங்கிருந்து வரும்?

* **Conversation history:** முந்தைய user turns, assistant turns
* **Session metadata:** user id, role, tenant, product
* **Temporal context:** "கடந்த மாதம்", "Q4" என்பதை resolve செய்ய தேவையான date
* **Document-level context:** chunk-க்கு முந்தைய / பிந்தைய paragraphs, section title, table headers

பொதுவாக இரண்டு வழிகள்:

1. **Contextualized Embeddings:** Query-ஐ conversation history-உடன் concat செய்து ஒரே embedding-ஆக மாற்றி search செய்வது. Simple, fast.
2. **Contextual Re-ranking:** முதலில் query மூலம் candidate chunks எடுத்து, பிறகு cross-encoder மூலம் query + context + chunk-ஐ பார்த்து re-rank செய்வது. Accuracy அதிகம், cost அதிகம்.

மேலும் advanced pattern: **Contextual chunking** என்பது retrieval-க்கு முன்பே chunk-ஐ create செய்யும்போதே அதன் parent context-ஐ இணைத்து வைப்பது. உதாரணமாக, ஒரு FAQ answer chunk-ஐ create செய்யும்போது product name, version, date-ஐ அதன் metadata-வாக embed செய்வது.

## 4. Architectural Reasoning

Contextual retrieval எப்போது useful?

* Multi-turn conversation உள்ள chatbot
* User-specific data உள்ள enterprise search
* Implicit references உள்ள queries: "அதை", "அதே", "மேலும்"
* Time-sensitive queries

Constraint it addresses: **Relevance vs Precision trade-off**. Plain embedding similarity போதாது.

Alternatives:
* **Naive RAG:** Query only. Fast, cheap, but context blind.
* **Hybrid search:** BM25 + vector. Better keyword match, ஆனால் conversation context handle பண்ணாது.
* **Graph RAG:** Relationships use செய்யும். Strong for entities, overkill for simple chat.

ஏன் architect choose பண்ணுவார்? ஒரு banking chatbot-ல் user "என் கடந்த transaction" என்றால் அது current user-க்கு மட்டும் relevant ஆக இருக்க வேண்டும். Context இல்லாமல் generic transaction history திரும்பினால் data leak ஆகும்.

Decision point: Context-ஐ எவ்வளவு தூரம் கொண்டு போகலாம்? Full history எடுத்தால் token cost அதிகம், noise அதிகம். அதனால் sliding window or summarization பயன்படுத்துகிறார்கள்.

## 5. Trade-offs

* **Relevance vs Latency:** Contextual re-ranking accuracy அதிகம் தரும், ஆனால் extra LLM/cross-encoder call வரும். p95 latency increase ஆகும்.
* **Freshness vs Consistency:** Conversation history dynamic ஆக மாறும். Embedding cache செய்ய முடியாது.
* **Privacy vs Personalization:** User-specific context வைத்தால் retrieval personalized ஆகும். ஆனால் multi-tenant isolation, logging, PII handling கவனிக்க வேண்டும்.
* **Complexity vs Operability:** Context window size, summarization strategy, metadata schema எல்லாம் maintain செய்ய வேண்டும். Team size சிறியதாக இருந்தால் over-engineering ஆகலாம்.

Failure mode: Context window-ல் irrelevant history கொடுத்தால் retrieval drift ஆகும். User ஒரு topic மாற்றினாலும் பழைய context இழுத்துக்கொண்டு தவறான chunks திரும்பும். அதனால் context reset / topic detection தேவை.

## 6. Practical Example

Enterprise support RAG.

User: *"நம்ம API-ல error வருது"*

Session metadata: tenant = acme-corp, product = payments-api, version = v2.3, user role = engineer

Conversation history:
User: "நான் ஸ்டேஜிங் environment-ல test பண்ணுகிறேன்"
Assistant: "சரி, staging base URL ..."

Contextual retrieval இல்லாமல்: "API error" என்ற generic chunks வரும்.

Contextual retrieval உடன்: Query = "நம்ம API-ல error வருது" + context = tenant, product, version, staging env, previous discussion.

Retrieval system இப்போது payments-api v2.3 staging error logs, acme-corp specific runbook, recent incidents-ஐ மட்டும் fetch செய்யும். Production error docs வராது.

Architecture: Query + context → contextualized embedding → vector DB search with metadata filter tenant=acme-corp AND product=payments-api → top 50 candidates → cross-encoder re-rank using query+history+chunk → top 5 to LLM.

## 7. Reasoning Challenge

உங்களிடம் ஒரு multi-tenant SaaS chatbot இருக்கிறது. 10k active conversations / minute. ஒவ்வொரு conversation-க்கும் 10 turns history இருக்கிறது. Contextual retrieval வேண்டும், ஆனால் latency budget 400ms.

Contextualized embeddings மூலம் query-ஐ 512 tokens-க்கு expand செய்வது vs cross-encoder re-ranking மூலம் 50 candidates-ஐ filter செய்வது.

இங்கே என்ன architecture தேர்வு செய்வீர்கள்? ஏன்? Cost, latency, relevance எப்படி balance செய்வீர்கள்?

## 8. Key Takeaways

* Contextual retrieval என்பது query மட்டுமல்ல, query + conversation + metadata + document context ஆகும்.
* Plain similarity தரும் relevance-ஐ contextual enrichment உண்மையான usefulness-ஆக மாற்றும்.
* Trade-off எப்போதும் latency, cost, complexity vs relevance.
* Context size-ஐ control செய்யாமல் retrieval drift ஆகும், privacy risk வரும்.
* Architect ஆக, context-ஐ எங்கே inject செய்ய வேண்டும் என்பதே முக்கிய decision: embed time, search time, or re-rank time.
