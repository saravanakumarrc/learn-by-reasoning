# Tool selection accuracy

> **Learning Path:** AI Evaluation
> **Section:** 18.3.2 — Agent metrics

### 1. Problem

உங்களிடம் ஒரு agent இருக்கு. அது user கேள்விக்கு பதில் கொடுக்கணும். அதற்கு `search_web`, `call_billing_api`, `query_vector_db`, `create_jira_ticket` மாதிரி 10-15 tools இருக்கு.

Agent சரியான tool-ஐ தேர்ந்தெடுக்கலைன்னா என்ன ஆகும்?

Wrong tool-ஐ call பண்ணி useless data வாங்கி, பிறகு retry பண்ணும். சில சமயம் sensitive data-ஐ தவறான API-க்கு அனுப்பும். User-க்கு தவறான பதில் போகும்.

Tool selection accuracy என்பது agent ஒரு task-க்கு **தேவையான சரியான tool-ஐ முதல் முயற்சியிலேயே தேர்ந்தெடுக்கிறதா** என்பதை அளக்கும் metric.

`Tool selection accuracy` இல்லாமல் agent-ஐ deploy பண்ணினால், latency அதிகரிக்கும், cost waste ஆகும், trust குறையும்.

### 2. Mental Model

Agent-ன் மூளையை ஒரு receptionist-ஆக நினைச்சுக்கோங்க.

Receptionist-க்கு 15 departments இருக்கு. Customer ஒரு request வரும்போது, receptionist சரியான department-க்கு forward பண்ணணும்.

Tool selection accuracy = receptionist எத்தனை முறை சரியான department-க்கு அனுப்பினார் / total requests.

இது tool *execution* சரியா என்பதை அல்ல, tool *choice* சரியா என்பதை அளக்கிறது.

### 3. How It Works

Evaluation-க்கு நமக்கு தேவை:

1. **Ground truth**: ஒரு user query-க்கு ideal tool set என்ன என்பது.
2. **Agent prediction**: Agent என்ன tool-ஐ choose பண்ணிச்சு.
3. **Comparison**.

Simple formula:
`Tool Selection Accuracy = Correctly Selected Tools / Total Tool Selection Opportunities`

முக்கிய nuance:
* Single tool task: Agent ஒரே ஒரு tool choose பண்ணணும். Exact match பார்க்கலாம்.
* Multi-tool task: Agent-க்கு 3 tools தேவை. Agent 2 சரியா, 1 தப்பா தேர்ந்தெடுத்தால்? Partial credit வேண்டுமா? அதுதான் design decision.

அளவீட்டு வகைகள்:
* **Exact Match Accuracy**: Predicted set == Ground truth set
* **Precision / Recall**: Agent எத்தனை தேவையான tool-ஐ catch பண்ணிச்சு, எத்தனை unnecessary tool-ஐ தேர்ந்தெடுத்துச்சு

Example: Ground truth = [search_web, query_vector_db]. Agent predicted = [search_web, call_billing_api]
Precision = 1/2, Recall = 1/2

### 4. Architectural Reasoning

Tool selection accuracy எப்போது முக்கியம்?

* Agent-க்கு tool set பெரிதாகும் போது. 5 tools vs 50 tools.
* Tools-க்கு cost / latency வேறுபடும் போது. `call_billing_api` தப்பா call பண்ணினால் cost.
* Tools mutually exclusive ஆக இருக்கும் போது. `delete_user` vs `create_user` தேர்வு தவறினால் disaster.

இது agent design-ஐ எப்படி பாதிக்கிறது?

* **Prompting strategy**: Tool descriptions clear-ஆ இருக்கா? Ambiguity குறையுதா?
* **Retrieval over reasoning**: Tool set பெரிதாகும் போது, agent-க்கு எல்லா tools-ஐயும் ஒரே சமயம் காட்டாமல், query-க்கு relevant tools-ஐ retrieve பண்ணி கொடுக்கும் system வேண்டும்.
* **Tool routing layer**: Separate classifier model, router model வைத்து tool selection-ஐ isolate பண்ணலாம்.
* **Fine-tuning**: Tool selection accuracy low ஆ இருந்தால், agent-ஐ tool description data மீது fine-tune செய்யலாம்.

Alternative metric: Tool execution success rate. அது tool choose பண்ணின பிறகு execution சரியா என்பதை பார்க்கும். Selection accuracy என்பது முந்தைய step.

### 5. Trade-offs

**Accuracy vs Coverage**: Agent ஒரு tool-ஐ மட்டும் தேர்ந்தெடுத்தால் accuracy high ஆக இருக்கும், ஆனால் multi-step task-ஐ miss பண்ணும். Over-select பண்ணினால் recall high, ஆனால் cost high.

**Granularity**: Tool name level-ல மட்டும் அளக்கலாம். ஆனால் உண்மையில் tool-ன் parameters சரியா இருக்கா என்பதும் முக்கியம். Selection accuracy alone sufficient இல்லை.

**Evaluation cost**: Ground truth tool labels manually create பண்ணணும். 1000 queries-க்கு human annotation தேவை. Synthetic data-ல generate பண்ணினால் distribution shift வரும்.

**Failure mode**: Agent சரியான tool-ஐ தேர்ந்தெடுத்தாலும், tool description confusing ஆக இருந்தால், agent தவறான parameters pass பண்ணும். அது selection accuracy-ல capture ஆகாது.

### 6. Practical Example

Enterprise support agent. Tools: `search_knowledge_base`, `get_user_profile`, `refund_request`, `escalate_to_human`, `check_order_status`.

Query: "என் last order எப்போ வரும்?"

Ground truth tool: `check_order_status`. Agent `search_knowledge_base` தேர்ந்தெடுத்தால், அது generic shipping policy கொடுக்கும். User கேள்வி தீராது.

இங்கே tool selection accuracy low ஆக இருந்தால், agent தேவையான user-specific info-ஐ எடுக்காமல் general info தரும். User frustration அதிகரிக்கும்.

இதை improve பண்ண, tool descriptions-ல "when to use" section add பண்ணி, few-shot examples கொடுத்து accuracy 62% -> 89% ஆகியது.

### 7. Reasoning Challenge

உங்கள் agent-க்கு 40 tools இருக்கு. Production-ல tool selection accuracy 78%. ஒரு tool call சராசரி cost $0.02 + 800ms latency.

நீங்கள் accuracy-ஐ 92% ஆக்க முடியும், ஆனால் அதற்கு agent-க்கு குறைந்த tools-ஐ மட்டும் காட்டும் router layer add பண்ணணும். Router ஒவ்வொரு request-க்கும் 150ms extra latency சேர்க்கும்.

நீங்கள் என்ன தேர்வு செய்வீர்கள்? Router add பண்ணுவீர்களா? ஏன்?

### 8. Key Takeaways

* Tool selection accuracy = Agent சரியான tool-ஐ முதல் முயற்சியில் தேர்ந்தெடுக்கிறதா என்பதன் அளவீடு.
* இது execution success அல்ல, choice quality.
* Tool set பெரிதாகும்போதும், tools expensive/unsafe ஆகும்போதும் இந்த metric critical ஆகிறது.
* High accuracy-க்கு clear tool descriptions, retrieval-based routing, and proper evaluation set தேவை.
* Accuracy-ஐ தனியாக பார்க்காமல், precision/recall மற்றும் downstream task success-உடன் சேர்த்து evaluate பண்ணுங்கள்.
