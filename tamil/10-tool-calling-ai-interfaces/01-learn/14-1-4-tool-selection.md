# Tool selection

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.4 — Learn

## 1. Problem

உங்கள் AI agent ஒரு user கேள்விக்கு பதில் சொல்லணும். அதுக்கு live data வேணும். அதுக்கு database query பண்ணணும். Payment create பண்ணணும். Web search பண்ணணும். File upload பண்ணணும்.

Agent-க்கு இதெல்லாம் தானாக தெரியாது. ஒரே model-ல எல்லா tool-ம் இருக்க முடியாது.

பிரச்சனை என்ன? Agent-க்கு 20 tools இருக்கு. User சொன்னது "என் last month invoice எங்கே?". Agent எந்த tool-ஐ எப்போது call பண்ணணும்? எந்த parameter கொடுக்கணும்? Tool call தோல்வி ஆனால் என்ன பண்ணணும்? Wrong tool-ஐ call பண்ணி hallucination வந்தால் என்ன ஆகும்?

Tool selection என்பது **right tool, right time, right arguments** என்பதை agent சரியாக decide பண்ணுவது தான்.

## 2. Mental Model

Tool selection என்பது ஒரு decision layer.

User intent → Planner → Tool choice → Arguments → Execute → Observe → Next step

Agent ஒரு முறை யோசிக்கிறது, tool-ஐ தேர்வு செய்கிறது, result வருகிறது, அதை பார்த்து அடுத்த move முடிவு செய்கிறது.

இது ஒரு loop. Tool catalog என்பது agent-க்கு கிடைக்கும் capability menu.

## 3. How It Works

Tool calling-க்கு மூன்று விஷயங்கள் தேவை:

**Tool definition:** Name, description, parameters schema. Agent-க்கு இது function spec மாதிரி தெரியும்.

**Selection policy:** Agent context + history பார்த்து, relevant tools filter பண்ணி, ஒன்று அல்லது பல tools தேர்வு செய்யும்.

**Execution & validation:** Tool-ஐ call பண்ணி, output-ஐ validate பண்ணி, failure ஆனால் retry அல்லது fallback.

நல்ல tool selection என்பது **over-selection இல்லாமல், under-selection இல்லாமல்** இருப்பது.

## 4. Architectural Reasoning

Tool selection எப்போது கஷ்டமாகிறது?

* Tools அதிகமாகும்போது 50+ tools
* Tools overlap ஆகும்போது `search_web` vs `search_internal_knowledge_base`
* Parameter dependencies இருக்கும்போது `create_invoice` க்கு `customer_id` முதலில் தேவை
* Multi-step workflows தேவைப்படும்போது

எனவே architect இவற்றை யோசிக்க வேண்டும்:

**Tool discoverability:** Agent-க்கு tool-ஐ எப்படி தெரியும்? All tools always visible என்பது noise. Dynamic tool routing / tool registry தேவை.

**Tool granularity:** ஒரு tool மிக பெரியதாக இருந்தால் agent confuse ஆகும். மிக சிறியதாக இருந்தால் too many calls.

**Tool description quality:** Description clear இல்லை என்றால் agent wrong tool-ஐ தேர்வு செய்யும். This is prompt engineering at tool level.

Alternatives:
* **Static tool list** - simple but doesn't scale
* **Hierarchical / categorized tools** - Finance tools, CRM tools
* **Retrieval-based tool selection** - user query vectorize பண்ணி, relevant tools retrieve பண்ணி, top-k மட்டும் agent-க்கு கொடுக்க
* **Router agent** - separate lightweight model only for tool selection

## 5. Trade-offs

**Tool count vs Selection accuracy.** Tools அதிகம் = more capability but higher chance of wrong selection. Solution: lazy loading, context-based filtering.

**Specificity vs Generality.** Generic tool like `run_sql` powerful ஆனால் unsafe. Specific tool like `get_user_orders_by_id` safe ஆனால் rigid.

**Autonomy vs Control.** Agent freely choose tools vs human-in-the-loop approval for sensitive tools like `refund_payment`. Security vs speed trade-off.

**Latency.** Every tool call adds network roundtrip. Tool selection bad ஆனால் unnecessary calls வரும். Cost and latency increase.

Failure modes:
* Hallucinated tool name
* Wrong parameter mapping
* Tool call loop - same tool repeatedly
* Tool dependency miss - prerequisite data இல்லாமல் call

## 6. Practical Example

Enterprise support agent.

Tools:
`search_tickets`, `get_customer_profile`, `fetch_order_status`, `create_refund`, `search_knowledge_base`, `escalate_to_human`

User: "என்னோட order 12345 delay ஆகுது, refund வேண்டும்"

Good selection flow:
1. `get_customer_profile` - user identify
2. `fetch_order_status` - order 12345 validate
3. `search_knowledge_base` - delay reason find
4. Decision: if eligible → `create_refund` else `escalate_to_human`

Bad selection: direct `create_refund` without validation → compliance risk.

Architect decision: Sensitive tools like `create_refund` க்கு guardrail + confirmation step வைக்க.

## 7. Reasoning Challenge

உங்களிடம் 80 tools உள்ளன. Agent average 3 hops-ல பதில் கொடுக்கணும். Tools அடிக்கடி fail ஆகுது. Cost கட்டுப்படுத்தணும்.

இந்த constraint-ல tool selection strategy எப்படி design பண்ணுவீர்கள்? Tool catalog-ஐ எப்படி expose பண்ணுவீர்கள்? Failure-க்கு என்ன fallback?

## 8. Key Takeaways

* Tool selection என்பது capability மட்டுமல்ல, decision quality.
* Tool definitions and descriptions agent-ன் reasoning quality-ஐ நிர்ணயிக்கும்.
* Scale ஆகும்போது, tool retrieval and routing முக்கியம்.
* Every tool choice brings latency, cost, and failure risk — choose deliberately.
