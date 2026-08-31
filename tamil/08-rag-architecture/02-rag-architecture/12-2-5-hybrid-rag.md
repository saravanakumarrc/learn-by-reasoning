# Hybrid RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.2.5 — RAG architecture

## 1. Problem

உங்களிடம் ஒரு RAG system இருக்கு. User கேள்வி கேட்கிறார். அதை embedding ஆக்கி vector database-ல search செய்கிறீர்கள். பெரும்பாலும் சரியான context கிடைக்கிறது.

ஆனால் சில கேள்விகளில் vector search தோல்வி அடைகிறது.

* "நேற்று Chennai office-ல நடந்த incident ticket எது?" → date + entity specific.
* "Q3 2024-ல revenue எவ்வளவு?" → exact number, range query.
* "Refund policy-ல 7 days rule எங்கே இருக்கு?" → keyword exact match தேவை.

Vector search என்பது semantic similarity. அது concept-ஐ புரிந்துகொள்ளும், ஆனால் exact keyword, numeric filter, structured lookup-ல மெல்லியதாகிறது.

மறுபுறம் keyword search மட்டும் போட்டால் semantic variation miss ஆகும். "cancel order" vs "order return" என்பது keyword-ல வேறு.

இங்கே painful point வருகிறது: **precision miss ஆகிறது, recall குறைகிறது, user trust குறைகிறது.**

இந்த பிரச்சனைக்கு பிறந்ததுதான் Hybrid RAG.

## 2. Mental Model

Hybrid RAG என்பது ஒரே query-க்கு இரண்டு search முறைகளை ஓடச் செய்து, results-ஐ combine செய்வது.

> Vector search = meaning புரிஞ்சுக்கும் fuzzy match
> Keyword BM25 = exact term, phrase, number, filter match

இரண்டும் ஒரே நேரத்தில் run ஆகும். பிறகு ranking fuse செய்யப்படும். இது "best of both worlds" தேடல்.

அனலாகி: ஒரு librarian-ஐ கேட்கிறீர்கள். ஒருவர் topic மூலம் புத்தகம் கண்டுபிடிக்கிறார், இன்னொருவர் exact title/number மூலம் கண்டுபிடிக்கிறார். இருவரின் list-ஐ merge செய்தால் miss குறையும்.

## 3. How It Works

Pipeline simple:

1. Query → embed ஆகும்
2. Query string அப்படியே keyword index-க்கு போகும்
3. Vector DB-ல similarity search → top K
4. Keyword index-ல BM25 search → top K
5. Fusion → final top N

Fusion முறைகள்:
* **Reciprocal Rank Fusion, RRF** - மிகப் பிரபலம். Rank position-ஐ weight செய்து score சேர்க்கும். Model-free, effective.
* Weighted sum / linear combination - vector score + keyword score normalize செய்து கூட்டுதல்.

பிறகு re-ranker உபயோகித்தால், fused results-ஐ LLM cross-encoder-ல refine செய்யலாம். ஆனால் அது optional.

Indexing side: ஒவ்வொரு document chunk-க்கும் embedding + raw text index இரண்டும் maintain செய்யப்படும். Elasticsearch, OpenSearch போன்றவை இரண்டையும் ஒரே engine-ல support செய்யும்.

## 4. Architectural Reasoning

Hybrid useful ஆகும் போது:

* Corpus mixed ஆக இருக்கும்போது: manuals, policies, tickets, financial reports. சில semantic, சில exact lookup.
* User queries mixed intent உள்ள போது: "how to reset password" and "invoice #12345 status".
* High recall தேவை. Customer support, legal, finance systems-ல hallucination cost அதிகம்.

Alternatives:
* Vector only - fast, semantic, ஆனால் exact match weak
* Keyword only - precise, ஆனால் paraphrase miss
* Vector + re-ranker only - cost high, exact filter இல்லை

Architect decision: Query complexity predictable இல்லை என்றால் Hybrid default ஆக்கு. Latency budget allow செய்தால்.

## 5. Trade-offs

* **Latency**: இரண்டு search + fusion = 2x cost. Parallel run செய்து max latency குறைக்கலாம். Cache செய்யலாம்.
* **Complexity**: இரண்டு indexes maintain, sync செய்ய வேண்டும். Chunking strategy இரண்டுக்கும் work ஆக வேண்டும்.
* **Cost**: storage double, compute double. RRF fusion cheap.
* **Tuning**: K values, fusion weights corpus-க்கு ஏற்ப மாறும். Evaluation set வைத்து tune செய்ய வேண்டும்.
* Failure mode: keyword noise அதிகம் என்றால் vector signal-ஐ மூழ்கடிக்கும். மோசமான fusion = worse than single.

## 6. Practical Example

Enterprise support RAG.

Corpus: 2M support tickets + product docs + refund policy PDFs.

User query: "Chennai customer-க்கு 2024-10-01 refund approve ஆனதா?"

Vector search: "refund approved for Chennai customer" concept-ஐ catch செய்யும்.
Keyword search: "2024-10-01", "Chennai", "refund approve" exact term-ஐ catch செய்யும்.

Hybrid-ல ticket ID கிடைக்கும். Vector only-ல date mismatch ஆகி வேறு ticket வந்திருக்கும்.

Architecture: Document ingestion → chunk 500 tokens → embedding to pgvector + text to Elasticsearch BM25. Query time parallel fetch 20 results each, RRF fuse to top 10, pass to LLM with citations.

## 7. Reasoning Challenge

உங்களிடம் product catalog RAG இருக்கு. User "red lightweight running shoes under $100" என்று கேட்கிறார்.

Vector search color + use case புரிந்துகொள்ளும். Keyword search price filter "<100", "red", "running shoes" exact match செய்யும்.

இங்கே hybrid வேண்டுமா? வேண்டாமா? Fusion-க்கு பதிலாக structured metadata filter பயன்படுத்துவது better ஆ? ஏன்?

## 8. Key Takeaways

* Hybrid RAG = vector semantic + keyword exact. Problem ஆனது recall and precision gap.
* RRF fusion simple and effective. Model-free combine செய்யலாம்.
* Exact filters, numbers, dates, IDs உள்ள queries-க்கு hybrid must.
* Latency and ops cost உயரும். Parallelize, tune K, measure recall.
* Architectural decision: Hybrid is not always needed. Query distribution பார்த்து தேர்வு செய்.
