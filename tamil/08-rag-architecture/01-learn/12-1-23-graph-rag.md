# Graph RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.1.23 — Learn

## 12.1.23 — Graph RAG

### 1. Problem

Vector RAG work ஆகுது, ஆனா ஒரு real problem வரும்.

User கேட்கிறார்: *"என் account-ல 2024-ல் யார் approve பண்ணின purchase orders, அவங்க எந்த vendor-கிட்ட most spending பண்ணினார்கள்?"*

Vector DB-ல நீங்கள் documents-ஐ chunks ஆக்கி embed பண்ணீர்கள். இந்த கேள்விக்கு answer கிடைக்குமா?

Chunk ஒன்று PO-க்கு, ஒன்று approval log-க்கு, ஒன்று vendor invoice-க்கு. இவை எல்லாம் connection-ஐ capture பண்ணாது. Similarity search தூரத்தை மட்டும் பார்க்கும்.

Result: fragmented answers, hallucination, multi-hop reasoning தோல்வி.

**Problem என்ன?** Relationship உள்ள data-வை flat vectors ஆக்கி தூரம் மட்டும் measure பண்ணும்போது, *who approved what, who is connected to whom* போன்ற graph nature questions பதில் வராது.

அப்போ என்ன தேவை? Entities மற்றும் அவற்றுக்கு இடையே உள்ள relations-ஐ explicit ஆக keep பண்ண வேண்டும்.

### 2. Mental Model

Graph RAG = Vector RAG + Knowledge Graph.

நினைத்துக்கொள்ளுங்கள்: documents-ல இருந்து நீங்கள் entities extract பண்ணி, அவற்றை nodes ஆக்குறீர்கள். Relations ஆக edges ஆக்குறீர்கள். பிறகு இந்த graph-ஐ LLM புரிந்துகொள்ளும் வகையில் traverse பண்ணி, relevant sub-graph-ஐ retrieve பண்ணி generation-க்கு கொடுக்கிறீர்கள்.

Vector மட்டும்: *"இந்த chunk இந்த query-க்கு பக்கத்தில் இருக்கிறதா?"*
Graph + Vector: *"இந்த entity-ஐ start பண்ணி, 2 hops வரை என்ன connect ஆகிறது?"*

### 3. How It Works

Pipeline simple:

**1. Extraction:** LLM or rule-based parser documents-ல இருந்து entities: `Person, Vendor, PO, Account` மற்றும் relations: `approved_by, purchased_from, belongs_to` extract பண்ணும்.

**2. Graph Build:** Entities nodes ஆக, relations edges ஆக graph DB-ல store. Neo4j, Neptune, or networkx + vector DB combo.

**3. Enrichment:** Node/edge properties-க்கு embeddings generate பண்ணி hybrid retrieval enable பண்ணலாம்.

**4. Query Time Reasoning:** User query வந்ததும்:
- Query-ல entities identify பண்ணு
- Graph-ல seed node-ல இருந்து traversal பண்ணி relevant sub-graph பெறு
- அந்த sub-graph-ஐ text ஆக்கி context ஆக கொடு
- LLM generation பண்ணு

இது multi-hop reasoning-ஐ explicit walk ஆக்குகிறது.

### 4. Architectural Reasoning

Graph RAG useful ஆகும் போது:

- Data naturally relational: org charts, supply chain, customer transactions, legal contracts, medical history
- Questions need *connection* not just *similarity*: who, what linked, how many hops
- Need explainability: ஏன் இந்த answer வந்தது என்பதற்கு path காட்ட முடியும்

Vector RAG alone போதும் when: factual lookup, document QA where chunk contains answer directly, semantic similarity enough.

Graph RAG choose பண்ணும்போது நீங்கள் trade: complexity, latency, freshness.

Alternatives: pure vector RAG with larger context, or hybrid search with keyword + vector. Graph adds structure cost.

### 5. Trade-offs

**2-4 important trade-offs:**

* **Accuracy vs Freshness:** Graph build & update expensive. Document update ஆனால் extraction, entity linking, graph update வேண்டும். Near real-time difficult.

* **Reasoning power vs Latency & Cost:** Graph traversal + LLM call + vector search = more hops. Query cost high. Sub-graph too big ஆனால் context overflow.

* **Schema drift & Extraction quality:** Extraction errors = wrong edges = wrong answers. LLM hallucination in extraction phase directly pollutes graph. Need validation.

* **Operability:** Vector DB மட்டும் maintain easy. Graph DB + embedding pipeline + orchestration add complexity. Team size & skill matters.

Failure mode: Over-connected graph. Traversal explode ஆகி irrelevant nodes வரும். Need hop limit, relevance scoring, pruning.

### 6. Practical Example

Enterprise procurement system.

Documents: PO files, email approvals, vendor master.

Graph nodes: `PO#1234`, `Vendor A`, `User Ramesh`, `Account Sales`
Edges: `PO#1234 -purchased_from-> Vendor A`, `PO#1234 -approved_by-> Ramesh`, `Ramesh -belongs_to-> Account Sales`

Query: *"Ramesh approved POs for Vendor A in last quarter?"*

Vector only: PO chunks-ல "Ramesh approved" மற்றும் "Vendor A" இருக்கலாம் ஆனால் link confirm ஆகாது.

Graph RAG: Seed `Ramesh` -> traverse `approved_by` -> PO nodes -> filter `purchased_from = Vendor A` and date. Result precise.

### 7. Reasoning Challenge

உங்களிடம் customer support chat logs + CRM data இருக்கு. Users கேட்கிறார்கள்: *"என் previous issue-ஐ யார் solve பண்ணினார்கள், அதே agent இப்போ available ஆ?"*

இதற்கு pure vector RAG போதுமா? இல்லை Graph RAG தேவையா? ஏன்? என்ன entities மற்றும் relations define பண்ணுவீர்கள்? Hop எத்தனை வரை போதும்?

### 8. Key Takeaways

* Graph RAG solves multi-hop, relationship heavy questions where vector similarity alone fails
* Entities + Relations explicit ஆக model பண்ணுவதால் reasoning traceable ஆகிறது
* Extraction quality is single point of failure. Garbage in, garbage out
* Use when connections matter more than surface similarity; accept higher complexity and update latency
