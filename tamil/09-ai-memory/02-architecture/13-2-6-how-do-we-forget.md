# How do we forget?

> **Learning Path:** AI Memory
> **Section:** 13.2.6 — Architecture

## 1. Problem

AI system-ல memory add ஆகிக்கிட்டே இருக்கும். User conversation, documents, agent actions, embeddings எல்லாம் accumulate ஆகும்.

இப்படி விட்டால் என்ன ஆகும்?

* Vector database size கிட்டத்தட்ட infinity-க்கு போகும்
* Retrieval latency அதிகரிக்கும், relevant results கிடைக்காமல் noise-ல மூழ்கும்
* Cost linear-ஆ வளரும்
* Old, irrelevant, toxic, outdated information-ம் same weight-ல இருக்கும்

Forget பண்ணாமல் இருந்தால் system slow ஆகும், inaccurate ஆகும், expensive ஆகும்.

எனவே memory-க்கும் lifecycle வேண்டும். Keep everything என்பது architecturally unsustainable.

## 2. Mental Model

Human memory-ல forgetting என்பது bug இல்லை, feature.

AI memory-ல forgetting = intentional decay and pruning.

நாம் மூன்று விஷயங்களை கட்டுப்படுத்துகிறோம்:

* **What to keep** - importance
* **How long to keep** - recency / TTL
* **How to compress** - summarize before discard

Forget செய்வது delete மட்டும் இல்லை. Summarize, archive, degrade, expire என்ற options இருக்கு.

## 3. How It Works

Architecture-ல forgetting என்பது usually 3 layers-ல நடக்கும்.

**Access Layer:** Retrieval-க்கு முன் filter
* Time window: last 90 days மட்டும்
* Relevance score threshold

**Scoring Layer:** ஒவ்வொரு memory item-க்கும் score கணக்கு
```
score = α * recency + β * frequency + γ * importance
```
Recency decay: exponential decay
Frequency: எத்தனை முறை access ஆச்சு
Importance: user marked, task critical, sentiment strong

Score கீழே போனால் candidate for forgetting.

**Action Layer:** என்ன செய்ய வேண்டும்?
* Soft delete / TTL expire
* Summarize -> one summary vector உருவாக்கி raw items-ஐ archive பண்ணு
* Move to cold storage: S3 / cheaper vector DB
* Hard delete for compliance / privacy

இது background job-ஆ continuous-ஆ ஓடும்.

## 4. Architectural Reasoning

எப்போது forgetting தேவை?

* Long-running agent, RAG system, personal assistant
* User base large, data volume high
* Cost and latency sensitive
* Regulatory retention policy உள்ளது

Alternatives:
* Keep everything forever -> simple, but cost & noise
* Manual delete -> not scalable
* No decay -> retrieval quality degrade ஆகும்

Architect choose பண்ணுவது:
Recency முக்கியமா? → TTL + sliding window
Domain knowledge stable ஆ? → summarize and keep summary
Privacy critical ஆ? → hard delete + audit log

## 5. Trade-offs

**Forgetting vs Recall Completeness**
Forget செய்தால் storage & latency குறையும். ஆனால் rare but important old memory தொலையும் risk.

**Summarization vs Raw Retention**
Summarize பண்ணி space save பண்ணலாம். ஆனால் details loss ஆகும். Reconstructive error வரும்.

**Automatic vs Policy-driven**
Automatic decay simple. ஆனால் business critical data தவறாக expire ஆகலாம். Policy-driven safe but operational overhead அதிகம்.

**Failure modes**
* Decay too aggressive → system forgets context, user experience breaks
* Decay too slow → vector DB bloat, retrieval drift
* Summarization bias → summary captures dominant voice, minority info lost
* Deletion without audit → compliance issue, non-reproducible answers

## 6. Practical Example

Enterprise RAG for support agent.

User tickets, KB articles, chat history 2 years accumulate ஆகி 40M vectors.

Architecture:
* Hot store: Pinecone for last 180 days, recency decay >0.7
* Warm store: Summarized monthly clusters stored in Qdrant with importance score
* Cold store: Raw logs in S3 Glacier, 1 year TTL

Background job daily:
Score compute பண்ணி bottom 5% items-ஐ summarize → summary vector create → raw items archive.

Result: Retrieval latency 180ms → 65ms, cost 40% down, relevance improve ஆச்சு.

## 7. Reasoning Challenge

உங்களிடம் healthcare AI memory இருக்கு. Patient conversations, clinical notes, lab results.

Regulation சொல்லுது: PHI data 7 years retain பண்ணணும். ஆனால் retrieval-க்கு recent 6 months மட்டும் தேவை.

இங்கே forgetting architecture எப்படி design பண்ணுவீர்கள்? Delete செய்ய முடியாது, ஆனால் hot retrieval-ல இருந்து எடுக்க வேண்டும். Trade-off என்ன?

## 8. Key Takeaways

* Forgetting என்பது cost, latency, quality-க்கான architectural necessity, இல்லாத bug அல்ல
* Score = recency + frequency + importance என்ற model-ல decide பண்ணு, random delete அல்ல
* Delete மட்டும் இல்லை: summarize, archive, TTL expire என்ற spectrum உண்டு
* Every forgetting policy creates risk of losing rare important memory, அதற்கு audit & recovery path வைத்திரு
