# Risk classification

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.12 — Learn

### 1. Problem

Responsible AI & Governance-ல நீங்க AI system deploy பண்ணும்போது ஒரு கேள்வி வரும்: இந்த model-ஐ எப்படி கண்காணிக்கணும்? எல்லா use-case-க்கும் ஒரே safety bar வச்சுட்டா என்ன ஆகும்?

ஒரு internal HR chatbot-க்கும், ஒரு credit approval agent-க்கும், ஒரு medical triage assistant-க்கும் ஒரே risk level சரியா? 

Risk classification இல்லாமல் என்ன பிரச்சனை வரும்? 
- Low risk-க்கு over-engineer பண்ணி cost, latency, velocity போகும்.
- High risk-க்கு under-protect பண்ணி compliance breach, harm, liability வரும்.
- Audit-ல "ஏன் இந்த guardrail வச்சீங்க?" என்று கேட்டால் justification இருக்காது.

எனவே engineers-க்கு தேவை: **risk-ஐ measure பண்ணி, அதுக்கு ஏத்த governance controls வைக்கணும்.**

### 2. Mental Model

Risk classification = **impact × likelihood × exposure**.

ஒரு AI system-க்கு harm ஏற்படும் potential எவ்வளவு, அது எவ்வளவு தடவை trigger ஆகும், எத்தனை users-க்கு தெரியும்.

நீங்க risk-ஐ tier-ஆ பிரிக்கிறீங்க: Minimal, Limited, High, Unacceptable.

ஒவ்வொரு tier-க்கும் **different control set** வரும். இது security-ல classification போல: public, internal, confidential, secret.

AI-ல இது model, data, use-case, deployment context எல்லாத்தையும் பார்த்து முடிவு பண்ணும்.

### 3. How It Works

Risk classification பொதுவா 3 inputs-ல இருந்து வரும்:

**A. Domain of use.** Financial decision, hiring, healthcare, legal advice = high impact. Summarization, content recommendation = lower.

**B. Autonomy & feedback loop.** Model suggestion மட்டும் vs model directly action எடுக்கும், மனுஷன் review இல்லாமல் automate ஆகும். Loop இருந்தால் harm compound ஆகும்.

**C. Scale & vulnerability.** எத்தனை people affected? Vulnerable population involved? Data sensitive-ஆ?

இதை வச்சு நீங்க ஒரு risk matrix பண்ணுவீங்க. EU AI Act, NIST RMF, ISO 42001 எல்லாம் இதே logic-ஐ follow பண்ணும்.

Output: ஒரு risk tier. அதுக்கு ஏத்த:
- Risk assessment documentation
- Human oversight level
- Testing & validation rigor
- Monitoring & logging
- Red teaming frequency
- Model card / transparency requirements
- Incident response SLA

### 4. Architectural Reasoning

இது ஏன் architect-க்கு முக்கியம்?

ஏனென்றால் **controls cost money and latency**. Risk classification தான் cost vs safety trade-off-ஐ justify பண்ணும்.

உதாரணமா:
- Minimal risk chatbot-க்கு basic prompt filtering + logging போதும்.
- High risk credit agent-க்கு: input validation, output policy enforcement, human-in-the-loop, audit trail immutable, drift monitoring, bias testing quarterly.

Alternatives? எல்லா system-க்கும் max controls வைக்கலாம். அது velocity-ஐ கொன்னுடும். அல்லது எதுவும் வைக்காமல் ship பண்ணலாம். அது liability.

Decision: Risk tier-ஐ முன்னாடியே define பண்ணி, அதுக்கு ஏத்த architecture pattern தேர்ந்தெடுக்கணும்.

### 5. Trade-offs

**Granularity vs Operability.** மிக நுணுக்கமா 10 tier வைச்சா governance team confuse ஆகும். 3-4 tier practical.

**Static vs Dynamic.** Risk classification ஒரு தடவை மட்டும் set பண்ணி முடிச்சா போதாது. Model update, new data, new use-case வந்தா risk மாறும். Re-classification process வேணும்.

**False sense of safety.** Classification பண்ணினாலும் controls implement பண்ணாமல் இருந்தால் பிரயோஜனம் இல்லை. Classification is input, not output.

**Compliance vs Real risk.** Regulation-ல limited என்று வந்தாலும் உங்கள் business context-ல high risk ஆகலாம். Regulation floor-ஆ தான், ceiling இல்லை.

Failure mode: Risk tier underestimate பண்ணினா audit fail, incident-க்கு பிறகு retroactive controls, trust loss.

### 6. Practical Example

Enterprise-ல RAG agent இருக்கு. Two deployments.

**A. Internal knowledge Q&A for sales team.** Data = public docs. Output = suggestion only. Human always reviews before sending to customer. Scale = 200 users.

Classification = Limited risk. Controls: basic prompt injection filter, logging to SIEM, quarterly eval.

**B. Same RAG agent, but deployed as customer-facing pricing quote generator.** Model directly writes quote email, no human review. Data = customer PII + pricing rules. Scale = 10k/day.

Classification = High risk. Controls: input PII masking, output validation against policy, human-in-the-loop for >X amount, immutable audit log, real-time monitoring for hallucination, bias testing, incident runbook.

Same model, different risk because **use-case and autonomy மாறியது.** Architecture முழுவதும் மாறும்.

### 7. Reasoning Challenge

உங்களிடம் ஒரு LLM agent இருக்கு. இது employee resume-ஐ parse பண்ணி hiring recommendation generate பண்ணும். இப்போது இது hiring manager-க்கு suggestion மட்டும் காட்டுது. 6 மாதம் கழித்து business விரும்புகிறது: top 5 candidates-ஐ auto-shortlist பண்ணி interview scheduler-க்கு அனுப்ப.

Risk classification மாறுமா? எந்த controls add பண்ணுவீங்க? Why?

### 8. Key Takeaways

- Risk classification என்பது harm potential-ஐ quantify பண்ணி governance cost-ஐ match பண்ணும் tool.
- Use-case, autonomy, scale, data sensitivity தான் tier decide பண்ணும், model size மட்டும் இல்லை.
- Classification-ஐ static document ஆக பார்க்காதே. Model, data, deployment மாறும் போதெல்லாம் re-evaluate பண்ணு.
- Tier என்பது decision framework. அதுக்கு ஏத்த controls, monitoring, accountability தான் architecturally important.

இப்போ உங்களுக்கு தெரியும்: **ஏன் risk classify பண்ணணும், எப்போ tier மாறும், என்ன trade-off வரும்.**
