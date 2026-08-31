# Working memory

> **Learning Path:** AI Memory
> **Section:** 13.1.7 — Memory types

### 1. Problem

ஒரு agent-ஐ ஒரு user conversation-ல run பண்ணும்போது என்ன பிரச்சனை வரும்?

User சொன்னது, agent tool call பண்ணிச்சு, result வந்தது, next turn-ல மறந்துடுச்சு. "நான் just சொன்னது என்ன?" ன்னு திரும்ப கேக்குது.

LLM-க்கு context window இருக்கு. ஆனா அது limited, expensive, மற்றும் stateless. ஒவ்வொரு request-லயும் முழு history-யும் அனுப்பினா token cost ஏறும், latency ஏறும், முக்கியமான signal noise-ல மறைஞ்சுடும்.

Engineer-க்கு தேவை: **இந்த session-க்குள்ள மட்டும் வேண்டிய facts-ஐ, short-term-ல hold பண்ணி, immediate reasoning-க்கு use பண்ணணும்.** அதுதான் Working Memory.

### 2. Mental Model

Working Memory = இப்போ நடக்கிற conversation-ன் short-term scratchpad.

Long-Term Memory போல permanent store இல்லை. Episodic Memory போல பெரிய history archive இல்லை.

இது ஒரு agent-ன் **current turn-ன் context** ஆக இருக்கு. User intent, last tool output, intermediate plan, temporary variables.

Analogy: ஒரு engineer meeting-ல whiteboard. Meeting முடிஞ்சதும் board clean ஆகும். அதுல current problem-ன் notes மட்டும் இருக்கும். அது permanent document இல்லை.

### 3. How It Works

Architecturally Working Memory என்பது session-scoped state.

பொதுவாக இது இப்படி implement ஆகும்:

* **In-context**: LLM prompt-ன் system + user messages + recent turns. இது simplest.
* **Session store**: Redis / in-memory store-ல session_id கீ-க்கு ஒரு small JSON object வைக்கிறது. Current entities, last action, partial plan.
* **Agent runtime state**: LangGraph / AutoGen போன்ற frameworks-ல state object. Each node update பண்ணும்.

Flow:
`User Input -> Working Memory Update -> Reason -> Tool Call -> Result -> Working Memory Update -> Next turn`

Memory update என்பது selective retention. எல்லாத்தையும் வைக்காம, relevant facts மட்டும் compress செய்து வைக்கிறது.

### 4. Architectural Reasoning

Working Memory எப்போ useful?

* Multi-turn conversation-ல context continuity வேண்டும்.
* Tool outputs-ஐ next step-ல use பண்ணணும்.
* Agent internal plan-ஐ step-by-step track பண்ணணும்.

Constraint it addresses: LLM stateless + context window limit.

Alternatives:
* **Everything in context window**: Simple ஆனா cost, latency, noise அதிகம்.
* **Only Long-Term Memory**: Too slow, too permanent. Current turn-ன் nuance தொலையும்.
* **No memory**: Stateless bot. ஒவ்வொரு turn-லயும் fresh start.

ஏன் architect choose பண்ணுவார்? Because reasoning quality directly depends on relevant recent facts. Working Memory gives fast, cheap, session-local access.

### 5. Trade-offs

**1. Freshness vs Noise**
Working Memory-ல நிறைய வச்சா context pollution ஆகும். குறைவா வச்சா needed fact missing ஆகும். Summarization policy முக்கியம்.

**2. Ephemerality vs Persistence**
Session முடிஞ்சதும் discard பண்ணலாம். Privacy-க்கு நல்லது. ஆனா user திரும்ப வந்தா continuity இழக்கும். எவ்வளவு நேரம் retain பண்ணுவது என்பது decision.

**3. Cost vs Latency**
In-context memory cheap to build ஆனா token cost அதிகம். External session store latency சேர்க்கும் ஆனா context window clean இருக்கும்.

**4. Consistency**
Concurrent updates வந்தா race condition வரும். Agent-ன் Working Memory single writer model இல்லனா stale state வரும். Session lock / last-write-wins தேவை.

Failure mode: Working Memory corrupt ஆனா agent hallucinates based on wrong intermediate data. Example: tool result mis-parsed and stored, next steps all wrong.

### 6. Practical Example

Enterprise support agent.

User: "என் order ID 98234 status என்ன?"
Agent DB tool call பண்ணி, status = Shipped, tracking = XYZ.

Working Memory-ல store:
```json
{
  "order_id": "98234",
  "last_topic": "order_status",
  "tracking": "XYZ",
  "user_intent": "status_check"
}
```

Next turn user: "tracking link தர முடியுமா?"
Agent Working Memory-ல order_id இருக்குறதால immediate link generate பண்ணும். History முழுவதும் search பண்ண தேவை இல்லை.

Session end ஆனதும், இந்த data discard / archive to Episodic Memory. Working Memory clean.

### 7. Reasoning Challenge

உங்க agent-க்கு 30 min session இருக்கு. User 50+ turns பேசுறான். ஒவ்வொரு turn-லயும் full history-யை context-ல வைக்க முடியாது. Working Memory-ல எதை வைப்பீங்க, எதை drop பண்ணுவீங்க? Summarization எப்போ trigger பண்ணுவீங்க? ஏன்?

### 8. Key Takeaways

* Working Memory = session-scoped, short-term scratchpad for current reasoning, not permanent storage.
* It bridges LLM statelessness and conversation continuity without bloating context window.
* Design decision: what to keep, how long to keep, how to compress, and when to discard.
* Every update to Working Memory is an architectural trade-off between freshness, cost, and noise.

இதை புரிஞ்சா agent-ன் turn-to-turn coherence ஏன் முக்கியம், எப்படி manage பண்ணுறோம் என்பது clear ஆகும்.
