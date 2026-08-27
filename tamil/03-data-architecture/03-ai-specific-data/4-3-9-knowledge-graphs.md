# Knowledge graphs

> **Learning Path:** Data Architecture
> **Section:** 4.3.9 — AI-specific data

## Problem

நீங்கள் ஒரு AI agent-க்கு RAG pipeline பண்ணிக்கிட்டு இருக்கீங்க. Vector database-ல documents-ஐ embeddings-ஆக போட்டு similarity search பண்ணீங்க. 

உபயோகர் கேட்கிறார்: *"நம்முடைய top 3 customers-க்கு common supplier யார், அந்த supplier இப்போது எந்த product-ஐ supply பண்ணலையா?"*

Vector search என்ன செய்யும்? ஒத்த மாதிரி தெரியும் documents-ஐ திருப்பி கொடுக்கும். ஆனால் multi-hop relationship-ஐ துல்லியமாக trace பண்ண முடியாது. Customer → Product → Supplier → current supply status என்ற chain-ஐ கண்டுபிடிக்க தேவைப்படும் reasoning குழம்பி போகும். LLM hallucinate பண்ணும்.

Relational DB-ல இதை joins வைத்து கேட்கலாம். ஆனால் schema மாறும்போது migration கஷ்டம். ஒவ்வொரு relationship-க்கும் table வைக்க முடியாது. Schema rigid, exploratory queries slow.

இந்த வலியிலிருந்து தான் knowledge graph வருகிறது. Relationship-ஐ first-class citizen ஆக்கி, entity-களை link செய்து reasoning-க்கு உதவும்.

## Mental Model

Knowledge graph = nodes + edges.

Node = entity. Customer, Product, Supplier, Order, User. ஒவ்வொரு node-க்கும் properties இருக்கும்.

Edge = relationship with type. `purchases`, `supplied_by`, `belongs_to`, `similar_to`. Edge-க்கும் properties இருக்கலாம்: date, amount, confidence.

மனதில் வையுங்கள்: relational DB table-கள் இல்ல, document-கள் இல்ல. இது graph. இதில் traversal தான் முக்கியம்.

## How It Works

அடிப்படை representation ரெண்டு வடிவம்.

**Triple store**: Subject - Predicate - Object. `Customer:123 purchases Product:456`. SPO.

**Property graph**: Neo4j மாதிரி. Node-க்கும் Edge-க்கும் key-value properties. Cypher query வைத்து traverse பண்ணலாம்.

AI-specific data-ல knowledge graph-ஐ பயன்படுத்தும் போது:

* Entity extraction + linking: text-ல இருந்து entities-ஐ extract பண்ணி canonical ID-க்கு map பண்ணுவது.
* Graph construction: relationships-ஐ explicit ஆக store பண்ணுவது.
* Query for reasoning: multi-hop traversal, path finding, connected components.
* Grounding for LLM: graph-ல இருந்து facts-ஐ retrieve பண்ணி LLM-க்கு context ஆக கொடுப்பது.

RAG + Knowledge Graph = Vector search fuzzy recall + Graph precise reasoning.

## Architectural Reasoning

எப்போது knowledge graph useful?

* Relationships matter more than text similarity. "who knows whom", "who bought what", "what depends on what".
* Multi-hop questions வருகிறது. 2-3 hops க்கு மேல் தேவை.
* Explainability தேவை. ஏன் இந்த answer வந்தது என்று path காட்ட வேண்டும்.
* Entity disambiguation தேவை. "Ravi" என்பது யார் என்று context வைத்து resolve செய்ய வேண்டும்.

Alternatives:

* Relational DB: schema strict, joins expensive for deep graph traversal.
* Document store + Vector DB: similarity good, relationship weak, no explicit provenance.
* Pure LLM reasoning: hallucination risk high.

Knowledge graph-ஐ தேர்வு செய்யும் போது நீங்கள் trade-off பண்ணுகிறீர்கள்: flexibility and reasoning power vs operational complexity.

## Trade-offs

* **Write complexity vs query power**: Graph-ஐ maintain பண்ணுவது கடினம். Entity linking, deduplication, relationship extraction தொடர்ந்து பண்ண வேண்டும். ஆனால் traversal query-கள் cheap.
* **Consistency vs evolution
