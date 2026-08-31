# Missing documents

> **Learning Path:** RAG Architecture
> **Section:** 12.3.2 — RAG failure modes

## 12.3.2 — RAG failure modes: Missing documents

### 1. Problem

உங்க RAG system-ல user ஒரு question கேக்கிறார். Retrieval பண்ணி top-k chunks எடுத்து, LLM-க்கு கொடுக்கிறீங்க. LLM பதில் சொல்லுது. ஆனா அந்த பதில் தப்பா இருக்கு, அல்லது "I don't have enough information"ன்னு சொல்லுது.

ஏன்? 
ஏன்னா தேவையான document-ஐ vector database-லேயே இல்லை. அல்லது document இருக்கு, ஆனா chunking/embedding-ல கெட்டுபோய் retrieve ஆகல.

இது silent failure. System crash ஆகாது. Latency நல்லா இருக்கும். ஆனா answer quality மோசமா இருக்கும். User trust போயிடும்.

### 2. Mental Model

RAG-ன் trust chain இப்படி:
**Source → Ingestion → Chunking → Embedding → Index → Retrieval → Context → Generation**

Missing documents என்பது chain-ன் முதல் பகுதியிலேயே break ஆகிறது. Retrieval எவ்வளவு smart-ஆ இருந்தாலும், index-ல தகவல் இல்லாமல் எதையும் கண்டுபிடிக்க முடியாது.

இது "garbage in, garbage out" க்கு முன்னாடி வரும் "nothing in" பிரச்சனை.

### 3. How It Works

Missing documents பொதுவாக 3 இடத்தில் உருவாகும்:

**a. Ingestion gap:** 
Source system-ல document create/update ஆனது, ஆனா ingestion pipeline-க்கு signal போகல. அல்லது pipeline fail ஆனது, retry இல்லை. 
Event-driven ingestion இல்லாததால் manual sync மிஸ் ஆகும்.

**b. Chunking / filtering loss:**
Document இருக்கு, ஆனா chunking strategy மோசமா இருக்கு. முக்கியமான info ஒரு chunk-ன் edge-ல cut ஆகி, context இழக்கிறது. அல்லது filter பண்ணும்போது PII, boilerplate நீக்கும்போது useful data தப்பா நீக்கப்படுது.

**c. Index staleness / drift:**
Document update ஆனது, ஆனா vector index மாற்றப்படல. Old embedding இன்னும் இருக்கு. அல்லது document delete ஆனது, index-ல இன்னும் இருக்கு. User-க்கு outdated அல்லது hallucinated answer.

Retrieval-ல top-k கிடைக்கும், ஆனா relevance zero. LLM அதை பயன்படுத்தி hallucinate பண்ணும்.

### 4. Architectural Reasoning

இது ஏன் painful? ஏன்னா RAG-ன் value proposition முழுக்க correctness மற்றும் coverage மேல தான். Missing doc இருந்தால் system மௌனமாக தோல்வி அடையும்.

எப்போ இது serious ஆகும்?
- Compliance / finance / healthcare போன்ற domain-ல, source of truth முக்கியம்
- Document set பெரியது, manual review சாத்தியமில்லை
- Updates frequent ஆக நடக்கும்

Options:
1. **Batch ingestion + periodic reconciliation.** எளிது, ஆனா lag அதிகம்.
2. **Event-driven ingestion with CDC.** Source change ஆன உடனே index update. Real-time, ஆனா operational complexity அதிகம்.
3. **Retrieval-time guardrails.** No relevant docs found என்றால் LLM-ஐ generate பண்ண விடாமல் fallback. இது missing-ஐ expose பண்ணும், ஆனா root cause-ஐ fix பண்ணாது.

Architect-க்கு முக்கியம்: coverage visibility வேண்டும். என்ன documents indexed, என்ன missing என்பதை தெரிந்துகொள்ள monitoring வேண்டும்.

### 5. Trade-offs

**Coverage vs Freshness vs Cost**
Real-time ingestion கொடுத்தால் freshness கிடைக்கும், ஆனா embedding compute cost, queue complexity அதிகரிக்கும்.

**Chunk size trade-off**
Small chunks = better retrieval precision, ஆனா context fragmentation. Large chunks = context retain ஆகும், ஆனா retrieval noisy ஆகும். Missing info chunk boundary-ல தொலையும்.

**Completeness check overhead**
ஒவ்வொரு query-க்கும் retrieval score low என்றால், document missing என்று அர்த்தமா? இல்லை query ambiguous-ஆ? இதை differentiate பண்ண கடினம்.

Failure modes:
- Silent staleness: User outdated policy document அடிப்படையில் decision எடுக்கிறார்.
- Partial coverage: சில departments-ன் docs மட்டும் index ஆகியிருக்கு, மற்றவை missing. User bias-ஐ assume பண்ண மாட்டார்.
- Poisoned fallback: No relevant docs என்றால் LLM-ஐ general knowledge-ல generate விட்டால் hallucination.

### 6. Practical Example

Enterprise HR RAG system. Employee handbook, payroll policy, benefits docs indexed.

Ingestion pipeline: SharePoint folder watcher → parser → chunker → embedding → vector DB.

Problem: Payroll policy PDF மாதத்திற்கு ஒருமுறை update ஆகும். Watcher cron job fail ஆனது. Log-ல error இல்லை, just silent skip.

User கேட்கிறார்: "ஜனவரி 2026 bonus payout date என்ன?"
System retrieve பண்ணது December 2025 version. LLM confidently தப்பான date சொல்லுது.

Fix: 
- Source of truth-ல document version metadata-ஐ store செய்து, index-ல last_ingested_version track செய்ய.
- Reconciliation job: daily ஒருமுறை source list vs index list compare செய்து missing/ stale docs alert.
- Retrieval score threshold + citation requirement. Score < 0.7 என்றால் "I don't have current info" என்று fallback.

### 7. Reasoning Challenge

உங்க company-ல 3 sources உள்ளன: GitHub repos, Confluence, Customer support tickets. 
GitHub daily update, Confluence weekly update, tickets real-time.

உங்க vector DB cost கட்டுப்படுத்த வேண்டும். Full re-embed ஒவ்வொரு முறையும் செலவு அதிகம்.

இங்கே ingestion frequency எப்படி design செய்வீர்கள்? Missing documents ஆகாமல் இருக்க என்ன observability வைப்பீர்கள்? ஏன்?

### 8. Key Takeaways

* RAG failure என்பது retrieval மட்டும் இல்லை, ingestion coverage முதல் problem தான்.
* Missing document = silent hallucination trigger. System healthy-ஆ தெரியும், ஆனா answer தப்பாகும்.
* Freshness-க்கு event-driven ingestion + periodic reconciliation இரண்டும் வேண்டும். ஒன்று மட்டும் போதாது.
* Retrieval score மற்றும் citation coverage-ஐ monitor செய்யாமல், missing docs-ஐ கண்டுபிடிக்க முடியாது.
