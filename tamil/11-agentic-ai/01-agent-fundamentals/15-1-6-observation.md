# Observation

> **Learning Path:** Agentic AI
> **Section:** 15.1.6 — Agent fundamentals

## 1. Problem

ஒரு agent-க்கு goal கொடுத்தீங்க. "Customer complaint-ஐ analyze பண்ணி refund due-ஆ என்ன check பண்ணு".

Agent என்ன பண்ணும்? அது environment-ஐ பார்க்க வேண்டும். Database-ல order உண்டா? Support ticket என்ன status? Customer history எப்படி? Payment gateway response என்ன?

Agent-க்கு அதைப் பார்க்க ஒரு வழி வேண்டும். அதுதான் **Observation**.

Observation இல்லாமல் agent blind-ஆ இருக்கும். அது கண்ணை மூடிக்கிட்டு decision எடுக்க முயற்சி பண்ணும். Hallucination வரும். தப்பான action எடுக்கும்.

> What goes wrong if we don't have good Observation? Agent தன் state-ஐ உண்மையாக update பண்ண முடியாது. Loop ஆகும். Goal-க்கு தூரம் போகும்.

## 2. Mental Model

Agent = Brain + Action

Observation = Agent-க்கு வரும் sensory input.

ஒரு human agent போல நினைத்துப்பாருங்கள். நீங்கள் ஒரு room-ல இருக்கீங்க. நீங்கள் பார்க்கும், கேட்கும், touch பண்ணும் data தான் observation. அதை வைத்துதான் next step decide பண்ணுவீங்க.

Agent-க்கு observation என்பது:
- Tool output
- API response
- Database query result
- User message
- Environment state change
- Previous action-ன் result

Observation என்பது raw data அல்ல. அது **meaningful, structured, timely** ஆக இருக்க வேண்டும். Agent அதை புரிந்து கொள்ளும் வகையில் இருக்க வேண்டும்.

## 3. How It Works

Agent loop எப்படி இயங்குகிறது?

`Thought → Action → Observation → Thought`

1. **Thought**: Agent current goal + history பார்த்து plan பண்ணும்.
2. **Action**: ஒரு tool-ஐ call பண்ணும். Eg: `get_order(order_id)`, `search_tickets(customer_id)`.
3. **Observation**: Tool return பண்ணிய output. Eg: `order found, amount 4999, status paid, 2 days ago`.
4. **Thought**: அந்த observation-ஐ வைத்து next action decide.

Observation-ன் quality முழு loop-ன் quality-ஐ decide பண்ணும்.

Observation-க்கு மூன்று பண்புகள் முக்கியம்:
- **Completeness**: தேவையான info இருக்கா?
- **Correctness**: உண்மையானதா? stale இல்லையா?
- **Timeliness**: எவ்வளவு வேகமாக கிடைக்கிறது?

## 4. Architectural Reasoning

Observation எப்போது useful ஆகும்?

Agent என்றாலே partial information-ல இருந்து decide பண்ணுவது. Environment-ஐ observe பண்ணாமல் progress measure பண்ண முடியாது.

Constraints:
- **Latency**: Observation slow ஆனால் agent slow ஆகும். Real-time agent-க்கு streaming observation தேவை.
- **Cost**: Tool call cost, LLM token cost. அதிக observation = அதிக cost.
- **Noise**: Too much observation = context window fill ஆகும். Agent confuse ஆகும்.

Alternatives:
- **Polling**: Regular interval-ல check பண்ணுவது. Simple ஆனால் wasteful.
- **Push / Webhook**: Event வரும்போது notify பண்ணுவது. Timely ஆனால் complex.
- **Summarized Observation**: Raw logs-ஐ summarize பண்ணி கொடுப்பது. Less noise ஆனால் info loss.

Architect choose பண்ணும்போது கேட்க வேண்டியது:
Observation எவ்வளவு fresh இருக்க வேண்டும்? Accuracy-க்கு எவ்வளவு pay பண்ண தயார்? Agent autonomous ஆக இருக்க வேண்டுமா, human-in-the-loop ஆக இருக்க வேண்டுமா?

## 5. Trade-offs

**1. Granularity vs Context Window**
Detailed observation = better decision. ஆனால் LLM context நிறைந்து விடும். Important signal noise-ல மறைந்து விடும். Trade-off: Summarization layer வைக்க வேண்டும்.

**2. Freshness vs Cost**
Real-time observation க்கு polling / streaming வேண்டும். அது cost + operational complexity அதிகம். Stale data-ல agent தப்பு decision எடுக்கும்.

**3. Trust vs Verification**
Observation எப்போதும் correct இல்லை. Tool fail ஆகலாம், API timeout ஆகலாம், data inconsistent ஆகலாம். Agent அதை blind-ஆ trust பண்ணினால் cascade failure வரும். Observation-க்கு validation / retry / fallback வேண்டும்.

Failure mode: Observation missing or empty. Agent அதை hallucinate பண்ணி assume பண்ணும். "Data not found" என்பதை "No problem" என்று நினைத்து விடும்.

## 6. Practical Example

Enterprise support agent.

Goal: Refund eligibility check.

Flow:
1. Thought: Order ID தேவை. Ask user.
2. Action: `get_order(order_id)`
3. Observation: `{"order_id":"123","amount":4999,"status":"delivered","delivery_date":"2025-11-01"}`
4. Thought: Delivery date 30 days-க்கு முன்னால. Policy 7 days மட்டுமே.
5. Action: `search_tickets(customer_id)`
6. Observation: `{"tickets":2,"last_escalation":"2025-10-20"}`

இப்போ agent-க்கு clear picture. Observation இல்லாமல் agent "refund approved" என்று blind-ஆ சொல்லி இருக்கும்.

Observation design:
- Tool output-ஐ structured JSON-ல return பண்ணுவது.
- Timestamp கூட சேர்ப்பது.
- Error state-ஐ explicit-ஆ கொடுப்பது.

## 7. Reasoning Challenge

உங்களிடம் ஒரு autonomous trading agent இருக்கு. Market price-ஐ observe பண்ணி buy/sell decision எடுக்கும். Price feed 100ms-க்கு ஒரு முறை update ஆகிறது. Network latency 50ms.

Agent-க்கு observation எப்படி design பண்ணுவீங்க? Polling செய்வீங்களா, streaming செய்வீங்களா? Observation stale ஆனால் என்ன ஆகும்? Cost, correctness, latency மூன்றுக்கும் trade-off எப்படி பார்ப்பீங்க?

## 8. Key Takeaways

- Observation என்பது agent-ன் sensory input. Loop-ன் quality அதை பொறுத்தது.
- Good observation = complete, correct, timely, structured.
- Too much observation = noise and cost. Too little = blind decisions.
- Observation failure = agent hallucination and wrong action.
- Architecting observation என்பது freshness, cost, trust ஆகியவற்றுக்கு இடையே trade-off பண்ணுவது.
