# Model capabilities

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.1.13 — Understand

## 1. Problem

நீங்கள் ஒரு AI Solution Architect-ஆக இருக்கிறீர்கள். Product team வருகிறது:

> "LLM-ஐ வைத்து chat assistant பண்ண வேண்டும். Code generate பண்ண வேண்டும். Document summarize பண்ண வேண்டும். Customer support ticket-ஐ classify பண்ண வேண்டும். Real-time translation-ம் வேண்டும்."

ஒரே model-ஐ எடுத்து எல்லாவற்றையும் செய்ய முடியுமா? எந்த model எடுக்க வேண்டும்? எந்த size? எங்கே host பண்ண வேண்டும்?

இங்கே problem என்னவென்றால் **model capabilities-ஐ தெரியாமல் architecture தேர்வு செய்தால்**, நீங்கள் overpay பண்ணுவீர்கள், latency அதிகரிக்கும், accuracy விழும், மற்றும் production-ல் தோல்வி காண்பீர்கள்.

Model capabilities என்பது வெறும் benchmark score அல்ல. அது **எந்த வகை task-க்கு model பொருத்தமானது, என்ன constraints-ல் வேலை செய்யும், எங்கே fail ஆகும்** என்பதை புரிந்து கொள்வது.

## 2. Mental Model

Model capability-ஐ ஒரு tool belt-ஆக நினைத்துக்கொள்ளுங்கள்.

ஒரு hammer, screwdriver, power drill எல்லாம் tool-தான். ஆனால் ஒவ்வொன்றும் வெவ்வேறு job-க்கு பொருத்தமானது.

LLM-களும் அப்படித்தான்.

Capability = **what the model can reliably do given its training data, architecture, context window, reasoning depth, tool use ability, and operational constraints**.

ஒரு model-க்கு 3 layers உள்ளன:

* **Base capability:** pre-training-ல் கற்ற general language understanding, reasoning, code, math
* **Fine-tuned capability:** instruction following, safety, style, domain adaptation
* **Operational capability:** context window size, speed, cost per token, latency, ability to call tools / use RAG

Architect-ஆக நீங்கள் எல்லா layers-ஐயும் பார்க்க வேண்டும்.

## 3. How It Works

Model capabilities எப்படி உருவாகின்றன?

**Training data distribution:** Model பார்த்த data என்ன என்பதுதான் முதல் filter. Legal document-கள் குறைவாக இருந்தால், legal reasoning மோசமாக இருக்கும்.

**Scale:** Parameters, compute, training tokens. பெரிய model-கள் ஆழமான reasoning, few-shot learning-ல் சிறப்பாக இருக்கும்.

**Context window:** 4K vs 128K. Long document summarize செய்ய வேண்டுமென்றால் context தேவை.

**Reasoning / inference time:** சில models internal chain-of-thought செய்கின்றன. அது accuracy-ஐ உயர்த்தும், ஆனால் latency மற்றும் cost அதிகரிக்கும்.

**Tool use & agent capability:** Model-க்கு API call செய்ய, function calling செய்ய தெரியுமா? RAG-ல் retrieve செய்த info-வை grounded-ஆக பயன்படுத்துமா? Hallucination rate என்ன?

இவை எல்லாம் சேர்ந்துதான் capability profile உருவாகிறது.

## 4. Architectural Reasoning

Model தேர்வு செய்யும்போது ஒரு architect கேட்க வேண்டிய கேள்விகள்:

* **Task type என்ன?** Classification vs generation vs reasoning vs code synthesis vs multi-step agent task.
* **Latency constraint என்ன?** Chatbot-க்கு 500ms வேண்டும். Long report generation-க்கு 10s ஏற்புடையது.
* **Accuracy vs cost trade-off:** 70B model 8B model-ஐ விட 3x accurate ஆக இருக்கலாம், ஆனால் 10x cost.
* **Data sensitivity:** On-prem deployment வேண்டுமா? Private data-ஐ cloud LLM-க்கு அனுப்ப முடியுமா?
* **Context length:** 100-page PDF summarize செய்ய வேண்டுமா? அப்போது 128K context தேவை.
* **Tool use தேவையா?** Database query, calculator, search engine-ஐ call செய்ய வேண்டுமா?

இதனால் தான் **one size fits all** இல்லை. சில use cases-க்கு small, fast, cheap model போதும். சில use cases-க்கு large reasoning model தேவை.

## 5. Trade-offs

**Capability vs Cost:** பெரிய model = better reasoning, ஆனால் per token cost அதிகம், throughput குறைவு.

**Capability vs Latency:** Deep reasoning, large context = slower response. Real-time support bot-க்கு இது தடை.

**Capability vs Control:** Open-source model-கள் self-host செய்யலாம், data privacy கிடைக்கும், ஆனால் operational complexity அதிகம். Closed API models எளிது, ஆனால் vendor lock-in.

**Capability vs Hallucination:** Stronger model என்றாலும் domain-specific tasks-ல் RAG இல்லாமல் hallucinate செய்யும். Capability என்பது standalone knowledge அல்ல, retrieval + grounding-உடன் பார்க்க வேண்டும்.

**Capability vs Maintainability:** ஒரே model-ஐ எல்லா tasks-க்கும் பயன்படுத்துவது எளிது. ஆனால் performance sub-optimal ஆகும். Multiple specialized models வைத்தால் routing logic, evaluation overhead வரும்.

## 6. Practical Example

Enterprise support platform.

Requirement: 
1. Incoming ticket-ஐ intent classify செய்ய
2. Knowledge base-ல் relevant articles retrieve செய்து answer generate செய்ய
3. Complex technical escalation-க்கு senior engineer-க்கு summary தயாரிக்க

எப்படி reason பண்ணுவீர்கள்?

* Intent classification: Simple text classification. 3B-8B class of model, low latency, cheap. Accuracy >95% போதும்.
* RAG answer generation: Context window 32K+, good instruction following, grounded generation. Mid-size model 14B-70B range.
* Complex summary for escalation: Deep reasoning தேவை. Larger reasoning model, maybe with longer inference time.

Architectural decision: **Router + Model tiering**. Simple tasks-க்கு small fast model. Complex tasks-க்கு large reasoning model. All share same RAG pipeline.

இதனால் cost 40-60% குறையும், latency improve ஆகும், மற்றும் quality maintain ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு fintech app உள்ளது. Two needs:

1. Real-time fraud transaction description generation: latency < 200ms, 1000 RPS.
2. Monthly compliance report generation from 200 pages of documents: accuracy critical, latency 30 sec acceptable.

ஒரே model-ஐ பயன்படுத்தலாமா? இல்லையென்றால் என்ன architecture தேர்வு செய்வீர்கள்? Cost, latency, accuracy எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* Model capability என்பது benchmark score அல்ல. Task fit, latency, cost, context, tool use ஆகியவற்றின் கூட்டு.
* ஒரு model எல்லாவற்றையும் சிறப்பாக செய்யாது. Architect ஆக capability profile-ஐ பார்த்து tiered model strategy வடிவமைக்க வேண்டும்.
* Capability decision என்பது technical மட்டுமல்ல. Business constraint: cost per request, availability, data privacy, operational complexity.
* Model தேர்வுக்கு முன் task-ஐ define செய்யுங்கள், failure mode-ஐ புரிந்து கொள்ளுங்கள், பிறகு model-ஐ தேர்வு செய்யுங்கள்.
