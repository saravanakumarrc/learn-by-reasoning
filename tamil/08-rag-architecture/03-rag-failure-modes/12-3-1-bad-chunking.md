# Bad chunking

> **Learning Path:** RAG Architecture
> **Section:** 12.3.1 — RAG failure modes

## 1. Problem

RAG system-ல உனக்கு query வருது. LLM context-ல retrieve பண்ண document chunks கொடுக்கிறோம். ஆனாலும் answer தப்பா வருது, hallucination பண்ணுது, அல்லது relevant information miss பண்ணுது.

ஏன்? 

ஏன்னா retrieve பண்ணது தான் relevant ஆனது இல்லை. Embedding similarity match ஆகல. 

அதுக்கு முக்கிய காரணம்: **chunking தப்பா இருக்கு.**

உதாரணமா ஒரு user profile-ல "பயனர் Chennai-ல இருக்கார். அவருக்கு premium plan வேண்டும்." இது ஒரே sentence-ல தொடர்புடையது. நீ chunking பண்ணும்போது ஒன்றை cut பண்ணி மற்றதை வேற chunk-ல போட்டுட்டா, query "user city?" என்றால் embedding match ஆகும். ஆனால் chunk-ல city மட்டும் இருக்கும், plan info இல்லை. அல்லது இரண்டும் ஒன்றாக இருந்தாலும் chunk boundary தப்பா வந்து context இழந்துவிடும்.

> Bad chunking என்றால் information-ஐ தவறான துண்டுகளாக வெட்டுவது. அதனால் meaning break ஆகிறது, retrieval தோல்வி அடைகிறது.

## 2. Mental Model

RAG-ல chunk என்பது retrieval-க்கு basic unit.

LLM-க்கு கொடுக்கும் context = retrieved chunks.

Embedding model-க்கு புரிய வேண்டியது chunk-இன் meaning.

எனவே chunk = **self-contained meaning unit**.

நல்ல chunking என்பது:

* ஒரு chunk-ல ஒரு logical idea முழுமையாக இருக்க வேண்டும்
* Related facts ஒன்றாக இருக்க வேண்டும்
* Chunk boundary-ல meaning cut ஆகக்கூடாது

Bad chunking என்பது இதற்கு எதிரானது.

## 3. How It Works

Chunking என்பது மூன்று decisions:

**1. Chunk size:** Too small → context loss. Too large → dilution, token waste, irrelevant noise.
Typical sweet spot 300-800 tokens, ஆனால் content-ஆல் மாறும்.

**2. Overlap:** Boundary-ல information repeat ஆகுமா?
Overlap இல்லாமல் cut பண்ணினால் sentence half-ல முடிந்து விடும். 10-20% overlap meaning preserve பண்ணும்.

**3. Strategy:** Fixed size vs semantic.

Fixed size: every N tokens cut. Simple ஆனால் sentence, paragraph break மதிக்காது.
Semantic chunking: topic boundary, heading, paragraph, sentence coherence பார்த்து cut. Better meaning preservation.

Bad chunking-ன் விளைவு:
* **Split entity:** "John Doe" ஒரு chunk-ல first name மட்டும், last name அடுத்த chunk-ல.
* **Split fact:** "invoice amount is 5000 and due date is 2025-10-01" - amount ஒரு chunk, date அடுத்த chunk.
* **Merge unrelated:** 3 different topics ஒரே chunk-ல. Embedding average ஆகி எதுக்கும் match ஆகாது.

## 4. Architectural Reasoning

Bad chunking எப்போது painful ஆகிறது?

* **Conversational / multi-hop queries:** "அந்த user எந்த city-ல இருக்கார்? அவர் plan என்ன?" இரண்டு facts ஒன்றாக தேவை.
* **Structured data in text:** tables, forms, specs. Row cut ஆனால் meaning lost.
* **Long documents:** legal contracts, support tickets, research papers.

Alternatives:
* **Semantic chunking with sentence boundaries:** `langchain` `RecursiveCharacterTextSplitter` with separators `["\n\n", "\n", ".", " "]`
* **Metadata aware chunking:** heading + paragraph together.
* **Hybrid:** large chunk for embedding, smaller sub-chunks for reranking.

Architect ஆக நீ choose பண்ணுவது: domain-ஆல் மாறும்.

Support ticket-க்கு semantic chunking + 200 token overlap நல்லது. Code repo-க்கு function level chunking நல்லது.

## 5. Trade-offs

**Small chunks vs large chunks**
Small = precise retrieval, ஆனால் context missing. Large = context rich, ஆனால் noise + similarity dilute.

**Overlap vs storage cost**
Overlap = better continuity, ஆனால் vector DB size அதிகம், cost அதிகம்.

**Semantic vs fixed**
Semantic = better quality, ஆனால் processing slow, complex. Fixed = fast, deterministic, ஆனால் meaning break risk.

**Failure modes:**
* **Lost co-reference:** "அவர்..." previous sentence-ல யார் என்று தெரியாது.
* **Unanswerable chunk:** chunk-ல subject இருக்கு ஆனால் object இல்லை.
* **Retrieval miss:** query semantically close ஆனால் chunk-இன் embedding diluted ஆகி top-k-ல வராது.

## 6. Practical Example

Enterprise support RAG system.

Document: Customer ticket.

Bad chunking with fixed 500 chars no overlap:
Chunk1 ends with "... customer requested refund because"
Chunk2 starts with "the product arrived damaged"

Query: "Why did customer request refund?"

Chunk1-ல reason incomplete. Chunk2-ல reason இருக்கு ஆனால் "because" link இல்லை. LLM hallucinate பண்ணும்: "reason not found".

Good chunking: semantic split at sentence, overlap 100 chars.

Chunk1: "... customer requested refund because the product arrived damaged. The damage was visible on packaging."
Query-க்கு match ஆகும், context complete.

## 7. Reasoning Challenge

உன்னிடம் 10,000 product spec PDFs இருக்கு. ஒவ்வொன்றிலும் specs table உள்ளது. Query வரும்: "Model X123 battery capacity?"

நீ fixed 1000 token chunking பண்ணி overlap 0 வச்சுருக்கே. Retrieval quality குறைவா இருக்கு. 

இங்கே chunking-ல என்ன பிரச்சனை வரலாம்? நீ strategy-ஐ எப்படி மாற்றுவாய்? Trade-off என்ன?

## 8. Key Takeaways

* Chunk என்பது retrieval unit. Meaning break ஆனால் RAG fail ஆகும்.
* Bad chunking = split fact, split entity, merge unrelated. இதனால் embedding match தோல்வி.
* Chunk size, overlap, strategy மூன்றும் domain-ஆல் மாறும். One size fits all இல்லை.
* Semantic boundary மதித்து chunk பண்ணு. Self-contained meaning-ஐ காப்பாற்று.
* Chunking தவறு என்றால் better retriever, better LLM எதுவும் காப்பாற்றாது.
