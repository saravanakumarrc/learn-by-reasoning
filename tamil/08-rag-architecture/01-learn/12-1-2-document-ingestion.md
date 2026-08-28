# Document ingestion

> **Learning Path:** RAG Architecture
> **Section:** 12.1.2 — Learn

## 1. Problem

உங்களிடம் ஒரு RAG system இருக்கு. LLM-க்கு user question கிடைக்கும்போது relevant context தேடி கொடுக்கணும். அந்த context எங்கிருந்து வரும்? PDFs, Word docs, internal wikis, tickets, product specs, meeting notes.

பிரச்சனை என்ன? Raw document-ஐ நேரடியாக LLM-க்கு கொடுக்க முடியாது. Document மிக பெரியது, unstructured ஆக இருக்கும், noise நிறைய இருக்கும். 

நீங்கள் 50,000 pages PDF collection-ஐ உள்ளே போடணும். ஒரே batch-ல எடுக்க முடியாது. File format வேறுபடும், tables, images, scanned pages இருக்கும். Document update ஆகும்போது re-ingest பண்ணணும். 

**What goes wrong if we don't have proper ingestion?** Search results irrelevant ஆகும், hallucination அதிகரிக்கும், stale data திரும்பும், pipeline fail ஆகும். Ingestion என்பது data quality-ஐ control செய்யும் gate.

## 2. Mental Model

Document ingestion = **raw document -> usable chunks with metadata -> vector + keyword store**.

அதாவது ஒரு factory line மாதிரி. Incoming document வரும். அதை clean பண்ணுவோம், structure எடுப்போம், அர்த்தமுள்ள pieces ஆக cut பண்ணுவோம், அதற்கு embedding generate பண்ணுவோம், மற்ற metadata ஒட்டுவோம். இறுதியில் retrieval layer-க்கு ready ஆகும்.

Core idea: LLM context window limited. அதனால் document-ஐ small, semantically coherent chunks ஆக split பண்ணணும். ஒவ்வொரு chunk-க்கும் meaning capture பண்ண embedding வேண்டும். Source traceability வேண்டும்.

## 3. How It Works

ஒரு typical ingestion pipeline:

**1. Ingest & Normalize**
Document source-ல இருந்து fetch. PDF, DOCX, HTML, Markdown. Format specific parser use பண்ணுவோம். `pdfplumber`, `docling`, `unstructured`. Scanned PDF என்றால் OCR வேண்டும்.

**2. Preprocess & Clean**
Noise remove: headers, footers, page numbers, tables of contents. Language detect. Text extraction. For technical docs, code blocks preserve பண்ணணும்.

**3. Chunking**
இது முக்கியமானது. Fixed size token window vs semantic chunking.

Simple: 500-1000 tokens, overlap 50-150 tokens.
Better: Section boundaries respect பண்ணி split. Headings, paragraphs, tables அடிப்படையில் split. Overlap maintain பண்ணுவது context loss தடுக்கும்.

**4. Enrich Metadata**
`doc_id, source_url, title, author, created_at, updated_at, chunk_index, page_number`. RAG-ல citation-க்கு இது must. Access control tag சேர்க்கலாம்.

**5. Embed & Index**
Chunk text-ஐ embedding model-ல போட்டு vector generate. அதை vector database-ல store. மேலும் keyword index / BM25 index-க்கு plain text store.

**6. Lifecycle Management**
Document update ஆனால் detect செய்து re-ingest. Versioning. Delete செய்தால் orphan chunks clean.

Pipeline ஆனது asynchronous ஆக இருக்கும். Producer - consumer queue மூலம் scale ஆகும்.

## 4. Architectural Reasoning

Document ingestion useful ஆகும் போது:
- Source heterogeneous, unstructured
- Retrieval accuracy முக்கியம்
- Data frequently changes
- Audit / citation தேவை

Alternatives:
- **On-demand ingestion**: Query வரும்போது மட்டும் parse செய்யலாம். Simple ஆனால் latency high, repeat work.
- **Pre-computed static index**: Batch nightly. Simple ஆனால் freshness குறைவு.
- **Streaming ingestion**: Document change ஆன உடனே pipeline trigger. Best for live systems.

Architect choose பண்ணும்போது கேட்க வேண்டியது:
- Chunking strategy retrieval quality-ஐ மாற்றும். Technical specs-க்கு larger chunk with table context தேவை. Chat logs-க்கு smaller.
- Embedding model என்ன? General vs domain fine-tuned.
- Metadata schema consistent இருக்கணும். இல்லை என்றால் filter query fail ஆகும்.
- Idempotency வேண்டும். Same document மீண்டும் ingest ஆனால் duplicate vector create ஆகக்கூடாது.

## 5. Trade-offs

**Chunk size vs retrieval precision**
சிறிய chunk = precise retrieval ஆனால் context loss. பெரிய chunk = context retain ஆனால் noise அதிகம், vector dilution.

**Sync vs async ingestion**
Sync = immediate visibility, ஆனால் upload slow, failure risk. Async = smooth UX, ஆனால் eventual consistency.

**Normalization vs fidelity**
Aggressive clean = cleaner embeddings. ஆனால் tables, formulas distort ஆகலாம். Domain docs-ல அசல் structure retain முக்கியம்.

**Cost vs quality**
Better parser, OCR, larger embedding model, semantic chunking = better quality ஆனால் cost & latency அதிகம்.

Failure modes:
- Parser fail -> silent data loss. Monitoring வேண்டும்.
- Chunk boundary mid-sentence -> meaning break.
- Metadata missing -> citation impossible.
- Re-ingest without dedupe -> vector DB bloat.

## 6. Practical Example

Enterprise knowledge base: Internal Confluence + product PDFs + support tickets.

Architecture:
`Confluence webhook -> SQS -> Ingestion Worker -> Parser -> Chunking Service -> Embedding Service -> Pinecone + Postgres`.

Document update ஆனால் webhook trigger. Worker document fetch, version check. Existing `doc_id` இருந்தால் old chunks delete பண்ணி new chunks insert. Metadata-ல `access_group` சேர்க்கப்பட்டு retrieval time filter.

Chunking: Heading aware. `## Architecture` section முழுவதும் ஒரே chunk ஆக வைக்க. Table இருந்தால் table as one chunk.

Result: User asks "Payment retry policy என்ன?" -> system relevant chunk retrieve பண்ணி source link + page number உடன் answer generate.

## 7. Reasoning Challenge

உங்களிடம் daily 10,000 new support tickets வருகிறது. ஒவ்வொரு ticket-ம் average 800 words. Customer query-க்கு real-time answer தேவை. Ticket update ஆகும். 

இங்கே ingestion pipeline-ஐ எப்படி design பண்ணுவீர்கள்? Chunk size என்ன வைப்பீர்கள்? Sync or async? Deduplication எப்படி handle பண்ணுவீர்கள்? ஏன்?

## 8. Key Takeaways

- Ingestion என்பது data quality gate. Bad input = bad retrieval எப்போதும்.
- Chunking strategy மற்றும் metadata design retrieval accuracy-ஐ decide செய்யும்.
- Ingestion asynchronous, idempotent, observable ஆக இருக்கணும்.
- Every architectural choice creates trade-off: freshness vs cost, precision vs context, simplicity vs fidelity.
