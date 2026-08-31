# Reflection

> **Learning Path:** Agentic AI
> **Section:** 15.2.7 — Agent patterns

### 15.2.7 — Agent patterns: Reflection

## 1. Problem

ஒரு agent-க்கு ஒரு task கொடுக்கிறீர்கள். அது reasoning பண்ணி output கொடுக்கிறது. ஆனால் அந்த output தவறாக இருக்கிறது, incomplete ஆக இருக்கிறது, அல்லது requirement-க்கு சரியாக match ஆகவில்லை.

என்ன ஆகும்?
நீங்கள் மனிதனாக இருந்தால், உங்கள் பதிலை திரும்ப பார்த்து "இது சரியா? எங்கே மிஸ் ஆகியிருக்கு?" என்று சுயமாக கேட்டுக்கொள்வீர்கள். Agent-க்கு அந்த self-check இல்லாமல், அது தான் நம்பியதை blind-ஆக return செய்யும்.

உதாரணம்: "Q3 sales report-ல் top 3 products-ஐ list பண்ணு". Agent data-வை fetch பண்ணி ஒரு list கொடுக்கிறது. ஆனால் அது Q2 data-வை எடுத்துவிட்டது. யாரும் கண்டுபிடிக்கும் வரை error உள்ளே இருக்கும்.

Reflection என்பது agent-க்கு அந்த "தன்னைத்தானே review செய்" என்ற loop-ஐ கொடுப்பது.

## 2. Mental Model

Reflection = **Agent produces → Agent critiques its own output → Agent improves**.

இது ஒரு internal critic போன்றது. Writer எழுதுகிறார், Editor படித்து திருத்துகிறார். இரண்டும் ஒரே model-ஆக இருக்கலாம், வெவ்வேறு prompt-களுடன்.

ஒரு distributed system-ல் retry/log போல, இங்கே உள்ள concept என்னவென்றால்: **first attempt is not final**.

## 3. How It Works

Basic loop:

1. **Generate**: Agent task-ஐ solve செய்து initial answer/plan தருகிறது.
2. **Reflect**: Same agent அல்லது separate critic model கேள்விகள் கேட்கிறது:
   - இந்த answer requirement-ஐ meet பண்ணுதா?
   - எந்த assumption தவறாக இருக்கிறது?
   - என்ன missing?
   - Format/logic சரியா?
3. **Revise**: Feedback-ஐ அடிப்படையாக வைத்து agent output-ஐ update செய்கிறது.
4. Iterate until quality threshold அல்லது max iterations.

இது chain-of-thought-க்கு அடுத்த step. CoT = think step by step. Reflection = think, then check your thinking.

Implementation-ல் இது பெரும்பாலும் self-prompting ஆகவே இருக்கும்: "You are a reviewer. Review the previous answer for factual errors, completeness, and alignment with the user request. Return critique and improved answer."

## 4. Architectural Reasoning

Reflection useful ஆகும் போது:
- Output quality critical ஆக இருக்கும்: code generation, report generation, legal/financial summary.
- Task ambiguous ஆக இருக்கும், multiple interpretations உள்ளன.
- Agent தனது tools-ஐ use செய்த பிறகு results inconsistent ஆக இருக்கலாம்.

இது address செய்யும் constraint: **reliability and correctness under uncertainty**.

Alternatives:
- **No reflection**: Fast, cheap, but error prone.
- **Human-in-the-loop**: Accurate ஆனால் slow, costly, non-scalable.
- **More context / better prompt**: Helps ஆனால் one-shot error-ஐ fix செய்யாது.

Architect choose reflection when cost of wrong output > cost of extra LLM calls.

## 5. Trade-offs

**Latency vs Quality**: ஒவ்வொரு reflection iteration = extra LLM call. Latency உயரும், cost உயரும். Real-time chatbot-க்கு இது கடினம்.

**Over-refinement**: Agent தன்னை திருத்திக்கொண்டே போகும். பதில் worse ஆகும். Divergence risk உண்டு.

**Self-bias**: Same model critic + generator ஆக இருந்தால், அது தனது own mistakes-ஐ detect செய்ய தவறலாம். Stronger critic model தேவைப்படலாம்.

**Operational complexity**: When to stop? Threshold எப்படி define செய்வது? max iterations, score-based stopping.

Failure mode: Reflection loop infinite loop-ல் மாட்டிக்கொள்ளும். Guardrails வேண்டும்.

## 6. Practical Example

Enterprise RAG agent: "எங்கள் Q3 sales policy-க்கு ஏற்ப discount எவ்வளவு கொடுக்கலாம்?"

Agent retrieves policy docs from vector database, generates answer.

Reflection step:
Critic: "நீ customer tier-ஐ check பண்ணினியா? Policy page 3-ல் Enterprise tier-க்கு மட்டுமே 15% limit உள்ளது. நீ 20% கொடுத்திருக்கிறாய். Also date range Q3 correct ஆ?"

Agent revises with correct tier and limit.

இங்கே reflection, retrieval error-ஐ catch செய்தது.

## 7. Reasoning Challenge

உங்களிடம் code generation agent உள்ளது. அது function generate பண்ணி unit test-கள் fail ஆனால் தானாக திருத்துகிறது. இந்த loop 3 iterations-க்குள் முடிய வேண்டும். ஆனால் சில tasks-ல் agent 3 iterations-க்குப் பிறகும் tests-ஐ pass செய்ய முடியவில்லை.

இந்த scenario-ல் reflection-ஐ எப்படி design செய்வீர்கள்? Stop condition என்ன? Cost vs correctness trade-off எப்படி manage செய்வீர்கள்?

## 8. Key Takeaways

- Reflection = self-critique and revise loop. Quality-க்காக latency/cost-ஐ trade செய்வது.
- First attempt is not final. Architecturally, generate → critique → revise என்பது core pattern.
- Same model-ஆக இருந்தால் bias உண்டு. Separate critic model அல்லது stronger verifier பயனுள்ளது.
- Stop condition, max iterations, and cost guardrails இல்லாமல் reflection production-ல் வேலை செய்யாது.
