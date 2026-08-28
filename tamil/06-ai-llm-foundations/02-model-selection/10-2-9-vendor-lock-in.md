# Vendor lock-in

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.2.9 — Model selection

## 1. Problem

நீங்கள் ஒரு product-ஐ build பண்ணிக்கிட்டு இருக்கீங்க. AI feature-க்கு OpenAI GPT-4o use பண்ணீங்க. API simple, performance நல்லா இருக்கு, team fast move பண்ணுது.

6 மாசம் கழித்து:
* Cost double ஆகுது
* Latency spike ஆகுது peak time-ல
* New safety policy வந்து உங்கள் use case block ஆகுது
* Competitor Anthropic Claude-ல better quality கிடைக்குது

இப்போ மாறணும்னா என்ன ஆகும்? உங்கள் whole app OpenAI-specific API calls, OpenAI-specific embeddings, OpenAI-specific fine-tuning format, OpenAI-specific rate limit logic, prompt engineering pattern-உம் அதுக்கு tune ஆகி இருக்கு.

இது painful ஆகுது. இதுதான் vendor lock-in.

> "What problem became painful enough that engineers needed this concept?"
> நீங்கள் ஒரு provider-க்கு மாற்ற முடியாத அளவுக்கு ஒட்டிக்கொண்டால், அவர்கள் உங்கள் cost, reliability, roadmap-ஐ control பண்ண ஆரம்பிக்கிறார்கள்.

## 2. Mental Model

Vendor lock-in = Exit cost.

ஒரு vendor-ஐ விட்டு வெளியே வருவதற்கான technical + operational + business cost எவ்வளவு அதிகமாக இருக்கோ, அவ்வளவு lock-in அதிகம்.

AI/LLM world-ல இது மூன்று layer-ல வரும்:
* **Model layer:** provider-specific API, model IDs, context window behavior
* **Data layer:** embeddings, fine-tuned weights, vector DB built on provider-specific embedding dimension
* **Application layer:** prompts, tool calling format, safety filters, pricing assumptions

ஒரு distributed system-ல ஒரு service இன்னொரு service-ஐ call பண்ணும்போது coupling இருக்கும். அதே coupling தான் vendor lock-in.

## 3. How It Works

Lock-in உருவாகிறது மூன்று வழியில்:

**1. API surface coupling**
OpenAI `chat.completions.create` vs Anthropic `messages.create`. Tool schema வேறு. Streaming format வேறு. Error codes வேறு.

**2. Data format coupling**
நீங்கள் OpenAI `text-embedding-3-small` use பண்ணி 1536 dimension vector-ஐ Pinecone-ல store பண்ணீங்க. இப்போ Mistral embedding-க்கு மாறினால் dimension 1024. உங்கள் whole vector DB rebuild பண்ண வேண்டும். RAG pipeline முழுக்க மாறும்.

**3. Behavioral coupling**
ஒவ்வொரு model-க்கும் tone, reasoning style, tool use reliability வேறு. நீங்கள் prompts-ஐ ஒரு model-க்கு மட்டும் tune பண்ணீங்கன்னா, அது மற்ற model-ல வேலை செய்யாது. Fine-tune பண்ணினால் அது weights-ஐ provider-க்குள்ளேயே lock பண்ணும்.

## 4. Architectural Reasoning

Model selection என்பது ஒரு one-time decision அல்ல. அது ஒரு ongoing trade-off.

**When lock-in useful ஆகும்:**
Early stage, speed > flexibility. MVP-க்கு OpenAI use பண்ணி 2 வாரத்தில் ship பண்ணலாம். இங்கே lock-in ஒரு conscious debt.

**When lock-in painful ஆகும்:**
* Cost at scale: LLM cost = traffic * tokens. Provider price change = P&L impact.
* Availability: ஒரு region down ஆனால் உங்கள் service down.
* Compliance: Data residency, EU data மட்டும் European provider-ல இருக்கணும்.
* Capability differentiation: RAG quality, coding, multilingual Tamil performance வேறுபடும்.

Architecturally, இதற்கு தீர்வு abstraction.

```
Your App -> Model Abstraction Layer -> Provider A/B/C
```

Abstraction layer உங்களுக்கு:
* Unified API for chat, embeddings, moderation
* Configurable routing: cost-based, latency-based, fallback
* Prompt normalization, tool schema translation
* Telemetry for quality & cost per provider

இது Kubernetes-ல abstraction போல. நீங்கள் pod-ஐ directly run பண்ணாமல் scheduler மூலம் run பண்ணுவது போல.

## 5. Trade-offs

**Abstraction vs Performance**
Abstraction layer latency add பண்ணும். Provider-specific optimizations like OpenAI structured output, native function calling-ஐ use பண்ண முடியாமல் போகும். Too much abstraction = leaky abstraction.

**Portability vs Features**
Generic OpenAI-compatible API எளிது. ஆனால் Anthropic-இன் thinking mode, OpenAI-இன் vision features, local model-இன் private fine-tune எல்லாம் expose ஆகாது.

**Cost of abstraction vs cost of lock-in**
Abstraction layer build & maintain பண்ண வேண்டும். Team size small என்றால் அது overhead. ஆனால் scale-க்கு பிறகு lock-in-இன் exit cost பெரியது.

**Failure modes**
Abstraction layer itself single point of failure ஆகும். Routing logic தவறாக route பண்ணினால் data leak ஆகலாம். Provider fallback-ல idempotency இல்லாமல் duplicate charge / duplicate action ஆகும்.

## 6. Practical Example

Enterprise RAG system.

நீங்கள் internal knowledge base-க்கு RAG build பண்ணீங்க. Choice:
* Option A: Directly OpenAI embeddings + GPT-4o for generation. 2 வாரத்தில் live.
* Option B: Abstraction layer + embedding adapter + provider router.

Option A-ல 6 மாசம் கழித்து compliance team சொல்கிறது: "Customer data cannot leave EU." OpenAI EU model availability limited. இப்போ முழு pipeline மாற வேண்டும். Embedding dimension மாறும். Vector DB rebuild. Prompts retune.

Option B-ல நீங்கள் config-ஐ மாற்றி European provider-க்கு route பண்ணீங்க. Embeddings re-index pipeline automated. Generation quality drop ஆனால் A/B test பண்ணி prompt adjust பண்ணீங்க. Migration 1 sprint.

Cost? Abstraction layer-க்கு 3 weeks initial investment. Trade-off clear.

## 7. Reasoning Challenge

உங்களிடம் production chatbot உள்ளது. 10M requests/month. Currently 100% OpenAI GPT-4o mini use பண்ணுகிறது.

Product team சொல்கிறது: "Latency P95 800ms-க்கு கீழ் வேண்டும். Cost 20% குறைய வேண்டும்."

உங்களுக்கு 2 வழி:
1. OpenAI-க்குள்ளே model downgrade / caching add பண்ணுவது
2. Abstraction layer build பண்ணி, 70% traffic-ஐ cheaper open-weight model-க்கு route பண்ணுவது, 30% sensitive traffic-ஐ OpenAI-ல வைப்பது

எந்த route தேர்வு செய்வீர்கள்? எப்போது abstraction-ஐ முதலில் build பண்ணுவீர்கள், எப்போது provider lock-in-ஐ accept பண்ணுவீர்கள்? அதன் operational complexity என்ன?

## 8. Key Takeaways

* Vendor lock-in என்பது exit cost. Model, embedding dimension, prompt behavior மூன்றும் lock பண்ணும்.
* Early stage-ல speed-க்காக lock-in ஒரு conscious debt. Scale-க்கு முன் abstraction plan பண்ணுங்கள்.
* Model abstraction layer உங்களுக்கு routing, fallback, cost control, compliance கொடுக்கும். அது latency மற்றும் feature access-க்கு trade-off.
* Architecture decision என்பது "இப்போ என்ன வேண்டும்" மட்டுமல்ல, "6 மாதத்தில் provider மாற வேண்டி வந்தால் என்ன ஆகும்" என்பதும் தான்.
