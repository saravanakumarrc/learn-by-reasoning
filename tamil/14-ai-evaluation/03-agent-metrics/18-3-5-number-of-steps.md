# Number of steps

> **Learning Path:** AI Evaluation
> **Section:** 18.3.5 — Agent metrics

## 1. Problem

ஒரு agent-ஐ deploy பண்ணியாச்சு. User query வந்ததும் agent tool-களை call பண்ணி, reasoning பண்ணி, response கொடுக்குது.

இப்போது ஒரு query-க்கு சில agents 2 steps-ல் முடிக்குது, சில agents 15 steps-ல் முடிக்குது.

இதனால் என்ன ஆகும்?

* Latency unpredictable ஆகும்
* Cost per query ஏறி விடும். ஒவ்வொரு step-க்கும் LLM call + tool call வரும்
* Same task-க்கு வேற வேற quality கிடைக்கும்
* Failure surface area அதிகரிக்கும். Steps அதிகம் என்றால் அதிக chance to fail

Production-ல agent performance-ஐ evaluate பண்ணும்போது, accuracy மட்டும் போதாது. **How many steps did it take to get there?** என்பது முக்கியம்.

அதனால்தான் agent metrics-ல் `Number of steps` ஒரு core metric.

## 2. Mental Model

Agent என்பது ஒரு loop.

`Observe → Think → Act → Observe → ...`

ஒரு step = ஒரு முறை agent தன்னுடைய LLM reasoning-ஐ run பண்ணி ஒரு action எடுத்தது.

Number of steps = அந்த query-க்கு loop எத்தனை முறை திரும்பியது.

இது agent-ன் efficiency, planning quality, மற்றும் user experience-ன் proxy.

## 3. How It Works

Agent execution-ஐ trace பண்ணும்போது நாம் ஒவ்வொரு turn-ஐயும் count பண்ணுகிறோம்.

* Step 1: LLM call → tool call: `search_web`
* Step 2: LLM call → tool call: `fetch_url`
* Step 3: LLM call → final answer

Number of steps = 3

இதை evaluate பண்ணும்போது நாம் பார்ப்பது:

* **Steps per query**: average, p50, p95, max
* **Steps distribution**: எத்தனை queries 1-3 steps-ல் முடிஞ்சது, எத்தனை 10+ steps எடுத்தது
* **Steps by task type**: simple FAQ vs multi-step research
* **Steps vs success rate**: steps அதிகரிக்கும் போது success drop ஆகிறதா?

Implementation-ல இது trivial. Agent framework-ல ஒவ்வொரு iteration-க்கும் counter increment பண்ணி log பண்ணினால் போதும்.

## 4. Architectural Reasoning

Number of steps useful ஆகிறது எப்போது?

* **Cost control**: ஒவ்வொரு step-க்கும் token cost + tool cost. Steps அதிகம் என்றால் cost அதிகம்.
* **Latency SLA**: User-facing agent-க்கு 2-3 steps-க்குள் முடிய வேண்டும். 10 steps எடுத்தால் user காத்திருக்க மாட்டார்.
* **Planning quality**: ஒரு good agent fewer steps-ல் சரியான tool-களை தேர்வு செய்யும். Bad agent hallucinate பண்ணி தேவையில்லாத tools-ஐ call பண்ணும்.
* **Operational limits**: Max steps cap வைத்து runaway loops-ஐ தடுக்கலாம்.

Alternatives?

* Time per query பார்க்கலாம். ஆனால் time network latency-ல் மாறும். Steps என்பது agent logic-ன் clean metric.
* Token count பார்க்கலாம். ஆனால் token count prompt size-ல் depend ஆகும்.

Steps என்பது architectural decision-ஐ drive பண்ணும்.

உதாரணமாக, steps அதிகம் வருகிறது என்றால்:

* Prompting weak? ReAct pattern improve பண்ண வேண்டுமா?
* Tool design பிரச்சனையா? Agent தெளிவாக tool output-ஐ புரிந்து கொள்ளவில்லை?
* Task decomposition தேவையா? Sub-agents use பண்ணலாமா?

## 5. Trade-offs

**Fewer steps vs More accuracy**

அதிக steps எடுத்தால் agent ஆழமாக research பண்ணலாம். ஆனால் cost, latency, failure risk அதிகரிக்கும். சில tasks-க்கு 1 step போதும், சில tasks-க்கு 7 steps தேவை.

**Max steps cap**

Cap வைத்தால் runaway loops தடுக்கலாம். ஆனால் complex queries fail ஆகும். Cap-ஐ எப்படி set பண்ணுவது என்பது trade-off.

**Steps uniformity**

ஒரு agent எல்லா queries-க்கும் ஒரே மாதிரி steps எடுக்க வேண்டும் என்பது ideal. Distribution wide ஆக இருந்தால் unpredictable cost & latency.

**Steps vs success**

Steps அதிகரிக்க அதிகரிக்க success rate குறையும். Tool calls தவறு செய்ய வாய்ப்பு அதிகரிக்கும். இது agent reliability-ன் red flag.

Failure mode: Agent loop-ல் stuck ஆகும். Same tool-ஐ திரும்ப திரும்ப call பண்ணும். இதை detect பண்ண steps + repetition metrics-உடன் பார்க்க வேண்டும்.

## 6. Practical Example

Enterprise support agent.

Task: "Customer order 12345-ன் status என்ன? refund possible?"

Good execution:

Step 1: `get_order(order_id)` → status found
Step 2: `check_refund_policy(status)` → policy found
Step 3: Final answer

Steps = 3. Cost low, latency ~2s.

Bad execution:

Step 1: `search_web` → irrelevant
Step 2: `get_order` → correct
Step 3: `search_web` again → hallucination
Step 4: `get_customer` → unnecessary
Step 5: `get_order` again → loop
Step 6: `check_refund_policy`
Step 7: Final answer

Steps = 7. Cost double, latency high, user frustrated.

Production-ல நீங்கள் dashboard-ல steps per query-ன் p95 பார்த்து, அது 5-ஐ தாண்டினால் alert raise பண்ணுவீர்கள். பிறகு traces-ஐ பார்த்து எந்த step-ல் waste ஆகிறது என்பதை fix பண்ணுவீர்கள்.

## 7. Reasoning Challenge

உங்களிடம் இரண்டு agent versions உள்ளன.

Version A: Average steps = 4, Success rate = 92%, p95 latency = 4s
Version B: Average steps = 7, Success rate = 96%, p95 latency = 9s

Cost per step = $0.01, SLA latency = 6s.

எந்த version-ஐ production-ல வைப்பீர்கள்? ஏன்? Steps metric-ஐ எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* Number of steps என்பது agent efficiency-ன் direct proxy. குறைவான steps = குறைவான cost, latency, failure risk.
* Steps-ஐ distribution-ஆக பார்க்கவும். Average மட்டும் போதாது. p95 முக்கியம்.
* Steps அதிகரித்தால் planning problem அல்லது tool design problem என்று அர்த்தம்.
* Max steps cap வைத்து runaway loops-ஐ தடுக்கவும், ஆனால் அது success rate-ஐ trade-off பண்ணும்.
* Agent evaluation-ல் accuracy-க்கு பக்கத்தில் steps-ஐ எப்போதும் track பண்ணுங்கள்.
