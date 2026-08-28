# Requirements gathering

> **Learning Path:** Non-AI System Design Practice
> **Section:** 9.1.1 — System design practice

## 1. Problem

System design practice-ல பெரும்பாலான engineers தப்பா ஆரம்பிப்பாங்க. Interviewer சொல்வார் "Design a food delivery app". நீங்க உடனே service breakdown, database schema வரைஞ்சுடுவீங்க.

Real project-ல இது இன்னும் ஆபத்தானது. Product manager சொல்வார் "நமக்கு fast checkout வேணும்". நீங்க 200ms latency target வச்சு architecture போடுவீங்க. ஒரு மாசம் கழிச்சு தெரியும், அவர் சொன்னது mobile users-க்கு 3G-ல வேலை செய்ய வேண்டும், அதற்கு 2 sec தான் முக்கியம், அதே நேரம் peak-ல 10x traffic வரும், fail ஆகக்கூடாது.

Requirements gather பண்ணாம architecture எழுதினா, நீங்க சரியான problem-க்கு சரியான solution போட மாட்டீங்க. Build அதிகம், rework இன்னும் அதிகம்.

## 2. Mental Model

Requirements gathering என்பது feature list எடுப்பது அல்ல. 
இது **constraints + goals + risks** எடுப்பது.

ஒரு system-ன் shape எப்போதும் இதை பொறுத்தது:
* What must it do? functional requirements
* How well must it do it? non-functional requirements
* Who uses it, when, how much? usage constraints

இதை புரிஞ்சுக்காம ஆரம்பிச்சா, நீங்க beautiful architecture build பண்ணி, business need-க்கு தேவையில்லாத architecture பண்ணியிருப்பீங்க.

## 3. How It Works

Practical-ல requirements gathering என்பது interview போல்.

Stakeholder-ஐ கேட்க வேண்டிய core கேள்விகள்:
* Who is the user? Internal employee, external customer, partner API?
* What is the primary use case? Happy path என்ன?
* Scale எவ்வளவு? Current traffic, peak, growth?
* Latency / throughput / availability target என்ன? SLA என்ன?
* Data consistency தேவையா? Strong consistency vs eventual consistency?
* Security, compliance, audit என்ன constraints?
* Existing system-களுடன் integrate ஆகணுமா? Legacy database, payment gateway?
* Success எப்படி measure பண்ணுவோம்? Metric என்ன?

இதில் functional requirement-களை விட non-functional requirements தான் architecture-ஐ decide பண்ணும்.

## 4. Architectural Reasoning

Requirements clear ஆன பிறகு தான் options தெரியும்.

எடுத்துக்கோங்க:
* Availability 99.99% வேணும் + low latency => multi-region, cache, read replica
* Cost sensitive + bursty traffic => auto-scale, serverless
* Strong consistency முக்கியம் => relational database, distributed transaction
* Event replay வேணும் => event streaming, Kafka

Requirements gather பண்ணாம இந்த decisions எடுக்க முடியாது. Wrong assumption போட்டால், architecture over-engineered ஆகும் அல்லது under-engineered ஆகும்.

## 5. Trade-offs

**Completeness vs Speed.** Perfect requirements என்பது இல்லை. Timebox செய்து 80% clarity-ல ஆரம்பிக்கலாம். முக்கிய constraints மட்டும் capture பண்ணுங்க.

**Explicit vs Implicit.** Stakeholder சொல்லாத requirement தான் பெரும் risk. "Oh, we assumed it works offline". அதை surface பண்ண வேண்டும்.

**Functional vs Non-functional.** Features எழுத ஈஸி. Latency, cost, operability பற்றி பேச யாரும் விரும்ப மாட்டாங்க. Architect தான் அதை கேட்க வேண்டும்.

Failure mode: Requirements change mid-way. அதற்கு architecture-ல flexibility வைக்க வேண்டும். Over-optimise பண்ணாதீங்க.

## 6. Practical Example

Enterprise logistics tracking system.

Initial request: "Truck location real-time-ல காட
