# Caching

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.4 — Learn to reason about

## 1. Problem

உங்க AI application-ல ஒரு user ஒரு query கொடுக்கிறார். அதுக்கு LLM call போகிறது. ஒரே query இரண்டு முறை வருகிறது. ஒரே vector search மீண்டும் நடக்கிறது. ஒரே embedding மீண்டும் generate ஆகிறது.

என்ன problem?
* Latency அதிகம். LLM call 500ms - 2s எடுக்கும்.
* Cost அதிகம். ஒரு token கூட காசு.
* Throughput limit ஆகிறது. Rate limit அடிக்கிறது.

நீங்கள் என்ன செய்வீர்கள்? Database-ஐ மீண்டும் மீண்டும் hit செய்வதை நிறுத்த வேண்டும். Compute-ஐ மீண்டும் மீண்டும் செய்வதை நிறுத்த வேண்டும்.

இதுதான் caching-ன் root problem. **ஒரே வேலையை திரும்ப திரும்ப செய்ய வேண்டாம்**.

## 2. Mental Model

Cache என்பது ஒரு விலை உயர்ந்த வேலையின் result-ஐ, வேகமான மற்றும் மலிவான இடத்தில் வைத்து வைத்துக்கொள்வது.

Think of it like an engineer’s notepad.

> "இந்த query-க்கு இந்த answer-ஐ நேற்றே கண்டுபிடித்தேன். மீண்டும் கணக்கிட வேண்டாம்."

Cache = Fast, cheap read layer முன்னால் வைப்பது. Miss ஆனால் தான் origin-க்கு போக வேண்டும்.

## 3. How It Works

Basic flow simple தான்:

Request → Cache Lookup → Hit? → Return
                 ↓ Miss
               Origin → Compute/DB/LLM → Store in Cache → Return

இதில் முக்கியமானது 3 விஷயங்கள்:

**Key**: என்னை identify பண்ணுவது. Query text, user id, parameters.
**Value**: Result. LLM response, embedding vector, DB row.
**TTL / Invalidation**: எப்போது cache-ஐ காலி செய்வது.

AI Cost Architecture-ல நீங்கள் cache பண்ணுவது:
* **Prompt cache**: User query + system prompt combo
* **Embedding cache**: Document text → embedding vector
* **RAG answer cache**: Query → retrieved context + final answer
* **Tool call cache**: Same tool input → same tool output

## 4. Architectural Reasoning

Caching useful ஆகும் போது?

* **Read heavy, write light**. Same data மீண்டும் மீண்டும் கேட்கப்படுகிறது.
* **Origin slow/expensive**. LLM, vector search, external API.
* **Staleness acceptable**. 5 நிமிடம் பழைய data போதும்.

AI system-ல இது பொதுவாக நடக்கும்:
User பலர் ஒரே popular question கேட்பார்கள். "What is RAG?" போன்றவை. Chat history-ல context repeat ஆகும்.

Alternatives என்ன?
* **No cache**: எப்போதும் origin. Simple ஆனால் costly.
* **Pre-compute**: எல்லாவற்றையும் முன்கூட்டியே கணக்கிடுவது. Waste.
* **Approximation**: Cheaper model use பண்ணுவது. Quality trade-off.

ஏன் cache தேர்வு? Cost மற்றும் latency-ஐ குறைக்க வேண்டும், correctness-ஐ அதிகம் குலைக்காமல்.

## 5. Trade-offs

**1. Freshness vs Cost**
Cache வைத்தால் stale data வரும். LLM answer-ல time sensitive info இருந்தால் பிரச்சனை. TTL குறைத்தால் hit rate குறையும்.

**2. Hit rate vs Memory / Cost**
Cache size அதிகம் என்றால் hit rate அதிகம். ஆனால் Redis, memory cost அதிகம். Wrong key design-ல memory waste.

**3. Complexity vs Operability**
Cache invalidation, cache stampede, thundering herd போன்ற problems வரும். Simple system cache-ஐ பெரிதாக்கும்போது operational complexity அதிகரிக்கும்.

**Failure modes**:
* **Cache miss storm**: Popular key expire ஆகி எல்லோரும் origin-க்கு போவார்கள். Origin down ஆகும்.
* **Stale read**: DB update ஆனது cache update ஆகவில்லை.
* **Key collision**: Different queries same key ஆகி தவறான answer.

## 6. Practical Example

நீங்கள் ஒரு AI support chatbot run பண்ணுகிறீர்கள். 10,000 users.

Flow:
User Query → Normalize → Check Redis cache with key = `hash(query + user_tier)`
Hit → Return in 10ms, $0 cost
Miss → Retrieve context from vector database → Call LLM → Store result in Redis with TTL 10 min → Return

முதல் நாள் hit rate 0%. மூன்றாவது நாள் hit rate 35% ஆகிறது. Monthly LLM cost 35% குறையும்.

Embedding cache:
Document ingestion-ல 50,000 docs. Same doc மீண்டும் upload ஆகிறது. Text hash-ஐ key ஆக்கி embedding vector-ஐ cache செய்தால், embedding API cost முற்றிலும் தவிர்க்கலாம்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG system இருக்கிறது. Users அதே question-ஐ சற்று வேறு wording-ல கேட்கிறார்கள்.

Option A: Exact query string-ஐ key ஆக்கி cache பண்ணுவது.
Option B: Query embedding-ஐ பயன்படுத்தி semantic similarity-ல cache lookup பண்ணுவது.

Cost, latency, correctness ஆகியவற்றை பார்த்து நீங்கள் எதை தேர்வு செய்வீர்கள்? எந்த trade-off ஏற்படும்?

## 8. Key Takeaways

* Cache என்பது **repeat work-ஐ தவிர்க்க** வைக்கப்பட்ட fast memory layer.
* AI Cost Architecture-ல caching = latency குறைப்பு + token cost குறைப்பு.
* Hit rate, freshness, invalidation ஆகிய மூன்றும் முக்கிய architectural decisions.
* ஒவ்வொரு cache-க்கும் ஒரு cost உண்டு: stale data மற்றும் operational complexity.
