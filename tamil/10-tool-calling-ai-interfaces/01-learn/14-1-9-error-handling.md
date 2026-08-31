# Error handling

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.9 — Learn

## 1. Problem

ஒரு AI agent ஒரு Tool call பண்ணுது. API timeout ஆகுது. Network glitch. அல்லது service crash ஆகுது.

என்ன ஆகும்?

Agent-க்கு error வருது. அது அப்படியே user-க்கு "error happened"ன்னு சொல்லிடுமா? அல்லது அதே request-ஐ மறுபடியும் அனுப்புமா? மறுபடி அனுப்பினா duplicate charge ஆகுமா?

Error handling இல்லாம, ஒரு flaky network ஒரு முழு workflow-ஐயும் கொண்டு போய் விடும்.

AI Interface-ல error handling என்பது just log பண்ணுறது இல்லை. Decision பண்ணுறது. Retry பண்ணலாமா? Fail fast பண்ணலாமா? User-க்கு partial result கொடுக்கலாமா?

## 2. Mental Model

Error handling என்பது **failure-ஐ expected behavior ஆக்குறது**.

ஒரு distributed system-ல failure normal. Network failure, timeout, 5xx, validation error, rate limit, tool not available... எல்லாம் normal.

Mental model: ஒவ்வொரு Tool call-க்கும் 3 outcomes உண்டு.

1. **Success** - expected output வந்தது
2. **Recoverable error** - retry, fallback, backoff பண்ணி success ஆக வாய்ப்பு உண்டு
3. **Non-recoverable error** - retry பண்ணினாலும் fail ஆகும். Stop பண்ணு.

இதை agent முடிவு செய்யணும்.

## 3. How It Works

Tool calling-ல error handling 3 layers-ல நடக்கும்.

**Layer 1: Transport layer**
Timeout, connection reset, 502/503. இது transient. Retry with exponential backoff + jitter பண்ணலாம்.

**Layer 2: Application layer**
4xx validation error, 401 unauthorized, 429 rate limit. இது client problem. Blind retry பண்ணக் கூடாது. Request-ஐ fix பண்ணணும்.

**Layer 3: Business logic layer**
Tool success ஆனாலும் business rule fail. Example: payment succeeded but amount zero. இது agent-க்கு reasoning தேவை.

ஒரு good pattern: 
`try → classify error → decide action → log with context → respond`

Classify error-க்கு error type, error code, retry count, idempotency key எல்லாம் பார்க்கணும்.

## 4. Architectural Reasoning

ஏன் இது architecturally முக்கியம்?

AI agent என்பது multiple tools-ஐ chain பண்ணும். ஒரு tool fail ஆனா முழு workflow-மும் fail ஆகும்.

Constraints:
- **Latency**: Retry எவ்வளவு நேரம் wait பண்ணலாம்?
- **Cost**: LLM token + tool call cost. Blind retry cost ஆகும்.
- **Consistency**: Duplicate side effects தடுக்கணும்.
- **User experience**: Agent stuck ஆகக்கூடாது.

எப்போ retry செய்யணும்?
- Idempotent operation + transient error → retry
- Non-idempotent operation + transient error → don't retry, or use idempotency key

Alternatives:
- Fail fast + user-க்கு திருப்பி கொடு
- Fallback tool use பண்ணு
- Degraded response கொடு: partial result

Architectural decision: Error handling policy-ஐ centralize பண்ணு. ஒவ்வொரு tool call-லும் scatter பண்ணாதே. Retry policy, circuit breaker, timeout, fallback ஒரே policy-ல manage பண்ணு.

## 5. Trade-offs

**Retry vs Fail Fast**
Retry improves reliability but increases latency and cost. Too many retries cause cascade failure.

**Idempotency vs Complexity**
Idempotency key வைக்கிறது duplicate operations தடுக்கும். ஆனால் tool design-ஐ complex ஆக்கும்.

**Granular error vs Generic error**
Detailed error classification agent-க்கு better decision தரும். ஆனால் implementation heavy.

**User transparency vs Abstraction**
User-க்கு raw error காட்டினால் trust குறையும். Too much abstraction என்றால் debug கஷ்டம்.

Failure modes:
- Retry storm: 50 agents same time-ல retry பண்ணி downstream-ஐ down பண்ணும்
- Silent swallow: Error-ஐ ignore பண்ணி wrong result return பண்ணும்
- Infinite loop: Agent error-ஐ recover பண்ண முடியாமல் loop-ல மாட்டிக்கும்

## 6. Practical Example

Enterprise booking agent.

Flow: check flight availability → reserve seat → charge payment → send confirmation email.

Payment tool timeout ஆனது.

First attempt: timeout error. Classify as transient. Idempotent? Payment-ல idempotency key இருக்கு. Retry with backoff 2s, 4s.

Second attempt: 200 OK, payment succeeded.

If idempotency key இல்லாமல் blind retry பண்ணி இருந்தா duplicate charge ஆகியிருக்கும்.

Email tool fail ஆனது: 5xx. Retry 2 times. Still fail. Non-critical path. Log பண்ணி user-க்கு "booking confirmed, email later"ன்னு degraded response கொடு.

Flight availability tool 400 bad request திரும்பியது. Validation error. Retry பண்ண வேண்டாம். Agent-க்கு signal கொடு: input fix பண்ணு.

## 7. Reasoning Challenge

உங்க agent-க்கு 20 parallel tool calls இருக்கு. ஒன்று rate limit 429 தருது. மற்ற 19 success ஆகுது.

இங்கே என்ன செய்வீர்கள்? Retry immediately? Backoff? மற்ற calls-ஐ wait பண்ணி வைப்பீர்களா? Agent-க்கு partial result கொடுக்கலாமா?

ஏன் அப்படி முடிவு செய்கிறீர்கள்? Cost, latency, user experience எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

- Error handling என்பது logging அல்ல, decision making.
- Transient error-க்கு retry, permanent error-க்கு fail fast.
- Idempotency இல்லாமல் retry செய்யாதே.
- Error classification + centralized policy = predictable agent behavior.
- ஒவ்வொரு retry-க்கும் cost, latency, cascade risk உண்டு.
