# Interruptions

> **Learning Path:** Agentic AI
> **Section:** 15.3.5 — Agent state

### 1. Problem

ஒரு agent ஒரு long-running task பண்ணிட்டு இருக்கு. உதாரணமா, user கிட்ட "என் மாசத்துக்கான ரிப்போர்ட் தயார் பண்ணு, மெயில் அனுப்பு"ன்னு சொல்லியிருக்கு.

Agent ரிப்போர்ட் generate பண்ண ஆரம்பிச்சது. அப்போதான் user chat-ல "அது வேண்டாம், முதல்ல இந்த வார invoice எங்கே?"ன்னு interrupt பண்ணுது.

இப்போ என்ன ஆகும்?

* Current task-ஐ நிறுத்தி புது request-ஐ எடுக்கணுமா?
* இரண்டையும் ஒன்னா handle பண்ண முடியுமா?
* Agent state-ல என்ன இருக்கு? Context, partial results, tool calls, conversation history எல்லாம் எப்படி manage பண்ணுவது?

இதுதான் interruption பிரச்சனை. Agent-க்கு state இருக்கு, அந்த state-ஐ எப்படி pause, resume, switch, merge பண்ணுவது?

### 2. Mental Model

Agent state = current goal + conversation history + working memory + tool outputs + pending actions.

Interruption = state-ஐ மாற்றும் external event.

ஒரு human assistant மாதிரி யோசி. நீ ஒரு document எழுதிட்டு இருக்க, boss வந்து "இந்த mail-ஐ முதல்ல பாரு"ன்னு சொன்னா, நீ document-ஐ save பண்ணி, மனசுல context-ஐ hold பண்ணிட்டு mail-க்கு போற. அதேதான் agent-க்கும் வேணும்.

எனவே இரண்டு விஷயங்கள் முக்கியம்:
1. **State preservation**: தற்போதைய task-ஐ எப்படி freeze பண்ணி safe ஆ வைக்கிறது?
2. **Context switching**: புது request வந்ததும் எப்படி priority decide பண்ணி, state-ஐ switch பண்ணுவது?

### 3. How It Works

Interruptions-ஐ handle பண்ண மூன்று basic patterns உண்டு.

**A. Preemptive Interrupt**
Agent தற்போது செய்யும் task-ஐ உடனே stop பண்ணி புது request-க்கு மாறுது.
State-ஐ checkpoint பண்ணி store பண்ணும். பின்னர் resume பண்ணலாம்.

**B. Queue and Continue**
புது request-ஐ queue-ல வைத்து, current task முடிந்த பிறகு எடுக்கும்.
User experience slow ஆகும், ஆனால் state corruption risk குறைவு.

**C. Parallel / Multi-threaded Agent**
Agent-க்கு multiple active contexts இருக்கும். ஒவ்வொரு user intent-க்கும் ஒரு state branch.
Resource அதிகம், ஆனால் interruption latency குறைவு.

Practically, state management இதில் நடக்கும்:
* **Session state**: conversation history, user profile
* **Task state**: current goal, step, tools used, partial results
* **Working memory**: short-lived reasoning, intermediate outputs

Interrupt வந்தால் agent:
1. Current task-ஐ checkpoint செய்யும்
2. Priority / policy படி decide செய்யும்: continue, pause, cancel
3. புது context-ஐ load செய்யும்
4. User-க்கு clear acknowledgment கொடுக்கும்

### 4. Architectural Reasoning

Interruptions useful ஆகும் எப்போ?

User driven, real-time systems-ல. Chat agent, customer support bot, autonomous workflow agent.

Constraint என்ன?
Latency vs consistency of state. User wants immediate response, ஆனால் current task-ஐ lose பண்ணக்கூடாது.

Alternative?
Stateless agent: ஒவ்வொரு request-ம independent. Simple, ஆனால் long task track பண்ண முடியாது.
Stateless + external memory: interruptions handle ஆகும், ஆனால் coherence குறைவு.

Architect choose பண்ணும் போது கேட்க வேண்டியது:
* Interruptions frequent ஆ?
* Task resumption முக்கியமா?
* User expects immediate context switch?
* State size எவ்வளவு? DB save cost?

### 5. Trade-offs

* **Resume vs Forget**: State-ஐ save பண்ணினால் cost, latency. Forget பண்ணினால் user frustration. Trade-off: checkpoint frequency.
* **Immediate switch vs Queue**: Immediate switch செய்தால் partial work waste ஆகும். Queue செய்தால் responsiveness குறையும்.
* **Single context vs Multi-context**: Single context simple and cheap. Multi-context better UX, ஆனால் operational complexity, memory usage அதிகம்.
* **Failure mode**: Interrupt வந்த பிறகு state corrupt ஆனால் agent lost work. Idempotency, durable state store வேண்டும்.

### 6. Practical Example

Enterprise support agent.

User: "என் கடந்த 6 மாத transactions-ஐ analyze பண்ணி summary கொடு"

Agent tool call start: database query -> aggregation -> LLM summarization.

Midway-ல user: "நிறுத்து, என் account-ஐ lock பண்ணு, suspicious login வந்திருக்கு"

Good architecture:
Agent current task-ஐ checkpoint பண்ணி persistent state store-ல வைக்கும்: task_id, step=aggregation_done, partial_result.
New intent detect பண்ணி priority high ஆக set பண்ணும்.
User-க்கு சொல்லும்: "Transaction analysis pause பண்ணிட்டேன், account lock பண்ண ஆரம்பிக்கிறேன்"
Lock complete ஆனதும், user-க்கு கேட்கும்: "Analysis-ஐ தொடர வேண்டுமா?"

இங்கே state machine clear ஆ இருக்கும்.

### 7. Reasoning Challenge

உங்களிடம் ஒரு agentic AI agent உள்ளது. Agent ஒரு multi-step workflow செய்து கொண்டிருக்கிறது: data fetch → analysis → report generation → email.

User திடீரென "Stop current workflow, now book me a flight for tomorrow" என்று interrupt செய்கிறார்.

நீங்கள் என்ன செய்வீர்கள்?
* Current workflow-ஐ அப்படியே தொடர்ந்து, flight booking-ஐ queue செய்வீர்களா?
* Workflow-ஐ immediate cancel செய்து flight-க்கு மாறுவீர்களா?
* இரண்டையும் parallel ஆக handle செய்வீர்களா?

ஏன் அந்த தேர்வு? State-ஐ எப்படி manage செய்வீர்கள்?

### 8. Key Takeaways

* Interruptions என்பது state management problem, not just request handling problem.
* Agent-க்கு checkpoint, pause, resume capability இல்லாமல் reliable long tasks சாத்தியமில்லை.
* Every interruption decision என்பது priority, user intent, resource cost இடையே trade-off.
* Clear user communication about what is paused, what is resumed, முக்கியம்.
