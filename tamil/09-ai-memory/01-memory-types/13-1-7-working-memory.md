# Working memory

> **Learning Path:** AI Memory
> **Section:** 13.1.7 — Memory types

### 1. Problem

ஒரு LLM agent-ஐ நீங்கள் build பண்ணுகிறீர்கள். User-க்கு conversation நடக்கிறது. 
Session-இல் user சொன்னது: "என்னோட budget 5 லட்சம்", "Bangalore-ல வீடு வேண்டும்", "2 BHK".

Agent-ஐ அடுத்த turn-ல் கேட்டால் "நீங்க எங்கே வீடு வேண்டும்?" என்று கேட்கிறது. ஏன்? Because model-க்கு context window மட்டுமே தெரியும். Long conversation-ல் முந்தைய தகவல் slide out ஆகிவிடும்.

இன்னொரு பிரச்சனை: ஒரே session-இல் real-time reasoning செய்ய வேண்டும். ஒரு math problem solve பண்ணும்போது intermediate steps-ஐ தற்காலிகமாக வைத்திருக்க வேண்டும். அதை எங்கே வைப்பது? Database-ல் போட்டால் slow, prompt-ல் வைத்தால் context window நிரம்பும்.

Working memory என்பது இந்த பிரச்சனைக்கான பதில்.

### 2. Mental Model

Working memory = Agent-ன் short-term scratchpad.

அது session-க்கு மட்டும் தேவையான, தற்காலிகமான தகவல்களை வைத்திருக்கும். Like human working memory.

Long-term memory என்பது durable knowledge store: vector DB, knowledge graph, RAG index. 
Working memory என்பது ephemeral, fast, in-session.

Analogy: நீங்கள் ஒரு meeting-ல் இருக்கிறீர்கள். Notebook-ல் meeting notes எடுக்கிறீர்கள் - அது working memory. Meeting முடிந்த பிறகு அதை filing cabinet-ல் file பண்ணினால் அது long-term memory.

### 3. How It Works

Agent ஒரு turn process பண்ணும்போது:

1. Input: user message + conversation history
2. Working memory-ல் இருந்து relevant facts load ஆகும்
3. Model reasoning செய்யும். Intermediate thoughts, plan, tool results, temporary variables எல்லாம் working memory-க்குள் write ஆகும்
4. Output generate ஆகும்

Implementation வகைகள்:
- **In-context working memory**: System prompt + conversation history + scratchpad inside context window. Simple, but token limit உள்ளது.
- **External working memory**: Session store in Redis / in-memory DB. Structured key-value. Agent ஒவ்வொரு turn-க்கும் read/write செய்யும். Faster than DB, persistent across turns.
- **Agent-specific buffer**: ReAct, Chain-of-Thought style. Model-ன் own internal reasoning tokens. Ephemeral to that single turn.

முக்கியம்: Working memory should be fast, mutable, and discardable. Durability தேவையில்லை.

### 4. Architectural Reasoning

Working memory தேவைப்படும் போது:
- Multi-turn conversation-ல் user intent தொடர்ச்சியாக இருக்க வேண்டும். Budget, location போன்ற slots fill பண்ண வேண்டும்.
- Complex task-ல் multi-step planning: agent plan -> execute -> observe -> revise. Plan-ஐ எங்கே வைக்கிறது?
- Tool use-ல் intermediate results-ஐ keep பண்ண வேண்டும். API call result-ஐ next step-க்கு use பண்ண வேண்டும்.
- Real-time personalization: current session-ன் tone, preferences.

Alternatives:
- Just rely on context window: Simple but expensive, token blow up, limited to ~128k tokens, no structured access.
- Push everything to long-term memory: Slow, over-persistent, session-specific noise long-term DB-ல் குப்பை ஆகும்.

Architectural decision: Session-scoped memory store with TTL. Redis with key `session:{id}:working`. Structure: `facts`, `plan`, `tool_state`, `scratch`.

### 5. Trade-offs

**Speed vs Durability**: Working memory fast, in-memory. Data loss ஆனால் பரவாயில்லை. Session restart ஆனால் rebuild பண்ணலாம். Long-term memory slow but durable.

**Context size vs Coherence**: Working memory-ல் too much info வைத்தால் context pollution. Relevant மட்டும் keep பண்ண வேண்டும். Summarization / eviction policy தேவை.

**Consistency vs Latency**: External working memory-க்கு read/write ஒவ்வொரு turn-லும் செய்ய வேண்டும். Latency add ஆகும். In-context மட்டும் வைத்தால் model latency மட்டும்.

Failure modes:
- Memory leak: session data accumulate ஆகி never expire ஆகும். Cost & privacy issue.
- Stale facts: User "budget 5L" என்று சொல்லி பிறகு "budget 7L" என்று change செய்தார். Working memory-ல் old value overwrite ஆகவில்லை என்றால் hallucination.
- Cross-session contamination: Session A-ன் working memory Session B-க்கு leak ஆகும்.

### 6. Practical Example

RAG-based real estate agent.

User: "Bangalore-ல 2 BHK வேண்டும்"
Agent working memory-ல்:
```
{
  "intent": "buy_home",
  "location": "Bangalore",
  "bedrooms": 2,
  "budget": null,
  "stage": "collecting_requirements"
}
```

Next turn: User: "budget 5 லட்சம் மாத rental"
Agent updates working memory: budget = 50000, stage = "searching"

Agent plan in working memory:
1. Search listings with filters
2. Call price check API
3. Summarize top 3

Tool result வந்த பிறகு, agent working memory-ல் `search_results` வைக்கும். அடுத்த turn-ல் user கேட்டால் மீண்டும் search செய்யாமல் அதே results-ஐ use பண்ணும்.

Session end ஆனதும் working memory expire ஆகும். User-ன் long-term preferences மட்டும் long-term memory-க்கு promote ஆகும்: "prefers Bangalore, 2 BHK".

### 7. Reasoning Challenge

உங்கள் agent-க்கு 30 min session timeout உள்ளது. ஒரு user 25 turns பேசியுள்ளார். Context window 80% நிரம்பியுள்ளது. Working memory-ல் 200+ facts accumulate ஆகியுள்ளன. Performance degrade ஆகிறது.

என்ன செய்வீர்கள்? Working memory-ல் எதை keep பண்ணுவீர்கள், எதை discard / summarize பண்ணுவீர்கள்? ஏன்?

### 8. Key Takeaways

- Working memory = session-scoped, ephemeral scratchpad for in-flight reasoning, not durable knowledge.
- இது long-term memory-ஐ replace செய்யாது, complement செய்கிறது.
- Speed, mutability, and bounded size தான் முக்கிய design constraints.
- Every write to working memory needs an eviction / summarization policy, இல்லை என்றால் context pollution ஆகும்.
- Architectural choice: in-context vs external session store. Trade-off latency vs control.
