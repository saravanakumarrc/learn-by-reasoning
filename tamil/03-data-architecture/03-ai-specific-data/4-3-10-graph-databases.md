# Graph databases

> **Learning Path:** Data Architecture
> **Section:** 4.3.10 — AI-specific data

## 1. Problem

ஒரு AI agent-க்கு "இந்த user-க்கு என்ன product recommend பண்ணலாம்?" என்று கேட்டால் போதாது. அதற்கு தேவை:
User -> purchases -> products -> category -> brand -> reviews -> similar users -> viewed items -> support tickets.

Relational database-ல இது 6-7 table joins ஆகும். 3 hop-க்கு மேல் போனால் latency குதிக்கும், query complex ஆகும், index-கள் பெருகும்.

AI-specific data-ல மற்றொரு வலி: RAG system-ல entity linking. "Apple" என்றால் fruit-ஆ? company-ஆ? Person-ஆ? Context-ஐப் புரிந்து கொள்ள relationships தேவை. Document-களை மட்டும் vector search பண்ணினால் multi-hop reasoning முடியாது. Knowledge graph இல்லாமல் hallucination அதிகரிக்கும்.

**Problem என்ன?** Connected data-வை connected way-ல query பண்ண வேண்டும். Relational model connected data-வை store பண்ணுவதில் நல்லது, traverse பண்ணுவதில் மோசம்.

## 2. Mental Model

Graph database என்பது data-வை nodes மற்றும் edges-ஆக பார்க்கிறது.

Node = entity. User, Product, Order, Document, Person.
Edge = relationship with direction and type. PURCHASED, WORKS_AT, CITES, SIMILAR_TO.
இரண்டிற்கும் properties இருக்கலாம். Edge-க்கு timestamp, amount போன்றது.

Mental model: **Adjacency list உடனே இருக்கும்.** ஒரு node-ஐ அடைந்ததும் அதன் neighbors ஒரு pointer மூலம் கிடைக்கும். Join இல்லை, traversal தான்.

இது ஒரு social network மாதிரி நினைத்துக்கொள்ளலாம். நண்பனின் நண்பனை கண்டுபிடிப்பது graph-ல natural.

## 3. How It Works

Property graph model தான் பெரும்பாலும் use ஆகிறது.

Node = id + label + properties
Edge = start node, end node, type, properties

Storage-ல index-free adjacency என்ற concept உள்ளது. Neo4j போன்ற systems-ல ஒரு node-ன் neighbors physical pointer மூலம் link ஆக இருக்கும். Traversal என்பது pointer chase. Random access disk I/O குறையும்.

Query language: Cypher, Gremlin. உதாரணம்:
```
MATCH (u:User)-[:PURCHASED]->(p:Product)<-[:PURCHASED]-(other:User)
WHERE u.id = $id
RETURN other
```
இது 2-hop pattern matching. Relational-ல இதற்கு self join தேவை.

Graph database write path heavy இல்லை. Node create, edge create, property update. Consistency மாடல் usually ACID per transaction.

## 4. Architectural Reasoning

Graph database useful ஆகும் போது:

* **Relationship is first-class.** Data-வின் value connection-ல இருக்கிறது. Fraud detection, recommendation, knowledge graph, access control graph.
* **Variable depth traversal தேவை.** "3 degrees of separation" போன்ற queries. Depth fixed இல்லை.
* **Schema flexible.** AI systems-ல entity types runtime-ல வளரும். New relation type add பண்ண வேண்டும். Relational migration painful.
* **Path explainability தேவை.** Agent ஏன் இந்த recommendation கொடுத்தது என்பதற்கு path காட்ட வேண்டும்.

Alternatives:
* Relational + recursive CTE. Small graph, read heavy, depth குறைவு என்றால் போதும்.
* Document store + vector search. Similarity க்கு நல்லது, structured relationship க்கு மோசம்.
* In-memory graph like RedisGraph. Low latency, limited persistence.

Decision point: Query pattern mostly traversal என்றால் graph. Mostly point lookup + filter என்றால் relational.

AI-specific data context-ல: Vector DB similarity க்கு, Graph DB reasoning க்கு. பல production RAG systems hybrid ஆக இருக்கின்றன: Vector DB for retrieval, Graph DB for entity relationships and multi-hop.

## 5. Trade-offs

* **Traversal fast, arbitrary scan slow.** Graph shines in local neighborhood queries. Full graph scan, aggregation queries relational-க்கு பின்னால் வரும்.
* **Write throughput vs read latency.** High write churn உள்ள graph-ல hotspot nodes உருவாகும். Super node problem.
* **Operational complexity.** Clustering, backup, sharding graph-ல கடினம். Relational ecosystem mature.
* **Consistency model.** Strong consistency per transaction உள்ளது, but cross-shard transactions கடினம்.

Failure mode: Graph becomes dense. ஒரு popular product-க்கு millions of PURCHASED edges. Traversal fan-out explosion. இதற்கு supernode mitigation, partitioning தேவை.

Cost trade-off: Developer
