# Agent evaluation

> **Learning Path:** AI Evaluation
> **Section:** 18.1.9 — Evaluation

## 1. Problem

நீங்கள் ஒரு agent-ஐ build பண்ணினீர்கள். LLM + tools + memory. Demo-ல அழகாக வேலை செய்யுது. Production-க்கு போனதும் என்ன நடக்குது?

சில queries-ல் சரியான tool-ஐ தேர்ந்தெடுக்காமல் hallucinate பண்ணுது. சில times-ல் extra steps எடுத்து latency ஆகுது. சில times-ல் correct answer வந்தாலும் reasoning path தப்பா இருக்கு.

Unit test போல agent-க்கு test எழுத முடியாது. Output subjective. Non-deterministic. Tool calls கூட dynamic.

> What goes wrong if we don't evaluate? You ship blind. Prompt change பண்ணினால் regression தெரியாது. Tool add பண்ணினால் break ஆனதும் தெரியாது. Cost எகிறும், reliability குறையும்.

Agent evaluation என்பது agent-ன் behavior-ஐ measurable ஆக்குவது.

## 2. Mental Model

Agent evaluation என்பது 3 layer-ல் பார்ப்பது:

**Output Quality** - Final answer correct ஆ?
**Behavior Quality** - Right tools use பண்ணுச்சா? Right steps-ல் வந்துச்சா?
**Operational Quality** - Latency, cost, failure rate எப்படி இருக்கு?

ஒரு distributed system-ல் நீங்கள் SLA define பண்ணுவீர்கள். Agent-க்கும் அதே மாதிரி SLA வேண்டும்.

## 3. How It Works

Evaluation-க்கு நமக்கு தேவை: **ground truth** மற்றும் **scoring function**.

Offline evaluation:
- Hand-crafted test set: input query + expected tool calls + expected final answer.
- Golden dataset create பண்ணி, agent-ஐ run பண்ணி compare பண்ணுவது.
- LLM-as-a-judge use பண்ணி semantic similarity score கொடுப்பது.

Online evaluation:
- Production traffic-ஐ shadow mode-ல் run பண்ணி real user query-க்கு agent output-ஐ log பண்ணி human review / reward model-ல் score பண்ணுவது.

Metrics:
- Task Success Rate: task complete ஆச்சா?
- Tool Call Accuracy: சரியான tool, சரியான parameters?
- Step Efficiency: தேவைக்கு அதிக steps இல்லாமல்?
- Hallucination Rate
- Latency P95, Cost per query

## 4. Architectural Reasoning

எப்போது evaluation தேவை?

Prompt change, tool change, model swap பண்ணும்போது. இது regression test போல.

Constraint அது address பண்ணுது: non-deterministic system-ல் confidence.

Alternatives:
- Manual QA only → scale ஆகாது, slow.
- Only output check → tool misuse catch ஆகாது.
- Only production monitoring → break ஆன பிறகு தான் தெரியும்.

ஆர்கிடெக்ட் choose பண்ணுவார்: offline golden set + online telemetry + LLM judge hybrid.

## 5. Trade-offs

**Golden dataset vs LLM-as-judge**
Golden dataset objective, expensive to maintain. LLM judge cheap, scalable, but itself biased.

**Offline vs Online**
Offline safe, controlled. Online real, but noisy and risky.

**Granularity**
Step-level evaluation gives root cause, costly to annotate. Output-level cheap, vague.

**Coverage**
Edge cases test பண்ண முடியும், but real world distribution shift நடக்கும்.

Failure mode: Overfitting to evaluation set. Agent evaluation set-ல் நல்ல score வாங்கி, production-ல் fail ஆகும். இது test set leakage போல.

## 6. Practical Example

Enterprise support agent: ticket resolve பண்ணும்.

Golden set: 200 real tickets with expected tool calls: `search_knowledge_base`, `fetch_user_profile`, `create_jira_ticket`.

Evaluation run:
- Success rate 78%
- 12% cases-ல் agent `create_jira_ticket` தேவையில்லாமல் call பண்ணுது → cost + noise
- Latency P95 8s

Reasoning: Agent prompt-ல் "always create ticket for ambiguity" rule இருந்தது. இது over-calling create பண்ணுது.

Fix: Prompt refine + evaluation re-run. Success rate 78% → 85%, unnecessary tool calls 12% → 3%.

Cost per query குறைந்தது, reliability ஏறியது.

## 7. Reasoning Challenge

உங்களிடம் RAG agent உள்ளது. இது retrieval + generation செய்யும். நீங்கள் embedding model upgrade பண்ணினீர்கள்.

எந்த evaluation setup வைப்பீர்கள், எந்த metrics-ஐ track பண்ணுவீர்கள், மற்றும் regression ஆனால் எப்படி தெரிந்து கொள்வீர்கள்? Reasoning செய்யுங்கள்.

## 8. Key Takeaways

- Agent evaluation என்பது output மட்டுமல்ல, tool choice, steps, cost, latency எல்லாம்.
- Offline golden set + online telemetry இரண்டும் வேண்டும்.
- LLM-as-a-judge scalable ஆனால் bias உண்டு, கலப்பு முறையில் use பண்ணுங்கள்.
- Evaluation இல்லாமல் agent-ஐ ship பண்ணுவது blind deployment.
