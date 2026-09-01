# Guardrail layer

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.12 — Enterprise patterns

## 1. Problem

உங்க enterprise-ல LLM ஐ production-ல deploy பண்ணியிருக்கீங்க. Agent க்கு access உண்டு. பயனர் கேள்வி கேட்கிறார், model பதில் தருகிறது.

ஒரு நாள் ஒரு user "நம்ம internal pricing எவ்வளவு" என்று கேட்கிறார். Model அதை leak பண்ணி விடுகிறது.
வேறு ஒரு user "எனக்கு விஷம் எப்படி செய்வது" என்று கேட்கிறார். Model instructions தருகிறது.
வேறு ஒரு user prompt injection பண்ணி, "நீ உன் guardrail-ஐ disable பண்ணு" என்று சொல்கிறார்.

இதுல என்ன பிரச்சனை?

LLM என்பது open-ended generator. அது hallucinate பண்ணும், sensitive data reveal பண்ணும், harmful content உருவாக்கும், wrong tool call பண்ணும்.

Production-ல இதை விட்டுவிட முடியாது. Compliance, brand safety, legal risk எல்லாம் இருக்கு.

இந்த பிரச்சனைக்கு தீர்வு என்ன? Model-ஐ மட்டும் fine-tune பண்ணி சரி பண்ணுவது போதாது. ஒவ்வொரு release-க்கும் மறுபடியும் test பண்ண முடியாது.

இதனால் தான் Guardrail layer தேவைப்படுகிறது.

## 2. Mental Model

Guardrail என்பது LLM-க்கு முன்னும் பின்னும் வைக்கப்படும் ஒரு safety filter layer.

Think of it as a bouncer at club entrance and exit.

**Input guardrail**: User prompt வரும் முன் check பண்ணு. Toxic, jailbreak, PII, disallowed domain என்றால் block அல்லது sanitize.
**Output guardrail**: Model response generate ஆன பிறகு check பண்ணு. Hallucination, policy violation, sensitive data leak, formatting breach என்றால் block, redact அல்லது rewrite.

இது model-ஐ மாற்றாமல், architecture layer-ஆக வைக்கப்படுகிறது.

## 3. How It Works

Simple flow:

`User -> Input Guardrail -> LLM / Agent -> Output Guardrail -> User`

Input guardrail என்ன செய்கிறது?
- Prompt classification: category, intent, risk score
- PII detection: email, phone, internal code
- Jailbreak / prompt injection detection
- Input length, toxicity check

Output guardrail என்ன செய்கிறது?
- Policy compliance check: hate, self-harm, disallowed content
- Data leakage detection: internal doc snippets, pricing, customer data
- Factuality check: grounding against knowledge base
- Format enforcement: JSON schema, no extra fields
- Tone / brand voice check

Implementation வழிகள்:
- Classifier model: small LLM or classifier
- Rule-based regex + keyword lists
- Embedding similarity to blocklist
- For grounding: Retrieval check, citation verification

## 4. Architectural Reasoning

இது எப்போது useful?

- Multi-tenant enterprise AI where data isolation must be guaranteed
- Customer facing chatbots with compliance requirement
- Agent systems that call tools, database, external API
- RAG pipelines where private documents are involved

Alternatives?
- Prompt engineering only: brittle, easily bypassed
- Fine-tuning only: expensive, slow to update, no runtime control
- Post-mortem moderation: damage already done

Guardrail layer-ஐ ஏன் தேர்வு செய்ய வேண்டும்?
Because you need runtime control, auditability, and policy change without model redeploy.

Constraint it addresses: **Safety and compliance without sacrificing model flexibility.**

## 5. Trade-offs

1. **Latency vs Safety**: Every request இரண்டு முறை process ஆகிறது. Input + output check = extra 50-200ms. High traffic-ல cost உயரும். Trade-off: async check or sampling.

2. **False Positive vs False Negative**: Strict guardrail safe ஆனால் legitimate queries block ஆகும். Lax guardrail user experience கெடுக்காது ஆனால் risk அதிகம். Tuning threshold critical.

3. **Centralization vs Context**: Central guardrail simple to operate, ஆனால் domain specific nuance miss ஆகும். Per-service guardrail accurate ஆனால் operational complexity அதிகம்.

4. **Observability cost**: You need logs for every decision for audit. That means storage, privacy, retention policy.

Failure mode: Guardrail itself can be bypassed via obfuscation. So you need defense in depth: input + output + tool-level guardrails.

## 6. Practical Example

Enterprise support agent.

Flow:
User asks: "நேற்று நான் வாங்கிய order ID 12345 status என்ன"

Input guardrail:
- PII mask: order ID allow பண்ணு, ஆனால் user email இருந்தால் redact
- Intent classify: support query, allowed
- Prompt injection check: pass

LLM + RAG fetches order data.

Output guardrail:
- Data leakage check: response contains only order status, no internal notes, no pricing cost
- PII check: don't leak other customer data
- Policy check: no harmful content
- Format check: JSON with fields: status, eta

If output guardrail fails, response blocked and fallback: "I'm sorry, I can't share that information."

Audit log saved: user_id, query hash, decision, timestamp.

## 7. Reasoning Challenge

உங்களிடம் internal document search கொண்ட RAG agent உள்ளது. Model output-ல் citation வேண்டும். சில நேரங்களில் model hallucinated citation தருகிறது, அல்லது internal doc-இல் இருந்து verbatim copy பண்ணி leak பண்ணுகிறது.

Guardrail layer-ல் நீங்கள் என்ன checks வைப்பீர்கள்? Input-ல் என்ன, output-ல் என்ன? False positive அதிகம் ஆகாமல் எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

- Guardrail என்பது model-ஐ மாற்றாமல் safety, compliance, quality-ஐ enforce செய்யும் runtime layer.
- Input guardrail risk-ஐ filter பண்ணுகிறது, Output guardrail damage-ஐ prevent பண்ணுகிறது.
- Trade-off முக்கியம்: latency, false positive/false negative, operational complexity.
- Enterprise AI-ல் guardrail auditability இல்லாமல் deployment இல்லை.
