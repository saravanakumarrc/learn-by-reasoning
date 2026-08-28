# Distillation

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.3.8 — Model patterns

## 1. Problem

உங்களிடம் ஒரு பெரிய LLM இருக்கு. 70B அளவு, excellent quality, ஆனால் inference cost அதிகம், latency அதிகம், GPU தேவை அதிகம்.

Production-ல் ஒரு chatbot, RAG service, அல்லது agent ஓட வேண்டும். User prompt வந்ததும் 2-3 seconds response வேண்டும். 1000 requests per minute வருகிறது. Large model-ஐ அப்படியே போட்டால் cost மாதத்திற்கு lakhs, latency போதாது, scaling கஷ்டம்.

அதே தரத்தை சிறிய model-ல் கொண்டு வர முடிந்தால் என்ன ஆகும்? Small model = குறைவான latency, குறைவான cost, edge-ல் கூட ஓடும்.

இங்கே வரும் pain: **Quality vs Cost/Latency/Operability trade-off.**

Distillation தேவைப்படுவதற்கான root cause இதுதான்.

## 2. Mental Model

Distillation என்பது ஒரு teacher-student உறவு.

Teacher = பெரிய, expensive, high-quality model.
Student = சிறிய, fast, cheap model.

Teacher-ஐ எப்போதும் பயன்படுத்தாமல், teacher-ன் knowledge-ஐ student-க்கு transfer பண்ணி, student-ஐ மட்டும் production-ல் வைக்கிறோம்.

இது student-ஐ ground truth labels-ல் மட்டும் train பண்ணுவது அல்ல. Teacher-ன் soft predictions, reasoning patterns, distribution-ஐ கற்றுக்கொள்ள வைக்கிறோம்.

## 3. How It Works

Classic distillation simple-ஆ:

1. Teacher model-ஐ ஒரு dataset-ல் run செய். உதாரணமாக instruction prompts.
2. Teacher output-ஐ மட்டும் இல்லாமல், teacher-ன் output distribution, logits-ஐ capture செய்.
3. Student model-ஐ அந்த teacher signals-க்கு மாற்ற train செய்.

Key idea: Hard label 0/1 க்கு பதிலாக teacher-ன் soft targets-ஐ use செய்வது. இது student-க்கு **why** புரிந்துகொள்ள உதவும்.

Modern LLM distillation-ல்:
* **Response distillation**: Teacher-ஐ வைத்து high-quality responses generate செய்து, அதை student training data-ஆக பயன்படுத்துதல். SFT data quality improve ஆகும்.
* **Logit distillation**: Teacher logits-ஐ student reproduce செய்ய வைத்தல்.
* **Process distillation**: Teacher-ன் chain-of-thought steps-ஐ student-க்கு கற்றுக்கொடுத்தல்.

Distillation ஒரு one-time training cost. Inference-ல் teacher தேவையில்லை.

## 4. Architectural Reasoning

Distillation எப்போது useful?

* **Latency sensitive services**: Chat UI, real-time assistant. Small model 50ms-ல் respond செய்யும்.
* **Cost sensitive at scale**: 10k RPM traffic-ல் large model cost prohibitive. Distilled 7B/3B model-ல் போதும்.
* **Edge / on-device**: Mobile, IoT, offline scenarios. Large model fit ஆகாது.
* **Filter / routing layer**: Distilled small model-ஆல் easy queries-ஐ filter செய்து, hard queries மட்டும் large model-க்கு route செய்யலாம்.

Alternatives:
* Quantization / Pruning: Same model-ஐ smaller footprint-க்கு கொண்டு வரும், quality drop இருக்கும்.
* Speculative decoding: Latency குறைக்கும் ஆனால் cost மாறாது.
* Caching: Repeat queries-க்கு மட்டும் வேலை செய்யும்.

Architect choice: Quality target-ஐ define செய். உதாரணமாக "Teacher-ன் 85% quality-ஐ 30% cost-ல் பெற வேண்டும்". அந்த target achieve ஆகுமா என்று distillation-ன் capacity gap-ஐ பார்க்க வேண்டும்.

## 5. Trade-offs

**Quality loss is inevitable.** Student teacher-ஐ 100% mimic செய்ய முடியாது. Complex reasoning, rare knowledge tasks-ல் gap தெரியும்.

**Data dependency.** Distillation quality training data quality-ஐ நம்பும். Teacher-ன் weak outputs-ஐ student கற்றால் garbage in garbage out.

**One-time compute cost.** Teacher inference for millions of examples அதிக GPU hours எடுக்கும். ஆனால் அது amortize ஆகும்.

**Maintainability.** Teacher update ஆனால் student re-distill செய்ய வேண்டும். Version drift வரும்.

**Security / IP.** Teacher model proprietary ஆக இருந்தால், teacher outputs-ஐ external data generation-க்கு use செய்யும் போது data leakage risk.

முக்கிய failure mode: Student overfits to teacher style, not task. Teacher hallucination-ஐ student learn செய்துவிடும்.

## 6. Practical Example

Enterprise RAG assistant.

Teacher: 70B instruct model. Retrieval context + question → high quality answer, good reasoning.

Constraint: 500 ms p95 latency, cost per query < $0.001.

Solution:
* Teacher-ஐ வைத்து internal curated Q&A dataset + real user queries-ல் synthetic high-quality responses generate செய். 
* அந்த responses-ஐ வைத்து 7B student model-ஐ fine-tune செய்.
* Production-ல் student model மட்டும் run செய். Hard queries-க்கு fallback to teacher.

Result: Latency 180ms, cost 4x குறைவு, quality human eval-ல் teacher-ன் ~90%.

இதுதான் real architectural decision: Distillation-ஐ quality gate ஆக use செய்யாமல், cost-latency gate ஆக use செய்வது.

## 7. Reasoning Challenge

உங்களிடம் customer support chatbot இருக்கு. 80% queries simple FAQ, 20% complex troubleshooting.

Large model-ஐ எல்லா query-க்கும் பயன்படுத்துகிறீர்கள். Cost அதிகம்.

Distillation strategy-ஐ எப்படி design செய்வீர்கள்? Small student model-ஐ மட்டும் பயன்படுத்துவீர்களா, அல்லது router + teacher fallback architecture வைப்பீர்களா? ஏன்?

## 8. Key Takeaways

* Distillation என்பது teacher-ன் knowledge-ஐ student-க்கு transfer செய்வது, model size குறைக்க.
* Problem solve ஆவது inference cost, latency, operability, not training accuracy.
* Student quality always < teacher, capacity gap-ஐ accept செய்ய வேண்டும்.
* Distillation + routing hybrid பல production systems-ல் best trade-off தரும்.
