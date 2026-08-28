# Knowledge graphs

> **Learning Path:** RAG Architecture
> **Section:** 12.1.22 — Learn

## 1. Problem

உங்களிடம் ஒரு RAG system இருக்கு. User கேட்கிறார்: "எங்கள் top customer-ஆன ACME Corp-க்கு கடந்த quarter-ல் யார் sales lead ஆக இருந்தார், அவருடைய contract renewal date என்ன?"

Vector database + LLM மட்டும் இருந்தால் என்ன ஆகும்?

Document chunks-ல் "ACME Corp", "sales lead", "Q2", "contract" எல்லாம் scattered-ஆ இருக்கும். Embedding similarity மூலம் பொருத்தமான chunks கிடைக்கலாம், ஆனால்:

* Relationship புரியாது. ACME Corp ↔ sales lead ↔ person ↔ renewal date என்ற link தெரியாது.
* Hallucination வரும். Model தன்னுடையதாக connections உருவாக்கும்.
* Multi-hop reasoning தேவைப்படும் query-கள் தோல்வியடையும்.

**Pain point:** Unstructured text-ல் facts இருக்கு, ஆனால் entities மற்றும் அவற்றின் relationships தெளிவாக இல்லை. RAG தனியாக relational reasoning செய்ய முடியாது.

இதுதான் knowledge graph தேவைப்படும் இடம்.

## 2. Mental Model

Knowledge graph = Entities + Relationships.

> "Nodes are entities. Edges are relationships with type and properties."

உதாரணமாக: `(Customer: ACME Corp) -[has_sales_lead]-> (Person: Arjun)` , `(Person: Arjun) -[owns_contract]-> (Contract: C-1029)` , `(Contract: C-1029) -[renewal_date]-> "2026-03-15"`

Text மட்டும் இல்லை, graph structure இருக்கு. இதனால் LLM-க்கு reasoning-க்கு தேவையான explicit connections கிடைக்கும்.

## 3. How It Works

1. **Extraction:** Documents, CRM, tickets, product catalogs இருந்து entities-ஐ identify பண்ணு. NER + relation extraction மூலம்.
2. **Normalization:** Same entity-க்கு multiple mentions இருந்தால் canonical ID create பண்ணு. ACME Corp = Acme Corporation.
3. **Graph Store:** Neo4j, Neptune, or vector + graph hybrid. Nodes, edges, properties store பண்ணு.
4. **Query Time:** User query-ஐ graph query-ஆ convert பண்ணு. Cypher / SPARQL-ல் path find பண்ணு. Result-ஐ structured answer-ஆ கொடு, அதை LLM context-ல் pass பண்ணு.

RAG + Knowledge Graph = Hybrid RAG. Vector search for semantic recall, graph for relational reasoning.

## 4. Architectural Reasoning

Knowledge graph useful ஆகும் போது:

* Data highly interconnected. Customer, order, product, employee, contract போன்ற entities இடையே links முக்கியம்.
* Multi-hop questions தேவை. "Who is manager of the team that built X?" போன்றது.
* Consistency and explainability முக்கியம். Why this answer? Because graph path shows it.

Alternatives:

* **Pure Vector RAG:** Simple, fast to build. ஆனால் relationship reasoning weak.
* **Structured DB + SQL:** Relational data-க்கு நல்லது, ஆனால் unstructured text-ல் knowledge capture செய்ய முடியாது.
* **LLM-only reasoning:** Hallucination risk அதிகம்.

Architect choose knowledge graph when relational accuracy > raw recall speed, and when you can afford extraction + maintenance cost.

## 5. Trade-offs

* **Accuracy vs Freshness:** Graph accurate ஆனால் stale ஆகும். Extraction pipeline slow ஆனால் graph update ஆகும். Real-time ingestion தேவை.
* **Complexity vs Value:** Entity resolution, schema design, versioning எல்லாம் operational overhead. Small dataset-க்கு overkill.
* **Query flexibility vs Performance:** Graph traversal fast for relationships, ஆனால் free-form semantic search-க்கு vector தேவை. Hybrid adds latency.
* **Explainability vs Privacy:** Graph explicit relationships expose. Sensitive links leak ஆகும் risk.

Failure mode: Bad extraction = bad graph. Garbage in, garbage out. Entity linking errors cause wrong paths, LLM confidently wrong answer கொடுக்கும்.

## 6. Practical Example

Enterprise support RAG.

Documents: Support tickets, product docs, customer CRM.

Graph entities: Customer, Product, IssueType, Engineer, Ticket.

Edges: `Customer -[owns]-> Product`, `Ticket -[about]-> IssueType`, `Ticket -[assigned_to]-> Engineer`.

User asks: "எங்கள் enterprise customer-களில் இந்த quarter-ல் network issue வந்தது, அதை fix பண்ணிய engineer யார்?"

Vector search மட்டும் ticket text-ல் "network issue" match பண்ணும். Graph query:

`MATCH (c:Customer {tier:'enterprise'})<-[:belongs_to]-(t:Ticket)-[:about]->(i:IssueType {name:'network'}) WHERE t.created >= ... RETURN t.assigned_to`

Result: Engineer name list. அதை LLM-க்கு கொடு, summary generate பண்ணு.

## 7. Reasoning Challenge

உங்களிடம் product catalog உள்ளது. 1M products, each with specs, reviews, compatibility info. Users கேட்கிறார்கள்: "My laptop model X-க்கு compatible ஆன மற்றும் 4.5+ rating உள்ள accessories எவை?"

Pure vector RAG-ல் என்ன பிரச்சனை வரும்? Knowledge graph எப்படி help பண்ணும்? Graph-ஐ build பண்ணும்போது என்ன schema முக்கியம்? Trade-off என்ன?

## 8. Key Takeaways

* Knowledge graph solves relational reasoning problem, not just recall.
* Entities + Relationships explicit ஆக்குவது hallucination-ஐ குறைக்கும்.
* Hybrid RAG = Vector for semantic, Graph for structured reasoning.
* Build cost high: extraction quality, entity resolution, maintenance தேவை.
* Use it when multi-hop, interconnected questions matter more than simple Q&A.
