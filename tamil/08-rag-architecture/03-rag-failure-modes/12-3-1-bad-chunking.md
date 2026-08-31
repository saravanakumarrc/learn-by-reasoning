# Bad chunking

> **Learning Path:** RAG Architecture
> **Section:** 12.3.1 — RAG failure modes

## 1. Problem

நீங்கள் ஒரு RAG system build பண்ணியிருக்கீங்க. Document-ஐ upload பண்ணி, chunk பண்ணி, embedding பண்ணி, vector database-ல store பண்ணி, query வந்தா retrieve பண்ணி LLM-க்கு கொடுக்கிறீங்க.

Query வருது: *"நம்ம customer refund policy-ல 30 days க்கு மேல return accept பண்ண மாட்டோம்னு சொல்லியிருக்காங்களா?"*

System answer தருது: *"நாங்கள் திரும்புதலை ஏற்றுக்கொள்ளவில்லை"* — ஆனால் அது ஒரு வேறு product category-க்கான policy.

ஏன் தப்பு? Retrieve ஆனது சரியான document-தான், ஆனால் chunk cut ஆன இடத்தில் context போய்விட்டது. Policy-ல 30 days rule இருந்தது, ஆனால் அது next chunk-ல இருந்தது. LLM-க்கு கிடைத்தது incomplete sentence.

இது **Bad chunking** failure. Information fragmented ஆகி, meaning lost ஆகிறது.

> What goes wrong if we don't have this? Wrong retrieval, hallucination, incomplete answers, user trust loss.

## 2. Mental Model

Chunking என்பது ஒரு document-ஐ LLM-க்கு digestible pieces ஆக cut பண்ணுவது. ஆனால் cut செய்யும் இடம் தப்பா இருந்தால், ஒரு concept அரை குறையாக பிரிந்து விடும்.

நினைச்சுக்கோங்க: ஒரு book-ஐ page-ஆக cut பண்ணுவது. Page எல்லைக்குள் ஒரு sentence நடுவில் cut ஆனால் படிக்க முடியாது.

Embedding model ஒரு chunk-க்கு vector உருவாக்கும். அந்த vector அந்த chunk-ன் meaning-ஐ represent பண்ணும். Chunk meaningless ஆனால் vector-ம் useless.

நல்ல chunk = self-contained, semantically complete, context preserve பண்ணும்.

## 3. How It Works

RAG pipeline-ல chunking மூன்று விஷயங்களை control பண்ணும்:

* **Size**: tokens per chunk. 500 vs 2000.
* **Overlap**: இரண்டு chunk-க்கு இடையே common tokens.
* **Boundary**: sentence, paragraph, heading, semantic boundary-ல cut பண்ணுவதா?

Bad chunking வரும் போது:
* **Overly small chunks**: ஒரு sentence மட்டும். Subject-verb-object துண்டாகி, meaning இல்லாமல் போகும். Embedding weak ஆகும்.
* **Overly large chunks**: ஒரு chunk-ல 5 topics இருக்கும். Query specific topic-க்கு retrieve ஆனாலும் noise அதிகம். LLM confuse ஆகும், context window waste ஆகும்.
* **Wrong boundary**: Table row cut ஆகி header இல்லாமல் போகும். List item நடுவில் cut ஆகும். Code block split ஆகும்.
* **No overlap**: Continuation இரண்டு chunk-க்கும் இடையே link இல்லாமல் போகும். 1st chunk end-ல "We do not accept returns after..." 2nd chunk start "30 days" என்று இருந்தால் retrieve ஒன்று மட்டும் வந்தால் answer incomplete.

## 4. Architectural Reasoning

Chunking ஏன் முக்கியம்? ஏனென்றால் vector search என்பது chunk level-ல தான் நடக்கும்.

Constraint பாருங்கள்:
* LLM context window limited. Relevant information மட்டும் கொடுக்க வேண்டும்.
* Embedding quality depends on semantic completeness.
* Retrieval recall and precision trade-off.

When bad chunking happens, you get:
* Low recall: சரியான information இருந்தாலும் chunk split ஆனதால் query match ஆகாது.
* Low precision: Irrelevant noise retrieve ஆகும்.

Architect decision என்ன?
* Fixed-size chunking with overlap vs semantic chunking.
* Structure-aware chunking: Markdown headings, tables, sections respect பண்ணுவது.

Alternative: RAG without chunking? Entire document ஒரே chunk ஆக வைக்கலாம். ஆனால் document 50k tokens ஆனால் LLM context overflow ஆகும், retrieval useless.

எனவே cut பண்ண வேண்டும், ஆனால் meaning preserve பண்ணி cut பண்ண வேண்டும்.

## 5. Trade-offs

**Size vs Specificity**: Small chunk = specific retrieval, ஆனால் context loss. Large chunk = context rich, ஆனால் noise அதிகம், vector diluted.

**Overlap cost**: Overlap வைத்தால் redundancy அதிகம், vector DB size, cost, indexing time increase ஆகும். ஆனால் boundary cut risk குறையும்.

**Semantic chunking complexity**: NLP model use பண்ணி topic boundary detect பண்ணலாம். Accuracy better, ஆனால் pipeline complex, latency, cost அதிகம்.

**Failure modes**:
* Hallucination from partial context
* Contradictory chunks retrieve ஆனால் LLM confused
* Table / code split ஆனால் data corruption
* Multi-language document-ல chunk boundary wrong ஆனால் meaning shift

## 6. Practical Example

Enterprise knowledge base: HR policy PDFs.

Bad approach: 1000 tokens fixed chunk, no overlap, naive split by characters.
Result: "Refund will be processed within" என்று ஒரு chunk முடியும். "7 business days after approval" அடுத்த chunk-ல start ஆகும். Query: "refund processing time?" Retrieve first chunk மட்டும் ஆனால் answer incomplete.

Good approach: Sentence-aware chunking + 150 token overlap. Heading preserve. Table rows as one chunk.

Query retrieve ஆனால் chunk contains full sentence with context: "Refund will be processed within 7 business days after approval is received."

இங்கே architecture choice: Pre-processing pipeline-ல `chunking strategy` config. Document type-க்கு தகுந்த மாதிரி strategy மாற்றலாம்: policy doc -> semantic chunking, log file -> fixed size with overlap, code repo -> file level + function level.

## 7. Reasoning Challenge

உங்களிடம் ஒரு customer support RAG system உள்ளது. Documents mix ஆக இருக்கு: FAQs, long conversation transcripts, product spec tables.

நீங்கள் fixed 500 token chunk + 50 token overlap use பண்ணியிருக்கீங்கள். Users complain answers incomplete, especially for refund policy and specs.

நீங்கள் என்ன செய்வீர்கள்? Chunk size மாற்றுவீர்களா? Overlap மாற்றுவீர்களா? Semantic boundary use பண்ணுவீர்களா? ஏன்?

## 8. Key Takeaways

* Chunking என்பது retrieval quality-ன் foundation. Bad chunk = bad RAG, even with perfect embedding model.
* Self-contained and semantically complete chunk-ஐ target பண்ணுங்கள். Cut என்பது meaning boundary-ல செய்ய வேண்டும், token count-ல மட்டும் அல்ல.
* Size, overlap, boundary மூன்றும் trade-off. Document type, query pattern, cost constraints-க்கு ஏற்ப tune பண்ணுங்கள்.
* Chunking failure-ஐ தடுக்க overlap + structure-aware splitting + chunk validation உதவும்.
