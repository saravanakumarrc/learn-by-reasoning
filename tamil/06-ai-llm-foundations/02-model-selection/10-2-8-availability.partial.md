# PARTIAL — Availability

> Reason: Ollama reached num_predict
> num_predict: 32768

## 1. Problem

நீங்கள் ஒரு customer support agent-ஐ LLM-உடன் கட்டினீர்கள். Launch-க்கு முன் எல்லாம் சரியாக இருக்கு. Production-க்கு வந்ததும் peak hour-ல user request அதிகமாகிறது.

அப்போது திடீரென:

* API திருப்பி 429 rate limit தருகிறது
* timeout ஆகிறது
* 5xx error வருகிறது
* latency 2 sec-ல இருந்து 12 sec ஆகிறது

User-க்கு response வராமல் போகிறது. Retry பண்ணினாலும் அதே. Business impact உடனே தெரியும்.

இது model-இன் quality பிரச்சனை இல்லை. **Availability** பிரச்சனை. Model selection-இல் நீங்கள் accuracy மட்டும் பார்த்து, service-ஐ எவ்வளவு நம்பலாம் என்பதை பார்க்கவில்லை.

## 2. Mental Model

Availability என்பது: *நீங்கள் கேட்டபோது, எதிர்பார்த்த latency-க்குள், successful response கிடைக்கும் நிகழ்தகவு*.

LLM context-ல் இது மூன்று விஷயங்களை உள்ளடக்கும்:

* **Service uptime** - API reachable-ஆ?
* **Capacity** - rate limit, quota, concurrency
* **Latency tail** - p95/p99 response time acceptable-ஆ?

ஒரு model 99.9% SLA கொடுத்தாலும், உங்கள் traffic pattern அதற்கு ஏற்றதா என்பது தனி கேள்வி.

## 3. How It Works

Availability-ஐ improve பண்ண ஆர்கிடெக்சர்ல பொதுவாக இதை பார்க்கிறோம்:

* **Multi-model fallback**: Primary LLM fail ஆனால் secondary model-க்கு failover
* **Regional routing**: Vendor-க்கு multiple regions இருந்தால் failover
* **Self-hosted buffer**: Proprietary API down என்றால் open source model உள்ளூரில் run பண்ணி degrade gracefully
* **Circuit breaker + retry with backoff**: Temporary failure-க்கு தானாக recover

இது எல்லாம் model quality-ஐ குறைக்காமல், service-ஐ usable-ஆ வைக்கும்.

## 4. Architectural Reasoning

Model selection-இல் availability ஒரு first-class constraint.

**எப்போது கவலைப்பட வேண்டும்?**

* User-facing synchronous flow. Chat, search, checkout assistant போன்றவை.
* Peak traffic predictable-ஆ இல்லை. Flash sale, support ticket spike.
* SLA commitment உள்ளது. 99.9% uptime வேண்டும்.

**Options:**

* **Proprietary hosted API**: OpenAI, Anthropic போன்றவை. High availability, managed infra, but rate limit, cost, vendor lock-in.
* **Self-hosted open model**: Llama, Mistral. Full control, no rate limit, but you own uptime, GPU ops, scaling.
* **Hybrid**: Critical path-க்கு hosted, fallback-க்கு self-hosted small model.

Decision driver என்பது **operational complexity vs control**.

## 5. Trade-offs

* **Cost vs Availability**: High availability கொடுக்கும் top-tier model விலை அ
