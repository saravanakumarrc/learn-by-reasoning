# Vector database costs

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.11 — Learn to reason about

## 1. Problem

உங்க RAG system production-ல வந்துருச்சு. 10M documents embed பண்ணி vector database-ல store பண்ணியிருக்கீங்க. First month free tier-ல nice-ஆ work ஆச்சு. இப்போ traffic 10x ஆகி, query per second 50 ஆகி, bill $8000 வந்துருச்சு.

எங்க போச்சு காசு? Storage? Compute? API calls? Embedding? அதுல எதுக்கு காசு அதிகமா போகுது தெரியல.

Vector database costs-ஐ reason பண்ண முடியாம இருந்தா, AI system-ஐ scale பண்ண முடியாது. Cost predictable ஆக்கணும்.

## 2. Mental Model

Vector database cost = **Storage + Compute + Operations + Data movement**.

இது relational database மாதிரி அல்ல. Vector DB-ல cost drivers வேற.

ஒரு vector = 768 or 1536 dimensions x 4 bytes ≈ 3-6 KB. Text-ஐ விட 100x பெருசு. அதனால storage வேகமா inflate ஆகும்.

மேலும் search என்பது brute force scan அல்ல. ANN index வச்சு approximate search பண்ணும். அந்த index memory-ல இருக்கணும். Memory = money.

## 3. How It Works

Vector DB vendors காசு வாங்குறது பெரும்பாலும் 4 விதத்தில்:

**1. Storage cost:** GB per month. Embeddings + metadata + index. Index size collection size-க்கு proportional.
**2. Compute / Instance cost:** Search என்பது CPU + RAM intensive. Instance size, node count.
**3. Operations cost:** Queries per second, vector upserts, read/write operations. Pinecone, Weaviate Cloud இப்படி charge பண்ணும்.
**4. Egress / API cost:** Query volume. High QPS = more compute.

Embedding cost தனி. Embedding model inference cost + vector DB cost. பலர் இதை mix பண்ணி confuse ஆகிறார்கள்.

## 4. Architectural Reasoning

Vector DB தேவைப்படும் போது cost எப்படி grow ஆகும்?

*Collection size grow ஆனா* → storage + index memory grow. Recall maintain பண்ண 95% → HNSW index-ல graph grows non-linearly.

*QPS grow ஆனா* → you need more replicas or bigger instance. Latency SLO maintain பண்ணணும் என்றால், memory-resident index வேண்டும். RAM expensive.

*Dimensionality அதிகம்* → 1536 vs 768 = 2x memory. Search latency கூடும்.

எப்போ useful?

- Real-time low latency search வேண்டும், மில்லியன் vectors.
- Multi-tenant isolation வேண்டும்.
- Managed ops வேண்டும்.

எப்போ இல்லாமல்?

Small collection < 1M vectors, low QPS → PostgreSQL with pgvector or even in-memory FAISS enough. Managed vector DB overkill.

## 5. Trade-offs

**Managed vs Self-hosted.** 
Managed = predictable ops, unpredictable bill. Self-hosted = upfront infra cost, you control scaling. Team size small என்றால் managed worth it. Cost sensitive என்றால் self-hosted + spot instances.

**Recall vs Cost.**
Higher recall = larger ef_search, larger index. Latency அதிகம், compute அதிகம். Production-ல 0.9 recall enough? 0.95? அந்த 5% க்கு 3x cost வரலாம்.

**Indexing strategy.**
HNSW = fast search, memory heavy. IVF / PQ = storage குறைவு, recall குறைவு. Cost vs quality trade-off.

**Embedding size.**
Bigger model = better quality, bigger vector = more storage + memory + compute. 3072 dim embedding 1536 விட double cost. Quality gain justify ஆகுதா?

**Update frequency.**
Frequent upserts = write amplification. Streaming ingestion-க்கு separate write-optimized path வேண்டும். இல்லைன்னா read performance degrade ஆகும்.

Failure mode: Cost spike. Traffic spike வந்தால் auto-scale பண்ணி bill 10x ஆகும். Rate limiting இல்லைன்னா surprise bill.

## 6. Practical Example

Enterprise support RAG: 50M support tickets embed செய்திருக்கிறீர்கள். 1536 dim, float32.

Rough calc: 50M * 6 KB ≈ 300 GB raw vectors. Index overhead 1.5x ≈ 450 GB RAM needed. Pinecone p2 pod = 4GB RAM ~ $... 128 pods? Bill பெருசு.

Reasoning: Do we need all 50M online?

*Tiering:* Hot 5M recent tickets in vector DB with high recall. Cold 45M in object storage + re-hydrate on demand. Hybrid search.

*Quantization:* Binary quantization or PQ 8-bit → memory 4x reduce, recall drop 2-3%. Acceptable?

*Dimensionality reduction:* 1536 → 768 via PCA. 50% memory save.

Result: Bill $8000 → $1800. Latency still <150ms.

## 7. Reasoning Challenge

உங்களுக்கு 20M vectors உள்ளன. QPS 200, p95 latency <100ms வேண்டும். Current bill $12k/month. 

Options:
A) Upgrade to bigger managed instance
B) Shard collection by tenant / region
C) Move cold data to S3 + query-time hybrid retrieval
D) Reduce embedding dimension from 1536 to 768

எந்த combo தேர்வு செய்வீர்கள்? ஏன்? என்ன trade-off accept பண்ணுறீங்க?

## 8. Key Takeaways

* Vector DB cost is driven by memory-resident index size, not just storage. RAM = biggest cost.
* Collection size, dimensionality, QPS, recall target ஆகியவை ஒன்றோடு ஒன்று பெருகும். Isolate them.
* Managed convenience costs predictability. Self-hosted costs ops complexity.
* Cost optimize பண்ணுவது தொழில்நுட்பம் மாற்றுவது அல்ல. Architecture decision: tiering, quantization, dimensionality, sharding.
