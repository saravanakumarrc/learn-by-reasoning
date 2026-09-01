# Policy engine

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.13 — Enterprise patterns

## 1. Problem

Enterprise AI Architecture-ல உங்களிடம் ஒரு RAG system இருக்கு. அதுல agent இருக்கு. Agent users-க்கு பதில் கொடுக்குது, tools-ஐ call பண்ணுது, data access பண்ணுது.

ஒரு நாள் product manager கேட்கிறார்:

> "Free tier users-க்கு sensitive PII data காட்டக்கூடாது. Finance team-க்கு மட்டும் internal cost data access வேணும். EU users-க்கு data residency rule apply ஆகணும். Compliance audit-க்கு யார் எந்த decision எடுத்தார் என்று log வேணும்."

இந்த rules எல்லாம் code-ல hard-code பண்ணி, service-க்குள்ள if-else-ல வச்சால் என்ன ஆகும்?

New rule வந்தா code deploy பண்ணணும். Rules business team control பண்ண முடியாது. Rules logic scattered ஆகி விடும். AI agent-ன் behavior-ம் inconsistent ஆகும். Audit impossible.

**What goes wrong?** Business policy, compliance, and access control logic is tangled with application code. Change is slow, risky, and not auditable.

## 2. Mental Model

Policy engine என்பது **decision logic-ஐ code-ல இருந்து பிரிச்சு, centralize பண்ணி, declarative-ஆ rule-ஆ எழுதி evaluate பண்ணும் ஒரு layer.**

Application: "இந்த user இந்த action பண்ணலாமா?" என்று கேட்கும்.
Policy engine: Context-ஐ வாங்கி, rules-ஐ evaluate பண்ணி, allow / deny + reason திருப்பி தரும்.

அதாவது, policy engine ஒரு **authoritative decision function**: `decision = f(user, resource, action, context)`

## 3. How It Works

Flow simple:

1. **Request comes in** → Service policy engine-ஐ call பண்ணும்
2. **Context gathering** → user attributes, tenant, time, location, data classification, LLM output, etc.
3. **Policy evaluation** → engine rules-ஐ evaluate பண்ணும். இது usually Rego, Cedar, OPA-style language.
4. **Decision + explanation** → allow/deny + obligations like log, mask PII, add watermark
5. **Enforcement** → Service decision-ஐ follow பண்ணும்

Policy engine itself stateless-ஆ இருக்கலாம். Rules versioned, stored in Git / database. Hot reload possible.

AI systems-ல முக்கியம்: Policy engine **prompt level, tool call level, output level**-லயும் வேலை செய்யும்.

Example: Agent ஒரு tool call செய்ய போகிறது. Before calling, policy engine "இந்த user-க்கு இந்த tool access உண்டா?" என்று check. After LLM generates answer, policy engine output-ஐ scan பண்ணி PII leak ஆகிறதா என்று check.

## 4. Architectural Reasoning

Policy engine எப்போ useful?

* **Cross-cutting rules**: Authentication, authorization, data privacy, compliance, rate limiting எல்லா service-க்கும் common.
* **Rules change frequently**: Business policy, legal, risk rules weekly மாறும்.
* **Multiple consumers**: API gateway, AI agent, backend services எல்லாம் same policy follow வேண்டும்.
* **Audit & explainability**: ஏன் deny ஆச்சு என்று trace வேண்டும்.

Alternatives?

* **Hard-coded if-else**: Small, static rules-க்கு okay. Scale ஆகாது.
* **Database flags**: Simple allow/deny list-க்கு okay. Complex context-க்கு சிரமம்.
* **RBAC / ABAC in IAM only**: Identity level control மட்டும். Business policy, content filtering வராது.

Architect choose policy engine when decision logic **complex, dynamic, auditable, centralized** ஆக இருக்க வேண்டும்.

## 5. Trade-offs

* **Latency**: Every request-ல policy evaluation add ஆகும். Hot path-ல 5-20ms overhead வரும். Cache decision, sidecar deployment, async evaluation பண்ணி குறைக்கலாம்.
* **Complexity shift**: Code complexity குறையும், policy complexity அதிகரிக்கும். Policy language-ஐ team கத்துக்கணும்.
* **Single point of failure**: Central engine down ஆனால் whole system stuck. High availability, local fallback needed.
* **Policy correctness**: Wrong policy = security hole அல்லது business loss. Testing, simulation, versioning critical.

Failure mode: Policy engine too permissive → data leak. Too restrictive → user experience break. Both need monitoring.

## 6. Practical Example

Enterprise AI Support Agent.

Flow:
`User query → Agent → Tool call to CRM → Policy engine check`

Policy:
```
allow tool CRM.read if user.role == "support" and user.tenant == resource.tenant and time within business hours
deny if data contains PII and user.tier == "free"
mask PII in output if user.region == "EU"
```

Agent ஒரு customer PII கேட்டால், policy engine deny பண்ணி, agent-க்கு "you don't have access" என்று திருப்பி தரும். Agent அதற்கு தகுந்த மாற்று பதில் கொடுக்கும்.

Audit log: `who, what, when, which policy version, decision` எல்லாம் store ஆகும். Compliance team rule மாற்றினால், policy repo-ல PR போட்டு deploy பண்ணினால் போதும். Code redeploy தேவையில்லை.

## 7. Reasoning Challenge

உங்களிடம் multi-tenant RAG + Agent system இருக்கு. 3 requirements வந்துள்ளன:

1. Free users-க்கு LLM output-ல internal financial data காட்டக்கூடாது
2. Agent tool call-க்கு முன் approval workflow வேண்டும் high-risk actions-க்கு
3. Audit team-க்கு எல்லா policy decisions 1 year retain வேண்டும்

Hard-code பண்ணாமல், policy engine-ஐ எப்படி place பண்ணுவீர்கள்? Pre-processing, post-processing, tool-gating என்று எங்கெங்கே evaluate பண்ணுவீர்கள்? Latency impact எப்படி manage பண்ணுவீர்கள்?

## 8. Key Takeaways

* Policy engine decision logic-ஐ code-ல இருந்து decouple பண்ணி, centralize & version பண்ணும்
* AI systems-ல policy enforcement input, tool call, output மூன்று இடத்திலும் வேண்டும்
* Rules change fast, code change slow. Policy engine business agility கொடுக்கும்
* Every decision must be auditable, explainable, and testable. Trade-off is latency + operational complexity
