# Naive RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.2.1 — RAG architecture

## 1. Problem

நீங்கள் ஒரு LLM-ஐ உங்கள் domain data-வுடன் பேச வைக்க வேண்டும். உதாரணமாக, உங்கள் bank-ன் கடந்த 3 வருட policy documents, 20,000 support tickets, product catalog இருக்கு.

User கேட்கிறார்: "என் savings account-க்கு lock period இருக்கா?"

LLM alone சொல்லும்: "பொதுவாக savings account-க்கு lock period கிடையாது." ஆனால் உங்கள் bank-ன் special savings scheme-க்கு 6 மாத lock உண்டு.

**Problem என்ன?** LLM-க்கு உங்கள் private knowledge இல்லை. Training data cutoff கடந்தது. Hallucination வரும். Retrieval இல்லாமல் accuracy கிடைக்காது.

இதை painful ஆக்குவது: Customer support agent wrong info கொடுத்தால் compliance issue. அதனால் தான் LLM-க்கு external knowledge கொடுக்க வேண்டும்.

## 2. Mental Model

Naive RAG என்பது: **Retrieve then Generate**.

User query வந்ததும், அதை vector database-ல் தேடு, relevant chunks கண்டுபிடி, அதை LLM prompt-க்கு context ஆக கொடு, LLM அதன் அடிப்படையில் answer generate பண்ணு.

Mental model ரொம்ப simple: LLM ஒரு smart reader. அவனுக்கு சரியான புத்தக பக்கத்தை காட்டு, அவன் சரியாக சொல்வான்.

## 3. How It Works

Flow:

1. **Indexing offline:** Documents -> chunk பண்ணு -> embedding model-ல் vector ஆக்கு -> vector database-ல் store பண்ணு. Metadata போடு: doc_id, source_url, timestamp.
2. **Query time:** User query வரும் -> query-ஐ embedding ஆக்கு -> vector DB-ல் similarity search. Top-K chunks எடு.
3. **Augmentation:** Retrieved chunks + user query ஐ சேர்த்து prompt பண்ணு.
   
   `Context: [chunk1] [chunk2]`
   `Question: ...`
   `Answer using only context.`

4. **Generate:** LLM answer கொடுக்கும்.

இது தான் naive RAG. Reranking, filtering, hybrid search இல்லை. Simple similarity search.

## 4. Architectural Reasoning

Naive RAG useful ஆகும் போது:

- நீங்கள் quick prototype பண்ண வேண்டும். Proof of concept.
- Data relatively clean, small to medium size.
- Query intent straightforward. "Find and answer".

Constraints it addresses:
- LLM knowledge cutoff
- Hallucination reduction
- Grounding to internal data

Alternatives:
- Fine-tuning LLM on your data. அது expensive, slow to update.
- LLM with tool use. Real-time but more complex.
- Naive RAG is cheapest first step.

Architect choose பண்ணும் reason: 1-2 weeks-ல working demo வேண்டும். Team-க்கு embedding + vector DB தெரியும். Operational complexity குறைவு.

## 5. Trade-offs

**Latency:** Retrieve + LLM generate = 2 hops. Vector search 50-200ms, LLM 1-3s. User wait அதிகம்.

**Relevance vs Context Length:** Top-K எடுக்கணும். K=3 என்றால் info miss ஆகலாம். K=10 என்றால் context window fill ஆகும், LLM confuse ஆகும்.

**Chunking trade-off:** Chunk too small -> context loss. Chunk too large -> noisy retrieval, token waste.

**Failure modes:** Retrieval fails -> LLM hallucinate. Vector DB outdated -> stale answer. Similarity search semantic gap -> wrong chunk retrieve ஆகும். No citation -> trust இல்லை.

**Consistency:** Same query வந்தாலும் retrieval order மாறலாம். Determinism இல்லை.

## 6. Practical Example

Enterprise support chatbot.

Documents: 5,000 PDFs of product manuals. Chunk size 800 tokens with 200 overlap. Embed with `text-embedding-3-small`. Store in Pinecone.

User asks: "My router firmware 2.4.1 has bug?"

System:
- Query embedding -> retrieve top 3 chunks from release notes.
- Context includes: "Firmware 2.4.1 released Jan 2025. Known issue: Wi-Fi drops after 48h."
- LLM answers: "Yes, known issue... Workaround: reboot..."

Naive RAG works here because question factual, document structured.

## 7. Reasoning Challenge

உங்களிடம் 2 million customer support conversations இருக்கு. User query: "Refund policy for cancelled flights during monsoon". 

Naive RAG-ல் similarity search மட்டும் போதுமா? Retrieval quality குறையும் என்றால் என்ன problem வரும்? 

Reranking அல்லது hybrid search add பண்ணுவதால் என்ன trade-off create ஆகும்?

சிந்தியுங்கள்: latency vs accuracy, cost vs relevance.

## 8. Key Takeaways

- Naive RAG = Retrieve relevant chunks → Give to LLM → Generate grounded answer. Simple, fast to build.
- இது LLM knowledge gap-ஐ fill பண்ணும், hallucination-ஐ குறைக்கும்.
- Trade-off: retrieval quality, latency, context noise, stale data.
- Prototype-க்கு நல்லது, production-க்கு reranking, filtering, citation, hybrid search தேவைப்படும்.
- Architecture decision என்பது data freshness, query complexity, accuracy requirement-ஐ பொறுத்தது.
