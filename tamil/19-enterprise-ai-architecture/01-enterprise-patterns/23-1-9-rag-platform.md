# RAG platform

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.9 — Enterprise patterns

## 1. Problem

உங்க company-ல ஒரு enterprise LLM assistant இருக்கு. User கேட்கிறார்: "கடந்த quarter-ல எங்க top 5 customers-க்கு என்ன discount கொடுத்தோம்?"

LLM-க்கு அந்த knowledge இல்லை. Model training data-ல இல்லை. Real-time database-ல இருக்கு. PDFs, contracts, CRM notes, Slack threads எல்லாம் scattered ஆ இருக்கு.

இப்போ என்ன ஆகும்?

Direct LLM-க்கு கொடுத்தால் hallucination. Database-ல query எழுத சொன்னால் SQL தப்பாகும். PDF-ஐ முழுசா context window-க்குள் போட முடியாது.

Problem painful ஆகிறது: **LLM-க்கு accurate, up-to-date, company-specific information எப்படி கொடுப்பது, மற்றும் அது cite பண்ணும்படி எப்படி ensure பண்ணுவது?**

அதுதான் RAG platform தேவைப்படும் root cause.

## 2. Mental Model

RAG என்பது LLM-ஐ மூடி மூடி வைக்காமல், external knowledge-ஐ retrieve பண்ணி prompt-ல சேர்க்கிறது.

Mental model: **LLM = Reasoner, Vector DB + Index = Memory, Retriever = Librarian**

User query வந்ததும், librarian போய் relevant chunks-ஐ தேடி எடுக்கிறார். அவற்றை LLM-க்கு கொடுக்கிறார். LLM அதன் மேல் reason பண்ணி answer கொடுக்கிறது. Cite செய்ய முடியும்.

இது memorize பண்ணுவது அல்ல, lookup பண்ணுவது.

## 3. How It Works

Enterprise RAG platform என்பது 4 layers உடன் வேலை செய்யும்.

**Ingestion:** Documents, DB records, tickets, API data வரும். அவற்றை chunk பண்ணுவோம். Text cleaning, PII masking, access control tags சேர்ப்போம்.

**Embedding & Indexing:** Chunk-களை embedding model மூலம் vector ஆக மாற்றி vector database-ல store பண்ணுவோம். Metadata உடன்: source, owner, created_at, tenant_id, permissions.

**Retrieval:** User query வரும். Query-ஐயும் embed பண்ணுவோம். Similarity search பண்ணி top-k chunks எடுப்போம். Reranker உடன் quality improve பண்ணுவோம். Access control filter apply பண்ணுவோம்.

**Generation & Guardrails:** Retrieved chunks + user query + system prompt -> LLM-க்கு. Answer உருவாக்கி, citations உடன் திருப்பி அனுப்பு. Logging, telemetry capture.

இது simple ஆ தெரியும். Enterprise-ல complexity வருவது data freshness, scale, multi-tenancy, governance.

## 4. Architectural Reasoning

இது எப்போ useful?

* Knowledge constantly change ஆகும்
* Data sensitive, model-க்குள் bake பண்ண முடியாது
* Source cite வேண்டும், audit வேண்டும்
* Multiple data sources combine வேண்டும்

Alternatives என்ன?

* Fine-tuning: Knowledge static, costly, stale ஆகும். Every update retrain வேண்டும்.
* Prompt only: Context window limited, hallucination அதிகம்.
* Direct DB query: LLM SQL generate பண்ணி risk அதிகம்.

ஏன் RAG தேர்வு?

Because retrieval gives you **control, freshness, traceability**. Architect-க்கு data source மாற்றினாலும் LLM மாற்ற தேவை இல்லை.

Enterprise pattern என்பது platform level-ல centralized RAG service பண்ணுவது. Each app தனியாக vector DB வைக்காமல், shared ingestion pipeline, unified index, common retrieval API, governance policy.

## 5. Trade-offs

**Latency vs Recall:** More chunks retrieve பண்ணினால் recall அதிகம், ஆனால் LLM context window நிரம்பும், latency அதிகரிக்கும். Reranking கூடுச்செலவு.

**Freshness vs Cost:** Real-time ingestion செய்தால் cost அதிகம். Batch update செய்தால் stale data.

**Accuracy vs Generalization:** Chunk size சிறியது -> precise retrieval. பெரியது -> context loss ஆகும்.

**Security vs Usability:** Tenant isolation, row-level access control செய்தால் retrieval complex ஆகும். நீங்கள் metadata filter போடாமல் விட்டால் data leak.

Failure mode: Retrieval fails ஆனால் LLM still answer கொடுக்கும், அது hallucination ஆகும். அதனால் retrieval empty என்றால் no answer policy வேண்டும்.

## 6. Practical Example

Enterprise support assistant.

Data sources: Zendesk tickets, product docs, internal Confluence, code repos.

Ingestion pipeline: Daily batch + ticket create webhook. Chunk per ticket, metadata: customer tier, product, PII flag.

Index: Pinecone / pgvector, tenant_id partition.

Retrieval flow: User asks in Tamil. Query embed, filter by user department permissions, retrieve top 5 chunks, rerank, send to LLM with instruction: "Answer only from context, cite ticket ID".

Result: Agent gets accurate answer, user gets citation link, compliance team gets audit log.

Scalability: 10M documents. Embedding cost, vector DB sharding, cache hot queries.

## 7. Reasoning Challenge

உங்களிடம் multi-tenant SaaS product இருக்கு. ஒவ்வொரு customer-க்கும் தனித்தனி knowledge base இருக்கு. 500 tenants, ஒவ்வொருவருக்கும் 1M docs வரை. Global search latency < 500ms வேண்டும்.

இங்கே vector DB-ஐ எப்படி design பண்ணுவீர்கள்? Single shared index with tenant_id filter vs per-tenant index? Embedding model ஒன்றா அல்லது per tenant fine-tuned? Ingestion cost எப்படி control பண்ணுவீர்கள்?

ஏன் அப்படி தேர்வு செய்வீர்கள்? Trade-off என்ன?

## 8. Key Takeaways

* RAG solves **knowledge freshness and traceability**, not just accuracy.
* Enterprise RAG platform = ingestion + indexing + retrieval + governance, not just vector search.
* Retrieval quality decides answer quality. LLM powerful ஆனாலும் garbage in garbage out.
* Every architectural choice here is trade-off between latency, cost, freshness, security.

இதை புரிஞ்சா, நீங்கள் RAG-ஐ ஒரு feature இல்ல, ஒரு platform மாதிரி design பண்ண முடியும்.
