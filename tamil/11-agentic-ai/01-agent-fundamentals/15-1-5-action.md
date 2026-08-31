# Action

> **Learning Path:** Agentic AI
> **Section:** 15.1.5 — Agent fundamentals

## 1. Problem

ஒரு LLM-க்கு நீங்கள் கேள்வி கேட்கிறீர்கள். அது உங்களுக்கு பதில் சொல்லும். அவ்வளவுதான்.

ஆனால் ஒரு real system-ல் உங்களுக்கு வேண்டியது:

> "என் bank account-ல இருந்து 5000 INR-ஐ savings-க்கு transfer பண்ணு, அதற்கு பிறகு எனக்கு email confirmation அனுப்பு."

LLM ஒன்றும் செய்யாது. அது text மட்டுமே தரும்.

இங்கேதான் pain வருகிறது. Model-க்கு reasoning இருக்கிறது, ஆனால் **world-ல் action எடுக்கும் ability இல்லை**.

ஒரு agent-க்கு வேண்டியது: observe → reason → act → observe...

Action என்பது அந்த **act** step.

## 2. Mental Model

Agent fundamentals-ல் மூன்று core pieces:

* **Perception:** user input, tools output, environment state
* **Reasoning:** LLM or planner எது next செய்ய வேண்டும் என்பதை தீர்மானிக்கிறது
* **Action:** உண்மையான வெளி உலகில் ஏதாவது செய்வது

Action = agent-ன் decision-ஐ external system-க்கு map பண்ணும் bridge.

Analogy: நீங்கள் ஒரு experienced engineer. உங்களுக்கு problem தெரியும், ஆனால் உங்கள் கைகள் இல்லை. Action என்பது உங்களுக்கு கைகள் கொடுப்பது.

## 3. How It Works

Agent ஒரு loop-ல் ஓடுகிறது:

1. **Current state-ஐ collect பண்ணு** - conversation history, tool outputs
2. **LLM-ஐ prompt செய்** - available tools, their description, constraints
3. **Model ஒரு action-ஐ தேர்வு செய்கிறது** - `transfer_funds(account_id, amount)` or `search_web(query)`
4. **Action executor அதை run செய்கிறது** - real API call, database write
5. **Result-ஐ திரும்ப loop-க்கு கொடு**

முக்கிய point: LLM directly code run செய்யாது. Action என்பது **structured output** → **tool invocation** pattern.

Tool spec பொதுவாக இப்படி இருக்கும்:
* name
* description
* parameters with type + constraints
* return schema

Model இதை பார்த்து decide செய்கிறது. இது function calling / tool use என்று அழைக்கப்படுகிறது.

## 4. Architectural Reasoning

Action எப்போது தேவை?

எப்போது task single turn-ல் முடியாதோ, அப்போது.

* Information retrieval தேவை - search web, query database
* Side effects உருவாக்க வேண்டும் - send email, create ticket, place order
* Multi-step workflow தேவை - booking flight + hotel + send itinerary

Constraints-ஐ address செய்வது:
* **Latency:** Action synchronous-ஆக இருந்தால் user wait செய்ய வேண்டும்
* **Safety:** எந்த action-ஐ allow செய்யலாம்? எதை block செய்ய வேண்டும்?
* **Observability:** எந்த action எப்போது எடுக்கப்பட்டது என்பதை audit செய்ய வேண்டும்

Alternatives:
* No agent, just LLM chat - simple, safe, ஆனால் no real work
* Hard-coded workflow - predictable, ஆனால் flexible இல்லை
* Agent with actions - flexible, ஆனால் complexity அதிகம்

ஆர்கிடெக்ட் ஏன் choose செய்வார்? User intent-ஐ understand செய்து, multiple systems-ஐ coordinate செய்ய வேண்டும் என்றால்.

## 5. Trade-offs

**1. Autonomy vs Control**
Action-க்கு அதிக freedom கொடுத்தால் agent creative ஆக இருக்கும், ஆனால் wrong tool-ஐ தவறாக call செய்ய வாய்ப்பு அதிகம். Guardrails, allow-list, confirmation steps தேவை.

**2. Synchronous vs Asynchronous**
Action immediately run செய்தால் latency அதிகம். Long running jobs-க்கு async + callback வேண்டும். ஆனால் state management கடினம்.

**3. Idempotency & Safety**
ஒரு payment action-ஐ model தவறுதலாக இரண்டு முறை call செய்தால் என்ன ஆகும்? Action layer-ல் idempotency key, dry-run, confirmation mandatory.

**4. Tool explosion**
Too many tools = model confusion. Too few tools = agent useless. Tool descriptions clear-ஆக இருக்க வேண்டும். Semantic search for tool selection பெரிய system-ல் தேவை.

Failure mode: Model hallucinate செய்து non-existent tool-ஐ call செய்யும். அதனால் strict schema validation + fallback critical.

## 6. Practical Example

Enterprise support agent.

User: "எனது last invoice-ல் charge தவறாக இருக்கிறது. Refund வேண்டும்."

Agent steps:
1. Perception: user message
2. Reasoning: Need customer ID, invoice ID, verify charge
3. Action 1: `get_customer_by_email(email)` → tool call
4. Observation: customer found, last invoice ID = INV-10293
5. Reasoning: Need invoice details
6. Action 2: `get_invoice(invoice_id)` 
7. Observation: invoice details
8. Reasoning: Charge is wrong, need refund
9. Action 3: `create_refund_request(invoice_id, reason)` 
10. Action 4: `send_email(to, template="refund_ack")`

இங்கே Action என்பது external service-ஐ touch செய்வது. Agent loop தொடர்கிறது.

## 7. Reasoning Challenge

உங்களிடம் 20 tools உள்ளன: `search_web`, `query_database`, `send_email`, `create_ticket`, `place_order`, `cancel_order`, `refund`, `get_weather`... User கேட்கிறார்: "எனது order-க்கு ஏன் delay ஆகிறது?"

Model முதலில் என்ன செய்ய வேண்டும்? Direct-ஆக `cancel_order` செய்யலாமா? அல்லது information gather செய்ய வேண்டுமா?

நீங்கள் என்ன guardrails வைப்பீர்கள்? Action-க்கு முன் confirmation தேவையா? எப்போது?

## 8. Key Takeaways

* Action என்பது agent-ன் decision-ஐ real world effect-ஆக மாற்றும் bridge
* Agent = observe → reason → act loop. Action இல்லாமல் agent சும்மா chatbot
* Tool design, safety, idempotency, observability தான் architectural decisions
* Every action creates new failure modes: wrong tool, wrong params, duplicate execution

இது புரிந்தால், agent system design செய்யும்போது நீங்கள் action layer-ஐ முதலில் design செய்வீர்கள், model-ஐ பிறகு.
