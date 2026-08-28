# Tool authorization

> **Learning Path:** Security Architecture
> **Section:** 6.3.12 — AI security

## 1. Problem

உங்க கம்பெனியில் ஒரு AI agent இருக்கு. அது customer support chat பண்ணும், அதுக்கு tools கொடுத்திருக்கீங்க: CRM-ல ticket பார்க்க, Jira-ல ticket create பண்ண, Slack-ல message அனுப்ப, payment refund பண்ண.

இப்போ ஒரு user login பண்ணி, "என்னோட லேட்டஸ்ட் invoice என்ன?"ன்னு கேட்கிறார். Agent சரியாக invoice-ஐ பார்க்க வேண்டும்.

அதே agent-க்கு refund tool-ம் இருக்கு. LLM தப்பா reason பண்ணினாலோ, prompt injection வந்தாலோ, அந்த user-க்கு அனுமதி இல்லாத refund-ஐயும் agent trigger பண்ணி விடலாம்.

இங்கே பிரச்சனை என்ன? Agent என்பது user-ன் proxy. ஆனால் agent-க்கு கொடுத்த capability-கள் எல்லாம் எல்லா users-க்கும் பொருந்தாது. 

Tool authorization இல்லாமல், நீங்கள் agent-ஐ ஒரு over-privileged service ஆகவே வளர்த்துட்டு இருக்கீங்க. அது security incident ஆகும்.

## 2. Mental Model

Tool-ஐ ஒரு door மாதிரி நினைச்சுக்கோங்க. Agent-க்கு அந்த door-ஐ திறக்கும் key இருக்கு. ஆனால் எந்த user session-க்கு எந்த door திறக்கணும் என்பதை தீர்மானிக்க வேண்டும்.

Tool authorization = **who can ask the agent to use which tool, with what parameters, on what data**.

இது user identity, session context, tool capability இவற்றுக்கு இடையே ஒரு policy layer.

நீங்கள் agent-க்கு என்ன tools கொடுக்கிறீங்க என்பது மட்டும் போதாது. Agent என்ன context-ல் இயங்குகிறது என்பதையும் அந்த tool call-க்கு முன் validate பண்ணணும்.

## 3. How It Works

சிம்பிள் flow:

**User Request → Agent Planner → Tool Candidate → AuthZ Check → Tool Execution**

1. **Tool Registry**: ஒவ்வொரு tool-க்கும் metadata இருக்கும். `name`, `required_permission`, `sensitive_level`, `owner_service`. Ex: `refund_payment` requires `payments:write` and `PII access`.
2. **Session Context**: User யார்? Role என்ன? Tenant என்ன? இது agent-ன் internal state-ல இருக்கும்.
3. **Policy Engine**: Agent tool-ஐ தேர்ந்தெடுக்கும் முன் அல்லது தேர்ந்தெடுத்த பிறகு, authorization check போகும். 
   `allow(user, tool, resource, action)` 
   இது policy ஐ evaluate பண்ணும். OPA, Cedar, மற்றும் custom policy ஏதாவது.
4. **Guardrails**: AuthZ fail ஆனால் tool call-ஐ block செய். Agent-க்கு safe fallback கொடு. Log it.

Implementation-ல முக்கியம்: AuthZ check-ஐ agent logic-ல mix பண்ணாமல், ஒரு separate enforcement point-ல வைக்கணும். அப்போது policy மாறினாலும் agent code touch ஆகாது.

## 4. Architectural Reasoning

Tool authorization எப்போது கட்டாயம்?

* Agent multiple tools access பண்ணும்போது
* Tools sensitive side-effects உள்ளதாக இருக்கும்போது - write, delete, money move
* Multi-tenant system-ல, ஒரு user மற்ற user-ன் data-ஐ தொடக்கூடாது
* Human-in-the-loop இல்லாமல் autonomous agent run ஆகும்போது

Alternatives:

* **No authz**: எல்லாம் allow. வேகமா, ஆனால் risky.
* **Static allow list per agent**: Agent-க்கு ஒரு set tools கொடு. Simple, ஆனால் user-level granularity இல்லை.
* **Dynamic policy per request**: User, tenant, data scope பார்த்து decide. Architecturally சரியானது.

நீங்கள் architect ஆக decide பண்ணும்போது கேட்க வேண்டியது: "Agent தப்பு பண்ணினால் impact என்ன?" Impact high என்றால் fine-grained authz must.

## 5. Trade-offs

* **Security vs Latency**: ஒவ்வொரு tool call-க்கும் authz check சேர்க்கிறீங்க. Network call, policy eval. Agent response slow ஆகும். Cache decisions பண்ணலாம், ஆனால் stale policy
