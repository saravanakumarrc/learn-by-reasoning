# Retrieval evaluation

> **Learning Path:** AI Evaluation
> **Section:** 18.1.8 — Evaluation

## 1. Problem

நீங்கள் ஒரு RAG system கட்டி முடித்தீர்கள். Embedding model, vector database, chunking strategy, reranker எல்லாம் set. 
இப்போது user கேள்வி கேட்கிறார். Answer quality நல்லா இருக்கிறது போல தெரிகிறது.

பிரச்சனை: **Retriever சரியான documents-ஐ தான் கொண்டு வருகிறதா?**

Retriever தவறான context-ஐ கொடுத்தால், LLM எவ்வளவு smart ஆக இருந்தாலும் hallucination அல்லது irrelevant answer தான் வரும். 
Generator-ஐ evaluate செய்வது easy இல்லை, ஆனால் retriever-ஐ evaluate செய்வது மிக முக்கியம். ஏனெனில் retrieval தான் whole RAG pipeline-ன் foundation.

> "What goes wrong if we don't have this?"  
> Bad retriever = good LLM-ம் waste. Relevant documents கிடைக்காமல், system-ன் accuracy ceiling குறைந்து விடும்.

## 2. Mental Model

Retrieval evaluation என்பது: **Query கொடுத்தால், system திரும்ப கொண்டு வரும் top-K documents எவ்வளவு relevant ஆக உள்ளன?**

இது information retrieval-ன் classic problem. நாம் measure பண்ணுவது ranking quality.

ஒரு analogy: Library-ல் நீங்கள் ஒரு கேள்வி கேட்கிறீர்கள். Librarian 10 books தருகிறார். அதில் 3 books தான் உண்மையில் பதில் கொடுக்கும். அந்த 3 books முதல் 3-லேயே இருக்கிறதா? அல்லது 10-வது இடத்தில் இருக்கிறதா? அதுவே evaluation.

## 3. How It Works

Retrieval evaluation-க்கு நமக்கு தேவை: **Queries + Ground truth relevant documents**.

Evaluation metrics:

**Ranking-based metrics:**
* **Hit Rate / Recall@K** - Top K results-ல் குறைந்தபட்சம் ஒரு relevant document உள்ளதா? RAG-ல் பெரும்பாலும் Recall@5 or Recall@10 பார்க்கிறோம்.
* **Recall@K** - Top K-ல் உள்ள relevant documents எத்தனை சதவீதம் மொத்த relevant documents-ல் இருந்து கொண்டு வரப்பட்டது.
* **Precision@K** - Top K-ல் உள்ள documents எத்தனை சதவீதம் relevant.

**Ranking quality metrics:**
* **MRR - Mean Reciprocal Rank** - முதல் relevant document எந்த rank-ல் வருகிறது. Rank 1 என்றால் 1, Rank 2 என்றால் 0.5.
* **nDCG@K** - Rank position-ன் முக்கியத்துவத்தை கணக்கில் கொள்கிறது. Top ranks-ல் relevant document வருவது அதிக value.

**RAG specific:**
* **Retrieval Precision** - Retrieved context-ல் facts correct ஆ? LLM-ன் answer-க்கு தேவையான information இருக்கிறதா?
* **Coverage** - Query-ன் sub-questions எல்லாம் retrieved docs-ல் cover ஆகிறதா?

இதை measure செய்ய, நாம் தயார் பண்ண வேண்டியது: labeled query set. Gold standard documents manually annotate செய்ய வேண்டும். அல்லது existing QA dataset-ஐ use செய்யலாம்.

## 4. Architectural Reasoning

**எப்போது useful?**
* Embedding model change செய்யும்போது
* Chunk size / overlap மாற்றும்போது
* Vector database மாற்றும்போது
* Reranker add/remove செய்யும்போது

**What constraint it addresses?** 
Latency vs recall trade-off. Top K அதிகமாக்கினால் recall உயரும், ஆனால் LLM context window, cost, latency அதிகரிக்கும்.

**Alternatives:**
* Manual spot-checking - quick ஆனால் scale ஆகாது
* End-to-end LLM-as-a-judge - Generator-ஐ evaluate செய்யும், retriever-ஐ தனியாக isolate செய்யாது
* Human evaluation - gold standard ஆனால் expensive

Retrieval evaluation ஒரு architect-க்கு உதவுவது: **Retriever quality தனியாக bottleneck ஆக உள்ளதா என்பதை தெரிந்து கொள்ள**. Generator-ஐ மாற்றாமல், retriever மட்டும் மாற்றி improvement கிடைக்கிறதா என்பதை isolate செய்ய முடியும்.

## 5. Trade-offs

1. **Recall vs Precision vs Latency.** Recall@10 உயர்த்த, K-ஐ அதிகரிக்க வேண்டும். ஆனால் LLM-க்கு அனுப்பும் tokens அதிகரிக்கும். Cost, latency உயரும்.

2. **Offline labeled data vs Online real queries.** Offline benchmark stable, ஆனால் real user query distribution-ஐ capture செய்யாமல் போகலாம். Online evaluation realistic ஆனால் ground truth கிடைப்பது கடினம்.

3. **Exact match vs Semantic relevance.** Keyword match செய்தால் easy to evaluate, ஆனால் embedding-based retrieval semantic relevance-ஐ target செய்கிறது. Human judgment தேவை.

4. **Evaluation cost.** High-quality annotations expensive. Synthetic queries generate செய்யலாம், ஆனால் bias வரும்.

Failure mode: Retriever-ன் recall மோசமாக இருந்தும், LLM-ன் parametric knowledge மூலம் answer correct ஆக தோன்றும். அப்போது evaluation misleading ஆகும். அதனால் retrieval evaluation-ஐ generator-லிருந்து decouple செய்ய வேண்டும்.

## 6. Practical Example

Enterprise support RAG system. Knowledge base: 200k internal support articles.

Goal: Query-க்கு relevant article top 5-ல் வர வேண்டும்.

நீங்கள் 500 real support tickets எடுத்து, ticket description-ஐ query ஆக பயன்படுத்தி, agent-ன் solution-ல் link செய்யப்பட்ட article-ஐ gold relevant ஆக mark செய்கிறீர்கள்.

Baseline: Embedding model A, chunk size 1000 tokens, no reranker.
Recall@5 = 0.42

Experiment 1: Chunk size 500 tokens.
Recall@5 = 0.51

Experiment 2: Hybrid search - BM25 + vector.
Recall@5 = 0.63

Experiment 3: + Cross-encoder reranker top 20 → 5
Recall@5 = 0.71, latency +80ms

இப்போது architect-க்கு clear: Hybrid search தான் biggest gain. Reranker improves but latency cost உள்ளது. Production-ல் SLA 300ms என்றால், reranker optional ஆக்கலாம்.

## 7. Reasoning Challenge

உங்களிடம் medical QA RAG system உள்ளது. Safety critical. Recall மிக முக்கியம். ஆனால் LLM context window 8k tokens.

Current setup: Recall@10 = 0.78, average retrieved tokens = 6000.

Product team கேட்கிறது: "Recall-ஐ 0.9-க்கு மேல் கொண்டு வா."

நீங்கள் என்ன செய்வீர்கள்? K-ஐ அதிகரித்தால் என்ன ஆகும்? Reranker, query expansion, hybrid search போன்ற options-ல் எது முதலில் try செய்வீர்கள், ஏன்?

## 8. Key Takeaways

* Retrieval evaluation என்பது ranking quality-ஐ measure செய்வது. Recall@K, nDCG@K போன்ற metrics மூலம்.
* Retriever-ஐ generator-லிருந்து தனியாக evaluate செய்யுங்கள், இல்லையெனில் bottleneck தெரியாது.
* Ground truth labeled queries இல்லாமல், retrieval improvement ஆனது பற்றி உறுதியாக சொல்ல முடியாது.
* Recall, precision, latency, cost இவைகளுக்கு இடையே trade-off உள்ளது. Business constraint-க்கு ஏற்ப K மற்றும் reranker தேர்வு செய்யுங்கள்.
