# Retrieval traces

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.9 — Observability

## 1. Problem

உங்க RAG system-ல user கேள்விக்கு பதில் தப்பா வருது. அல்லது hallucinating பண்ணுது. அல்லது சரியான document இருந்தும் அதை use பண்ணாமல் பதில் கொடுக்குது.

இப்போ நீங்க debug பண்ண முயற்சிக்கிறீங்க. LLM output மட்டும் பார்த்தால் போதாது. ஏன் அந்த பதில் வந்தது என்பதை தெரிஞ்சுக்கணும். 

எந்த chunks retrieve ஆச்சு? எந்த chunks பார்க்காமல் போய்விட்டது? Retrieval score என்ன? LLM அந்த retrieved context-ஐ பயன்படுத்தினதா, ignore பண்ணினதா?

**What goes wrong if we don't have this?** Production-ல bad answer வந்தால் root cause தெரியாது. Embedding quality தப்பா, chunking தப்பா, retriever config தப்பா, prompt தப்பா என்று guess பண்ண வேண்டியிருக்கும். Fix செய்வது slow, expensive.

---

## 2. Mental Model

Retrieval trace என்பது ஒரு query-க்கு ஏற்பட்ட **retrieval journey-யின் audit log**.

> Query → Retriever → Candidate pool → Ranked results → Selected top-K → Passed to LLM

இந்த flow-ல என்ன நடந்தது என்பதை step-by-step capture பண்ணுவது தான் retrieval trace.

இது distributed system-ல request trace மாதிரி. ஆனால் இங்கே focus ரெண்டு system boundary-ல: vector database / retriever மற்றும் LLM.

ஒரு trace-ல இருக்க வேண்டியது:
* query text, embedding vector id
* retriever config: top-K, filter, hybrid weights
* retrieved documents: doc id, chunk text, score, metadata
* reranker output if any: score change
* final context sent to LLM

இது ஒரு decision record. பின்னால் பார்த்து, "இந்த answer ஏன் இப்படி வந்தது" என்பதை reproduce பண்ண முடியும்.

---

## 3. How It Works

RAG request வரும்போது, tracing SDK அல்லது middleware ஒரு trace span உருவாக்கும்.

1. **Retrieval span** start
2. Retriever-க்கு query போகும். Vector DB query latency, number of candidates scanned capture ஆகும்.
3. Raw results வரும். ஒவ்வொரு result-க்கும் score, doc id, chunk hash save ஆகும்.
4. Reranker இருந்தால் அதன் input/output log ஆகும்.
5. Top-K context assemble ஆகி LLM-க்கு போகும். Context size, token count log ஆகும்.

இந்த data structured JSON-ல store ஆகும். Observability backend-ல query ID வைத்து join பண்ணலாம்: retrieval trace + LLM trace + final answer.

Practical-ல LangSmith, Arize, Langfuse போன்ற tools இதை auto capture பண்ணும். Custom-ல நீங்கள் OpenTelemetry span attributes-ல doc ids, scores வைக்கலாம்.

---

## 4. Architectural Reasoning

Retrieval trace useful ஆகும் போது?

* **Quality debug**: Answer wrong ஆனால் retrieval empty / irrelevant ஆக இருந்ததா?
* **Retriever tuning**: Top-K 5 vs 10, hybrid vs pure vector, filter change செய்தால் result எப்படி மாறுகிறது?
* **Data drift detection**: சில queries-க்கு score திடீரென குறைந்து விட்டதா? Embedding model அல்லது document corpus மாறியதா?
* **Cost & latency**: ஒவ்வொரு query-க்கும் எத்தனை candidates scan ஆகிறது? Reranker latency bottleneck ஆகிறதா?

Alternatives: Just log LLM prompt/output. அது போதாது. Retrieval என்பது black box ஆகி விடும். Full document dump log பண்ணலாம், ஆனால் அது search & analysis கஷ்டம்.

Architectural decision: Trace data-ஐ long-term store செய்ய வேண்டுமா? High volume-ல cost அதிகம். Sampling பண்ணலாம், or error cases மட்டும் full trace save பண்ணலாம்.

---

## 5. Trade-offs

* **Observability vs Cost**: ஒவ்வொரு retrieval result-க்கும் chunk text store பண்ணினால் storage பெரியது. Doc id + score மட்டும் store பண்ணி, text-ஐ on-demand fetch பண்ணலாம். Trade-off: faster storage vs slower debugging.
* **Privacy & PII**: User query, retrieved doc text sensitive ஆக இருக்கலாம். Trace storage-ல encryption, retention policy தேவை.
* **Noise**: Top-K 20 retrieve பண்ணினால் trace பெரிதாகும். அதில் useful signal குறைவு. Trace schema minimal ஆக வைத்து, முக்கிய attributes மட்டும் log பண்ணுவது நல்லது.
* **Causality**: Retrieval trace சொல்லும் "what was retrieved". அது "why LLM ignored it" சொல்லாது. அதற்கு LLM attribution trace தேவை. ரெண்டையும் join பண்ண வேண்டும்.

Failure mode: Trace incomplete ஆனால், false root cause analysis நடக்கும். Ex: retriever சரியாக இருந்தும் LLM context window overflow ஆகி context truncate ஆகி இருந்தால், retrieval trace மட்டும் பார்த்தால் நீங்கள் retriever-ஐ blame பண்ணி விடுவீர்கள்.

---

## 6. Practical Example

Enterprise support chatbot. User கேட்கிறார்: "Refund policy for cancelled flights after 24 hours".

System returns wrong policy. Retrieval trace பார்த்தால்:
* Query embedding → vector DB returned top-5
* Rank 1: blog post about flight change, score 0.78
* Rank 2: FAQ about refund, score 0.71
* Rank 3-5: unrelated travel insurance docs

Reranker promoted blog post to top. LLM used blog post.

Root cause தெரியும்: Retriever score high ஆனால் doc type filter இல்லை. Blog post authoritative policy document அல்ல. Fix: Metadata filter `doc_type = policy` add பண்ணு, அல்லது reranker training data bias fix பண்ணு.

இல்லாமல் நீங்கள் embedding model மாற்றி try பண்ணிக்கொண்டே இருப்பீர்கள்.

---

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இல்லை. 1000 RPS RAG service இருக்கு. ஒவ்வொரு request-க்கும் average 8 retrieved chunks, ஒவ்வொரு chunk 500 tokens.

Retrieval trace-ஐ full text-உடன் store செய்யலாமா? செய்ய வேண்டாமா? என்ன strategy எடுப்பீர்கள்? Cost, debug ability, privacy எப்படி balance பண்ணுவீர்கள்?

---

## 8. Key Takeaways

* Retrieval trace என்பது RAG-ன் **why**-ஐ புரிந்துகொள்ளும் audit trail.
* Query → candidates → scores → final context என்ற flow-ஐ capture பண்ணுவது, bad answers-க்கு root cause-ஐ குறைந்த நேரத்தில் கண்டுபிடிக்க உதவும்.
* Trace data design-ல storage cost, privacy, signal-to-noise trade-off இருக்கு. Doc id + score + metadata போதும், full text optional.
* Retrieval trace alone போதாது. LLM trace உடன் join பண்ணி, retrieval-to-answer causality பார்க்க வேண்டும்.
