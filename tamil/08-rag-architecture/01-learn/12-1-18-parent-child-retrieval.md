# Parent-child retrieval

> **Learning Path:** RAG Architecture
> **Section:** 12.1.18 — Learn

## 1. Problem

உங்க RAG system-ல ஒரு document-ஐ vectorize பண்ணி store பண்றீங்க. User query வரும்போது top-k chunks retrieve பண்ணி LLM-க்கு கொடுக்கிறீங்க.

பிரச்சனை என்ன?

ஒரு chunk தனியா எடுத்துப் பார்த்தா context இல்லாம இருக்கும். `பணம் எப்படி return ஆகும்?`ன்னு கேட்டா, `7 working days`ன்னு மட்டும் வந்தா போதாது. அது எந்த policy-க்கு சொந்தம், refund எப்போ trigger ஆகும், exception என்னன்னு தெரியணும்.

இன்னொரு பக்கம், full document-ஐயே retrieve பண்ணினா token cost அதிகம், relevance குறையும். 2000 words உள்ள ஒரு support article-ஐ முழுசா அனுப்புவது waste.

அதனால் தேவை: **relevance-க்கு சின்ன chunk, context-க்கு பெரிய parent**. இரண்டையும் ஒன்னா கொடுக்கணும்.

> What goes wrong if we don't have this? Hallucination அதிகம், incomplete answer, அல்லது அதிக tokens use பண்ணி cost inflate ஆகும்.

## 2. Mental Model

Parent-child retrieval என்பது two-level indexing.

* **Parent:** பெரிய chunk, முழு meaning உள்ள paragraph அல்லது section. இது context-ஐ கொடுக்கும்.
* **Child:** parent-ல இருந்து வந்த சின்ன chunk, சில வாக்கியங்கள். இது retrieval-க்கு உதவும்.

Query வரும்போது child-களில் search பண்ணுவோம். Relevance match ஆன child-ஐ கண்டுபிடிச்சதும், அதோட parent-ஐ fetch பண்ணி LLM-க்கு கொடுப்போம்.

Analogy: Library-ல index card சின்னது, book பெரியது. Card வச்சு book-ஐ கண்டுபிடிக்கிறோம்.

## 3. How It Works

1. Document ingest பண்ணும்போது chunking strategy:
   * Parent chunk size: 800-1500 tokens, overlap இருக்கலாம்.
   * Child chunk size: 150-300 tokens, parent-ல இருந்து split.
2. Child chunks-க்கு embedding generate பண்ணி vector database-ல store.
   Child-க்கு parent_id reference வைக்கணும்.
3. Parent chunks-ஐயும் text store-ல வைக்கணும், vectorize தேவை இல்லை.
4. Query time:
   * Query embedding → child vector search → top-k children.
   * Deduplicate by parent_id.
   * Fetch corresponding parents.
   * Parents-ஐ LLM context-க்கு கொடு.

Implementation note: Hybrid search சேர்க்கலாம். Child-ல keyword search + vector search பண்ணி recall improve பண்ணலாம்.

## 4. Architectural Reasoning

இது எப்போ useful?

* Document-ல meaning span பெரியது, ஆனா query specific. Legal contract, support KB, product manual போன்றவை.
* Chunking ஒரே size-ல மட்டும் போதாது. Small chunk → loss of context. Large chunk → poor retrieval.
* Retrieval quality முக்கியம், ஆனா token budget கட்டுப்பாடு இருக்கு.

Alternatives:

* **Flat small chunks:** Retrieval நல்லா இருக்கும், context குறைவு.
* **Flat large chunks:** Context நல்லா இருக்கும், retrieval மோசம், token cost அதிகம்.
* **Hierarchical summarization:** Parent summary வைத்து retrieve. ஆனா summarize செய்ய computation வேண்டும்.

Parent-child choose பண்ணுறதால கிடைக்குறது: **retrieval precision + context completeness**.

## 5. Trade-offs

**Pros:**
* Relevant small units-ல search பண்ண முடியும், context முழுசா கிடைக்கும்.
* Parent deduplication-ல token waste குறையும்.

**Cons / Trade-offs:**
* **Index size & cost:** Child-கள் அதிகம், embedding cost, storage cost increase ஆகும்.
* **Latency:** Two hop: vector search + parent fetch. Cache பண்ணினால் குறையும்.
* **Complexity:** Chunking strategy, parent-child linking, orphan handling maintain பண்ண வேண்டும்.
* **Over-fetch:** ஒரு parent-ல பல children match ஆனா duplicate parent fetch ஆகும். Deduplication logic தேவை.

Failure mode: Parent-child mapping break ஆனால் context lost. Ingestion pipeline-ல ID consistency முக்கியம்.

## 6. Practical Example

Enterprise support KB.

ஒரு refund policy article 1200 words. 
Parent chunk: முழு section `Refund Policy for Electronics`.
Child chunks: `7 working days`, `invoice required`, `no refund after 30 days`, `exchange window` போன்ற snippets.

User query: `electronics return எத்தனை நாள் கொடுப்பீங்க?`

Child `7 working days` match ஆகும். Parent fetch ஆகும். LLM-க்கு parent முழுசும் போகும். Answer complete ஆகும், policy exception-ம் கிடைக்கும்.

இல்லாமல் flat small chunks use பண்ணினால் `7 working days` மட்டும் கிடைத்திருக்கும். Userக்கு `working days means?`ன்னு follow up வந்திருக்கும்.

## 7. Reasoning Challenge

உங்களிடம் 2M documents இருக்கு. ஒவ்வொரு doc-க்கும் average 5 parents, 20 children.

Constraint: vector DB cost கட்டுப்படுத்த வேண்டும், latency < 200ms.

இங்கே parent-child எல்லா document-க்கும் apply பண்ணுவீங்களா? அல்லது selective?

> யோசிங்க: எந்த document types-க்கு இது value கொடுக்கும், எந்த type-க்கு waste. எப்படி decide பண்ணுவீங்க?

## 8. Key Takeaways

* Parent-child என்பது retrieval accuracy-க்கு small chunk, reasoning-க்கு large context கொடுக்கும் pattern.
* Child-ல search செய், parent-ஐ fetch செய் என்பது core flow.
* Cost, latency, complexity trade-off இருக்கு. High-value long-form documents-க்கு மட்டும் use பண்ணுவது சரியான decision.
* Chunking strategy தான் system quality-ஐ decide பண்ணும், model choice அல்ல.
