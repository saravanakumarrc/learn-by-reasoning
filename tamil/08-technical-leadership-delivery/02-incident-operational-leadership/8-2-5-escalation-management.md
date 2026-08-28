# Escalation management

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.2.5 — Incident & operational leadership

### 1. Problem

நள்ளிரவு 2 மணி. Payment service latency 5s ஆக உயர்ந்திருக்கு. On-call engineer alert பார்த்தார். Logs பார்த்தார். Root cause புரியல. 20 நிமிடம் தேடினார். என்ன செய்யறது?

இப்போ ஒன்னு, அவர் தனியா அதுக்குள்ள அமிழ்ந்து போகணும். ரெண்டு, அவருக்கு தெரிஞ்சவங்களை எழுப்பணும். மூணு, எப்போ எழுப்பணும்? யாரை எழுப்பணும்? எப்படி எழுப்பணும்?

இதை முடிவு செய்யாம விட்டா என்ன ஆகும்? Incident நீளும். MTTR ஏறும். Business impact பெருசாகும். அதே நேரம், தேவையில்லாம எல்லாரையும் எழுப்பினா alert fatigue வரும். நம்பிக்கை போகும்.

Escalation management என்பது இந்த இடைவெளியை முன்கூட்டியே வடிவமைப்பது தான்.

### 2. Mental Model

Escalation என்பது people chain இல்லை. இது **time-bound decision pipeline**.

ஒரு incident ஆரம்பிச்சதும் குறிப்பிட்ட நேரத்திற்குள் குறிப்பிட்ட outcome இல்லைன்னா, automatically அடுத்த layer-க்கு போகும்.

அதாவது:
**Detect → Triage → Contain → Escalate if no progress → Resolve**

நீங்கள் escalation policy-ஐ வடிவமைக்கும்போது, நீங்கள் கேட்பது:
- எவ்வளவு நேரத்தில் என்ன மைல்ஸ்டோன் எட்டணும்?
- அது எட்டலன்னா யார் அடுத்து வருவார்?
- அவருக்கு என்ன context தேவை?

### 3. How It Works

நடைமுறையில் escalation மூன்று விஷயங்களால் ஆனது.

**Severity classification.** 
SEV-1 = customer impacting, revenue loss. SEV-2 = degraded. SEV-3 = internal. இதை முடிவு செய்தால் மட்டுமே escalation speed தெரியும்.

**On-call rotation + escalation policy.**
L1 = service owner on-call. L2 = senior engineer / team lead. L3 = manager / architect / SRE lead.
ஒவ்வொரு level-க்கும் SLA கொடுக்கப்படும். உதாரணமா, SEV-1 alert வந்த 5 நிமிடத்திற்குள் acknowledge பண்ணணும், 15 நிமிடத்தில் containment start பண்ணணும்.

**Communication channel.**
PagerDuty / Opsgenie போன்ற tool-ல் policy define பண்ணுவீங்க. First responder 5 minக்குள் respond இல்லைன்னா auto-escalate. Bridge call auto-create ஆகும்.

Runbook இருந்தால், escalation தாமதம் குறையும். இல்லைன்னா ஒவ்வொரு முறையும் tribal knowledge தேட வேண்டியிருக்கும்.

### 4. Architectural Reasoning

Escalation policy-ஐ design பண்ணும்போது constraints பார்க்கணும்.

**Team size & availability.** சின்ன team-ல L1, L2 வேறுபடுத்த முடியாது. அப்போ escalation window குறைவா வைக்கணும்.

**Service criticality.** Payment, auth மாதிரி core service-க்கு escalation chain குறுகியதாக இருக்கணும். Internal dashboard-க்கு அதிக tolerance இருக்கலாம்.

**Blast radius.** ஒரு incident பல service-ஐ தொடுத்தால், escalation-ல cross-team coordination தேவை. அதனால் incident commander role தெளிவா இருக்கணும்.

Decision எப்போ? Incident response playbook-ல escalation criteria முன்கூட்டியே define பண்ணுவது. Ad-hoc "அவரை கூப்பிடு" என்பது failure mode.

### 5. Trade-offs

**Speed vs Noise.** தாமதமா escalate பண்ணினா MTTR அதிகம். மிக விரைவா escalate பண்ணினா on-call burnout, alert fatigue.

**Centralization vs Autonomy.** ஒரே incident commander எல்லாவற்றையும் control பண்ணினால் decision fast ஆகும், ஆனால் single point of failure. Team-க்கு autonomy கொடுத்தால் learning அதிகம், ஆனால் coordination கடினம்.

**Escalation path transparency vs flexibility.** Policy-ஐ முன்கூட்டியே எழுதினால் fairness இருக்கும். ஆனால் ஒவ்வொரு incident-மும் unique. தேவைக்கு தகுந்தாற்போல override வேண்டும்.

Failure mode: escalation ஆனாலும் context transfer இல்லை. அடுத்தவர் முதல் முதல்ல ஆரம்பிக்கிறார். அதை தடுக்க incident channel-ல timeline, what tried, what not tried என்பது பதிவாக வேண்டும்.

### 6. Practical Example

Enterprise e-commerce. Black Friday.

SEV-1 policy:
0-5 min: L1 on-call acknowledges PagerDuty alert, joins Slack incident channel.
5-15 min: If no containment, auto-escalate to L2 senior SRE + create Zoom bridge.
15-30 min: If still no mitigation, escalate to Engineering Manager + Product lead. Communication to customer starts.

இங்கே escalation என்பது "யாரை எழுப்புவது" மட்டுமல்ல. 15 நிமிடத்தில் status update public channel-க்கு போக வேண்டும். Customer communication trigger ஆக வேண்டும்.

இதன
