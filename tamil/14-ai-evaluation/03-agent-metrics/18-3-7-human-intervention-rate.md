# Human intervention rate

> **Learning Path:** AI Evaluation
> **Section:** 18.3.7 — Agent metrics

## 1. Problem

உங்கள் agent தானாக decisions எடுத்து action எடுக்கிறது. Production-ல் விட்டால் என்ன ஆகும்?

சில cases-ல் agent தவறாக respond பண்ணும். Hallucination, wrong tool call, unsafe output, business rule violate பண்ணும். 

இப்போது கேள்வி: எந்த cases-ல் human-ஐ கொண்டு வர வேண்டும்? எப்போதும் human review பண்ணினால் cost அதிகம், latency அதிகம். ஒருபோதும் review பண்ணாமல் விட்டால் risk அதிகம்.

இந்த trade-off-ஐ quantify பண்ண வேண்டும். அதுதான் Human intervention rate-ன் பின்னணி.

## 2. Mental Model

Human intervention rate = Agent தானாக handle பண்ண முடியாததால் human-க்கு escalate ஆன requests-ன் விகிதம்.

அதாவது:

`Human Intervention Rate = Escalated conversations / Total conversations`

இது ஒரு guardrail metric. Agent autonomy எவ்வளவு உள்ளது என்பதை சொல்லும்.

Low rate = agent confident and reliable.
High rate = agent immature அல்லது risk threshold strict.

## 3. How It Works

Agent ஒரு request வாங்கும் போது:

1. **Confidence / Policy check** - Agent-க்கு internal confidence score இருக்கும். அல்லது policy rules trigger ஆகும்.
2. **Auto-action** - Confidence high + policy safe என்றால் தானாக execute.
3. **Escalate** - Confidence low, high risk operation, unknown intent, safety violation risk என்றால் human reviewer-க்கு handoff.

Human intervention rate இதை measure பண்ணும். முக்கியம்: escalation trigger என்ன என்பதை clearly define பண்ண வேண்டும். இல்லை என்றால் metric meaningless.

## 4. Architectural Reasoning

இது useful ஆகும் எப்போது?

* Agent-ஐ production-ல் roll out செய்யும் போது autonomy level decide பண்ண.
* Cost vs safety trade-off manage பண்ண.
* Model upgrade அல்லது prompt change செய்த பிறகு quality regression check பண்ண.

என்ன constraint-ஐ address பண்ணுகிறது?

* **Risk**: Financial transaction, PII exposure, compliance violation.
* **Cost**: Human reviewer expensive, latency high.
* **User trust**: Wrong answer கொடுத்தால் churn.

Alternatives:

* **Full auto**: No intervention. Rate = 0%. Best cost, worst risk.
* **Full human-in-the-loop**: Every request reviewed. Rate = 100%. Safe but defeats agent purpose.
* **Selective escalation**: Confidence threshold / policy based. இதுதான் practical.

Architect ஏன் இதை choose பண்ணுவார்? 
ஏனெனில் agent maturity-ஐ track பண்ண முடியும். Intervention rate குறையும் போது, agent-ஐ மேலும் autonomy கொடுக்கலாம்.

## 5. Trade-offs

* **Safety vs Autonomy**: Intervention rate குறைக்கணும் என்றால் agent மேலும் risky decisions எடுக்கும். Rate அதிகப்படுத்தினால் agent useless ஆகும்.
* **Latency vs Accuracy**: Human handoff என்றால் response time seconds to minutes ஆகும். User experience hit ஆகும்.
* **Cost vs Coverage**: Human reviewers team size directly cost-ஐ குறிக்கும். Rate அதிகமானால் staffing scale வேண்டும்.
* **False positives**: Agent safe ஆன case-களையும் escalate செய்தால் unnecessary cost. False negatives - dangerous case auto pass ஆகி போகும்.

Failure mode: Threshold-ஐ தவறாக set பண்ணினால் metric ஏமாற்றும். Ex: Agent அதிக confidence ஆக fake பண்ணும், escalations குறையும், ஆனால் actual errors அதிகரிக்கும்.

## 6. Practical Example

Enterprise customer support agent.

Total conversations: 10,000 / day
Agent auto resolve: 7,500
Escalated to human agent: 2,500

Human Intervention Rate = 25%

Architect முடிவு: 
High risk intents - refund, account closure, legal query - auto escalation policy உள்ளது.
Low confidence threshold <0.7 என்றால் escalation.

After fine-tuning + better retrieval, rate 25% → 18% ஆக குறைந்தது. Human team cost குறைந்தது, CSAT stable.

இங்கே metric-ஐ தனியாக பார்க்காமல், escalated cases-ல் human-ம் தவறு செய்தாரா, agent-ன் auto cases-ல் error rate என்ன என்பதையும் பார்க்க வேண்டும்.

## 7. Reasoning Challenge

உங்களிடம் finance agent உள்ளது. Payment approval செய்யும்.

Option A: Intervention rate 5% வைக்க. Human review மட்டும் >$10k transactions.
Option B: Intervention rate 30% வைக்க. >$1k transactions-க்கு human review.

Business wants low cost, Compliance wants zero fraud. நீங்கள் எந்த threshold-ஐ தேர்வு செய்வீர்கள்? அதை justify பண்ண எந்த கூடுதல் metrics தேவை?

## 8. Key Takeaways

* Human intervention rate = agent autonomy-ன் proxy metric. Low is good, but not at cost of safety.
* Rate-ஐ set பண்ணுவது risk appetite, cost, latency மூன்றுக்கும் இடையே trade-off.
* Metric alone போதாது. Escalation quality, false positive/negative rate, auto case error rate ஆகியவற்றுடன் பார்க்க வேண்டும்.
* Agent improve ஆகும் போது intervention rate குறைய வேண்டும். இது learning signal.
