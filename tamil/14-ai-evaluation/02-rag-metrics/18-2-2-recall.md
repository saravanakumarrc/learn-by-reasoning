# Recall

> **Learning Path:** AI Evaluation
> **Section:** 18.2.2 — RAG metrics

## 1. Problem

உங்க RAG system ஒரு query க்கு answer தருது. User கேட்டது: "Q3-ல எந்த product அதிகம் விற்றது?"

System திரும்பி வந்த answer லோ, சரியான document-ஐ தான் பயன்படுத்திச்சா? இல்லை தப்பான document-ஐ எடுத்துட்டு hallucination பண்ணிச்சா?

RAG-ல இரண்டு step இருக்கு:
1. **Retrieval** - query-க்கு relevant chunks-ஐ vector database-ல இருந்து தேடி எடுப்பது
2. **Generation** - LLM அந்த chunks-ஐ பார்த்து answer எழுதுவது

Generation quality மோசமா இருந்தா தெரியும். ஆனா retrieval தப்பா இருந்தா? LLM நல்லா எழுதியிருக்கும், ஆனாலும் சரியான context இல்லாம எழுதும். 

அப்போ உங்களுக்கு தேவை: Retrieval stage சரியா வேலை பண்ணுதான்னு measure பண்ண ஒரு metric. அதுதான் Recall.

## 2. Mental Model

Recall என்பது: **ground truth-ல உள்ள relevant documents-ல எத்தனை percent-ஐ நாம் retrieve பண்ணோம்?**

அதாவது, உண்மையிலேயே answer-க்கு தேவையான chunks 100 இருந்தா, நீங்க top-K-ல 70-ஐ கொண்டு வந்தீங்கன்னா Recall = 0.7.

Precision என்பது நீங்க கொண்டு வந்தவை எத்தனை relevant? Recall என்பது நீங்க miss பண்ணினவை எத்தனை?

ஒரு library-ல நூல்களை தேடுற மாதிரி. Relevant books 10 இருக்கு. நீங்க 7-ஐ மட்டும் கண்டுபிடிச்சீங்க. Recall 70%. மீதி 3 books shelf-ல இருந்தும் உங்களுக்கு தெரியல.

## 3. How It Works

RAG evaluation-ல ஒரு query-க்கு நாம் ground truth relevant chunks-ஐ manually label பண்ணோம்.

Formula:
```
Recall@K = | Relevant retrieved in top K | / | Total relevant in ground truth |
```

உதாரணம்:
Query: "refund policy for premium users"
Ground truth relevant chunks = 5 [chunk A, B, C, D, E]
Retriever top 10 results-ல A, C, E மட்டும் வந்தா
Recall@10 = 3 / 5 = 0.6

Retriever top 5-ல A, C மட்டும் வந்தா
Recall@5 = 2 / 5 = 0.4

K increase பண்ணும்போது Recall பொதுவா increase ஆகும். ஏன்னா retrieve பண்ற pool பெருசாகுது.

RAG metrics-ல Recall என்பது retrieval quality-யின் core signal. Generation quality-யை measure பண்ண Faithfulness, Answer Relevancy வரும்.

## 4. Architectural Reasoning

Recall முக்கியமா ஆகும் போது?

**When you need completeness, not just a good answer.** 

நீங்க financial compliance report generate பண்றீங்க. "All transactions over 1M in Q3" என்ற query-க்கு ஒரு doc miss ஆனாலும் audit fail ஆகும். இங்கே Recall > Precision.

நீங்க conversational chatbot பண்றீங்க. Top 1-2 chunks போதும். User-க்கு quick answer வேணும். இங்கே Precision முக்கியம்.

Alternatives:
- **Recall@K** - simple, interpretable
- **MRR, MAP** - ranking quality-க்கு
- **nDCG** - relevance graded இருந்தா

ஆர்கிடெக்ட் ஏன் Recall-ஐ track பண்ணணும்?
Retriever தான் bottleneck. Embedding model மாற்றினீங்க, chunk size மாற்றினீங்க, hybrid search add பண்ணினீங்க - எல்லாத்துக்கும் impact தெரியணும். Recall என்பது retrieval improvement-ஐ measure பண்ண ஒரு stable signal.

## 5. Trade-offs

**Recall vs Precision**
Recall அதிகப்படுத்த retrieval pool-ஐ பெருசாக்குவது. Top K = 50 பண்ணா Recall அதிகம். ஆனா LLM-க்கு noise கொடுக்கும். Context window fill ஆகும். Generation quality குறையும். Cost அதிகம்.

**Recall vs Latency & Cost**
Vector search பண்ண K அதிகமாக்குறது ஒரு பிரச்சனை இல்ல. ஆனா re-ranking model run பண்ணும்போது cost linear-ஆ increase ஆகும். Hybrid search-ல BM25 + vector combine பண்ணா Recall improve ஆகும், ஆனா latency அதிகம்.

**Recall vs Ground Truth Quality**
Recall measure பண்ண ground truth labeling தேவை. Manual annotation expensive. Synthetic labels பயன்படுத்தினா bias வரும். அதனால metric-ஐ நம்புவது கஷ்டம்.

**Failure mode:** High Recall, Low Precision = LLM confused. Relevant + irrelevant chunks mix ஆகும். Hallucination risk அதிகம்.

## 6. Practical Example

Enterprise RAG for internal knowledge base.

Query: "2024-ல customer discount policy எப்போ மாறியது?"
Ground truth relevant chunks: 4 docs
- policy_v1.pdf chunk 12
- policy_v2.pdf chunk 3
- email_announcement March
- FAQ page

Current retriever: embedding-only, top 10
Retrieved: policy_v1, policy_v2, FAQ, unrelated sales doc
Recall@10 = 3/4 = 0.75

Architect முடிவு: Hybrid search add பண்ணினார். BM25 keyword match-ஐ combine பண்ணினார்.
Now retrieved: 4/4 docs
Recall@10 = 1.0

Trade-off: Latency 120ms -> 210ms. Re-ranker cost double. ஆனா compliance team-க்கு completeness முக்கியம், அதனால accept பண்ணினாங்க.

## 7. Reasoning Challenge

உங்க RAG system-ல recall@10 = 0.92 இருக்கு. ஆனால் user complaints "answer incomplete" வருது.

உங்க LLM context window 8k. Top K = 10 chunks, average chunk 500 tokens = 5k tokens.

இங்கே problem என்ன? Recall மட்டும் பார்த்தா போதுமா? நீங்க என்ன மெட்ரிக் add பண்ணுவீங்க, ஏன்?

## 8. Key Takeaways

- Recall measures retrieval completeness: ground truth relevant docs-ல எத்தனை percent retrieve ஆச்சு
- High Recall முக்கியம் when completeness is critical: compliance, legal, research
- Recall improve பண்ண K increase, hybrid search, better embedding பண்ணலாம், ஆனா Precision, latency, cost-ஐ trade-off பண்ணும்
- Recall alone போதாது. Generation stage-க்கு Faithfulness, Answer Relevancy மாதிரி metrics வேணும்
- Architectural decision: Recall target-ஐ business risk-ஆல set பண்ணுங்க, metric-ஆல இல்ல
