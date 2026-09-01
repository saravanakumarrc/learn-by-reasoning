# Precision

> **Learning Path:** AI Evaluation
> **Section:** 18.2.1 — RAG metrics

## 1. Problem

RAG system build பண்ணீங்க. LLM context-ல relevant documents retrieve பண்ணி answer generate பண்ணுது.

Production-ல customer கேட்டான்: "இந்த invoice-க்கு refund policy என்ன?"

System answer கொடுத்தது: "Refund 30 days க்குள். Contact support."

இது சரியா? உண்மையில் retrieved document-ல 30 days refund policy இருக்கு, ஆனா அது invoice-க்கு மட்டும் இல்ல, general services-க்கு. Wrong context use பண்ணி சரியான மாதிரி பதில் கொடுத்துடுச்சு.

இங்கே என்ன problem? System நிறைய relevant ஆன documents retrieve பண்ணுது, ஆனா உண்மையில் user query-க்கு தேவையான precise information மட்டும் இல்ல.

Evaluation-ல இதை எப்படி catch பண்ணுவது? Accuracy மட்டும் பார்த்தால் போதாது.

Precision தேவைப்படுவது இதுக்குதான்.

## 2. Mental Model

Precision என்பது: **Retriever கொடுத்த results-ல எத்தனை உண்மையில் relevant?**

ஒரு basket-ல பழம் எடுத்தா, அதுல எத்தனை பழம் கெட்டுபோனது? Precision அதை measure பண்ணும்.

Retrieval-ல:
Retrieved set = top-k documents
Relevant set = query-க்கு உண்மையில் தேவையான documents

Precision = | Relevant ∩ Retrieved | / | Retrieved |

Simple. நீங்கள் 10 documents retrieve பண்ணினீங்க, அதுல 7 தான் உண்மையில் relevant என்றால் Precision@10 = 0.7

## 3. How It Works

RAG evaluation-ல Precision பயன்படுத்தும்போது:

1. Query கொடுங்கள்
2. Retriever top-k results தரும்
3. Human or gold standard labels உதவி, ஒவ்வொரு retrieved document-ம் relevant ஆ? இல்லையா? என்று mark பண்ணுங்கள்
4. Count செய்யுங்கள்

Precision@k என்பது k என்ற cut-off-ல் Precision.

RAG pipeline-ல இது retrieval stage-க்கு மட்டும் அல்ல. Generation-ல hallucination குறைக்க retrieved context precise ஆ இருந்தால் தான் possible.

Precision மட்டும் பார்த்தால் recall தெரியாது. Relevant document-ல ஒன்றை மிஸ் பண்ணினாலும் தெரியாது.

அதனால் Precision மற்றும் Recall ஜோடியாக பார்க்கப்படும்.

## 4. Architectural Reasoning

Precision எப்போது முக்கியம்?

**Query specific ஆக இருக்கும் போது.** Legal, finance, medical RAG-ல ஒரு irrelevant document கூட context-ல வந்தால் LLM அதை பயன்படுத்தி wrong answer generate பண்ணும்.

ஒரு chatbot-ல user chat history retrieve பண்ணும்போது, too broad retrieval = noise.

Constraint: **Context window limited**. LLM-க்கு 10k tokens கொடுக்க முடியும், ஆனா irrelevant docs fill பண்ணினால் useful info squeeze ஆகும்.

Options:
- High recall retriever + filter later
- High precision retriever + retrieve more rounds

Architect decision: Precision first retriever என்றால் embedding model fine-tune, query rewriting, reranker use பண்ணுவீர்கள். Recall first என்றால் broad search, hybrid search.

RAG-ல பொதுவாக: First retrieve broad with high recall, then rerank for high precision. Precision@10 improves with reranker.

## 5. Trade-offs

**Precision vs Recall.** இது classic trade-off. Precision அதிகப்படுத்தினால் recall குறையும். k குறைத்தால் precision அதிகம், ஆனா relevant doc miss ஆகும் risk.

**Precision vs Latency/Cost.** Reranker, cross-encoder use பண்ணி precision improve பண்ணலாம். ஆனா latency அதிகம், cost அதிகம்.

**Precision vs Coverage.** Domain specific queries-க்கு generic embedding model low precision தரும். Fine-tune பண்ணினால் precision improve ஆகும், ஆனா maintenance cost வரும்.

Failure mode: High precision metric, ஆனா real user satisfaction low. ஏனெனில் evaluation set-ல gold labels imperfect ஆக இருக்கலாம். Human judgement தேவை.

## 6. Practical Example

Enterprise knowledge base RAG.

Queries: "Q4 2025 Bangalore office leave policy"

Retriever top-5:
1. Bangalore office leave policy 2025 - relevant
2. Chennai office leave policy 2025 - not relevant
3. Q4 2025 finance report - not relevant
4. Bangalore office leave policy 2024 - partially relevant
5. Company wide holiday list 2025 - relevant

Precision@5 = 2.5 / 5 ≈ 0.5

Architect இதை பார்த்து: Reranker add பண்ணலாம். Query expansion பண்ணி "Bangalore" + "leave policy" + "2025" weight அதிகப்படுத்தலாம். Hybrid search with BM25 + vector.

After rerank:
1. Bangalore office leave policy 2025 - relevant
2. Bangalore office leave policy 2024 - partially relevant
3. Company wide holiday list 2025 - relevant
4. Chennai office leave policy 2025 - not relevant
5. Q4 2025 finance report - not relevant

Precision@3 = 2.5/3 ≈ 0.83

Context quality improve ஆனது. LLM hallucination குறையும்.

## 7. Reasoning Challenge

உங்கள் RAG system-ல customer support agent. Query: "iPhone 15 Pro warranty claim process"

Retriever top-10-ல 4 docs relevant, 6 docs irrelevant. Precision@10 = 0.4

Business requirement: Answer must be 100% accurate, no noise. User trust critical.

நீங்கள் Precision improve பண்ண என்ன architecture decision எடுப்பீர்கள்? Recall குறைவதை எப்படி handle பண்ணுவீர்கள்?

## 8. Key Takeaways

- Precision = retrieved results-ல எத்தனை உண்மையில் relevant, அதை measure பண்ணும் metric
- RAG-ல high precision = less noise in context = less hallucination
- Precision@k useful for retrieval stage evaluation, especially with limited context window
- Precision improve பண்ண reranker, query rewriting, better embedding model உதவும், ஆனா recall மற்றும் latency trade-off வரும்
- Production RAG-ல Precision மற்றும் Recall இரண்டையும் ஒன்றாக பார்த்து decision எடுக்க வேண்டும்
