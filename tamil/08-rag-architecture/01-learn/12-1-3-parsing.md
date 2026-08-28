# Parsing

> **Learning Path:** RAG Architecture
> **Section:** 12.1.3 — Learn

## 1. Problem

உங்க RAG system-க்கு user question வருது. அதுக்கு relevant context கொண்டு வரணும். அதுக்கு முதல்ல source documents-ஐ process பண்ணணும்.

Source என்ன? PDF, HTML, Confluence page, CSV, code repo, support tickets.

இந்த raw documents-ஐ நேரடியாக vector database-ல தள்ளினால் என்ன ஆகும்?

ஒரு 50-page PDF ஒரே chunk-ஆ இருந்தா embedding அர்த்தமில்லாமல் போகும். Context window-க்கு அப்பால் போய்விடும். Search-ல precision குறையும்.

மறுபுறம் document-ஐ மிகச் சிறிய sentences-ஆ cut பண்ணினால் meaning துண்டாகும். "Payment failed" என்பதற்கு காரணம் எந்த paragraph-ல இருக்கு என்று தெரியாது.

Parsing இல்லாமல் RAG வேலை செய்யாது. Parsing என்பது raw source-ஐ structured, retrievable units-ஆ மாற்றுவது.

> What goes wrong if we don't have this? Garbage in, garbage out. Wrong retrieval, wrong generation.

## 2. Mental Model

Parsing = **Extract → Clean → Chunk → Enrich**.

Extract: File format-ல இருந்து text-ஐ எடுப்பது.
Clean: Noise, boilerplate, headers, footers நீக்குவது.
Chunk: Logical units-ஆ பிரிப்பது.
Enrich: Metadata, hierarchy, section titles சேர்ப்பது.

ஒரு document-ஐ புத்தகம் என்று நினைத்துக்கொள்ளுங்கள். Parsing என்பது அதன் table of contents, chapter, page numbers புரிந்து, meaningful paragraphs-ஆ வெட்டி, ஒவ்வொரு chunk-க்கும் "இது எந்த chapter-ல இருந்து வந்தது" என்ற label கொடுப்பது.

## 3. How It Works

RAG-ல parsing என்பது இரண்டு layer-ஆ வேலை செய்யும்.

**Format Parsing:** PDF, DOCX, HTML, Markdown, CSV, JSON. இதற்கு PyPDF, unstructured, langchain document loaders போன்றவை உபயோகம். Table extraction, image OCR தேவைப்படலாம்.

**Semantic Chunking:** Fixed size tokens-ஆ cut பண்ணுவதை விட, meaning-ஐ preserve பண்ணி chunk பண்ணுவது.

எடுத்துக்காட்டு: `chunk_size = 800 tokens`, `overlap = 100 tokens`. Overlap இருப்பதால் sentence cross boundary-ல cut ஆவது தடுக்கப்படும்.

இன்னும் நல்லது: **Structure-aware chunking**. Heading hierarchy-ஐ பார்த்து chunk boundary set பண்ணுவது. `## Pricing` heading கீழ் வரும் content ஒன்றாக இருக்கும். 

Metadata attach பண்ணுவது முக்கியம்: source_url, document_id, page_number, section_title, created_at. Retrieval-ல rerank செய்யும் போது இது உதவும்.

## 4. Architectural Reasoning

Parsing எப்போது useful ஆகிறது?

Source heterogeneous-ஆ இருக்கும் போது. PDFs மற்றும் Confluence pages இரண்டும் இருந்தால் common pipeline தேவை.

Document size பெரியதாக இருக்கும் போது. Long context-ஐ retrieve செய்ய முடியாது.

Retrieval quality consistency தேவைப்படும் போது.

Alternatives என்ன?

* Naive chunking: character count-ஆல் split. வேகமாக, ஆனால் meaning loss.
* Recursive chunking: separators `-`, `##`, paragraph.
* Semantic chunking: embedding similarity-ஆல் boundary decide.

ஆர்கிடெக்ட் எதை தேர்வு செய்வார்? 
Domain-ஐ பார்த்து. Legal contract-ல section boundary மிக முக்கியம். Support chat-ல conversation turn boundary முக்கியம். Code repo-ல function boundary முக்கியம்.

## 5. Trade-offs

**Chunk size vs retrieval precision.** பெரிய chunk = more context, but noisy retrieval. சிறிய chunk = precise, but context fragmented.

**Parsing depth vs cost and latency.** Deep parsing, table extraction, OCR, layout analysis செய்தால் quality உயரும். ஆனால் pipeline slow ஆகும், cost அதிகம்.

**Structure preservation vs simplicity.** Heading hierarchy keep பண்ணினால் retrieval better. ஆனால் parser complex ஆகும். Flat text easy.

**Re-parse frequency.** Source document update ஆனால் re-parse தேவை. Incremental parsing vs full re-index என்பது operational complexity.

Failure modes: Parser PDF table-ஐ நேர்கோட்டு text-ஆ மாற்றி விட்டால் meaning மாறும். Heading missing ஆனால் hierarchy lost. Chunk overlap இல்லாமல் போனால் sentence half cut.

## 6. Practical Example

Enterprise knowledge base RAG.

Sources: Product docs PDF, internal wiki HTML, API spec Markdown.

Pipeline:
1. Ingest job: S3-ல புதிய file வந்ததும் trigger.
2. Format parser: unstructured.io-ல PDF-ஐ extract. Tables-ஐ markdown-ஆ மாற்று.
3. Clean: page headers/footers, "Confidential" watermark நீக்கு.
4. Structure-aware chunk: Heading `##` level-ஐ respect பண்ணி chunk. max 1000 tokens, overlap 150.
5. Enrich metadata: doc_id, source_type, section_path, page.
6. Embed and store in vector DB with metadata filter.

Query time-ல user asks "Refund policy for enterprise plan". Retrieval-ல metadata filter `source_type = product_docs` + semantic search சேர்ந்து hit rate improve ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் 2 மில்லியன் support tickets இருக்கு. ஒவ்வொரு ticket-ம் average 3,000 words, chat format. User message, agent message alternate ஆகிறது.

நீங்கள் RAG-ல retrieve பண்ண வேண்டும். அப்போது நீங்கள் chunk எப்படி define செய்வீர்கள்? Fixed 800 token window போதுமா? Conversation context தொலைந்து விடாமல் இருக்க என்ன parsing strategy எடுப்பீர்கள்? ஏன்?

## 8. Key Takeaways

* Parsing என்பது extraction அல்ல, meaning-ஐ preserve செய்யும் structured breakdown.
* Chunking strategy retrieval quality-ஐ நேரடியாக தீர்மானிக்கும். Size, overlap, structure awareness முக்கியம்.
* Metadata without parsing is blind. Source, hierarchy, position ஆகியவை reranking-க்கு அவசியம்.
* Every parsing decision is a trade-off between fidelity, cost, latency, and operational complexity.
