# Context overload

> **Learning Path:** RAG Architecture
> **Section:** 12.3.5 — RAG failure modes

## 1. Problem

உங்கள் RAG system ஒரு enterprise document மீது கட்டப்பட்டிருக்கு. User ஒரு complex question கேட்கிறார். Retriever 15 chunks எடுக்கிறது, ஒவ்வொன்னும் 800 tokens. System prompt 500 tokens, user query 100 tokens, response budget 500 tokens.

Total = ~13,000 tokens. 

LLM context window 16k என்றால் fit ஆகும். ஆனால்:

* Latency போய் விடுகிறது
* Cost per query அதிகரிக்கிறது
* Model attention dilute ஆகிறது, relevant signal relevant noise-ல மறைந்து விடுகிறது
* Hallucination அதிகரிக்கிறது

இது தான் **context overload**.

நீங்கள் அதிக தகவலை கொடுக்க முயற்சிக்கும்போது, model உண்மையில் குறைவாக புரிந்துகொள்கிறது. 

> What goes wrong if we don't have this? Model தேவையற்ற chunks-ல திளைத்து, முக்கியமான fact-ஐ miss செய்கிறது. User experience degrade ஆகிறது.

## 2. Mental Model

Context window ஒரு limited working memory போல.

ஒரு engineer-க்கு 50 pages printout கொடுத்து "இதுல answer கண்டுபிடி" என்றால் என்ன ஆகும்? Time எடுக்கும், முக்கிய page எது என்று குழம்பும்.

Context overload = **too much retrieved data, too little signal density**.

Retrieval சரியாக இருந்தாலும், அளவு தவறாக இருந்தால் RAG fail ஆகும்.

## 3. How It Works

RAG pipeline-ல் overload எங்கே வருகிறது:

1. **Retriever over-fetch**: Top-K அதிகம். k=20 வைத்தால், பெரும்பாலும் irrelevant chunks வரும்.
2. **Chunk size too large**: 2000 tokens per chunk என்றால், 10 chunks = 20k tokens.
3. **No reranking / filtering**: Similarity score மட்டும் பார்த்து, redundancy உள்ள chunks சேர்க்கப்படும்.
4. **Conversation history bloat**: Multi-turn chat-ல் முழு history-யும் append செய்வது.
5. **Multi-document aggregation**: User 5 documents குறிப்பிட்டால், அனைத்தையும் முழுமையாக சேர்ப்பது.

LLM context window நிரம்பும்போது, model early tokens மீது attention குறைக்கிறது. உங்கள் best chunk கடைசியில் வந்தால், அது மறந்துவிடப்படுகிறது.

## 4. Architectural Reasoning

Context overload என்பது retrieval quality பிரச்சனை அல்ல, **selection பிரச்சனை**.

எப்போது useful?

* Large corpus, long documents
* Complex multi-hop queries
* High QPS, cost sensitive services
* Agentic RAG where multiple tools return data

Alternatives:

* **Increase context window**: 128k, 200k models. வேலை செய்யும், ஆனால் cost x2, latency x1.5. Signal-to-noise improve ஆகாது.
* **Better retrieval**: Hybrid search, reranker. உதவும், ஆனால் K அதிகமாக இருந்தாலும் overload தொடரும்.
* **Compression & summarization**: Retrieved chunks-ஐ condense செய்து, key facts மட்டும் வைக்க.

Architect முடிவு எப்போது செய்ய வேண்டும்? 

When retrieval recall > precision needed. நீங்கள் முதலில் recall உயர்த்தி, பிறகு precision trim செய்ய வேண்டும்.

## 5. Trade-offs

**Relevance vs Coverage**: குறைவான chunks = less latency, better focus, ஆனால் முக்கிய fact miss ஆகலாம். 

**Compression vs Fidelity**: Summarize செய்தால், noise குறையும், ஆனால் nuance, numbers, citations காணாமல் போகலாம்.

**Latency vs Accuracy**: Rerank + filter + re-rank adds 100-300ms. User acceptable ஆ?

**Cost vs Quality**: Larger context = higher token cost. Production-ல் per query cost budget உண்டு.

Failure modes:

* **Redundancy collapse**: 10 chunks same paragraph-ல் இருந்தால், model அதே தகவலை 10 முறை படிக்கிறது.
* **Position bias**: முதல்/கடைசி chunks மீது model bias உண்டு. முக்கிய fact middle-ல் இருந்தால் lose ஆகும்.
* **Citation hallucination**: Context அதிகமாக இருந்தால், model source-ஐ தவறாக map செய்யும்.

## 6. Practical Example

Enterprise RAG for policy documents.

User query: "Remote work policy-ல் reimbursement எப்படி claim பண்ணுறது, tax implication என்ன?"

Retriever returns:

* 8 chunks from Remote Work Policy v3
* 5 chunks from Tax Guide 2024
* 4 chunks from Expense Reimbursement SOP

Total 17 chunks ~ 12k tokens.

Architecture decision:

1. Retrieve top 30 with hybrid search
2. Cross-encoder reranker ஓடி top 8 தேர்வு
3. Deduplicate by semantic similarity >0.9
4. Chunk-level summarizer: each chunk-ஐ 2-3 sentences-க்கு compress
5. Final context ~ 2,500 tokens

Result: Latency 1.2s → 0.6s, cost 40% down, answer accuracy up because model focused.

## 7. Reasoning Challenge

உங்களிடம் customer support RAG இருக்கு. Average query 3 documents தொடர்புடையது. Retriever top 15 chunks தருகிறது. 70% queries-ல் answer முதல் 5 chunks-ல் இருக்கிறது. ஆனால் remaining 30% queries-ல் 6-15 வரை தேவைப்படுகிறது.

Context overload-ஐ தடுக்க நீங்கள் என்ன செய்வீர்கள்? 

Reranker மட்டும் போதுமா? அல்லது adaptive K + compression வேண்டுமா? ஏன்?

## 8. Key Takeaways

* Context overload என்பது too much data, not bad retrieval.
* Signal density > raw recall. 5 relevant chunks > 20 noisy chunks.
* Rerank, dedupe, compress, and adaptive K இவை மூன்றும் ஒன்றாக தேவை.
* Every token in context has a cost: latency, money, attention dilution.
* Design for the 95th percentile query, not the worst case.
