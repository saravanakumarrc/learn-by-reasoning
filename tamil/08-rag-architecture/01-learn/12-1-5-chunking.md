# Chunking

> **Learning Path:** RAG Architecture
> **Section:** 12.1.5 — Learn

### 12.1.5 — Chunking

## 1. Problem

உங்க RAG system-ல ஒரு 100 page PDF-ஐ, ஒரு 2000 line code file-ஐ, அல்லது ஒரு long customer conversation-ஐ retrieve பண்ண வேண்டியிருக்கு.

அதை முழுசா ஒரே embedding-ஆ convert பண்ணினால் என்ன ஆகும்?

Query specific ஆ இருந்தாலும், embedding average ஆகிவிடும். "Refund policy for annual plan" என்று கேட்டாலும், document-ல உள்ள எல்லா information-ம் mix ஆகி response fuzzy ஆக வரும்.

மறுபுறம், ஒவ்வொரு sentence-ஐயும் தனியாக embedding பண்ணினால், context போய்விடும். "Annual plan" என்றால் என்ன என்பதை அடுத்த paragraph தான் explain பண்ணும்.

**Pain point:** LLM-க்கு context window limit இருக்கு. Retrieval செய்த information relevant ஆகவும், self-contained ஆகவும் இருக்கணும். அதுக்கு document-ஐ எப்படி cut பண்ணுவது?

இங்கே தான் chunking தேவைப்படுகிறது.

## 2. Mental Model

Chunking என்பது ஒரு document-ஐ small, retrievable, context-rich pieces ஆக split பண்ணுவது.

நினைச்சுக்கோங்க: ஒரு புத்தகத்தை library-ல index பண்ணும்போது, முழு புத்தகத்தையும் ஒரே card-ல வைக்க மாட்டீங்க. Chapter, section level-ல தான் வைப்பீங்க.

Chunk = retrieval unit. Embedding ஆகும் unit. LLM-க்கு அனுப்பப்படும் unit.

ஒரு நல்ல chunk என்பது:
* Self-contained ஆக இருக்கும்
* Query-க்கு பதில் கொடுக்கும் அளவுக்கு context உள்ளது
* மிகப் பெரியதாகவோ மிகச் சிறியதாகவோ இல்லை

## 3. How It Works

Basic flow:

`Document → Preprocess → Split into chunks → Add overlap / metadata → Embed each chunk → Store in vector database`

இரண்டு முக்கிய decisions:

**Chunk size:** tokens-ல. பொதுவாக 512 - 1500 tokens range. Embedding model-ன் context window-க்கு ஏற்ப.

**Chunking strategy:**

* **Fixed size + overlap:** எளிமையானது. 1000 tokens எடு, 150 tokens overlap விடு. Sentence boundary-ல cut பண்ணு. RAG-க்கு safe default.
* **Semantic / Recursive:** Heading, paragraph, sentence structure-ஐ பார்த்து split பண்ணு. `recursive_character_text_splitter` போல. Semantic coherence காக்கும்.
* **Sentence / Paragraph based:** Small docs-க்கு okay. Context loss ஆகும் risk உண்டு.
* **Hybrid:** Large chunk for context + small chunk for retrieval. Some systems two-level hierarchy use பண்ணும்.

Overlap ஏன்? ஒரு chunk cut ஆனால் meaning half break ஆகிவிடக்கூடாது. 10-20% overlap context continuity காப்பாற்றும்.

Metadata முக்கியம்: source file, page number, section heading, chunk_id. Retrieval-க்கு பிறகு citation கொடுக்க இது தேவை.

## 4. Architectural Reasoning

Chunking என்பது retrieval quality-ஐ decide பண்ணும்.

**When it helps:**
* Long documents, multi-page PDFs, conversation history, code repos
* Query specific information தேவை
* Hallucination குறைக்க citation தேவை

**Alternatives:**
* Whole document embedding: Small docs மட்டும் work ஆகும். 1-2 page வரை.
* No chunking + LLM summarization first: Summarization loss ஆகும். Need re-run.

Architect ஆக நீங்கள் தேர்வு செய்வது என்ன?
* Domain matters. Legal contract-ல clause boundary முக்கியம். Support chat-ல conversation turn boundary முக்கியம். Code-ல function boundary முக்கியம்.
* Retrieval latency vs recall trade-off. Small chunks = more vectors = larger index, higher recall but more noise.

## 5. Trade-offs

**Chunk size vs Context**
* Small chunk: precise retrieval, but context missing. "Refund" என்றால் "annual plan" என்றால் என்ன என்பது தெரியாது.
* Large chunk: context rich, but embedding dilute ஆகும். Irrelevant info கூட வந்துவிடும்.

**Overlap vs Cost**
Overlap கொடுத்தால் redundancy increase ஆகும். Vector DB cost, embedding cost increase. ஆனால் boundary cut issues குறையும்.

**Structure aware vs Simple**
Recursive split quality நல்லது. ஆனால் preprocessing complex. Fixed size fast and robust.

**Failure modes:**
* Over-chunking: same info 10 chunks-ல repeat ஆகும். Retrieval noisy.
* Under-chunking: LLM context window overflow. Relevant info truncate ஆகும்.
* No overlap: cut in middle of sentence → embedding meaningless.
* Metadata missing: citation இல்லாமல் trust இல்லை.

## 6. Practical Example

Enterprise support RAG.

உங்களிடம் 5 ஆண்டு support tickets இருக்கு. ஒவ்வொன்றும் 3-4 pages.

Strategy:
* Recursive splitter use பண்ணு: Ticket → sections by heading: Issue Summary, Steps Tried, Resolution.
* Chunk size ~800 tokens, overlap 120 tokens.
* Metadata: ticket_id, product, date, customer tier.

Query: "Annual plan user cannot cancel subscription on iOS"

Retrieval ல Resolution section-ன் chunk மட்டும் வரும். Context முழுவதும் இருக்கும். LLM-க்கு கொடுக்கும்போது citation கூட கொடுக்க முடியும்.

இங்கே fixed size மட்டும் use பண்ணி இருந்தால், Resolution cut ஆகி இருக்கும்.

## 7. Reasoning Challenge

உங்களிடம் codebase RAG build பண்ண வேண்டும். 1 million lines Python code.

ஒரு function average 50 lines. File average 500 lines.

நீங்கள் chunking எப்படி design செய்வீர்கள்? Fixed size tokens vs function boundary? Overlap வேண்டுமா? ஏன்?

நினைச்சுப்பாருங்க: ஒரு query "payment retry logic எப்படி work ஆகிறது?" என்றால், ஒரு function மட்டும் போதுமா? அல்லது class level context வேண்டுமா?

## 8. Key Takeaways

* Chunking = retrieval unit design. Embedding quality retrieval quality-ஐ decide பண்ணும்.
* Chunk should be self-contained and context-rich. Size is a trade-off, not a rule.
* Structure aware split > blind split. Overlap boundary problems-ஐ குறைக்கும்.
* Metadata and chunking strategy together தான் good RAG-ஐ கொடுக்கும்.
* Every chunking decision creates a new trade-off: recall vs precision vs cost vs latency.

இது ஏன்னா, எப்போ use பண்ணணும், எதுக்காக choose பண்ணுறோம்னு reason பண்ண முடியுமா?
