# Embedding costs

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.10 — Learn to reason about

## 1. Problem

உங்கள் AI product-ல RAG agent இருக்கு. User query வந்ததும், அதை embedding பண்ணி vector database-ல search பண்றீங்க. ஒவ்வொரு query-க்கும் 1 embedding, ஒவ்வொரு document chunk-க்கும் 1 embedding.

இப்போ traffic 10k queries/day இருந்து 1M queries/day ஆக வளருது. Monthly bill பார்த்தால் embedding API cost மட்டுமே முக்கியமான line item ஆகி இருக்கு.

**What goes wrong?** Embedding cost linear-ஆ grow ஆகும். அதை கட்டுப்படுத்தாமல் விட்டால், model performance-க்காக செலவு அதிகமாகி, unit economics break ஆகும்.

Embedding costs-ஐப் புரிந்துகொள்ளாமல் architect பண்ணினால், நீங்கள் சரியான model, batching, caching strategy தேர்வு செய்ய முடியாது.

## 2. Mental Model

Embedding cost = **tokens processed × price per token**.

ஆனால் architect-க்கு முக்கியம் இது: **Embedding cost has two different profiles**.

1. **Indexing cost**: One-time, but huge. Document corpus-ஐ chunk பண்ணி embed பண்ணும்போது. Millions of chunks.
2. **Query cost**: Recurring, high frequency. Every user query-க்கும் embed பண்ண வேண்டும்.

இந்த இரண்டுக்கும் வெவ்வேறு constraints, trade-offs இருக்கு.

## 3. How It Works

ஒரு text-ஐ embedding model-க்கு அனுப்பும்போது, tokenizer அதை tokens ஆக பிரிக்கும். உதாரணமாக, 500 characters ~ 125 tokens.

Provider-கள் price per 1M tokens basis-ல charge பண்றாங்க. உதாரணமாக:
- `text-embedding-3-small`: ~ $0.02 / 1M tokens
- `text-embedding-3-large`: ~ $0.13 / 1M tokens

ஒரு document 1,000 chunks ஆக இருந்தால், ஒவ்வொரு chunk 500 tokens என்றால் 500k tokens = $0.01 for small model.

Query side: 1M queries/day, avg 50 tokens/query = 50M tokens/day = 1.5B tokens/month. அதுவே $30/month for small model.

Cost scale ஆகிறது: **corpus size × chunk size** + **query volume × query length**.

## 4. Architectural Reasoning

Embedding cost-ஐ optimize பண்ணும்போது architect கேட்க வேண்டிய கேள்விகள்:

**Model choice constraint**
Small model cheaper, large model better recall. Indexing-க்கு quality முக்கியம், query-க்கு latency முக்கியம். பலர் hybrid பண்றாங்க: Indexing-க்கு large, query-க்கு small.

**Batching**
API call per chunk என்பது overhead + cost. Batching 100 chunks in one request = fewer calls, better throughput. But latency trade-off.

**Caching**
Same query திரும்ப திரும்ப வருமா? Same document chunk-ஐ மீண்டும் embed பண்ண வேண்டுமா? Embedding deterministic ஆக இருந்தால் cache hit = zero cost.

**Dimensionality**
1024-dim vector vs 256-dim. Storage cost, search cost இரண்டும் குறையும். But recall குறையலாம்.

When this becomes useful? When you have >100k documents or >10k queries/day. அதுக்கு முன் cost negligible.

## 5. Trade-offs

**Quality vs Cost**
Large embedding model = better semantic search, but 6-7x cost. Architect decide பண்ண வேண்டியது: Is recall improvement worth the cost? பெரும்பாலும் domain-specific data-க்கு fine-tuned small model போதும்.

**Freshness vs Caching**
Cache embeddings to save cost. ஆனால் document update ஆனால் cache invalidation தேவை. Stale embedding = wrong results.

**Batch size vs Latency**
Bigger batch = better cost efficiency, but query latency increase ஆகும். Real-time chat agent-க்கு 200ms budget இருக்கும்போது batch பண்ண முடியாது.

**Self-host vs API**
Open-source model like BGE, E5 self-host பண்ணினால் API cost zero. ஆனால் GPU infra cost, maintenance, scaling complexity வரும். Team size small ஆனால் API தான் cheaper.

Failure mode: Cost spike. Traffic 10x ஆனால் embedding bill 10x. Rate limit அல்லது budget overrun ஆகி service down. Cost guardrails இல்லாமல் architecture fragile.

## 6. Practical Example

Enterprise knowledge base RAG system.

Constraints:
- 2M documents, avg 10 chunks each = 20M chunks
- 500k queries/month
- SLA: p95 latency < 800ms

Reasoning:
Indexing cost one-time. 20M chunks × 300 tokens avg = 6B tokens. text-embedding-3-small-ல ~ $120. Large model-ல ~ $780. Quality test பண்ணி small model போதும் என்று தெரிந்தால் small தேர்வு.

Query cost: 500k queries × 50 tokens = 25M tokens/month = ~ $0.5/month. Negligible.

Optimization: Query embeddings-க்கு 24 hour TTL cache வைக்க. Top 10k common queries cover ~40% traffic. Cache hit = 40% cost saving + latency drop.

Implementation: Embedding service layer-ல request dedupe + cache check. Miss ஆனால் batch up to 32 queries.

Result: Cost predictable, latency stable.

## 7. Reasoning Challenge

உங்களிடம் customer support chatbot இருக்கு. Daily 200k queries. ஒவ்வொரு query-யும் unique. Corpus 500k chunks, weekly update ஆகிறது.

இப்போ embedding bill எதிர்பார்த்ததை விட 3x high ஆக இருக்கு.

Cost-ஐ குறைக்க என்ன architectural decisions பார்ப்பீர்கள்? Caching work ஆகுமா? Model downgrade செய்வது safe ஆ? Batching எங்கே apply பண்ணலாம்?

## 8. Key Takeaways

- Embedding cost = tokens × price, but profile differs for indexing vs query.
- Indexing-க்கு quality, query-க்கு latency & cost முக்கியம். Hybrid model choice பண்ணலாம்.
- Cache repeated queries and stable chunks. Determinism இருந்தால் தான் cache useful.
- Self-host saves API cost but adds infra & ops cost. Team size & scale decide செய்யும்.
- Every cost saving creates trade-off: recall, freshness, latency, complexity.
