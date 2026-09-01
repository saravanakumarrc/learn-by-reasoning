# Context recall

> **Learning Path:** AI Evaluation
> **Section:** 18.2.5 — RAG metrics

## 1. Problem

உங்கள் RAG system-ல் LLM-க்கு கொடுக்கும் context-ல் சரியான தகவல் இல்லாமல் போனால் என்ன ஆகும்?

User கேட்ட "நேற்றைய quarterly revenue என்ன?" என்றால், retriever கடந்த வருட report-ஐ மட்டும் கொண்டு வந்து விட்டது. LLM அதை நம்பி ஒரு தவறான எண்ணை generate பண்ணிடும்.

மறுபுறம், context-ல் தேவையில்லாத நிறைய docs கொண்டு வந்தால் என்ன ஆகும்? Token cost ஏறும், latency ஏறும், LLM confuse ஆகி hallucinate பண்ணும்.

அதனால் architect-க்கு இரண்டு கேள்வி முக்கியம்:
1. தேவையான தகவல் context-ல் வந்ததா?
2. தேவையில்லாத தகவல் context-ல் வந்ததா?

இதை அளவிடாமல் RAG-ஐ improve பண்ண முடியாது.

## 2. Mental Model

Context recall என்பது **retriever-ன் திறன்** அளவீடு.

நினைத்துக்கொள்ளுங்கள்: நீங்கள் ஒரு librarian. User ஒரு கேள்வி கேட்டார். நீங்கள் சில books-ஐ table-ல் வைக்கிறீர்கள். LLM அந்த books-ஐ மட்டும் படித்து பதில் சொல்ல வேண்டும்.

Context recall = சரியான books-ஐ table-ல் வைத்தீர்களா என்பது.

இது answer quality-க்கு முன் வரும் metric. Retriever தவறு செய்தால், generation எவ்வளவு நல்ல LLM-ஆக இருந்தாலும் சரியான பதில் வராது.

## 3. How It Works

ஒரு query-க்கு ground truth என்னென்ன documents தேவை என்பது தெரிந்திருக்க வேண்டும்.

எடுத்துக்காட்டாக:
Query: "RAG-ல் context window overflow எப்படி handle பண்ணுவது?"
Relevant docs: doc A, doc C, doc F

Retriever top-k = 5 docs தந்தது: A, B, D, C, E

அப்போ:
Recall@k = relevant docs retrieved / total relevant docs

இங்கே 2/3 = 0.667

MRR, NDCG போன்ற ranking metrics-க்கும் உள்ளது, ஆனால் RAG-க்கு முதலில் recall தான் foundation.

நடைமுறையில் ground truth இல்லாததால், human-annotated query set உருவாக்குகிறோம். அல்லது LLM-as-judge மூலம் "இந்த document query-க்கு relevant ஆ?" என்று label பெறுகிறோம்.

## 4. Architectural Reasoning

Context recall எப்போது useful?

* RAG pipeline-ல் retriever change பண்ணும்போது, embedding model மாற்றும்போது, chunking strategy மாற்றும்போது.
* Re-ranker add பண்ணினால் recall குறையுமா? அதை check பண்ண.
* Hybrid search vs pure vector search compare பண்ண.

Alternatives:
* Precision@k: retrieved docs-ல் எத்தனை relevant என்பது. Recall-ஐ மட்டும் பார்த்தால் spam docs கொண்டு வரலாம்.
* Recall முக்கியம் ஆனால் context size limited. அதனால் Recall@k-க்கு பிறகு Precision மற்றும் context compression பார்க்க வேண்டும்.

Architect decision: Top-k எவ்வளவு வைக்க வேண்டும்? k அதிகரித்தால் recall ஏறும், ஆனால் token cost, latency, noise ஏறும். அதனால் recall curve-ஐ பார்த்து sweet spot தேர்வு செய்ய வேண்டும்.

## 5. Trade-offs

* **Recall vs Precision**: Recall அதிகப்படுத்த high k எடுக்கலாம். ஆனால் LLM-க்கு noise அதிகம். Trade-off தெளிவாக தெரியும்.
* **Recall vs Latency/Cost**: ஒவ்வொரு extra doc-க்கும் embedding search, re-rank, token cost. Production-ல் budget constraint உள்ளது.
* **Recall vs Position**: முதல் 3 docs-ல் relevant வந்ததா? LLM முதல் docs-க்கு அதிக attention தரும். Recall@k மட்டும் போதாது, recall at early positions முக்கியம்.
* **Evaluation cost**: Ground truth annotation expensive. LLM-as-judge cheap ஆனால் bias உண்டு.

Failure mode: Retriever சிறந்த recall கொடுக்கிறது ஆனால் retrieved docs contradictory ஆக இருந்தால் LLM confuse ஆகும். Recall alone is not enough.

## 6. Practical Example

Enterprise support RAG system.

Query: "Customer ID 4821-க்கு refund policy என்ன?"

Ground truth relevant chunks: policy doc v2, ticket #4821 notes.

Embedding model v1: Recall@5 = 0.4. Policy doc கிடைக்கவில்லை.
Chunk size 512 tokens, overlap 50.

நீங்கள் chunk size-ஐ 256 ஆக்கி, metadata filter customer_id சேர்த்தீர்கள்.

Recall@5 = 0.8 ஆனது.

ஆனால் retrieved docs 5-ல் 3 docs duplicate information. LLM answer-ல் repetition வந்தது.

இங்கே நீங்கள் re-ranker சேர்த்து top-3-க்கு compress பண்ணி recall@3-ஐ மெயிண்டெய்ன் செய்தீர்கள். இப்போது latency 120ms-ல் இருந்து 210ms ஆகியது.

இந்த trade-off-ஐ metrics மூலம் தான் justify பண்ண முடியும்.

## 7. Reasoning Challenge

உங்களிடம் 2 retrievers உள்ளது:

Retriever A: Recall@10 = 0.92, Precision@10 = 0.35
Retriever B: Recall@10 = 0.71, Precision@10 = 0.68

Context window 4k tokens. Average doc size 600 tokens. LLM cost $0.002 per 1k tokens.

நீங்கள் agent-based RAG build பண்ணுகிறீர்கள், அங்கே LLM தான் முடிவு எடுக்கும். எந்த retriever-ஐ தேர்வு செய்வீர்கள்? k-ஐ மாற்றுவீர்களா? ஏன்?

## 8. Key Takeaways

* Context recall என்பது retriever-ன் திறனை அளவிடும் metric. Generation quality-க்கு முன் வரும்.
* Recall@k அதிகரித்தால் கிடைக்கும், ஆனால் cost, latency, noise-ம் அதிகரிக்கும்.
* Recall-ஐ மட்டும் பார்க்காமல் early position recall மற்றும் precision-உடன் சேர்த்து முடிவு செய்ய வேண்டும்.
* Production-ல் recall curve-ஐ பார்த்து k மற்றும் re-ranker strategy தேர்வு செய்யுங்கள்.
