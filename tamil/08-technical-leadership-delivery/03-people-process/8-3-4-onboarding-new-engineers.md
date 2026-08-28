# Onboarding new engineers

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.3.4 — People & process

## Problem

நீங்க ஒரு 4 வருஷமா வளர்ந்த microservices system-ஐ lead பண்றீங்க. 12 services, 3 databases, event-driven flow, கொஞ்சம் legacy code-ம் இருக்கு. இப்போ ஒரே வாரத்துல 3 engineers join பண்றாங்க.

ஒருவர் அவுட்சோர்ஸ் vendor-ல இருந்து வரார். ஒருவர் startup-ல இருந்து வரார். ஒருவர் fresh.

இவர்களுக்கு repo access கொடுத்து, Wiki link அனுப்பினால் போதுமா?

2 வாரம் கழித்து நடக்கிறது:
- கேள்விக்கு பதில் கிடைக்க 2-3 days ஆகுது. Senior engineers context switch ஆகி burnout ஆகிறார்கள்.
- New joiner ஒரு small bug fix-க்கு 5 files திறக்கிறார், 3 service-களை புரிஞ்சுக்காம change பண்ணி staging-ல break பண்றார்.
- "ஏன் இப்படி design பண்ணீங்க?" என்று கேட்டால், "அப்போ அப்படி தான் வேண்டி இருந்தது" என்று மட்டும் பதில்.

இதுதான் onboarding-ன் real cost. Information இல்லை என்பதல்ல பிரச்சனை. **Mental model இல்லை**. System எப்படி முடிவுகள் எடுக்கப்பட்டது, எந்த constraints இருந்தது, எங்கே landmines இருக்கு என்பது தெரியாமல், engineer safe contribution செய்ய முடியாது.

## Mental Model

Onboarding என்பது documentation dump அல்ல. 

இது **cognitive map building**.

ஒரு நகரத்திற்கு புதிதாக வந்தவருக்கு நீங்கள் map மட்டும் கொடுக்க மாட்டீர்கள். "எந்த பகுதி risky, எந்த road peak hour-ல் மாட்டும், எங்கே police check post இருக்கு" என்ற local knowledge தேவை.

அதேபோல் codebase-க்கு:
Context > Code > Culture > Ownership

அதாவது, *எதுக்காக இந்த system இருக்கு* புரிஞ்சா தான் *எந்த file-ஐ தொடலாம்* புரியும்.

## How It Works

Effective onboarding ஒரு pipeline மாதிரி வேலை செய்யும்.

1. **Context First, Code Later.** Business domain, customer flow, SLAs, failure modes. எந்த service critical, எந்தது best-effort என்பது.
2. **Bounded Exploration.** Repo முழுவதும் காட்டாமல், critical path-ஐ மட்டும் map பண்ணுங்கள். Request flow, data flow, event flow.
3. **Decision History.** Architecture Decision Records - ஏன் Kafka choose பண்ணோம், ஏன் not synchronous call. இது "don't repeat old mistakes" ஆக மாறும்.
4. **Safe Contribution Path.** First PR என்பது documentation fix அல்லது small observability improvement. Production impact இல்லாத, review-க்கு எளிதான விஷயம்.

இது 30-60-90 மாதிரி இல்லை. Time-boxed outcomes-ஆக இருக்கும்:
- Day 7: Can run local stack and explain one end-to-end flow.
- Day 30: Can fix a bug without hand-holding.
- Day 60: Can design a small change with trade-offs.

## Architectural Reasoning

ஏன் structured onboarding தேவை?

Constraint இது: **Knowledge is a distributed system with high latency and single point of failure.**

Senior engineers தான் knowledge silo. அவர்கள் unavailable ஆனால் ramp up நின்று விடும். இது bus factor.

Alternatives:
- **Ad-hoc buddy**: Fast start, but buddy-யின் style-க்கு ஏற்ப மாறுபடும். Scalable இல்லை.
- **Self-service docs**: Scale ஆகும், ஆனால் context இல்லாமல் engineers lost ஆகிறார்கள்.
- **Structured program**: High upfront cost, ஆனால் repeatable, measurable.

Architect-ஆக நீங்கள் தேர்வு செய்யும்போது பார்க்க வேண்டியது team size, churn rate, system complexity. 5-10 engineers தாண்டியதும் ad-hoc முறை break ஆகும்.

## Trade-offs

**Speed vs Depth.** Quick win கொடுத்து momentum கொடுக்கலாம். ஆனால் deep understanding இல்லாமல் long term mistakes வரும்.

**Standardization vs Customization.** Company level onboarding template உர
