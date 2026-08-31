# Human approval

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.1.12 — Learn

## 1. Problem

உங்கள் AI agent-க்கு tool calling capability கொடுத்திருக்கீங்க. அது database-ல data update பண்ணும், payment initiate பண்ணும், email அனுப்பும், production config மாற்றும்.

ஒரு user சொல்றார்: *"என் மாத வரவு செலவு report-ஐ முதலாளிக்கு மெயில் பண்ணு"*

Agent என்ன பண்ணும்? அது report-ஐ தயார் பண்ணி மெயில் அனுப்பிவிடும்.

இப்போ user தவறுதலாக சொல்றார்: *"என் அக்கவுண்டிலிருந்து 5 லட்சம் ரூபாய் என் நண்பனுக்கு மாற்று"*

Agent அப்படியே transfer பண்ணிட்டா? அல்லது user hallucinate பண்ணி சொல்லிட்டாரா? Agent எப்படி தெரிஞ்சுக்கும்?

இங்கே painful problem வருது: **Agent-க்கு autonomy கொடுத்தால் தப்பு நடக்கும். முழுக்க முழுக்க block பண்ணினால் agent உபயோகமே இல்லை.**

Human approval என்பது இந்த gap-க்கான architecture.

## 2. Mental Model

Human approval = **Agent proposes, human disposes**.

Agent ஒரு action-ஐ plan பண்ணும், அதன் impact, risk, data-ஐ summarize பண்ணும். அப்புறம் human-க்கு "இதை செய்யலாமா?" என்று கேட்கும். Human yes/no தருவார். Agent அப்புறம் தான் execute பண்ணும்.

இது ஒரு safety valve. முழு autonomy இல்லை, முழு manual இல்லை. Hybrid.

## 3. How It Works

Flow எப்படி இருக்கும்:

1. **Intent capture**: User request வரும்.
2. **Tool planning**: Agent எந்த tools தேவை, என்ன parameters என்று decide பண்ணும்.
3. **Approval gate**: Action risk level-ஐ evaluate பண்ணும். High-risk என்றால் human approval trigger ஆகும்.
4. **Proposal generation**: Agent ஒரு clear proposal உருவாக்கும். 
   - என்ன action?
   - ஏன் இந்த action?
   - என்ன data மாறும்?
   - Side effects என்ன?
5. **Human review**: UI / chat / Slack / email-ல human-க்கு proposal போகும். Approve / Reject / Edit.
6. **Execution**: Approval வந்த பிறகு மட்டுமே tool call execute ஆகும்.
7. **Audit**: Decision log ஆகும்.

Important point: Approval-க்கு முன் tool-ஐ execute பண்ணக்கூடாது. Agent முன்கூட்டியே side effect உண்டாக்கக்கூடாது.

## 4. Architectural Reasoning

எப்போது human approval தேவை?

- **Irreversible actions**: payment, refund, delete, terminate user, publish to production.
- **High blast radius**: bulk update, mass email, data export.
- **Sensitive data access**: PII, health data, financial data access.
- **Policy violation risk**: agent தவறாக interpret பண்ணி policy break ஆகும்.

Constraint: Latency. Human approval slow. Real-time use case-க்கு பொருந்தாது.

Alternatives:
- **Full auto**: low risk actions like search, read-only query.
- **Policy guardrails**: rule-based block before execution. Fast but rigid.
- **Human approval**: flexible, context-aware, but slow.

Architect choose பண்ணும் போது கேட்க வேண்டியது:
- இந்த action தவறாக நடந்தால் cost என்ன?
- Human-ன் context இல்லாமல் agent முடிவு எடுக்க முடியுமா?
- Approval loop-ஐ எவ்வளவு சீக்கிரம் close பண்ண முடியும்?

## 5. Trade-offs

**Safety vs Speed**: Approval safety கூட்டும், latency கூட்டும். User experience slow ஆகும்.

**Trust vs Control**: முழு trust கொடுத்தால் agent useful. முழு control வைத்தால் agent useless.

**Operability**: Approval queue pile up ஆகலாம். Who approves? On-call? Manager? Escalation policy தேவை.

**Failure modes**: Human approves wrong thing because proposal unclear. Agent summary misleading. அதனால் proposal clarity critical.

**Audit & Compliance**: Approval log இல்லை என்றால் compliance audit fail. Who approved, when, why என்பது traceable ஆக இருக்க வேண்டும்.

## 6. Practical Example

Enterprise support agent.

User: *"கடந்த மாத invoice-ஐ மீண்டும் அனுப்பு"*

Agent plan: `get_invoice(id) -> send_email(to=user)`

Read-only + email send = medium risk. Approval தேவையில்லை.

User: *"எனக்கு 3 மாத discount கொடு"*

Agent plan: `get_subscription(user) -> apply_discount(30%) -> update billing`

இது financial impact உள்ளது. Agent proposal உருவாக்கும்:

> Action: User U12345 subscription-க்கு 30% discount 90 நாள்
> Current plan: Pro ₹2000/month
> New amount: ₹1400/month
> Reason: User requested.
> Impact: Revenue loss ≈ ₹18000

Human approver UI-ல இதை பார்த்து approve/reject பண்ணுவார்.

இதே agent-ஐ RAG + tools உடன் இணைத்தால், agent context-ஐ புரிந்து proposal-ஐ contextually generate பண்ண முடியும்.

## 7. Reasoning Challenge

உங்களிடம் AI agent இருக்கு. அது HR system-ல employee leave approve பண்ணும். Manager chat-ல "அருண்-க்கு 2 நாள் leave approve பண்ணு" என்று கேட்கிறார்.

நீங்கள் இதை முழு auto-வாக விடலாமா? அல்லது human approval வைக்கலாமா? ஏன்?

இன்னும் ஒரு step மேலே: Leave approve என்பது reversible தான். ஆனால் team coverage impact உண்டு. Agent எப்படி decide பண்ணும்?

## 8. Key Takeaways

- Human approval என்பது autonomy-க்கும் safety-க்கும் இடையே உள்ள architectural compromise.
- Approval gate-ஐ risk level-ஆல் trigger செய். எல்லாவற்றுக்கும் approval வேண்டாம்.
- Proposal clarity தான் approval-ன் success. என்ன நடக்கும், ஏன் நடக்கும், impact என்ன என்பது தெளிவாக இருக்க வேண்டும்.
- Every approval adds latency and operational overhead. அதை design-ல கணக்கில் வை.
