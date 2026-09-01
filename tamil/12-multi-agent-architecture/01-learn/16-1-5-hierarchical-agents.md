# Hierarchical agents

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.5 — Learn

## 1. Problem

ஒரே agent-க்கு எல்லா வேலையும் கொடுத்துட்டா என்ன ஆகும்?

உதாரணமா, ஒரு customer support agent. User கேட்கிறான்: "என் last order எங்க இருக்கு, return பண்ணணும், refund எப்ப வரும்?"

ஒரு single agent இதுக்கு:
- order database-ஐ query பண்ணனும்
- shipping carrier API-யை call பண்ணனும்
- return policy-யை புரிஞ்சுக்கனும்
- refund workflow-ஐ trigger பண்ணனும்
- user-க்கு சரியா explain பண்ணனும்

இது ஒரே context window-ல overfit ஆகும். Latency அதிகம், error rate அதிகம், reasoning குழம்பும். ஒரு தப்பு ஆனா முழு request-ம் fail.

இங்கே problem என்ன? **Scope too broad, responsibility too many, failure blast radius பெருசு.**

## 2. Mental Model

Hierarchical agents = **Manager - Worker model**.

Top-level ஒரு **orchestrator / coordinator agent**. அது problem-ஐ புரிஞ்சுக்கும், sub-tasks ஆக break down பண்ணும், specialized agents-க்கு delegate பண்ணும், results-ஐ synthesize பண்ணி final answer கொடுக்கும்.

ஒரு company மாதிரி நினைச்சுக்கோ. CEO strategy decide பண்ணுவார், department heads execute பண்ணுவார்கள். CEO எல்லா code-உம் எழுத மாட்டார்.

## 3. How It Works

Flow ரொம்ப simple:

1. **Router / Planner Agent** request-ஐ receive பண்ணும்
2. Intent classify பண்ணி task decomposition பண்ணும்
   > "order status" → Inventory Agent, "return" → Returns Agent, "refund timeline" → Finance Agent
3. Sub-agents-க்கு context + constraints கொடுத்து parallel / sequential ஆக call பண்ணும்
4. Results collect பண்ணி consistency check பண்ணும்
5. User-க்கு coherent response synthesize பண்ணும்

Sub-agents என்பது domain-specific. Inventory agent-க்கு தெரிந்தது database query மட்டும். Returns agent-க்கு தெரிந்தது policy engine மட்டும்.

Communication usually message passing வழியா. Tools, memory, and output schema standardized இருக்கும்.

## 4. Architectural Reasoning

இது எப்போ useful?

* **Complexity high:** ஒரு request-ல 3+ different domains mix ஆகுது
* **Different skill sets:** Retrieval தேவைப்படும் agent, reasoning தேவைப்படும் agent, action தேவைப்படும் agent
* **Latency & scalability:** Specialized agents-ஐ independent ஆக scale பண்ணலாம். Inventory agent heavy load பார்க்குதுன்னா அதை மட்டும் scale பண்ணு
* **Failure isolation:** Returns agent fail ஆனாலும் order status agent still work பண்ணும்

Alternatives:
* **Flat multi-agent:** எல்லா agents-ம் directly user-க்கு talk பண்ணும். Coordination chaos.
* **Single monolithic agent:** Simple tasks-க்கு ok, but brittle and expensive
* **Pipeline:** Fixed order, no dynamic delegation

Architect ஏன் choose பண்ணுவார்? **Separation of concerns + reusability.** ஒரு specialized agent-ஐ வேறு workflow-ல reuse பண்ணலாம்.

## 5. Trade-offs

**Complexity ↑**: Orchestration logic, state management, error handling between layers வேண்டும்

**Latency ↑**: Sequential delegation-ல hop count அதிகம். Parallelize பண்ணினாலும் coordination overhead இருக்கும்

**Observability hard:** End-to-end trace பண்ணனும். Which sub-agent failed? Partial success எப்படி handle?

**Cost ↑:** Multiple LLM calls. Token usage அதிகம். Smart routing and caching தேவை

**Failure modes:** Manager agent-இன் bad decomposition = wrong results. Sub-agent hallucination-ஐ manager filter பண்ணனும்

## 6. Practical Example

Enterprise RAG agent system.

Top **Orchestrator Agent** = Query understanding

User: "Q3 sales dropped in Chennai, why?"

Orchestrator decompose:
* Sales Agent → vector DB / SQL ல Q3 Chennai sales data retrieve
* Market Agent → competitor news, economic indicators retrieve
* Product Agent → product mix, returns data retrieve

ஒவ்வொரு agent-ம் தனக்கான tools மட்டும் use பண்ணும். Orchestrator results-ஐ combine பண்ணி: "Sales drop 18%, mainly due to competitor discount + monsoon impact on logistics. Top product returns increased."

இங்கே single agent 3 different data sources + reasoning செய்ய முயற்சித்தால் context pollution ஆகும். Hierarchy-ல் clarity வரும்.

## 7. Reasoning Challenge

உங்களிடம் 20 consumers-க்கு personalized onboarding flow வேண்டும். ஒவ்வொரு user-க்கும் 5 steps: profile collect, preference quiz, recommendation generate, email send, follow-up schedule.

ஒரே agent எல்லா user-க்கும் handle பண்ண முடியாது. Throughput வேண்டும், steps consistent ஆக இருக்கணும், ஒரு step fail ஆனாலும் மற்ற step continue ஆகணும்.

இங்கே hierarchical design எப்படி இருக்கும்? Manager agent என்ன செய்யும், worker agents என்ன? ஏன் இது flat design-ஐ விட better?

## 8. Key Takeaways

* Hierarchical agents = decomposition for complexity, not just scaling
* Manager decides what, workers decide how
* Trade-off is coordination overhead vs. specialization and reliability
* Use when tasks are multi-domain, failure isolation முக்கியம், reuse வேண்டும்
