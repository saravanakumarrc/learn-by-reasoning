# Procedural memory

> **Learning Path:** AI Memory
> **Section:** 13.1.6 — Memory types

## 1. Problem

நீங்க ஒரு AI agent build பண்றீங்க. அது ஒவ்வொரு முறையும் task செய்யும்போது reasoning-ல இருந்து ஆரம்பிக்கிறது. ஒரு முறை கத்துக்கிட்ட skill-ஐ next time மறந்துட்டு மறுபடியும் step-by-step think பண்ணுது.

உதாரணமா, ஒரு data pipeline-ல file-ஐ validate பண்ணி, clean பண்ணி, load பண்ணும் workflow. முதல் முறை agent 10 steps யோசிச்சு செய்யுது. இரண்டாவது முறை அதே file type வந்தாலும் மறுபடியும் 10 steps யோசிக்குது.

இங்கே என்ன problem? **Latency, cost, and inconsistency**. ஒவ்வொரு முறையும் reasoning cost வருது, slow ஆகுது, தப்பு வாய்ப்பு அதிகம்.

இதுக்கு தான் procedural memory தேவை.

## 2. Mental Model

Procedural memory = **how to do things, not what things are**.

Declarative memory என்பது facts, knowledge. "இந்த customer-க்கு credit limit 1L" என்பது fact.

Procedural memory என்பது skill. "credit check எப்படி பண்ணனும்", "payment retry எப்படி handle பண்ணனும்", "invoice generate பண்ணும் steps".

மனுஷனுக்கு procedural memory என்பது riding a bike. நீங்க ஒவ்வொரு முறையும் physics calculate பண்ண மாட்டீங்க. Body automatically knows.

AI-ல அதே வேணும். Learned behavior pattern-ஐ store பண்ணி, next time direct execution.

இது basically learned policy, not retrieved fact.

## 3. How It Works

Procedural memory AI-ல usually மூன்று வழிகளில் store ஆகும்:

**1. Parameter memory**
Model weights-லேயே skill embed ஆகும். Fine-tuning or RLHF மூலம். மாடல் அந்த pattern-ஐ internalize பண்ணிக்கும். இது implicit procedural memory.

**2. Skill library / Tool patterns**
Pre-defined reusable workflows. Ex: `validate_and_load_csv`, `retry_with_backoff`. Agent இதை call பண்ணும். இது explicit procedural memory.

**3. Traces / Replays**
Past successful execution traces-ஐ store பண்ணி, next time similar context-ல அதை template ஆக use பண்ணுவது. இது case-based procedural memory.

Key point: Procedural memory is **action-oriented**. Input → Action sequence → Output. Context match ஆனால் action repeat பண்ணு.

## 4. Architectural Reasoning

எப்போது procedural memory useful?

* Repetitive tasks with stable steps
* Low latency தேவைப்படும் automation
* Human-like skill acquisition வேண்டும்
* Reasoning cost-ஐ குறைக்க வேண்டும்

உதாரணமா, RAG system-ல query rewrite பண்ணும் skill. முதல் முறை LLM யோசிச்சு rewrite செய்யும். அந்த successful rewrite pattern-ஐ procedural memory-ல store பண்ணி, same query type வந்தால் direct apply பண்ணலாம்.

Alternatives:
* Pure prompt engineering: ஒவ்வொரு முறையும் instruction கொடு. Costly, inconsistent.
* Episodic memory only: past conversation-ஐ retrieve பண்ணி reuse பண்ணு. Similar but not generalized skill.

Procedural memory choose பண்ணுவது என்பது **reasoning-ஐ amortize பண்ணுவது**. Expensive thinking ஒரு முறை, reuse பல முறை.

## 5. Trade-offs

**Speed vs Flexibility**
Procedural memory fast, but rigid. Novel situation வந்தால் fail ஆகும். Too much proceduralization = overfitting.

**Learning vs Stability**
Weights-ல procedural memory store பண்ணினால், update hard. Catastrophic forgetting வரும். Skill library approach-ல version control easy, but maintenance overhead.

**Transparency vs Performance**
Parameter memory black box. Skill library explicit, auditable, but less fluid.

**Failure mode:** Stale procedure. Business rule மாறியும் agent பழைய steps-ஐ follow பண்ணும். Procedural memory needs invalidation signal, just like cache.

## 6. Practical Example

Enterprise support agent.

Problem: Customer password reset request வந்தால், agent எப்போதும் இதே flow follow பண்ணும்:
1. Identity verify
2. Check account lock status
3. Send OTP
4. Reset password
5. Log audit

முதல் முறை agent reasoning மூலம் இதை discover பண்ணும். அதன் trace-ஐ procedural memory-ல store பண்ணு.

Next time similar intent detect ஆனால், agent direct `password_reset_procedure` skill-ஐ invoke பண்ணும். Reasoning skip.

If new compliance rule வந்து step 2.5 add ஆகணும் என்றால், skill library-ல procedure update பண்ணு. All future executions reflect.

இங்கே episodic memory என்ன பண்ணும்? Specific customer past interaction-ஐ recall பண்ணும். Semantic memory என்ன பண்ணும்? Password policy fact-ஐ recall பண்ணும். Procedural memory என்ன பண்ணும்? **How to execute reset**.

## 7. Reasoning Challenge

உங்களிடம் ஒரு financial reconciliation agent உள்ளது. ஒவ்வொரு நாளும் 5000 transactions reconcile பண்ண வேண்டும். முதல் முறை agent rules-ஐ learn பண்ணி சரியா reconcile பண்ணியது. நாள் தோறும் data pattern மாறிக்கொண்டே இருக்கிறது, ஆனால் core logic same.

நீங்கள் procedural memory-ஐ எப்படி design பண்ணுவீர்கள்? Weights-ல embed பண்ணுவீர்களா? Skill library-ல store பண்ணுவீர்களா? Trace replay use பண்ணுவீர்களா? ஏன்?

## 8. Key Takeaways

* Procedural memory = **how to do**, not **what is**. Skill, not fact.
* Reasoning cost-ஐ amortize பண்ண, repeatable tasks-க்கு essential.
* Parameter memory implicit ஆக fast, ஆனால் update கடினம். Skill library explicit ஆக controllable.
* Every procedure needs invalidation. Stale skill என்பது silent failure.
* Architecturally, procedural memory separates learning phase from execution phase.
