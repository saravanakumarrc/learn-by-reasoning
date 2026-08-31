# Supervisor

> **Learning Path:** Agentic AI
> **Section:** 15.2.5 — Agent patterns

## 1. Problem

உங்களுக்கு ஒரு complex task வருது. உதாரணமா: "ஒரு customer complaint-க்கு root cause கண்டுபிடிச்சு, related orders-ஐ list பண்ணி, refund eligible-ன்னு check பண்ணி, summary generate பண்ணு".

ஒரே agent இதை முழுசா செய்ய முயற்சி செய்தால் என்ன ஆகும்?

Context window explode ஆகும். Tool use தப்பும். Reasoning shallow ஆகும். ஒரு step-ல தோல்வி ஆனால் முழு task fail.

இப்போ problem என்ன? **Single agent-க்கு ஒரே நேரத்தில் பல வேலைகள், பல திறன்கள் தேவைப்படுது.** அது brittle ஆகிடும்.

இதை தீர்க்க engineers உருவாக்கியது தான் Supervisor pattern.

## 2. Mental Model

Supervisor pattern என்பது **ஒரு manager + பல specialists**.

Manager என்பவன் task-ஐ புரிந்து கொண்டு, அதை sub-tasks-ஆக break பண்ணி, சரியான specialist agent-க்கு delegate பண்ணி, results-ஐ orchestrate பண்ணி final answer திருப்புவான்.

உதாரணம்: Hospital-ல Head Doctor supervisor மாதிரி. அவர் diagnosis பண்ணுவது இல்லை. Radiologist, Pathologist, Cardiologist போன்ற specialists-க்கு refer பண்ணுவார். Results வந்ததும் அவர் ஒரு plan உருவாக்குவார்.

Agent-லயும் அதே.

Supervisor = orchestrator with routing logic.
Worker agents = focused, single responsibility.

## 3. How It Works

Flow simple:

1. **Input** வரும். Supervisor LLM context-ஐ பார்த்து intent extract பண்ணும்.
2. **Decomposition**: Task-ஐ smaller steps ஆக split பண்ணும். 
3. **Routing**: எந்த worker-க்கு எந்த sub-task போகும் என்பதை decide பண்ணும். Static mapping or dynamic LLM-based routing.
4. **Delegation**: Sub-task + relevant context worker-க்கு அனுப்பும்.
5. **Aggregation**: Worker outputs வந்ததும், supervisor அதை combine / validate / refine பண்ணி final response கொடுக்கும்.
6. **Loop**: தேவைப்பட்டால் clarify கேட்கும் அல்லது re-delegate பண்ணும்.

Supervisor-க்கு tools வேண்டாம். அவனுக்கு தேவை routing logic, state tracking, context summarization.

Worker agents-க்கு தான் tools இருக்கும்: database query, web search, code execution, RAG retrieval, API call.

## 4. Architectural Reasoning

Supervisor pattern useful ஆகும் போது:

* **Task multi-step ஆக இருக்கும்** மற்றும் steps independent ஆக இருக்கும்.
* Different expertise தேவைப்படும். உதாரணமா data extraction, analysis, summarization.
* Error isolation தேவை. ஒரு worker fail ஆனாலும் மற்றவை தொடரும்.
* You want reusability. Same workers can be used by multiple supervisors.

Alternatives என்ன?

* **Single Agent with tools**: Simple tasks-க்கு fine. Complexity grow ஆனதும் hallucination, tool misuse அதிகம்.
* **Chain / Sequential agents**: Task fixed order-ல இருந்தால் work ஆகும். ஆனால் dynamic routing இல்லை.
* **Parallel agents**: All agents run together, no coordination. Supervisor இல்லாமல் integration messy.

Supervisor-ஐ choose பண்ணுவது என்பது **coordination cost-ஐ accept பண்ணி, specialization benefit எடுப்பது.**

## 5. Trade-offs

**Pros:**
* Clarity and maintainability. ஒவ்வொரு agent-க்கும் clear responsibility.
* Better performance. Specialist agents smaller prompt, less context, faster.
* Fault tolerance. ஒரு worker fail ஆனால் supervisor retry / alternative route பண்ணலாம்.

**Cons / Trade-offs:**
* **Latency increases**. Sequential delegation + aggregation = more round trips.
* **Supervisor is bottleneck**. Routing logic தப்பானால் முழு system தப்பும். Supervisor பலவீனமானால் system brittle ஆகும்.
* **Complexity in state management**. Multi-agent conversation state-ஐ track பண்ண வேண்டும்.
* **Cost**. More LLM calls = more token cost.

Important failure modes:

* Supervisor over-delegates: unneeded workers call பண்ணி cost waste.
* Supervisor under-delegates: worker-க்கு போதுமான context இல்லாமல் போகும்.
* Feedback loop missing: worker output bad என்பதை supervisor detect பண்ண தவறினால் garbage in garbage out.

## 6. Practical Example

Enterprise support agent.

Supervisor: Support Orchestrator

Workers:
1. Ticket Classifier - intent classify
2. Order Lookup Agent - DB query
3. Policy Checker Agent - refund/return eligibility
4. Summarizer Agent - final customer-friendly reply

Customer message: "My order #12345 didn't arrive, can I get refund?"

Supervisor steps:
* Classify -> Order Lookup
* Lookup result + policy -> Policy Checker
* All results -> Summarizer

If order not found, supervisor re-ask customer for details instead of failing.

Here supervisor never talks to DB directly. Workers own tools.

## 7. Reasoning Challenge

உங்களிடம் ஒரு financial analysis agent இருக்கு. Tasks: stock data fetch, news sentiment analyze, risk score compute, investment recommendation generate.

நீங்கள் Supervisor pattern use பண்ணினால் எந்த sub-tasks-ஐ separate workers ஆக்குவீர்கள்? Supervisor எப்போது parallel run பண்ணலாம், எப்போது sequential ஆக இருக்க வேண்டும்?

நீங்கள் Supervisor-ஐ ஒரு single LLM-ல build பண்ணினால், routing தப்பாகும் risk எப்படி குறைப்பீர்கள்?

## 8. Key Takeaways

* Supervisor = coordinator, not worker. அவன் task decompose + route + aggregate பண்ணுவான்.
* Pattern உருவானது single agent brittleness-க்கு பதில். Specialization + coordination.
* Latency, cost, supervisor bottleneck என்பது main trade-offs.
* Use it when task complex, multi-domain, and failure isolation முக்கியம்.

இதை புரிந்து கொண்டால், agent system-ஐ design பண்ணும் போது **who decides, who does** என்பதை தெளிவாக பிரிக்க முடியும்.
