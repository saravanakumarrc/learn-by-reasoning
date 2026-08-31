# ReAct

> **Learning Path:** Agentic AI
> **Section:** 15.2.1 — Agent patterns

## 1. Problem

உங்களுக்கு ஒரு agent வேண்டும். அது LLM மூலம் user question-க்கு பதில் சொல்லணும். ஆனால் பதில் தருவதற்கு உண்மையான data தேவைப்படும். Database query பண்ணனும், API call பண்ணனும், web search பண்ணனும்.

சாதாரண prompt-only LLM எடுத்துக்கோங்க. அது தன்னிடம் உள்ள knowledge-ல இருந்து தான் பதில் கொடுக்கும். Hallucination வரும். உண்மையான tool use தேவை.

இப்போது tool use சேர்த்தீர்கள். Agent ஒரு plan போட்டு tools-ஐ call பண்ணும். ஆனால் பிரச்சனை: Plan முழுக்க முன்கூட்டியே உருவாக்கி விட்டு பிறகு execute பண்ணுவது.

உதாரணம்: "Last quarter-ல Chennai store-ன் revenue எவ்வளவு? அதை growth-ஆக மாற்று." Agent முதலில் quarter dates எடுக்கணும், store id தேடணும், revenue query பண்ணணும். ஆனால் அது முதல் step-ல தவறான quarter-ஐ assume பண்ணினால், முழு plan தவறாகிவிடும்.

அதனால் தேவை: **Reasoning பண்ணும்போதே tool result-ஐ பார்த்து அடுத்த step முடிவு செய்யும்** திறன்.

அந்த தேவையில் இருந்து ReAct வருகிறது.

## 2. Mental Model

ReAct = **Reason + Act**

Agent ஒரு loop-ல ஓடும்:

1. **Think** - இப்போ என்ன தெரியும், என்ன தெரியாது என்று reason பண்ணு
2. **Act** - தெரியாததை தெரிந்துகொள்ள ஒரு tool-ஐ call பண்ணு
3. **Observe** - Tool-ல இருந்து observation வாங்கு
4. மீண்டும் Think...

இது human மாதிரி. நீங்கள் ஒரு புதிய city-க்கு போகும்போது, map-ஐ பார்க்கிறீர்கள், அதை வைத்து அடுத்த கேள்வி கேட்கிறீர்கள். ஒரே நேரத்தில் முழு route-ஐ plan பண்ணுவதில்லை.

## 3. How It Works

ReAct prompt-ன் core structure:

```
Thought: நான் இப்போ என்ன செய்ய வேண்டும்?
Action: tool_name(input)
Observation: tool-ல இருந்து வந்த result
Thought: இந்த result-ஐ பார்த்த பிறகு என்ன அடுத்த step?
...
Final Answer: ...
```

LLM output ஒவ்வொரு iteration-லும் Thought/Action/Observation format-ல வரும். Parser அதை பிரித்து tool call செய்யும், மீண்டும் LLM-க்கு கொடுக்கும்.

முக்கியம்: Thought என்பது chain-of-thought அல்ல. அது **actionable reasoning** - அடுத்த tool எது, எந்த parameter என்பதை தீர்மானிக்கும் reasoning.

## 4. Architectural Reasoning

ReAct எப்போது useful?

* Question multi-step ஆக இருக்கும் போது
* Tool output பொறுத்து அடுத்த step மாறும் போது
* Incomplete information இருக்கும் போது

Alternatives:
* **Tool Calling / Function Calling**: LLM ஒரே முறை plan பண்ணி tools-ஐ call செய்யும். Deterministic ஆன workflow-க்கு நல்லது. ஆனால் dynamic reasoning குறைவு.
* **Chain-of-Thought only**: No tool, hallucination risk.
* **Reflexion / Self-correction**: ReAct-க்கு பிறகு correctness-ஐ improve பண்ணும் pattern.

Architect ஏன் ReAct choose பண்ணுவார்? Agent-க்கு autonomy வேண்டும், user question open-ended ஆக இருக்கும், tool set பெரிதாக இருக்கும்.

Trade-off: Loop அதிக iterations எடுக்கும். Latency அதிகரிக்கும். Cost அதிகரிக்கும். LLM-ன் reasoning quality மோசமாக இருந்தால் infinite loop / wrong tool selection ஆகும்.

## 5. Trade-offs

**Latency vs Accuracy**: ஒவ்வொரு step-க்கும் LLM call + tool call. 3-5 iterations சகஜம். Real-time use case-க்கு கடினம்.

**Control vs Autonomy**: ReAct agent தன்னிச்சையாக tool தேர்வு செய்யும். Debugging கடினம். ஒரு tool தவறாக தேர்வு செய்தால் முழு answer corrupt ஆகும்.

**Hallucination in Thought**: LLM thought step-ல தவறான assumption போடலாம். Observation-ஐ misinterpret பண்ணலாம். அதற்கு guardrails வேண்டும்.

**Operational complexity**: Loop termination எப்படி? Max steps limit வேண்டும். Tool output size பெரிதாக இருந்தால் context window நிரம்பும்.

## 6. Practical Example

Enterprise support agent.

User: "நேற்று fail ஆன payment-கள் எத்தனை? அவற்றில் refund status என்ன?"

ReAct flow:
Thought: நேற்று date என்ன? 2025-10-18. Failed payments எடுக்க வேண்டும்.
Action: get_failed_payments(date=2025-10-18)
Observation: 42 payments failed. IDs: [p1,p2,...]

Thought: ஒவ்வொரு payment-க்கும் refund status தேவை.
Action: get_refund_status(payment_ids=[p1,p2,...])
Observation: 12 refunded, 30 pending.

Thought: Pending-க்கு காரணம் தெரியுமா?
Action: get_failure_reason(payment_ids=[...pending...])
Observation: 20 timeout, 10 insufficient funds.

Final Answer: 42 failed, 12 refunded, 30 pending...

இங்கே முதல் observation வந்த பிறகு தான் அடுத்த tool எது என்பது தெளிவாகிறது. Pre-planned workflow இங்கே கடினம்.

## 7. Reasoning Challenge

உங்களிடம் 2 tools இருக்கு: `search_web` மற்றும் `query_vector_db`. User கேட்கிறார்: "எங்கள் product-ன் latest feature-ன் competitor comparison தா".

உங்கள் agent ReAct pattern follow பண்ணும். ஆனால் web search slow, vector DB fast ஆனால் internal data மட்டுமே.

நீங்கள் எப்போது எந்த tool-ஐ முதலில் call பண்ணுவீர்கள்? ஏன்? Loop எப்படி முடியும்?

## 8. Key Takeaways

* ReAct என்பது reasoning மற்றும் acting-ஐ interleave செய்யும் loop. முன்கூட்டியே முழு plan பண்ணுவதில்லை.
* Tool observation-ஐ பார்த்து அடுத்த step தீர்மானிக்கப்படுகிறது. இது dynamic problems-க்கு தேவை.
* Latency, cost, control குறையும். Autonomy, accuracy அதிகரிக்கும்.
* Good ReAct agent-க்கு clear tool description, max steps, thought grounding தேவை.
