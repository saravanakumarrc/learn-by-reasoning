# State

> **Learning Path:** Agentic AI
> **Section:** 15.1.8 — Agent fundamentals

## 1. Problem

ஒரு agent-ஐ ஒரு task கொடுத்தீங்க. அது tool use பண்ணுது, web search பண்ணுது, database-ல read பண்ணுது, LLM-ஐ call பண்ணுது.

Mid-way-ல user சொல்றார்: "Wait, முந்தின step-ல என் budget 5000-க்கு மாத்து."

அந்த agent-க்கு இப்போ என்ன நினைவிருக்கு? Last 3 steps-க்கு முன்னாடி என்ன decide பண்ணிச்சு? எந்த tool output-ஐ use பண்ணி இருந்துச்சு? எந்த assumption போட்டிருந்துச்சு?

Stateless LLM call-களை மட்டும் இணைத்தால், ஒவ்வொரு turn-ம் fresh start. Context window-ல history போடலாம், ஆனால் அது complete memory இல்லை. Agent தன்னோட progress, intermediate results, user preferences, partial plan எல்லாம் track பண்ண வேண்டும்.

**What goes wrong if we don't have state?** Agent திரும்ப திரும்ப அதே question கேட்கும், முன்னாடி செய்த வேலையை மறந்துவிடும், inconsistent decision எடுக்கும், long-running task-ஐ முடிக்க முடியாது.

State என்பது agent-ன் "நினைவு" மற்றும் "current working context".

## 2. Mental Model

Agent state = **what the agent knows about itself, the task, and the world at this moment**.

அது மூன்று layer-ல இருக்கும்:

* **Conversation state**: last few messages, user intent, clarification needed
* **Task state**: current goal, sub-tasks done / pending, plan, progress
* **World state**: data it has fetched, tool outputs, external facts, user profile

LLM-ஐ ஒரு brain ஆக நினைக்காதீங்க. LLM stateless. State-ஐ store பண்ணி, retrieve பண்ணி, update பண்ணி, அதை prompt-ல inject பண்ணுவது agent framework-ன் வேலை.

அனலாகி: Agent ஒரு carpenter. LLM என்பது hands. State என்பது workbench-ல இருக்கும் blueprint, cut pieces, measuring tape, notes. Hands மட்டும் இருந்தால் போதாது.

## 3. How It Works

Agent loop-ல state எப்படி flow ஆகும்:

1. **Read state**: current task state + conversation history + relevant world facts ஐ load பண்ணு
2. **Reason**: LLM-க்கு state + user input கொடுத்து next action decide பண்ணு
3. **Act**: tool call செய்
4. **Update state**: tool output, new facts, plan progress-ஐ state-ல write பண்ணு
5. Repeat

State store எங்கே இருக்கும்?
* In-memory for short session
* Database / Redis for persistence across restarts
* External system like vector DB for facts

State representation எப்படி இருக்கும்?
* Structured fields: `goal`, `plan[]`, `current_step`, `context{}`, `user_preferences{}`
* Often as JSON or in a state machine

Important concept: **State transition is deterministic and auditable**. Agent என்ன decide பண்ணிச்சு, ஏன் பண்ணிச்சு என்பதற்கு trail வேண்டும்.

## 4. Architectural Reasoning

State இல்லாமல் agent என்ன செய்ய முடியும்? Single-turn QA.

State இருந்தால் என்ன செய்ய முடியும்?
* Multi-step planning and execution
* Contextual memory across sessions
* Error recovery and retry with same context
* Human-in-the-loop intervention

எப்போது state முக்கியம்?
* Long-running tasks > 1 LLM call
* Tools use பண்ணும் agentic workflow
* Personalization வேண்டும்
* Consistency வேண்டும்

Alternatives:
* **Full context replay**: Every turn full history ஐ prompt-ல போடு. Simple ஆனால் token cost அதிகம், noisy, மறந்துவிடும்.
* **Summarization**: History-ஐ summarize பண்ணி சுருக்கு. Lossy.
* **Explicit state store**: Structured state ஐ maintain பண்ணி, need-to-know மட்டும் inject பண்ணு. Architecturally clean.

Architect choose பண்ணும்போது கேட்க வேண்டியது: State எவ்வளவு நேரம் survive வேண்டும்? Session மட்டுமா, user lifetime-க்கா? State update atomic ஆக இருக்க வேண்டுமா? Concurrent updates வருமா?

## 5. Trade-offs

**Memory vs Relevance**: எல்லா state-ஐயும் வைத்திருக்கலாம், ஆனால் LLM context limit, noise increase. எதை keep பண்ணுவது என்பது design decision.

**Consistency vs Availability**: State store strong consistency வேண்டுமா? Distributed agent-ல multiple workers same state-ஐ update பண்ணினால் race condition வரும். Optimistic locking / versioning தேவை.

**Structured vs Free-form**: Structured state predictable, queryable, testable. Free-form text memory flexible ஆனால் unreliable. பெரும்பாலும் hybrid.

**Persistence cost**: State-ஐ long term store பண்ணினால் cost, privacy, compliance வரும். What data can we remember about user?

Failure modes:
* Stale state: World மாறியிருக்கு, ஆனால் agent state update ஆகலை
* Lost state: Crash-ல state lost → agent confused
* Prompt injection via state: Malicious tool output state-ல save ஆகி, next turn-ல LLM-ஐ manipulate பண்ணும்

## 6. Practical Example

Enterprise support agent.

User: "என் order #10234-ன் status என்ன?"

Agent state init:
```json
{
  "goal": "find order status",
  "order_id": "10234",
  "steps_done": [],
  "user_id": "u_881"
}
```

Step1: Read state → call order DB tool → result: "shipped, tracking ABC123"
Update state: `steps_done: ["order_lookup"]`, `tracking_id: "ABC123"`, `last_fact: "shipped"`

User: "எப்போ வரும்?"

Agent state-ல tracking_id இருக்கு, அதை use பண்ணி courier API call பண்ணும். State இல்லாமல், agent மறுபடியும் order id கேட்டிருக்கும்.

இங்கே state agent-ஐ coherent ஆக்குகிறது.

## 7. Reasoning Challenge

உங்களிடம் ஒரு travel planning agent இருக்கு. User 3 sessions-க்கு முன்னாடி "I hate flying" என்று சொன்னார். அது long term preference. இப்போ user "Chennai to Bangalore plan பண்ணு" என்கிறார்.

State design எப்படி இருக்கும்? Session state, user profile state, world state என எதை எங்கே store பண்ணுவீர்கள்? எதை prompt-ல inject பண்ணுவீர்கள், எதை filter பண்ணுவீர்கள்? ஏன்?

## 8. Key Takeaways

* State என்பது agent-ன் working memory, not just chat history
* LLM stateless, agent stateful ஆக இருக்க வேண்டும்
* State-ஐ explicit ஆக design பண்ணு: what to keep, where to store, how to update, how long to keep
* Every architectural choice for state creates trade-offs: consistency, cost, privacy, complexity
* Good state design = predictable, auditable, recoverable agent behavior
