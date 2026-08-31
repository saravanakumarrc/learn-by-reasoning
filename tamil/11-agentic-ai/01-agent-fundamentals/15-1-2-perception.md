# Perception

> **Learning Path:** Agentic AI
> **Section:** 15.1.2 — Agent fundamentals

## 1. Problem

ஒரு agent-ஐ நீங்கள் build பண்ணும்போது முதல் கேள்வி இது: இந்த agent-க்கு உலகம் பத்தி தெரியுமா?

உங்க system-ல் ஒரு user "என் last month-ல் எந்த invoice-க்கு payment pending?" என்று கேட்கிறார். Agent-க்கு இரண்டு விஷயம் தெரிய வேண்டும்:
1. User யார்?
2. Invoice data எங்கே இருக்கு, அதை எப்படி படிக்கிறது?

இந்த "தெரிந்து கொள்ளும்" வேலைதான் Perception.

Agent-க்கு perception இல்லை என்றால் என்ன ஆகும்? அது blind-ஆக இருக்கும். Tool-ஐ எப்போது use பண்ணணும், எந்த data-ஐ trust பண்ணணும், user intention என்ன என்பதே தெரியாது.

அதனால் agent hallucinates, wrong tool-ஐ call பண்ணும், outdated data-வை use பண்ணும்.

> What problem became painful enough? 
> Agent-க்கு world state பற்றி real-time, contextual understanding இல்லாமல் autonomous decision எடுக்க முடியாது.

## 2. Mental Model

Perception = **Input ingestion + Contextual interpretation**.

இது ஒரு sensor layer மாதிரி. Human-க்கு eyes, ears, memory இருக்கு. Agent-க்கு perception stack இருக்கு.

அது 3 விஷயங்களை combine பண்ணும்:
* **External input**: user message, UI event, sensor data
* **Internal state**: memory, conversation history, current goal
* **Environment context**: database, API, file system, time, user profile

பிறகு அதை ஒரு structured representation-ஆக மாற்றும்: "user wants X, needs Y data, from Z source".

இது reasoning-க்கு முந்தைய step.

## 3. How It Works

Perception pipeline எளிமையாக இப்படி இருக்கும்:

**Raw Input → Preprocessing → Understanding → Context Enrichment → Intent Representation**

* Preprocessing: text normalization, audio transcription, image preprocessing. Noise remove பண்ணுது.
* Understanding: LLM-based parsing, entity extraction, intent classification. "last month pending invoice" என்பதை `query = invoices`, `filter = status=pending`, `time_window = last_month` என்று parse பண்ணும்.
* Context Enrichment: current conversation, user profile, recent actions, external data lookup. User ID தெரியுமா? Access rights உள்ளதா?
* Intent Representation: structured output, e.g., JSON schema, function call parameters. இது reasoning module-க்கு கொடுக்கப்படும்.

Technically இது mostly LLM prompting + retrieval + schema validation. RAG-ல் embedding search, vector database query போன்றவை இங்கேதான் வரும்.

## 4. Architectural Reasoning

எப்போது perception முக்கியமாகிறது?

* Multi-turn conversation-ல் context drift வராமல் தடுக்க
* Tool use தேவையை சரியாக detect பண்ண
* Hallucination குறைக்க

Alternatives என்ன?

* **Naive prompting**: raw user text-ஐ direct-ஆக LLM-க்கு கொடுத்து reasoning பண்ண விடுவது. Fast ஆனால் error prone.
* **Structured schema + validation**: Input-ஐ strict schema-க்கு force பண்ணுது. Accuracy அதிகம், ஆனால் flexibility குறையும்.
* **Perception with memory retrieval**: Conversation history + long-term memory-ல் retrieve பண்ணி enrich பண்ணுது. Cost அதிகம், ஆனால் coherent agent கிடைக்கும்.

Architect choose பண்ணும் போது கேட்கும் கேள்வி:
* Input noisy ஆ? Human natural language இல்லை, sensor data?
* Latency constraint உள்ளதா? Perception heavy ஆனால் slow ஆகும்.
* Safety / compliance தேவை உள்ளதா? Intent-ஐ validate பண்ண வேண்டும்.

## 5. Trade-offs

**Accuracy vs Latency**: More context retrieval, better understanding, but higher latency and cost. Real-time agent-க்கு trade-off தேவை.

**Generality vs Specificity**: Generic perception model flexible ஆனால் domain-specific nuance miss பண்ணும். Fine-tuned / domain schema சிறப்பாக புரியும் ஆனால் maintain பண்ண கஷ்டம்.

**Stateful vs Stateless**: Stateful perception conversation continuity கொடுக்கும், ஆனால் memory consistency, privacy, scalability problem வரும். Stateless simple ஆனால் context loss ஆகும்.

**Failure modes**: Misinterpretation, missing entities, outdated context retrieval, prompt injection through user input. இதனால் agent wrong tool-ஐ call பண்ணும் அல்லது sensitive data leak ஆகும்.

## 6. Practical Example

Enterprise support agent.

User: "நேற்று நான் raise பண்ணின ticket-க்கு status என்ன?"

Perception step:
1. Raw input parse: intent = ticket_status_check, entity = "நேற்று", reference = "நான் raise பண்ணின"
2. Context enrichment: authenticate user, fetch recent tickets created by user in last 24h from ticketing API. Conversation history-ல் ticket ID mention ஆகியிருக்கா?
3. If one ticket found → bind it. If multiple → disambiguation needed.
4. Output representation: `{action: get_ticket_status, ticket_id: T-48291, user_id: u_123}`

இங்கே perception தவறினால், agent random ticket-ஐ check பண்ணும். அதனால் privacy violation, wrong answer.

இந்த pipeline-ல் retrieval, entity linking, time resolution எல்லாம் perception-தான்.

## 7. Reasoning Challenge

உங்களிடம் customer service agent இருக்கு. User voice call-ல் பேசுகிறார். Background noise அதிகம். User-ன் account-ல் last 6 months-ல் 200+ transactions இருக்கு. User சொல்கிறார்: "அந்த expensive purchase-க்கு refund வேணும்".

Perception-ல் என்ன முக்கிய challenges இருக்கு? Intent disambiguation, entity resolution எப்படி செய்வீர்கள்? Noise handling, context retrieval எதை prioritize பண்ணுவீர்கள்? Perception output-ஐ validate செய்யாமல் reasoning-க்கு அனுப்பினால் என்ன ஆகும்?

## 8. Key Takeaways

* Perception என்பது agent-க்கு world-ஐ புரிந்துகொள்ளும் sensor layer. Reasoning-க்கு முன் இது தேவை.
* Good perception = clean input + context enrichment + structured intent representation.
* Accuracy, latency, cost மூன்றுக்கும் இடையே trade-off உள்ளது. Context எவ்வளவு retrieve பண்ண வேண்டும் என்பது design decision.
* Perception தவறினால், agent சரியான tool-ஐ கூட கண்டுபிடிக்க முடியாது. இதுதான் agentic failure-ன் root cause.
