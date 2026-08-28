# ANN indexes

> **Learning Path:** RAG Architecture
> **Section:** 12.1.10 — Learn

## 1. Problem

உங்க RAG system-ல user query வந்ததும் அதுக்கு பொருத்தமான documents-ஐ கண்டுபிடிக்கணும். அதுக்கு முதல்ல query-ஐ embedding ஆக்குறீங்க. இப்போ உங்க vector database-ல 10 million vectors இருக்கு, ஒவ்வொன்னும் 1536 dimensions.

> ஒவ்வொரு query-க்கும் brute force ஆக 10 million vectors-உம் dot product பண்ணி nearest neighbour கண்டுபிடிக்க முடியுமா?

அது செய்தால் latency seconds-ல போகும். Throughput குறையும். Cost ஏறும். Real-time RAG-க்கு workable இல்ல.

இங்க தான் பிரச்சனை: **exact nearest neighbour தேடுவது accurate ஆனா மெதுவு. மெதுவான exact search-ஐ பயன்படுத்த முடியாது.**

## 2. Mental Model

ANN = Approximate Nearest Neighbour.

நீங்கள் 100% accurate result வேண்டாம். Top-10-ல 9 correct வந்தால் போதும்.

ANN index என்பது: search space-ஐ organize பண்ணி, பெரும்பாலும் சரியான neighbours-ஐ குறைந்த steps-ல கண்டுபிடிக்கும் ஒரு data structure.

Analogy: நீங்கள் Chennai-ல ஒரு நண்பரை தேடுகிறீர்கள். Exact search என்பது ஒவ்வொரு வீட்டிற்கும் சென்று பார்ப்பது. ANN என்பது area, street, landmark பார்த்து approximate ஆக தேடுவது. நீங்கள் 100% guarantee இல்லை, ஆனால் வெகு வேகமாக செல்ல முடியும்.

## 3. How It Works

Brute force தேவையில்லை. Vector space-ஐ partition பண்ணி index பண்ணுறோம்.

முக்கியமான ANN families:

* **HNSW - Hierarchical Navigable Small World**: Graph based. ஒவ்வொரு vector-க்கும் neighbours connect பண்ணி multi-layer graph உருவாக்குறது. Search-ல top layer-ல இருந்து start பண்ணி greedy walk பண்ணி கீழே இறங்குறோம். Very low latency, high recall. Memory heavy.
* **IVF - Inverted File Index**: Space-ஐ coarse centroids-ஆக பிரித்து, query-க்கு nearest centroids-ஐ முதலில் தேர்ந்தெடுத்து, அதற்குள் மட்டும் brute force பண்ணுறோம். Fast, simple.
* **PQ / OPQ - Product Quantization**: Vector-ஐ compress பண்ணி codebook-ஆக store பண்ணுறது. Storage குறைவு, search RAM-ல வேகமாக நடக்கும். Accuracy trade-off.
* **Flat / Brute Force**: Small dataset-க்கு மட்டும்.

Search flow: Query embedding → ANN index traverse → candidate set ~ few hundred → exact distance re-rank on candidates → top-K return.

## 4. Architectural Reasoning

எப்போ ANN தேவை?

* Vector count > few hundred thousand
* Latency SLO < 50-100ms
* Recall requirement 0.85-0.95 enough

Constraint-கள்:

* **Latency vs Recall**: HNSW high recall low latency. IVF + PQ memory சேமிக்கும்.
* **Write throughput**: HNSW insert பண்ணுவது relatively expensive. Bulk load முக்கியம்.
* **Memory**: HNSW RAM heavy. PQ compress பண்ணி disk friendly.
* **Dataset size**: 10M+ vectors → IVF-PQ hybrid பொதுவான தேர்வு.

Decision example: Real-time chatbot with 5M docs, 100 QPS, p95 < 50ms → HNSW with moderate ef_search.

Alternatives: brute force for <100k vectors. Elasticsearch kNN for existing search infra. Annoy for low memory read-heavy.

## 5. Trade-offs

* **Recall vs Speed**: ef_search / beam width அதிகரித்தால் recall மேலே போகும், latency அதிகரிக்கும்.
* **Memory vs Accuracy**: HNSW accurate but RAM heavy. PQ saves RAM but recall drops.
* **Build time vs Query time**: Index building offline heavy. Incremental updates சிக்கல். HNSW-ல dynamic insert செய்யலாம் ஆனால் quality degrade ஆகலாம்.
* **Operability**: Index tuning பண்ண வேண்டும். Parameters like M, ef_construction, nlist. Wrong tuning = poor recall or slow search.

Failure mode: Cold start-ல index memory-க்கு fit ஆகவில்லை என்றால் swap ஆகி latency spike. Also, data drift-ல embeddings distribution மாறினால் index quality குறையும்.

## 6. Practical Example

Enterprise support RAG: 20M support tickets embeddings.

Requirement: p95 < 80ms, recall@10 > 0.9.

Decision: IVF-PQ hybrid. nlist = 4096 centroids. m = 64 PQ. Build nightly batch.

Query time: coarse quantizer → 50 nearest clusters → PQ distance scan → top 200 candidates → exact re-rank.

Result: RAM usage ~ 8GB vs flat 120GB. Latency 35ms. Recall@10 ~0.92.

Trade-off: New tickets add ஆகும்போது index refresh தேவை. Real-time requirement இல்லாததால் daily rebuild acceptable.

## 7. Reasoning Challenge

உங்களிடம் 2 பில்லியன் vectors உள்ளன. 95% read, 5% write per day. Latency SLO 100ms. Memory budget limited. HNSW பயன்படுத்தலாமா? என்ன architecture தேர்வு செய்வீர்கள்? PQ compression மற்றும் sharding எப்படி பயன்படும்?

## 8. Key Takeaways

* ANN என்பது exact search-க்கு பதிலாக speed-க்காக approximate ஆக தேடுவது.
* HNSW latency குறைவு, IVF-PQ memory மற்றும் scale க்கு நல்லது.
* Index choice என்பது recall requirement, latency SLO, dataset size, memory budget ஆகியவற்றின் trade-off.
* ஒரு index-ஐ தேர்வு செய்தால் tuning, rebuild strategy, மற்றும் recall monitoring தேவை.
