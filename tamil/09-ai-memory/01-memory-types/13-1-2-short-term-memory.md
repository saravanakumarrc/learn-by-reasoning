# Short-term memory

> **Learning Path:** AI Memory
> **Section:** 13.1.2 — Memory types

## 1. Problem

ஒரு LLM agent-ஐயோ, AI system-ஐயோ build பண்ணும்போது ஒரு basic pain point வரும்.

User இப்போ என்ன சொன்னார், அதுக்கு முன்னாடி என்ன சொன்னார், இந்த conversation-ல overall goal என்ன — இதை மறந்துட்டா agent எப்படி coherent-ஆ பேசும்?

Short-term memory இல்லாமல் ஒவ்வொரு turn-உம் isolated-ஆ தெரியும். User "அதை" என்று சொன்னால், "அது" எது என்று தெரியாது. Context window-ல data இருக்கும், ஆனால் *actively hold* பண்ணி reasoning-ல use பண்ணுவது வேறு.

**What goes wrong if we don't have this?** Hallucination, repetition, context loss, user frustrate ஆகிறார். Agent ஒவ்வொரு முறையும் from scratch start ஆகும்.

## 2. Mental Model

Short-term memory = **working memory**. இது ஒரு session-க்குள், ஒரு task-க்குள் நடக்கும் சமீபத்திய context-ஐ hold பண்ணி, next step-க்கு use பண்ணும் mechanism.

அனாலஜி: நீங்கள் ஒரு phone call-ல் பேசும்போது கடைசி 2-3 minutes மட்டும் தான் உங்கள் head-ல active-ஆ இருக்கும். அதை வைத்து தான் respond பண்ணுவீர்கள். Long-term memory என்பது notes app, short-term என்பது உங்கள் working table top.

## 3. How It Works

Practically, short-term memory என்பது 3 sources-இன் combination:

1. **Context window / conversation history**: Last N turns of chat. LLM இயற்கையாகவே இதை attend பண்ணும்.
2. **Working state**: Agent loop-ல் current goal, plan, intermediate results, last action output. இது session state-ஆ memory-ல hold ஆகும்.
3. **Buffer / scratchpad**: LLM reasoning steps, temporary calculations, tool outputs இப்போதைக்கு hold பண்ணும் place.

Implementation-ல இது usually:
* in-memory store for session
* session state in Redis / in-process cache
* or simply sliding window of messages passed to LLM

Key point: இது **ephemeral, fast, limited**. Long-term memory போல persistent இல்லை.

## 4. Architectural Reasoning

Short-term memory useful ஆகும் போது:
* Multi-turn conversation where coherence முக்கியம்
* Agent multiple tools use பண்ணி step-by-step task solve பண்ணும் போது
* User intent evolve ஆகும், clarification தேவைப்படும் போது

Constraint it addresses: LLM-க்கு stateless nature. Every request independent. Short-term memory state-ஐ inject பண்ணி stateless-ஐ stateful-ஆ மாற்றும்.

Alternatives:
* **Only context window**: Simple, but token cost high, history truncate ஆகும், long session-ல degrade ஆகும்
* **Full retrieval every turn**: Slow, noisy, irrelevant info கலக்கும்
* **State machine**: Deterministic, but flexible இல்லை

Architect choose பண்ணுவார் when latency low வேண்டும், session duration short, and coherence critical.

## 5. Trade-offs

1. **Recency vs. Completeness**: Recent context மட்டும் keep பண்ணினால் speed high, ஆனால் important earlier detail loss ஆகும். Window size increase பண்ணினால் cost + latency increase.
2. **Memory pollution**: Bad short-term memory = bad next response. Wrong state hold பண்ணினால் error propagate ஆகும். Need clear state reset / summarization.
3. **Stateless scaling vs. session affinity**: Short-term memory keep பண்ண session sticky ஆக வேண்டியிருக்கும். Horizontal scale செய்யும்போது session store share பண்ண வேண்டும்.
4. **Privacy & cost**: Conversation history memory-ல வைத்திருப்பது data retention issue கொண்டு வரும். How long to keep? When to evict?

Failure mode: Context window overflow ஆனால் important info truncate ஆகும். Agent முன்பு சொன்ன commitment-ஐ மறக்கும். User trust போய்விடும்.

## 6. Practical Example

Enterprise support agent.

User: "எனக்கு Bangalore office-க்கு travel request create பண்ணுங்க"
Agent: dates கேட்கிறது
User: "15-17 Dec"
Agent: budget கேட்கிறது
User: "50k"

இங்கே short-term memory இல்லாமல், 3rd turn-ல agent "எந்த office?" என்று திரும்ப கேட்கும்.

Architecture: Session ID -> Redis hash with keys: `current_goal`, `collected_params`, `last_tool_output`. Every turn, agent fetches session state, merges with last 4 messages, calls LLM. LLM output-ஐ parse பண்ணி state update பண்ணும்.

இதனால் agent coherent-ஆ தொடர முடியும். Session end ஆனதும் memory evict ஆகும்.

## 7. Reasoning Challenge

உங்கள் agent 30 min conversation நீளும். User ஆரம்பத்தில் company policy பற்றி கேட்டார், பிறகு travel request பற்றி பேசினார். இப்போது user "அந்த policy-ஐயும் travel request-ல apply பண்ணுங்க" என்கிறார்.

Context window-ல policy mention இல்லை, truncate ஆகிவிட்டது. Short-term memory-ல current task மட்டும் இருக்கிறது.

இங்கே என்ன problem வரும்? Short-term memory மட்டும் போதுமா? என்ன add பண்ணுவீர்கள்?

## 8. Key Takeaways

* Short-term memory = session-க்குள் active working context, coherence-க்கு அவசியம்
* இது fast, ephemeral, limited. Long-term memory-க்கு complement
* Window size, state management, eviction policy ஆகியவை trade-offs தரும்
* ஒவ்வொரு architectural solution create another trade-off — இங்கே complexity, latency, cost vs coherence
