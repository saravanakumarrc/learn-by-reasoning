# Planner/executor

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.9 — LLM patterns

## 1. Problem

ஒரு complex task கொடுத்தால் LLM ஒரே முறையில் சரியாக solve பண்ணுமா?

உதாரணமா: "நம்ம customer-ன் last 6 months order history எடுத்து, return pattern analyze பண்ணி, அதுக்கு ஏத்த மாதிரி personalized email draft பண்ணு, அதை CRM-ல save பண்ணு."

ஒரே prompt-ல LLM-க்கு கொடுத்தால் என்ன நடக்கும்?
- Tool call-கள் தப்பாகும், parameter missing ஆகும்
- Reasoning skip ஆகும், hallucination வரும்
- Multi-step dependency தெளிவாக தெரியாது
- Error ஆனால் recover பண்ண முடியாது

Pain point: LLM ஒரு general problem solver, ஆனால் **plan பண்ணி step-by-step execute பண்ண தெரியாது**. அதனால் agent-கள் flaky ஆக இருக்கு.

## 2. Mental Model

Planner/executor pattern என்பது ஒரு team போல நினைக்கவும்.

**Planner** = Architect. என்ன problem, என்ன steps தேவை, என்ன tools தேவை, என்ன order-ல செய்யணும் என்பதை plan பண்ணும்.

**Executor** = Engineer. Planner கொடுத்த plan-ஐ பார்த்து, ஒவ்வொரு step-ஐயும் faithfully execute பண்ணும். Tool call பண்ணும், data fetch பண்ணும்.

இரண்டும் ஒரே LLM ஆக இருக்கலாம், ஆனால் different prompt / different role-ல run ஆகும். அல்லது different model-கள்.

Key idea: **Planning and execution are separate concerns.**

## 3. How It Works

Flow எளிமையா இருக்கும்:

1. User request வரும்
2. Planner LLM-க்கு கொடுக்கப்படும்: "Given task, available tools, constraints, generate a step-by-step plan"
3. Plan output JSON / structured format-ல வரும்: steps, dependencies, required inputs/outputs
4. Executor loop ஓடும்:
   - Step 1 execute, result validate
   - Result-ஐ next step-க்கு pass பண்ணு
   - Fail ஆனால் error handling / replanning trigger
5. Final result compile ஆகும்

Planner ஒரு முறை மட்டும் plan பண்ணலாம், அல்லது execution-ல தடங்கல் வந்தால் replan பண்ணலாம்.

## 4. Architectural Reasoning

எப்போ இது useful?

- Task 3+ steps, multiple tools தேவைப்படும் போது
- Steps-க்கு இடையே data dependency இருக்கும் போது
- Retry, error recovery தேவைப்படும் போது
- Auditability வேண்டும் போது - plan-ஐ log பண்ணலாம்

Alternative என்ன?
- **ReAct**: Think-Act loop ஒரே model-ல. Simple, fast, ஆனால் long task-ல drift ஆகும்.
- **Chain of Thought**: Single shot reasoning. Simple tasks-க்கு fine.
- **Router**: Task type பார்த்து tool-க்கு route பண்ணும். Planning இல்லை.

Planner/executor choose பண்ணுவது ஏன்?
Complex, non-deterministic workflow-ல **control** வேண்டும். Planner gives you visibility into *what will happen before it happens*. Debugging எளிது.

Trade-off: Latency அதிகம், cost அதிகம். Two LLM calls minimum.

## 5. Trade-offs

**Pros:**
- Better accuracy for multi-step tasks
- Clear separation, plan-ஐ review / human approve பண்ணலாம்
- Failure isolation. ஒரு step fail ஆனால் மறுபடியும் அதே step-ஐ மட்டும் retry பண்ணலாம்

**Cons / Failure modes:**
- Planner hallucinate பண்ணி invalid plan தரலாம். Executor blindly follow பண்ணும்.
- Plan rigid ஆக இருக்கும். Mid-execution new information வந்தால் adapt செய்ய முடியாது. அதனால் replanning logic தேவை.
- Latency + cost double. Planner + Executor.
- Plan validation தேவை. இல்லை என்றால் executor தவறான tool-ஐ call பண்ணும்.

முக்கிய trade-off: **Control vs Simplicity**. ReAct simple ஆனால் control குறைவு. Planner/executor control அதிகம் ஆனால் complexity அதிகம்.

## 6. Practical Example

Enterprise support agent.

User: "என்னுடைய last invoice-ஐ refund பண்ணுங்க. Amount $120. Reason: duplicate charge."

Planner output:
1. Authenticate user from session
2. Fetch last 3 invoices from billing API
3. Identify invoice with duplicate charge flag
4. Validate refund eligibility via policy checker
5. Create refund request in payment service
6. Send confirmation email

Executor ஒவ்வொரு step-ஐயும் run பண்ணும். Step 3-ல duplicate கண்டுபிடிக்க முடியலை என்றால், executor error-ஐ planner-க்கு திருப்பி அனுப்பி replan பண்ண சொல்லும்: "Check last 6 invoices instead".

இப்படி plan visible ஆக இருப்பதால் compliance team-க்கு audit trail கொடுக்க முடியும்.

## 7. Reasoning Challenge

உங்களுக்கு RAG based research agent இருக்கு. Task: "Competitor A and B-ன் last quarter pricing strategy-ஐ compare பண்ணி report தரவும்."

Tools: web search, internal vector DB, spreadsheet API.

Planner ஒரு plan தந்தது:
1. Search web for Competitor A pricing
2. Search web for Competitor B pricing
3. Fetch internal sales data
4. Generate report

என்ன problem இருக்கு இந்த plan-ல? நீங்கள் plan-ஐ எப்படி மாற்றுவீர்கள்? Execution failure-ஐ எப்படி handle பண்ணுவீர்கள்?

## 8. Key Takeaways

- Planner = what to do and in what order. Executor = do it faithfully.
- Multi-step, tool-heavy tasks-க்கு planning முக்கியம், ReAct போதாது.
- Plan-ஐ validate செய்யாமல் executor-க்கு கொடுத்தால் garbage in garbage out.
- Every plan creates rigidity. Replanning mechanism must exist.
- Control, auditability, reliability கிடைக்கும், cost and latency விலை கொடுக்க வேண்டும்.
