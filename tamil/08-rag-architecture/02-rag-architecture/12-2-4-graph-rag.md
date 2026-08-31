# Graph RAG

> **Learning Path:** RAG Architecture
> **Section:** 12.2.4 — RAG architecture

## 1. Problem

உங்க RAG system வேலை செய்யுது. Vector search-ல embedding பண்ணி, top-k chunks எடுத்து LLM-க்கு கொடுக்கிறீங்க.

ஆனா ஒரு painful situation வருது:

> "ஒரு customer-ன் order history, அவர் complaint பண்ணின tickets, அவர் பேசின sales rep, அவருக்கு தரப்பட்ட discount — இதெல்லாம் ஒரே customer-க்கு connect ஆகி இருக்கு."

Vector search உங்களுக்கு similar text chunks தரும். ஆனா **relationship** புரியாது. Customer → Order → Product → Supplier என்ற chain-ஐ புரிஞ்சுக்க முடியாது.

Result: LLM context-ல unrelated facts கிடைக்கும், hallucination அதிகமாகும், multi-hop reasoning தோல்வி அடையும்.

**What goes wrong if we don't have this?** 
"இந்த supplier-க்கு கடந்த 6 மாதத்தில் return rate எவ்வளவு?" என்ற கேள்விக்கு, chunks தனித்தனியாக இருந்தால் LLM join பண்ண முடியாது. அது guess பண்ணும்.

---

## 2. Mental Model

Graph RAG = Documents-ஐ text chunks மட்டுமல்ல, **entities and relationships-ஐ nodes and edges-ஆக** பார்க்கிறோம்.

Vector RAG = "இந்த text similar ஆ?" என்று கேட்கிறது.
Graph RAG = "இந்த entity இந்த entity-யுடன் எப்படி connect ஆகி இருக்கு?" என்று கேட்கிறது.

Mental model simple: Knowledge Graph + Retrieval + Generation.

Documents → Entities extract → Relationships extract → Knowledge Graph build → Query-க்கு subgraph retrieve → LLM-க்கு context.

உதாரணமாக, ஒரு news article-ல "Apple acquired Darling" என்று இருந்தால், vector RAG அதை text-ஆக மட்டும் store பண்ணும். Graph RAG `Apple` node, `Darling` node, `acquired` edge-ஐ create பண்ணும்.

---

## 3. How It Works

**Step 1: Ingestion with extraction**
Document வந்ததும் chunk பண்ணுவது மட்டுமல்ல, LLM or NER model வைத்து entities எடுக்கிறோம். Person, Company, Product, OrderId போன்றது.
பிறகு relationships extract: `customer_123 ordered order_456`, `order_456 contains product_X`.

**Step 2: Graph store**
Nodes = entities. Edges = relationships with type and properties.
இதை store பண்ண Graph database-ல, Neo4j / Neptune / TigerGraph அல்லது vector DB-ல graph extensions.

**Step 3: Query time**
User question வந்ததும், அதிலிருந்து entities extract பண்ணி graph-ல match பண்ணி relevant subgraph-ஐ traverse பண்ணி எடுக்கிறோம்.
பிறகு அந்த subgraph-ஐ natural language-ஆ convert பண்ணி LLM-க்கு கொடுக்கிறோம்.

> "Who is the supplier for products that customer X returned?"
> Query → customer X node → returned orders → products → supplier. 3-hop traversal.

---

## 4. Architectural Reasoning

Graph RAG useful ஆகும் போது?

* **Multi-hop reasoning தேவை:** A → B → C என்ற chain தேவைப்படும் போது.
* **Structured relationships matter:** Ownership, hierarchy, dependencies, lineage.
* **Explainability தேவை:** "ஏன் இந்த answer வந்தது?" என்று path காட்ட வேண்டும்.
* **Entity-centric domain:** Legal, finance, healthcare, e-commerce, knowledge base.

Alternatives:
* **Vector RAG only:** Simple, fast, good for semantic similarity. Relationships புரியாது.
* **Hybrid RAG:** Vector + keyword + graph. Real world-ல இதுதான் பெரும்பாலும்.

Architect ஏன் choose பண்ணுவார்?
Vector RAG context-ஐ தரும். Graph RAG **connection-ஐ தரும்**. Compliance audit, fraud detection, recommendation, support bot போன்றவற்றில் connection தான் key.

---

## 5. Trade-offs

**1. Complexity vs Accuracy**
Graph build பண்ண entity extraction, relation extraction தேவை. Extraction error வந்தால் graph-ல wrong edge create ஆகும். Pipeline maintain பண்ண கடினம். Vector RAG-க்கு ஒப்பிடும்போது ops overhead அதிகம்.

**2. Latency vs Reasoning depth**
Graph traversal fast ஆக இருந்தாலும், multi-hop query + subgraph expansion latency add பண்ணும். Real-time chatbot-க்கு கவனம் தேவை.

**3. Freshness**
Document update ஆனதும் graph-ஐ update பண்ண வேண்டும். Incremental graph update, entity deduplication கடினம். Vector DB-ல re-index ஒப்பிடும்போது state management அதிகம்.

**4. Cost**
LLM calls for extraction, graph storage, traversal compute. Small dataset-க்கு overkill.

Failure mode: Extraction model hallucinate பண்ணி fake relationship create பண்ணிடும். அப்புறம் RAG poison ஆகும். So extraction quality is bottleneck.

---

## 6. Practical Example

Enterprise support system.

Customer 12345 குறித்து 200 tickets, 50 orders, 10 payments உள்ளது.

Vector RAG-ல "customer 12345 refund" என்று search பண்ணினால் relevant chunks கிடைக்கும்.

Graph RAG-ல:
Node: Customer12345
Edges: placed Order789, filed TicketA, contacted AgentRavi, received DiscountCodeX
Order789 → contains ProductP1, ProductP2
ProductP1 → supplied by SupplierS1

User கேள்வி: "Customer 12345-க்கு ஏன் discount தரப்பட்டது?"

Graph traversal: Customer12345 → received DiscountCodeX → reason = "high return rate with SupplierS1". SupplierS1 node-ல return rate property உள்ளது.

LLM-க்கு subgraph context தரப்பட்டதும், coherent answer generate ஆகும். Path show பண்ணி explainability கூட கிடைக்கும்.

---

## 7. Reasoning Challenge

உங்களிடம் 1M documents உள்ள knowledge base உள்ளது. Queries 70% single-hop factual lookups, 30% multi-hop reasoning like "which vendor supplied the defective parts in projects delayed by more than 2 months".

நீங்கள் Graph RAG-ஐ full-க்கு implement பண்ண வேண்டுமா? Partial-ஆ? Hybrid approach எப்படி design பண்ணுவீங்க? Latency budget 800ms.

ஏன் அப்படி முடிவு எடுக்கிறீங்க? Extraction cost, freshness, query pattern எப்படி influence பண்ணும்?

---

## 8. Key Takeaways

* Graph RAG solves **relationship and multi-hop reasoning** problem, not just similarity.
* Vector RAG = what is similar. Graph RAG = how is connected.
* Build cost high: entity/relation extraction quality = system quality.
* Use hybrid: vector for recall, graph for reasoning, not either/or.
* Every architectural solution creates trade-off: Graph gives reasoning, takes complexity, latency, maintenance.

**இது ஏன் தேவைன்னு புரிஞ்சுது. எப்னோ use பண்ணணும்னு தெரியும்.**
