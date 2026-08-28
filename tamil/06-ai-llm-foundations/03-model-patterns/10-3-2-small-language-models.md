# Small language models

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.3.2 — Model patterns

## 1. Problem

நீங்கள் ஒரு enterprise app-ஐ build பண்ணறீங்க. LLM-ஐ use பண்ணணும். ஆனா...

* Latency முக்கியம். User-facing chatbot-ல 2-3 seconds-க்கு மேல wait பண்ண மாட்டாங்க.
* Cost முக்கியம். 1M requests per day, GPT-4 level pricing-ல budget collapse ஆகும்.
* Data private. Customer data-வை external API-க்கு அனுப்ப முடியாது. On-prem வேணும்.
* Device-லயே run பண்ணணும். Mobile app, edge device.

Large language model வச்சா இதெல்லாம் painful ஆகும். Model size பெருசு, GPU memory தேவை, inference slow, cost high.

இந்த constraints வந்ததும் engineers கேட்க ஆரம்பிச்சாங்க: Full capability வேண்டாம், specific task-க்கு மட்டும் போதும் என்றால், சின்ன model போதுமா?

## 2. Mental Model

Small language model என்பது **capability-வை குறைச்சு, size-வை குறைச்சு, speed-வும் cost-வும் குறைக்கிற compromise**.

Think of it like இது ஒரு specialist, not a generalist.

Large model = PhD generalist who can write essay, code, reason.
Small model = Skilled technician who can do one job very fast and cheaply, like classification, intent detection, summarization of fixed format.

Model size usually 1B to 8B parameters, sometimes up to 14B. Runs on CPU, small GPU, or even on-device.

## 3. How It Works

Size குறைக்க 3 வழிகள்:

**1. Train smaller from scratch or distill.** Large teacher model-ல இருந்து knowledge-வை student small model-க்கு transfer பண்ணுவது distillation. Output distribution-ஐ mimic பண்ணி train பண்ணுவாங்க.

**2. Quantization.** FP16/FP32 weights-ஐ INT4/INT8-க்கு மாற்றுவது. Accuracy சிறிது குறையும், but memory 4x குறையும், inference 2-3x fast.

**3. Architecture pruning / efficient attention.** Slimmer attention, Mixture-of-Experts selective activation, etc.

Result: Model இன்னும் language புரிஞ்சுக்கும், ஆனா long reasoning, rare knowledge, complex instruction following-ல தோற்கும்.

## 4. Architectural Reasoning

எப்போது small model useful?

* **Latency sensitive, high volume tasks.** Real-time intent classification, spam detection, entity extraction. 10ms response வேணும் என்றால் small model on CPU போதும்.
* **Cost sensitive at scale.** 1M requests/day. Large model per token cost * 1M = மாதம் லட்சங்கள். Small model self-hosted = fixed infra cost.
* **Privacy / offline.** Healthcare, finance data. Data leave பண்ணக்கூடாது. Small model on-prem or edge-ல run ஆகும்.
* **Specific domain with limited distribution.** Customer support FAQ, internal documentation Q&A. Domain small, so model need not know world knowledge.

எப்போது வேண்டாம்?

* Complex reasoning, multi-step planning, code generation, creative writing where quality drop unacceptable.
* Need broad world knowledge up-to-date.

Decision என்பது **accuracy vs latency vs cost vs privacy** trade-off-ல இருக்கு.

## 5. Trade-offs

**1. Capability vs Efficiency.** Small model-ல reasoning depth குறையும். Hallucination அதிகம். Prompt engineering sensitive. Complex prompt கொடுத்தால் degrade ஆகும்.

**2. Generality vs Specialization.** Large model zero-shot works. Small model-க்கு fine-tuning or few-shot examples கொடுக்கணும். Otherwise performance தரை.

**3. Operational simplicity vs accuracy.** On-device / on-prem small model = no API dependency, deterministic latency. ஆனா model updates, monitoring, evaluation overhead உங்கள் தலையில்.

**4. Cost model shift.** Large model = pay per token. Small model = upfront infra + engineering cost to fine-tune, evaluate, maintain. Low volume-ல large model cheaper, high volume-ல small model wins.

Failure modes: Overconfidence on wrong answers, context length குறைவு, long text-ல forget, instruction following fail.

## 6. Practical Example

Enterprise RAG chatbot with internal docs.

Problem: Employees ask questions on 10k internal PDFs. Need sub-second response, data cannot leave VPC.

Architecture:
* Small model 3B quantized INT4 on CPU cluster.
* Retrieval: vector database with embeddings from small embedding model.
* Pipeline: User query -> retrieve top-k chunks -> construct prompt with 2-3 examples -> small model generates answer with citation.

Why small? Latency <500ms, cost per query near zero, runs inside VPC. Accuracy enough for factual retrieval because model only needs to extract and rephrase, not reason deeply.

If user asks complex multi-hop reasoning, system falls back to larger model. Hybrid routing.

## 7. Reasoning Challenge

உங்களிடம் banking mobile app உள்ளது. On-device fraud explanation தேவை: transaction summary-ஐ user friendly sentence-ஆ மாற்ற வேண்டும். 10 million users, offline mode வேண்டும், latency <100ms.

Large LLM API use பண்ணலாமா? Small language model use பண்ணலாமா? எப்படி decide பண்ணுவீங்க? Accuracy, size, update frequency எப்படி balance பண்ணுவீங்க?

## 8. Key Takeaways

* Small language models exist because latency, cost, privacy, and on-device constraints made large models painful.
* They trade general intelligence for speed and efficiency. Specialist work-க்கு ideal.
* Use them when task is narrow, volume high, and latency/cost/privacy constraints dominate.
* Every deployment needs evaluation: accuracy on real data, fallback strategy, and clear understanding of where it will fail.
