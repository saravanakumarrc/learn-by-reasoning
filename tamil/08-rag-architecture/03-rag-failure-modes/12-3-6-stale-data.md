# Stale data

> **Learning Path:** RAG Architecture
> **Section:** 12.3.6 — RAG failure modes

### 12.3.6 — RAG failure modes: Stale data

## 1. Problem

உங்கள் RAG system ஒரு enterprise knowledge base-ஐ serve பண்ணுது. Document update ஆகும். உதாரணமாக, pricing page மாறியது, policy update ஆனது, product spec மாறியது.

User query வருது: "இந்த மாதம் subscription price என்ன?"

LLM vector database-ல இருந்து retrieve பண்ணி answer கொடுக்குது. ஆனா அந்த answer 2 மாதம் பழைய price-ஐ காட்டுது.

என்ன நடந்தது? Source document update ஆனது. ஆனால் embedding pipeline அதை process பண்ணல. Vector index மாறல. Cache-ல பழைய chunk இருக்கு.

User-க்கு wrong information போய்விட்டது. Trust போய்விட்டது. இதுதான் stale data failure.

**What goes wrong if we don't have this?** Freshness guarantee இல்லாமல் RAG ஒரு hallucination machine ஆகிவிடும், ஆனால் source உள்ளது என்ற பாசாங்கில்.

## 2. Mental Model

RAG = Retrieve + Generate.

Retrieve என்பது **point-in-time snapshot** of knowledge.

Source world மாறிக்கொண்டே இருக்கும். Embedding index, vector database, cache ஆகியவை மாறாமல் இருந்தால், நீங்கள் past-ஐ retrieve பண்ணி present-க்கு generate பண்ணுகிறீர்கள்.

Stale data என்பது **source freshness ≠ index freshness** என்ற gap.

## 3. How It Works

Typical flow:
`Source Document -> Ingestion -> Chunking -> Embedding -> Vector DB -> Retrieval -> LLM`

Stale data வரும் இடங்கள்:

* **Ingestion lag:** Document update ஆனது, ஆனால் crawler / webhook trigger ஆகல.
* **Index lag:** Document ingest ஆனது, ஆனால் embedding job queue-ல் pending-ல் இருக்கு.
* **Version mismatch:** Multiple sources. Vector DB-ல் old version chunk இன்னும் இருக்கு, new version add ஆனது ஆனால் delete ஆகல.
* **Cache staleness:** Retrieval result or LLM answer cache ஆகி, source மாறியும் serve ஆகுது.

இது silent failure. Error வராது. Wrong answer வரும்.

## 4. Architectural Reasoning

இது painful ஆகும் போது தேவை:

* Time-sensitive knowledge: pricing, inventory, policy, SLA, medical guidelines
* High write churn: documents நிறைய update ஆகும்
* Compliance need: "as of date" prove பண்ண வேண்டும்

Options:

* **Pull-based re-ingest:** Periodic full crawl. Simple ஆனால் lag அதிகம்.
* **Push-based update:** Source system webhook emit செய்யும். Ingestion near real-time.
* **Versioned index:** ஒவ்வொரு document-க்கும் version, timestamp, updated_at. Retrieval-ல் filter.
* **Hybrid freshness:** Hot documents real-time sync, cold documents batch sync.

Architect முடிவு எடுக்கும்போது கேட்க வேண்டியது:
Latency requirement என்ன? Data freshness SLA என்ன? 5 min? 1 hour? 1 day?

## 5. Trade-offs

* **Freshness vs Cost:** Real-time embedding = compute cost அதிகம். Batch = cheap ஆனால் stale.
* **Consistency vs Availability:** New document ingest ஆகும் வரை old answer serve செய்வது safe ஆ? அல்லது "I don't know" சொல்வது safe ஆ?
* **Index size vs Correctness:** Old version-ஐ delete பண்ணாமல் வைத்தால் duplicate retrieval வரும். Delete பண்ணினால் replay/ audit கஷ்டம்.
* **Operability:** Freshness monitoring வேண்டும். Source updated_at vs index updated_at drift-ஐ track செய்ய வேண்டும்.

Failure mode: Update ஆன document-க்கு embedding பண்ணும்போது chunk boundary மாறி, old chunks orphan ஆகி vector DB-ல் தங்கிவிடும். User still gets old info.

## 6. Practical Example

Enterprise RAG for support.

Product docs S3-ல் உள்ளது. `price.md` Aug 1-ல் ₹999 என்று இருந்தது. Sep 1-ல் ₹1,199 ஆக மாறியது.

Ingestion pipeline daily batch 2 AM-ல் run ஆகும். Sep 1-ல் 10 AM-க்கு user query வந்தது. Vector DB-ல் ₹999 தான் இருக்கு. LLM confidently answer கொடுக்குது.

Fix:
* Source-ல் webhook போட்டு S3 object updated event-ஐ capture செய்ய.
* Ingestion service document-ஐ fetch பண்ணி, version check பண்ணி, old chunks-ஐ delete பண்ணி new chunks-ஐ upsert பண்ணு.
* Vector metadata-ல் `doc_updated_at` store பண்ணு. Retrieval-ல் `doc_updated_at > 30 days` என்றால் warn செய்.
* Answer-ல் citation along with "as of Sep 1 2025" காட்டு.

## 7. Reasoning Challenge

உங்கள் RAG system-ல் 1M documents உள்ளது. 5% documents மட்டும் வாரம் ஒரு முறை update ஆகும். Freshness SLA 1 hour.

நீங்கள் full re-index every hour செய்வீர்களா? அல்லது incremental update + versioning செய்வீர்களா? ஏன்? Cost, latency, correctness எப்படி trade-off ஆகும்?

## 8. Key Takeaways

* Stale data = source update ஆனது, ஆனால் index update ஆகவில்லை. Silent wrong answer.
* Freshness ஒரு architectural constraint, feature அல்ல.
* Ingestion lag, index lag, cache lag மூன்றையும் monitor செய்ய வேண்டும்.
* Hot data-க்கு push, cold data-க்கு batch. Version metadata retrieval-ல் பயன்படுத்து.
* Always answer-ல் source timestamp காட்டு. Trust restore ஆகும்.
