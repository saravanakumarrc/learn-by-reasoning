# Missing documents

> **Learning Path:** RAG Architecture
> **Section:** 12.3.2 — RAG failure modes

## 1. Problem

உங்க RAG system-ல user கேள்வி கேட்கிறார்: "Q3-ல நம்ம churn rate எவ்ளோ?"

LLM-க்கு போகும் context-ல relevant document இல்லை. Embedding search பண்ணினாலும் top-k results-ல அந்த doc வரல. அல்லது doc corpus-லேயே இல்லை.

என்ன ஆகும்? LLM hallucinate பண்ணும். அல்லது "I don't have information" என்று சொல்லும். இரண்டும் business-க்கு பிரச்சனை.

Missing documents என்பது **retrieval failure-ன் மிகவும் சாதாரண வடிவம்**. ஆனால் இது system design முடிவு, மாடல் திறமை அல்ல.

## 2. Mental Model

RAG = Retrieve + Generate.

Generate எவ்ளோ நல்லா இருந்தாலும், Retrieve தரும் context தான் ceiling-ஐ set பண்ணும்.

Missing document என்பது:

* **Corpus gap**: Document எப்போதும் index-ல இல்லை.
* **Index gap**: Document உள்ளது, ஆனால் chunking / embedding / metadata தப்பு, அதனால் retrieve ஆகவில்லை.
* **Access gap**: Document உள்ளது, ஆனால் permission / freshness காரணமாக user-க்கு தர முடியாது.

இது "zero recall" சூழ்நிலை.

## 3. How It Works

Retrieval path இப்படி இருக்கும்:

User query → embedding → vector database search → top-k chunks → reranker → LLM context.

Missing document நிகழும் இடங்கள்:

* **Ingestion மிஸ்**: Source system-ல document உருவாகிறது, ஆனால் ingestion pipeline trigger ஆகவில்லை. E.g., Confluence page update ஆனது, crawler வந்து பார்க்காமல் போனது.
* **Chunking மோசம்**: ஒரு 50 page PDF-ஐ 500 token chunk-களாக வெட்டினால், அந்த specific fact ஒரு chunk border-ல cut ஆகி, embedding meaning-ஐ lose பண்ணும்.
* **Embedding drift**: Query phrasing மற்றும் document phrasing இடையே semantic gap. Technical term-கள் synonyms இல்லாமல் match ஆகாது.
* **Vector DB limitations**: Top-k = 5 என்று வைத்தால், relevant doc rank 6-ல் இருந்தால் மிஸ்.
* **Filter மிஸ்**: Metadata filter தப்பாக வைத்தால், relevant doc filter out ஆகும்.

## 4. Architectural Reasoning

Missing documents எப்போது painful ஆகும்?

* Enterprise RAG-ல compliance / financial data தேவைப்படும் போது.
* Real-time data தேவைப்படும் போது. E.g., ticket status, inventory.
* Long-tail queries, rare documents.

Alternatives / Mitigations:

* **Better coverage**: Ingestion completeness-ஐ monitor பண்ணு. Source inventory vs indexed inventory reconciliation.
* **Hybrid retrieval**: Vector மட்டும் இல்லாமல் keyword BM25 + vector + metadata filter சேர்த்து recall-ஐ உயர்த்து.
* **Query expansion**: LLM-ஐ use பண்ணி query-ஐ paraphrase பண்ணி multiple embeddings generate பண்ணு.
* **Retrieval augmentation**: RAG system "I don't know" சொல்ல வேண்டும், hallucinate கூடாது. Retrieval confidence score < threshold என்றால், safe fallback.

என்ன constraint address பண்ணுகிறது? **Recall over precision**. Architect-கள் பெரும்பாலும் precision-ல focus பண்ணுவார்கள். Missing doc case-ல recall தான் முக்கியம்.

## 5. Trade-offs

* **Recall vs Latency & Cost**: Hybrid retrieval, query expansion, larger top-k எல்லாம் recall-ஐ உயர்த்தும், ஆனால் latency மற்றும் vector DB cost உயரும்.
* **Freshness vs Stability**: Real-time ingestion வைத்தால் missing doc குறையும், ஆனால் ingestion pipeline complexity, failure modes அதிகரிக்கும்.
* **Chunk size trade-off**: Small chunk → precise retrieval ஆனால் context loss. Large chunk → context retain ஆனால் noise அதிகம், embedding less discriminative.
* **Confidence threshold**: Low threshold வைத்தால் hallucination risk. High threshold வைத்தால் "I don't know" அதிகம், user experience கெடும்.

Important failure mode: **Silent missing**. System success rate 95% காட்டும், ஆனால் அந்த 5% critical queries-ல தான் missing doc நடக்கும்.

## 6. Practical Example

ஒரு bank-ன் RAG chatbot.

Source: internal policy PDFs, FAQs, ticket system.

Q: "நான் credit card-ஐ freeze பண்ணினேன், எப்படி unfreeze பண்ணுவது?"

Document உள்ளது, ஆனால் 2024 policy update PDF ingestion ஆகவில்லை. Index-ல 2023 version மட்டுமே உள்ளது. User-க்கு outdated steps தரப்படுகிறது.

Architectural fix:

1. Ingestion audit log: Source document list vs vector DB document list diff daily.
2. Hybrid retrieval: keyword "unfreeze" + vector search.
3. Retrieval confidence score < 0.7 என்றால், LLM-க்கு context கொடுக்காமல் "இதற்கு நிச்சயமான பதில் இல்லை, support team-ஐ தொடர்பு கொள்ளுங்கள்" என்று fallback.
4. Freshness SLA: Policy docs-க்கு ingestion lag < 1 hour.

## 7. Reasoning Challenge

உங்களிடம் customer support RAG உள்ளது. 50k documents indexed. User queries-ல 12% "I don't know" response வருகிறது. Logs பார்த்தால், retrieval returns non-empty, ஆனால் LLM says insufficient context.

Missing documents தான் காரணமா? இல்லை retrieval quality problem தானா? 

நீங்கள் என்ன மெட்ரிக்ஸ் பார்ப்பீர்கள், என்ன experiment design பண்ணுவீர்கள்? Recall-ஐ உயர்த்த, precision-ஐ கெடுக்காமல் என்ன architecture மாற்றம் செய்வீர்கள்?

## 8. Key Takeaways

* Missing document என்பது corpus, ingestion, chunking, embedding, filtering chain-ல எங்கும் நடக்கலாம்.
* RAG-ல recall தான் ultimate ceiling. Precision-ஐ மட்டும் optimize பண்ணினால் போதாது.
* "I don't know" என்று சொல்லும் திறன், hallucination-ஐ விட முக்கியம்.
* Ingestion coverage-ஐ monitor பண்ணு, missing doc-ஐ silent failure ஆக விடாதே.
