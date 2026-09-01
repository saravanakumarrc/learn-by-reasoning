# Supervisor architecture

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.4 — Learn

## 1. Problem

உங்களிடம் ஒரு complex task இருக்கு. உதாரணமா: "ஒரு customer complaint-ஐ analyze பண்ணி, refund policy படி eligible-ஆனதா check பண்ணி, CRM-ல update பண்ணி, customer-க்கு personalized email அனுப்பு".

இதை ஒரே LLM agent பண்ண முயற்சித்தால் என்ன ஆகும்?

Context window overflow ஆகும். Tool calls தவறாகும். Reasoning தெளிவில்லாமல் போகும். ஒரு step-ல தவறு நடந்தால் முழு workflow தோல்வி.

மறுபுறம், ஒவ்வொரு sub-task-க்கும் தனி agent வைத்தால், யார் முடிவெடுப்பது? யார் next step-ஐ தேர்வு செய்வது? Agents ஒன்றோடொன்று எப்படி coordinate செய்வது?

இந்த coordination problem தான் supervisor architecture வர காரணம்.

## 2. Mental Model

Supervisor architecture என்பது **ஒரு manager + கீழே specialists**.

Manager பார்க்கும் வேலை: Task-ஐ புரிந்துகொள்வது, sub-tasks-ஆக பிரிப்பது, எந்த specialist-க்கு எந்த வேலை என்று assign செய்வது, result-ஐ review செய்து next step decide செய்வது.

Specialists பார்க்கும் வேலை: தங்கள் domain-ல deep work செய்வது. Retrieval, code generation, summarization, classification போன்றவை.

அனாலஜி: Hospital-ல senior doctor supervisor. Patient வந்ததும் triage பண்ணி, radiologist-க்கு scan, lab-க்கு test, pharmacist-க்கு prescription என்று delegate செய்கிறார். Senior doctor தான் final decision எடுக்கிறார்.

## 3. How It Works

Flow பொதுவாக இப்படி இருக்கும்:

1. **Input → Supervisor**
User request வருகிறது.

2. **Decomposition**
Supervisor task-ஐ analyze செய்து plan செய்கிறது. "இதுக்கு 3 steps தேவை. Step 1: data fetch, Step 2: policy check, Step 3: communication"

3. **Routing / Delegation**
ஒவ்வொரு step-க்கும் தகுந்த worker agent-க்கு handoff செய்கிறது. Routing rule static ஆகவோ, LLM-based dynamic ஆகவோ இருக்கலாம்.

4. **Execution & Observation**
Worker தன் tool-களை use செய்து result திருப்பி அனுப்புகிறது.

5. **Loop**
Supervisor result-ஐ validate செய்கிறது. போதுமானதா? இன்னும் தகவல் தேவையா? அடுத்த agent-க்கு போகலாமா? Loop முடிந்து final output-ஐ synthesize செய்கிறது.

Key point: Supervisor-க்கு tools இருக்காது அல்லது குறைவாகவே இருக்கும். அது **orchestration logic**-ஐ வைத்திருக்கும். Workers-க்கு domain tools இருக்கும்.

## 4. Architectural Reasoning

இந்த architecture எப்போது useful?

* Task multi-step, multi-domain ஆக இருக்கும்போது
* Different skills தேவைப்படும்போது. ஒரு agent எல்லாம் தெரிந்திருக்க முடியாது
* Error isolation தேவைப்படும்போது. ஒரு worker fail ஆனாலும் supervisor recover செய்யலாம்
* Auditability தேவைப்படும்போது. யார் என்ன செய்தார் என்று trace பண்ணலாம்

Alternatives என்ன?

* **Single Agent**: simple, fast, low latency. ஆனால் complex task-ல hallucination அதிகம்.
* **Hierarchical Agents**: Supervisor கீழே sub-supervisor. Very large systems-க்கு.
* **Router / Reflect**: Simple routing without looped supervision.

Architect ஏன் supervisor-ஐ தேர்வு செய்வார்? Because **control vs capability trade-off**. Capability-ஐ workers-க்கு delegate செய்து, control-ஐ centralize செய்ய வேண்டும்.

## 5. Trade-offs

**Latency**: Every delegation round trip சேர்கிறது. Supervisor + workers = more calls, more tokens.

**Complexity & Operability**: System state manage செய்ய வேண்டும். Supervisor stuck ஆனால் whole flow stuck.

**Single point of failure**: Supervisor தான் brain. அது bias ஆனால் whole decision தவறாகும். Supervisor-ஐ robust ஆக்க வேண்டும், good prompt + validation.

**Cost**: More LLM calls. ஒரு task-க்கு 1 call இல்லாமல் 4-5 calls.

**Consistency**: Workers தங்கள் output format follow செய்யவில்லை என்றால் supervisor parse செய்ய முடியாது. Contract / schema தேவை.

Failure modes: Supervisor over-delegate செய்து loop-ல மாட்டிக்கொள்வது, worker hallucination-ஐ filter செய்யாமல் accept செய்வது, context loss between steps.

## 6. Practical Example

Enterprise support automation:

Supervisor: `SupportOrchestrator`
Workers: `TicketClassifier`, `PolicyChecker`, `RefundAgent`, `EmailWriter`

Flow:
User message → Supervisor classifies intent. Classifier-க்கு delegate செய்கிறது. Output: refund_request.

Supervisor PolicyChecker-க்கு ask செய்கிறது: order_id, policy rules fetch. Checker vector DB-ல policy retrieve செய்து eligible ஆ? என்று சொல்கிறது.

Supervisor decision: eligible ஆனால் RefundAgent-க்கு delegate. Agent payment API call செய்கிறது.

அடுத்து EmailWriter-க்கு delegate செய்து personalized email generate செய்கிறது.

Supervisor final summary-ஐ user-க்கு திருப்பி அனுப்புகிறது.

இங்கே supervisor தான் policy compliance-ஐ ensure செய்கிறது. Worker ஒவ்வொன்றும் தன் domain-ல specialist.

## 7. Reasoning Challenge

உங்களிடம் 3 agents உள்ளன: Researcher, Summarizer, Critic. Supervisor ஒவ்வொரு query-க்கும் முதலில் Researcher-க்கு அனுப்புகிறது, பிறகு Summarizer, பிறகு Critic.

ஒரு query-ல Critic "insufficient evidence" என்று திரும்பி அனுப்புகிறது. Supervisor இப்போது என்ன செய்ய வேண்டும்? Loop-ஐ தொடர வேண்டுமா, Researcher-க்கு மீண்டும் அனுப்பி deeper search செய்ய சொல்ல வேண்டுமா, அல்லது user-க்கு partial answer கொடுக்க வேண்டுமா?

நீங்கள் supervisor-ஆக இருந்தால், termination condition-ஐ எப்படி design செய்வீர்கள்? Max iterations vs confidence threshold?

## 8. Key Takeaways

* Supervisor architecture = **control centralization + capability decentralization**.
* Task decomposition and routing தான் supervisor-ன் core value.
* Latency, cost, complexity அதிகரிக்கும், ஆனால் reliability, auditability, specialization improve ஆகும்.
* Supervisor-ஐ fail-safe ஆக்கு: validation, loop limits, fallback paths வை.
* Simple tasks-க்கு supervisor overkill. Complexity justify ஆகும் போதுதான் use செய்.
