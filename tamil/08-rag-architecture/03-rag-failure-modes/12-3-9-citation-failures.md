# Citation failures

> **Learning Path:** RAG Architecture
> **Section:** 12.3.9 — RAG failure modes

## 12.3.9 — RAG failure modes: Citation failures

### 1. Problem

நீங்கள் ஒரு RAG system கட்டி முடித்தீர்கள். LLM க்கு context கொடுக்கிறீர்கள், answer வருகிறது. ஆனால் business user கேட்கிறார்: "இந்த தகவல் எங்கிருந்து வந்தது?"

நீங்கள் source ஐ காட்ட முடியவில்லை. அல்லது காட்டினாலும் அது தவறான paragraph ஆக இருக்கிறது. அல்லது citation இருக்கிறது ஆனால் answer-ல் இருக்கும் claim அந்த source-ல் இல்லை.

இது citation failure. Production RAG-ல் இது மிகவும் painful ஆன problem.

ஏனென்றால்:

* Compliance team கேட்கும். Financial, legal domain-ல் source இல்லாமல் answer ஏற்க முடியாது.
* User trust போய்விடும். "Hallucination ஆக இருக்கலாம்" என்று நினைப்பார்கள்.
* Debugging கடினம். எந்த retrieval step தவறு, எந்த generation step தவறு என்று தெரியாது.

> What goes wrong if we don't have reliable citations? Answer is unverifiable, untrustable, and unmaintainable.

### 2. Mental Model

RAG-ல் உண்மையில் மூன்று flow இருக்கிறது.

1. **Retrieve** → relevant chunks கண்டுபிடி
2. **Ground** → LLM அந்த chunks மீது மட்டும் answer உருவாக்கு
3. **Cite** → answer-ல் உள்ள ஒவ்வொரு claim-க்கும் source link போடு

Citation failure என்பது 2 மற்றும் 3 இடையே gap வருவது. LLM உருவாக்கிய claim, retrieved context-ல் இல்லாததை reference பண்ணுவது. அல்லது context சரியாக இருந்தும் LLM அதை பயன்படுத்தாமல் hallucinate பண்ணுவது.

ஒரு analogy: ஒரு researcher ஆவணங்களை table மீது போட்டு விட்டு, "இதை base பண்ணி எழுது" என்றால், researcher சில facts-ஐ தன்னிச்சையாக கற்பனை செய்து விடுகிறார். அதற்கு பிறகு bibliography ல் தவறான page number கொடுக்கிறார்.

### 3. How It Works

Citation failure பொதுவாக மூன்று வகையில் வரும்.

**a) Retrieval failure leading to citation mismatch**
Retriever தவறான chunk-ஐ கொண்டு வருகிறது. Semantic similarity இருக்கிறது ஆனால் factual support இல்லை. LLM அந்த chunk-ஐ cite பண்ணுகிறது, ஆனால் claim அந்த chunk-ல் இல்லை.

**b) Generation drift**
Retrieved chunks சரியாக இருக்கிறது. ஆனால் LLM, multiple chunks-ஐ combine செய்யும் போது inference செய்கிறது. அந்த inference-க்கு direct citation இல்லை. ஆனால் model அதற்கும் citation கொடுக்கிறது.

**c) Citation formatting failure**
LLM answer சரியாக இருக்கிறது, grounding நல்லா இருக்கிறது. ஆனால் citation IDs, document IDs, page numbers தவறாக generate ஆகிறது. அல்லது citation missing.

இவை எல்லாம் ஏன் நடக்கிறது?

* LLM-க்கு instruction following weak. "Cite every claim" என்றாலும், அது சில claims-ஐ skip பண்ணும்.
* Context window நிரம்பி, chunk boundaries மறைந்து விடும்.
* Embedding model-ல் nuance புரியாமல் போகும்.
* No verification step. Generate → cite என்று ஒரே step-ல் போய்விடும்.

### 4. Architectural Reasoning

Citation reliability வேண்டுமானால், generate செய்த பிறகு verify செய்ய வேண்டும்.

அடிப்படை design options:

**Option 1: Prompt-based citation**
Prompt-ல் "Cite sources for every claim" என்று சொல். Simple, cheap. ஆனால் unreliable. Model தான் cite செய்கிறது, தானே validate செய்கிறது.

**Option 2: Retrieval-Augmented Generation with citation enforcement**
Answer generation-க்கு பிறகு, ஒரு separate verification step. ஒவ்வொரு cited sentence-க்கும், அது source chunk-ல் உள்ளதா என்று check பண்ணு. String match, embedding similarity, or NLI model use பண்ணு.

**Option 3: Extractive RAG**
LLM-க்கு summarize செய்யாமல், retrieved chunks-ல் இருந்து sentences-ஐ extract பண்ணு. அப்போ citation தானாக correct ஆகும். Trade-off: answer less fluent.

**Option 4: Structured output + post-processor**
LLM output-ஐ JSON-ல் claim + citation_id format-ல் வரவழை. பிறகு citation_id valid ஆக உள்ளதா, chunk-ல் claim support ஆகிறதா என்று validate.

எந்த architect இதை தேர்வு செய்வார்?

* High trust domain = legal, medical, finance → Option 2 or 4
* Low latency chatbot → Option 1 with light monitoring
* Knowledge base small and static → Option 3

### 5. Trade-offs

**Accuracy vs Latency**: Verify step சேர்த்தால் latency உயரும், cost உயரும். ஆனால் trust கிடைக்கும்.

**Granularity**: Chunk level citation vs sentence level citation. Chunk level cheap, ஆனால் imprecise. Sentence level precise, ஆனால் mapping hard.

**Coverage**: ஒவ்வொரு claim-க்கும் citation கட்டாயம் என்றால், model "I don't know" சொல்ல வேண்டியிருக்கும். அது user experience-ஐ பாதிக்கும்.

**Operational complexity**: Citation store, chunk ID management, versioning. Document update ஆனால் old citations stale ஆகும். அதை track பண்ண வேண்டும்.

Failure modes:

* **Hallucinated citation**: source இல்லாத ID generate ஆகும்.
* **Weak citation**: claim-க்கு related ஆன chunk cite செய்யப்படும், ஆனால் exact support இல்லை.
* **Citation overload**: 10 citations for one simple fact. User confused.

### 6. Practical Example

Enterprise HR policy assistant.

User கேட்கிறார்: "Maternity leave எத்தனை நாள்?"

Retriever கொண்டு வருகிறது: HR policy doc v2, page 12: "Maternity leave is 26 weeks as per policy effective Jan 2024."

LLM answer: "Maternity leave is 26 weeks. [HR Policy v2 p12]"

இது சரி.

இப்போ document v3 update ஆகி 18 weeks ஆக மாறியது. Vector DB update ஆகவில்லை. Retriever still old chunk கொண்டு வருகிறது. Answer outdated ஆகிறது, citation valid ஆனால் stale.

இங்கே citation failure இல்லை, data freshness failure. ஆனால் user-க்கு தெரியும்: citation இருந்தும் தவறான தகவல்.

Solution: Document versioning + citation metadata: `doc_id, version, chunk_hash`. Retrieval time-ல் freshness check. Generate போது citation-ல் version காட்டு.

### 7. Reasoning Challenge

உங்களிடம் RAG system உள்ளது. Users கேட்கும் claims-க்கு 95% accuracy வேண்டும். LLM க்கு 4k context கொடுக்கிறீர்கள். 20 chunks. Generation பிறகு citation மட்டும் கேட்கிறீர்கள்.

நீங்கள் கண்டீர்கள்: 12% answers-ல் citation-கள் claim-ஐ support செய்யவில்லை.

Latency budget 800ms. Cost sensitive.

இங்கே என்ன architecture மாற்றம் செய்வீர்கள்? Verify step சேர்க்கலாமா? அல்லது prompt மாற்றலாமா? ஏன்?

### 8. Key Takeaways

* Citation failure என்பது retrieval failure அல்ல, grounding + verification gap.
* Generate செய்தவுடன் cite செய்வது போதாது. Claim support-ஐ independent ஆக validate செய்ய வேண்டும்.
* High trust system-ல் extractive or verify-after-generate pattern முக்கியம்.
* Document versioning, chunk IDs, and citation metadata இல்லாமல் production RAG maintain செய்ய முடியாது.

இது ஏன் தேவைன்னு புரிஞ்சுது. எப்போ citation enforcement வேணும்னு தெரியும். எதை trade-off பண்ணுறோம்னு reason பண்ண முடியும்.
