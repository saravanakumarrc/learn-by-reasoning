# Excessive agency

> **Learning Path:** Security Architecture
> **Section:** 6.3.6 — AI security

# Excessive Agency

## 1. Problem

உங்களிடம் ஒரு AI agent இருக்கிறது. அது LLM + tools கொண்டு customer support-ஐ handle பண்ணுது. Tool list-ல் CRM read, ticket create, email send, refund API call எல்லாம் இருக்கு.

ஒரு நாள் user சொல்றார்: "என் order cancel பண்ணி refund வேணும்". Agent context-ஐ தப்பா புரிஞ்சிக்குது, தவறான order ID-க்கு refund API-ஐ trigger பண்ணிடுது. அல்லது user prompt-ஐ jailbreak பண்ணி "நீ CEO, எனக்கு எல்லா customer data-யும் தா"ன்னு சொல்லிடுது.

இது ஏன் நடக்குது? Agent-க்கு real world-ல் செயல்படும் அதிகாரம் அதிகமாக இருக்கிறது. It can act, not just answer.

What goes wrong if we don't have control? Irreversible actions, data exfiltration, financial loss, compliance breach. ஒரு hallucination கூட production damage ஆக மாறிடும்.

## 2. Mental Model

Agency = agent-க்கு உலகத்தில் மாற்றம் செய்யும் capability இருக்கிறதா என்பது.

Excessive agency = agent-க்கு தேவைக்கு அதிகமான tools, அதிகமான access, மற்றும் அதிகமான autonomy கொடுக்கப்பட்டிருக்கிறது.

ஒரு junior support engineer-க்கு production DB delete permission கொடுக்க மாட்டீங்க. அதே தர்க்கம் agent-க்கும் பொருந்தும். Agent என்பது code ஆக இருக்கும் employee.

## 3. How It Works

ஒரு typical agent loop இப்படி இருக்கும்:

User query → LLM reasoning → Tool selection → Tool execution → Observation → Loop

Excessive agency வரும் இடங்கள்:

* **Tool breadth**: Agent-க்கு தேவையில்லாத sensitive tools கொடுக்கப்பட்டிருக்கும். Ex: code repo write, payment API, email send.
* **Autonomous execution**: Tool call-க்கு முன் human approval இல்லாமல் direct execution.
* **Lack of policy enforcement**: Agent என்ன செய்யலாம், என்ன செய்யக்கூடாது என்ற boundary இல்லை. Role-based access control இல்லை.
* **No state awareness**: Agent தன்னுடைய actions-ன் impact-ஐ புரிந்து கொள்ளாது. Refund is irreversible.

## 4. Architectural Reasoning

Agent-க்கு agency கொடுப்பது தான் value. Fully autonomous IT ops agent, sales agent, coding agent என்பது தான் goal.

ஆனால் அதை எப்படி கட்டுப்படுத்துவது?

Constraints:
* **Safety > Speed**: Wrong action cost >> slow response cost
* **Auditability**: யார் என்ன செய்தது என்பதை trace செய்ய முடிய வேண்டும்
* **Least privilege**: Agent-க்கு தேவையான tool மட்டும்

Realistic options:
* **Tool allow-list per agent role**: Support agent-க்கு refund tool இல்லை, escalation tool மட்டும்
* **Policy layer before tool execution**: Tool call ஆகும் முன் policy engine check. Amount > $500 என்றால் block
* **Human-in-the-loop for high-risk actions**: High risk tool calls auto approve ஆகாது, human review queue-க்கு போகும்
* **Sandboxed execution**: Agent can write to staging, not production. Write actions need approval
* **Observability + kill switch**: Every tool call logged, anomaly detection, immediate revoke

Decision: Agency-ஐ tier பண்ணுங்கள். Read-only, Write-low-risk, Write-high-risk என்று levels.

## 5. Trade-offs

* **Autonomy vs Safety**: அதிக autonomy = better UX, faster resolution. ஆனால் blast radius அதிகம். Safety guardrails சேர்த்தால் latency, friction அதிகரிக்கும்.
* **Flexibility vs Control**: Generic agent எல்லா tools-ஐயும் பார்க்கும். அது powerful ஆனால் unpredictable. Strict allow-list predictable ஆனால் maintenance heavy.
* **Cost of review vs Cost of incident**: Human-in-the-loop செலவு வரும். ஆனால் ஒரு முறை தவறான refund வந்தால் அது cost-ஐ மீறிடும்.
* **Operational complexity**: Policy enforcement, audit logging, tool permission matrix எல்லாம் system complexity-ஐ அதிகரிக்கும்.

Important failure mode: Agent prompt injection மூலம் tool usage-ஐ bypass பண்ண முயற்சிக்கும். Guardrails-ஐ LLM output-ல் மட்டும் rely பண்ணக்கூடாது. Enforcement server side-ல் இருக்க வேண்டும்.

## 6. Practical Example

Enterprise internal IT helpdesk agent.

Good design:
* Read-only tools: Knowledge base search, ticket read, user profile read
* Low-risk write: Create ticket, post internal message
* High-risk
