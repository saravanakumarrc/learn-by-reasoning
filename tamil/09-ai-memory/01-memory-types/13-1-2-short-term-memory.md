# Short-term memory

> **Learning Path:** AI Memory
> **Section:** 13.1.2 — Memory types

## 1. Problem

உங்ககிட்ட ஒரு agent இருக்கு. User chat-ல "என்னோட last order-ல என்ன items இருந்துச்சு?"ன்னு கேட்கிறார். 

Agent இப்போ தான் order service-ஐ call பண்ணி data எடுத்துட்டு வந்திருக்கு. அடுத்த turn-ல user "அதுல இருந்த laptop-ஐ return பண்ணுங்க"ன்னு சொல்றார்.

Agent-க்கு அந்த last order என்னன்னு நினைவு இருக்கணும். ஒவ்வொரு turn-க்கும் முழு conversation-ஐயும் database-ல இருந்து fetch பண்ணி, எல்லா context-யும் மறுபடியும் முழுசா feed பண்ண முடியுமா? முடியும், ஆனா slow ஆகும், expensive ஆகும்.

இன்னொரு பக்கம், LLM-க்கு context window limited. 1000 turns-க்கு முன்னாடி நடந்தது இன்னைக்கு தேவையில்லை. ஆனா கடைசி 3-4 turns-ல நடந்தது இப்போதைக்கு critical.

**What problem became painful enough?** Agent-க்கு "இப்போ நடக்கிற conversation-க்கு தேவையான recent context-ஐ கைவசம் வச்சுக்கணும்", ஆனா அதை permanent-ஆ store பண்ணக்கூடாது. அது short-term memory தேவை.

## 2. Mental Model

Short-term memory = இப்போ நடக்கிற session-க்கு தேவையான recent state.

உதாரணத்துக்கு மனுஷன் short-term memory மாதிரி. நீங்க ஒரு phone number-ஐ கேட்டு 30 seconds வரை நினைவு வச்சிருப்பீங்க, அப்புறம் மறந்துடுவீங்க.

AI system-ல short-term memory என்பது:

* **Session scope** ஆன working context
* Fast access, volatile
* Turn-to-turn coherence-க்கு தேவை
* Long-term memory-க்கு promote பண்ணாமல் தானாக expire ஆகும்

## 3. How It Works

இது system-ல 3 வழிகளில் வரும்.

**1. In-context window.** LLM-க்கு கடைசி N messages-ஐயே prompt-ல வைக்கிறோம். இது simplest form. No extra store.

**2. Ephemeral session store.** Redis / in-memory cache-ல session_id கீயில் recent facts, entities, intermediate results வைக்கிறோம். TTL 15-60 mins.

**3. Working memory buffer.** Agent framework-ல ஒரு small structured buffer இருக்கும். `current_order_id`, `current_user_intent`, `last_action_result` போன்ற fields.

Flow:

User message → Retrieve session short-term memory → Merge with long-term profile → Build prompt → LLM generates → Update short-term memory with new facts → Respond

Key point: Short-term memory is **derived and updated every turn**, not static lookup.

## 4. Architectural Reasoning

எப்போ short-term memory தேவை?

* Multi-turn conversation, task completion தேவைப்படும் போது
* User refers to "that", "it", "the same" போன்ற pronouns
* Agent needs to maintain state across tool calls within same session

Alternative என்ன?

* **Only long-term memory:** எல்லாத்தையும் DB-ல write பண்ணி திரும்ப read பண்ணலாம். ஆனா latency high, noise அதிகம்.
* **Only context window:** Window fill ஆகும், cost அதிகம், privacy risk.

Architect ஏன் choose பண்ணுவார்?

Short-term memory gives you **low-latency coherence** with **bounded cost**. Session end ஆனதும் தானாக clean ஆகும், compliance-க்கு எளிது.

## 5. Trade-offs

**1. Freshness vs Noise.** எவ்வளவு history வைக்கணும்? Too little → context loss. Too much → prompt dilution.

**2. Volatile vs Durable.** Memory-ஐ persist பண்ணலாம் ஆனா அப்போ அது short-term இல்ல. Session crash ஆனால் மறுபடியும் start பண்ண வேண்டும்.

**3. Cost.** In-context வச்சால் token cost per request. Cache வச்சால் infra cost. Trade-off clear ஆ இருக்கணும்.

**Failure modes:**

* Session affinity loss. User next request வேற pod-க்கு போனால் memory miss.
* Stale memory. User conversation topic மாறினாலும் பழைய facts influence பண்ணும்.
* Memory leak. TTL set பண்ணாமல் cache grow ஆகும்.

## 6. Practical Example

E-commerce return agent.

User: "என்னோட கடைசி order-ல laptop வந்துச்சா?"
Agent order service-ஐ call பண்ணி order_id=8421 என்று கண்டுபிடித்து, items list எடுத்து பதில் சொன்னது.

Short-term memory-ல store பண்ணுவோம்:
```
session_abc123:
  last_order_id: 8421
  last_query_items: ["laptop", "mouse"]
  last_action: "order_lookup"
  ttl: 20 min
```

Next turn:
User: "அதை return பண்ணுங்க"

Agent short-term memory-ல இருந்து last_order_id எடுத்து, return API-க்கு call பண்ணும். User மறுபடியும் order number சொல்ல வேண்டாம்.

Session end ஆனதும் 20 min-க்கு அப்புறம் Redis key expire ஆகும். அதே data long-term user profile-ல save பண்ண வேண்டாம்.

## 7. Reasoning Challenge

உங்க agent-க்கு 10,000 concurrent users இருக்காங்க. ஒவ்வொரு session-க்கும் short-term memory-ஐ Redis-ல வச்சிருக்கீங்க. Latency p95 50ms ஆக இருக்கணும். Cost குறைக்கணும்.

இப்போ peak time-ல Redis memory 80% fill ஆகுது. TTL-ஐ 5 min-ல இருந்து 2 min-க்கு குறைக்கலாமா? அல்லது context window size-ஐ அதிகரித்து cache dependency-ஐ குறைக்கலாமா?

எந்த trade-off பார்ப்பீங்க? Session drop ஆனால் என்ன ஆகும்?

## 8. Key Takeaways

* Short-term memory = session-scoped, recent, volatile working context. Coherence-க்கு தேவை.
* இது long-term memory-ஐ replace பண்ணாது, complement பண்ணும். Recent facts fast, durable facts slow.
* Design decision: எவ்வளவு context-ஐ window-ல வைக்கிறோம் vs cache-ல வைக்கிறோம் என்பது latency, cost, correctness trade-off.
* Every session memory has TTL. Expire strategy என்பது architecture decision, not implementation detail.
