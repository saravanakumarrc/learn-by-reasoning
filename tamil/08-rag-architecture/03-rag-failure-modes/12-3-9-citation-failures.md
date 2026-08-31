# Citation failures

> **Learning Path:** RAG Architecture
> **Section:** 12.3.9 — RAG failure modes

## 1. Problem

RAG system-ல LLM ஒரு answer கொடுக்கும்போது, அதுக்கு source-ஐ cite பண்ணணும். "இந்த தகவல் இந்த document-ல இருந்து வந்தது"ன்னு சொல்லணும்.

ஆனா real world-ல என்ன நடக்குது?

LLM retrieval செய்த chunks-ஐ பார்த்து answer generate பண்ணுது. பிறகு அந்த answer-க்கு citation attach பண்ணுது. இங்கே தான் failure வருது.

ஒரு citation failureன்னா: LLM சொன்ன தகவலுக்கு சரியான source இல்லை, தவறான source attach ஆகி இருக்கு, source-ல அந்த தகவலே இல்லை, அல்லது citation format தவறாக இருக்கு.

இது ஏன் painful? Legal, finance, healthcare மாதிரி domain-ல "இதை எங்கிருந்து எடுத்தீங்க?"ன்னு கேட்பார்கள். Citation இல்லாமல் அல்லது தவறான citation-உடன் answer கொடுத்தால் trust போய்விடும். Audit-ல தோல்வி.

## 2. Mental Model

Citation என்பது answer-க்கும் retrieved context-க்கும் இடையேயான link.

நினைச்சுக்கோ: LLM ஒரு student, retrieved chunks ஒரு pile of books. Student answer எழுதி, "இந்த வரி இந்த புத்தகத்தின் page 12-ல இருந்து"ன்னு reference கொடுக்கணும்.

Citation failure ஆனால் student கற்பனை செய்ததை உண்மைன்னு சொல்லி, தவறான புத்தகத்தை cite பண்ணிடுறார். அல்லது உண்மையான புத்தகத்தை பார்த்து தவறான page சொல்றார்.

## 3. How It Works

RAG pipeline-ல citation fail ஆகும் இடங்கள்:

**Retrieval mismatch:** Query-க்கு தொடர்பில்லாத chunk retrieve ஆகி, LLM அதை பயன்படுத்தி answer கொடுக்குது. Citation technically valid ஆனால் semantically wrong.

**Hallucinated grounding:** LLM context-ல இல்லாத தகவலை generate பண்ணி, அருகில் இருந்த ஒரு chunk-ஐ citation-ஆக தூக்கி விடுது. இதை *citation hallucination*ன்னு சொல்லலாம்.

**Chunk boundary error:** உண்மையான statement ஒரு chunk-ல split ஆகி இருக்கும். LLM ஒரு பகுதியை மட்டும் பார்த்து citation கொடுக்கும். Source-ல அந்த full claim இல்லை.

**Aggregation without traceability:** பல chunks-ல இருந்து தகவல் எடுத்து ஒரு summary உருவாக்கினால், எந்த chunk எந்த part-க்கு பொறுப்பு என்று map பண்ண முடியாது.

**Post-processing loss:** Generation-க்கு பிறகு citation metadata தொலைந்து விடும். LLM output JSON-ல citation field empty ஆகி விடும்.

## 4. Architectural Reasoning

Citation தேவைப்படும் system-ல, retrieval-க்கு பிறகு citation integrity-ஐ enforce பண்ணணும்.

எப்போது useful?
* Audit trail தேவை
* Compliance / legal review
* High-stakes decision support

எப்படி address பண்ணலாம்?

**Retrieval-time filtering:** Relevance score threshold வைத்து irrelevant chunks-ஐ drop பண்ணு. Reranker use பண்ணு.

**Generation constraints:** Prompt-ல "cite only from provided context, do not invent" என்று strict instruction. Better: structured output where each sentence must have citation id.

**Post-generation verification:** LLM answer-ன் ஒவ்வொரு claim-ஐயும் retrieved chunk-டுடன் cross-check பண்ணும் verifier model / rule-based checker. Citation-க்கு பின்னால் உள்ள text-ல claim உண்மையாக இருக்கிறதா என்பதை validate பண்ணு.

**Chunking strategy:** Overlap + metadata rich chunks. Citation granularity fine ஆக்கு. Page number, paragraph id வைத்திரு.

Alternative: Citation-ஐ generate செய்யாமல், retrieval result-ஐயே answer-ஆக return பண்ணு. But user experience கெட்டுவிடும்.

## 5. Trade-offs

* **Strict citation vs answer completeness:** Strict enforcement செய்தால் LLM safe answer தரும், ஆனால் "I don't know" அதிகம் வரும். Relax செய்தால் hallucinations அதிகம்.
* **Verification cost vs latency:** Post-generation verification ஒரு extra LLM call அல்லது model inference. Latency + cost increase.
* **Granularity vs usability:** Sentence-level citation accurate ஆனால் output clutter ஆகும். Paragraph-level citation clean ஆனால் traceability குறையும்.
* **Precision vs recall:** Retrieval tight ஆக்கினால் citation accurate ஆகும், ஆனால் useful context miss ஆகலாம்.

Failure mode: Verifier-ஐ தவறாக tune பண்ணினால், valid citations-ஐயும் reject பண்ணி false negatives வரும். User trust குறையும்.

## 6. Practical Example

Enterprise knowledge base RAG: HR policy bot.

User கேட்கிறார்: "Maternity leave எத்தனை நாள்?"

Retriever 2 chunks கொடுத்தது:
* Chunk A: "Maternity leave 180 days for permanent employees"
* Chunk B: "Paternity leave 15 days"

LLM answer: "Maternity leave 180 days and paternity leave 15 days."

Citation: [Chunk A, Chunk B] - correct.

இப்போது retrieval fail ஆனால்: Chunk C மட்டும் வந்தது: "Contract employees get 90 days maternity leave". LLM 180 days-ஐ தான் சொல்லும் பழக்கத்தால் answer-ஐ 180 days என்றே generate பண்ணி, Chunk C-ஐ cite பண்ணிடும். இது citation failure.

Solution: Prompt-ல context-க்கு மட்டும் answer பண்ணு, plus post-generation check: answer-ல உள்ள "180 days" string chunk-ல இருக்கிறதா என்பதை search பண்ணு. இல்லைன்னா citation strip பண்ணி "insufficient source" flag செய்.

## 7. Reasoning Challenge

உங்கள் RAG system financial report analysis செய்கிறது. Analyst ஒரு query கேட்டால், LLM பல sentences generate பண்ணி, ஒவ்வொன்றுக்கும் citation கொடுக்கிறது. நீங்கள் கண்டுபிடித்தீர்கள் 12% sentences-ல cited chunk-ல அந்த claim exact match இல்லை, ஆனால் semantically related.

நீங்கள் என்ன செய்வீர்கள்? Strict verifier-ஐ on பண்ணி citations-ஐ reject செய்யலாமா, அல்லது fuzzy match threshold adjust பண்ணி allow செய்யலாமா? Latency முக்கியம். Cost முக்கியம். Compliance முக்கியம்.

ஏன் அந்த தேர்வு?

## 8. Key Takeaways

* Citation failure என்பது retrieval mismatch, hallucinated grounding, அல்லது traceability loss-ல இருந்து வரும்.
* Answer correctness-க்கு citation integrity தனி concern. LLM-க்கு trust பண்ணாதீர்கள், verify பண்ணுங்கள்.
* Architecturally, citation-ஐ generate செய்வது மட்டும் போதாது. Post-generation grounding check + retrieval quality முக்கியம்.
* Trade-off எப்போதும் strictness vs coverage. Domain risk அதற்கு தீர்மானிக்கும்.
