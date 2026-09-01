# Token usage

> **Learning Path:** LLMOps / AI Observability
> **Section:** 19.1.6 — Observability

## 1. Problem

ஒரு LLM-powered service build பண்ணும்போது, முதல் 2 வாரம் எல்லாம் சுமாரா ஓடும். ட்ராஃபிக் வர ஆரம்பித்ததும் cost, latency, மற்றும் quality எல்லாம் ஒரே நேரத்தில் கெட்டுப்போகும்.

உங்களிடம் ஒரு customer support agent இருக்கு. ஒரு user message வந்தால், அதை context-உடன் LLM-க்கு அனுப்பி பதில் generate பண்ணுகிறீர்கள். 

இப்போது கேள்வி:
* ஒரு request-க்கு எத்தனை tokens செலவாகிறது?
* அந்த tokens-ல எது prompt, எது system, எது tool call, எது output?
* ஏன் சில requests 2x cost ஆகிறது?
* எந்த prompt பகுதி waste ஆகிறது?

இதை தெரியாமல், நீங்கள் பில்லை மட்டுமே பார்த்து கோபப்படுவீர்கள். Observability இல்லாமல், token usage என்பது black box.

## 2. Mental Model

Token usage = **money + latency + capacity**.

ஒரு token ≈ சிறிய chunk of text. LLM-கள் input tokens-க்கும் output tokens-க்கும் வெவ்வேறு விலை வைத்திருக்கும். Input cheap, output expensive.

நீங்கள் pay per token. ஒரு request-ன் total cost = `input_tokens * input_price + output_tokens * output_price`.

Observability என்றால், ஒவ்வொரு request-க்கும் இந்த எண்ணிக்கையை track பண்ணி, எங்கே waste ஆகிறது என்பதை reason பண்ணுவது.

Mental model: ஒரு request என்பது ஒரு token budget. அந்த budget எப்படி spend ஆகிறது என்பதை பார்க்க வேண்டும்.

## 3. How It Works

LLM call-க்கு முன் மற்றும் பின் நீங்கள் token count-ஐ capture பண்ண வேண்டும்.

Typical flow:
`User message -> Preprocessing -> System prompt + Conversation history + RAG context -> Prompt tokens -> LLM -> Output tokens`

நீங்கள் track செய்ய வேண்டியது:
* **Prompt tokens**: system + user + history + tool messages + RAG context
* **Completion tokens**: LLM output
* **Total tokens**: prompt + completion
* **Token per request distribution**: p50, p95, p99
* **Cost per request** and cost per user / per feature

இதை நீங்கள் LLM provider response-ல் வரும் `usage.prompt_tokens`, `usage.completion_tokens` மூலம் பெறலாம். அதை log செய்து, request id-உடன் correlate பண்ண வேண்டும்.

## 4. Architectural Reasoning

Token usage observability ஏன் தேவை?

**Cost control.** LLM bill monthly spike ஆனால் எந்த feature காரணம் என தெரியாது. Token usage per feature tag பண்ணினால், expensive feature-ஐ கண்டுபிடிக்க முடியும்.

**Latency.** Output tokens அதிகம் என்றால் latency அதிகம். User experience-க்கு முக்கியம்.

**Quality trade-off.** RAG-ல் நீங்கள் 10 documents கொடுக்கிறீர்கள். அது 4k tokens ஆகும். Quality improve ஆகிறதா? அல்லது noise தானா? Token usage by component பார்த்தால் தெரியும்.

**Capacity planning.** Peak traffic-ல் token per second rate தெரிந்தால், rate limits மற்றும் quota திட்டமிட முடியும்.

நீங்கள் choose செய்ய வேண்டியது: token usage-ஐ எங்கே capture பண்ணுவது?
* Gateway / LLM proxy layer: எல்லா calls-க்கும் centralized
* Application code: fine-grained tagging கிடைக்கும்
* Both: best practice

## 5. Trade-offs

**Granularity vs overhead.** ஒவ்வொரு token-ஐயும் detailed breakdown-உடன் log பண்ணினால் log volume பெருகும். Sampling பண்ணலாம். ஆனால் cost anomaly miss ஆகும்.

**Cost vs context.** அதிக context = better answer, அதிக tokens. நீங்கள் எப்போதும் max context கொடுக்க முடியாது. Token budget set பண்ணி, context compression, summarization பயன்படுத்த வேண்டும்.

**Provider visibility.** Different models have different pricing and tokenization. Token count model-க்கு மாறும். ஒரே text வெவ்வேறு model-ல் வெவ்வேறு token count. அதனால் cost compare பண்ணும்போது normalized metric வேண்டும்.

**Failure mode:** Token limit exceed ஆனால் request fail ஆகும். Observability இல்லை என்றால், ஏன் fail ஆகிறது என தெரியாது. Prompt too long, history not truncated, RAG context too big - எது என தெரியாது.

## 6. Practical Example

உங்களிடம் banking chatbot உள்ளது. ஒவ்வொரு request-க்கும்:
* System prompt: 800 tokens
* Conversation history: avg 1200 tokens
* RAG context: 2500 tokens
* Output: avg 300 tokens

Total ~ 4800 tokens/request. p95-ல் 9000 tokens.

நீங்கள் token usage dashboard பார்த்தால், RAG context தான் 50% cost. அதில் 80% tokens irrelevant chunks. நீங்கள் retrieval-ல் top-k 10 இருந்து 5 ஆக்கி, reranking சேர்த்தால், tokens 40% குறைந்தது. Quality drop இல்லை.

இல்லாமல் நீங்கள் blind-ஆக model downsize பண்ணியிருப்பீர்கள். அது quality-ஐ கெடுக்கும்.

மற்றொரு example: ஒரு agent tool call பண்ணும் போது, tool output-ஐ முழுவதும் prompt-க்கு திருப்பி அனுப்புகிறீர்கள். அது 3k tokens waste. Token usage by component பார்த்தால், tool output summarization தேவை என தெரியும்.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers இல்லை, ஆனால் ஒரு LLM service இருக்கு. ஒரு user request-க்கு avg cost $0.02. Monthly active users 100k, daily 20k requests. திடீரென cost 3x ஆகியுள்ளது. Token usage dashboard-ல் input tokens stable, output tokens 2.5x increase. 

என்ன architecture / product change இதை ஏற்படுத்தியிருக்கலாம்? நீங்கள் எந்த metric-ஐ முதலில் பார்ப்பீர்கள்? Cost குறைக்க என்ன options?

## 8. Key Takeaways

* Token usage என்பது cost, latency, quality இன் proxy. இதை observe செய்யாமல் LLM system ஓட்ட முடியாது.
* ஒவ்வொரு request-க்கும் prompt vs completion breakdown, per feature tagging, மற்றும் distribution தெரிய வேண்டும்.
* அதிக token எப்போதும் நல்லது அல்ல. Waste உள்ள இடத்தை கண்டுபிடித்து, context compression, better retrieval, output length control மூலம் optimize செய்யலாம்.
* Observability இல்லாமல், நீங்கள் cost-ஐ control செய்ய முடியாது, மற்றும் trade-offs-ஐ reason பண்ண முடியாது.
