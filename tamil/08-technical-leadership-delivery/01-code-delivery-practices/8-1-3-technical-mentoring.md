# Technical mentoring

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.1.3 — Code & delivery practices

## 1. Problem

உங்க team-ல ஒரு senior developer code review-ல எல்லா PR-யும் பார்க்கிறார். அவர் தான் deployment script, rollback logic, production incident-க்கு root cause எல்லாம் தெரியும். அவர் ஒரு வாரம் leave எடுத்தாலோ, அல்லது quit பண்ணிட்டாலோ என்ன ஆகும்?

Delivery stall ஆகும். Code quality drop ஆகும். New joiner-கள் "இதை யார் கேட்கறது?" என்று stuck ஆகி நிற்பார்கள். இதுதான் bus factor problem.

Technical mentoring-ன் core problem இது: **knowledge சிதறாமல், delivery speed குறையாமல், team-ஐ scale பண்ண வேண்டும்.**

Training என்பது syntax கத்துக்கொடுப்பது. Mentoring என்பது *why we chose this architecture, why this trade-off, இந்த failure எப்படி வரும்* என்ற context transfer.

## 2. Mental Model

Mentoring = guided ownership transfer.

Mentor என்பவர் answer கொடுப்பவர் அல்ல. Good question கேட்க வைப்பவர்.

Loop மூன்று step:
**Observe → Ask → Let them do**

Senior: "இந்த PR-ல retry logic எதுக்கு இல்ல?" என்று கேட்கிறார். Junior யோசித்து தானே சேர்க்கிறார். இப்போது அந்த reasoning junior-க்கு சொந்தமாகிறது.

## 3. How It Works

Code & delivery practice-ல mentoring என்பது formal training session அல்ல.

1. **Pair on real delivery:** Production bug fix, incident postmortem, release checklist-ல் சேர்த்து கொள்ளுங்கள். Artificial exercise விட real pressure-ல தான் learning stick ஆகும்.
2. **PR review as reasoning, not correction:** "Change this" என்பதற்கு பதில் "இந்த change செய்தால் consistency எப்படி பாதிக்கும்? Alternative என்ன?" என்று கேளுங்கள்.
3. **Make thinking visible:** Architect ஏன் இந்த service boundary எடுத்தார், ஏன் event-driven தேர்ந்தெடுத்தார் என்பதை design doc review-ல் வெளிப்படையாக பேசுங்கள்.
4. **Graduated responsibility:** Junior முதலில் review-கள் பார்க்க, பின் small delivery own பண்ண, பின் on-call rotation-ல் வர.

## 4. Architectural Reasoning

Mentoring useful ஆகும் போது:
- Team size 5-க்கு மேல் வளரும்போது, knowledge silo வரும்
- System complexity அதிகரிக்கும்போது, new engineer ramp up time பெருகும்
- Delivery frequency அதிகரிக்க வேண்டும், ஆனால் senior-கள் bottleneck ஆகிறார்கள்

Alternative என்ன? Documentation மட்டும் எழுதுவது. அது necessary ஆனால் போதாது. Context transfer ஆகாது. சில teams mentoring-க்கு பதில் hiring senior-கள் மூலம் scale பண்ண முயற்சிக்கின்றன. அது cost அதிகம், knowledge still centralized.

Architect க்கு தேவையானது: delivery reliability-க்கு மனித system-ஐ design செய்வது.

## 5. Trade-offs

**Short-term velocity vs long-term velocity.** Mentor time எடுத்துக்கொள்ளும், PR review slow ஆகும். ஆனால் 3 மாதத்தில் அந்த engineer independently ship பண்ண ஆரம்பிக்கிறார்.

**Depth vs breadth.** Mentor ஒருவருக்கு மட்டும் deep mentoring கொடுத்தால் அவர் தான் go-to ஆகிவிடுவார். Rotation பண்ணுங்கள்.

**Spoon feeding vs struggle.** நேரடியாக solution கொடுத்தால் fast. ஆனால் learning ஆகாது. Engineer அடுத்த similar problem வந்தால் stuck ஆகுவார்.

**Mentor burnout.** Senior-கள் எப்போதும் mentor role-ல் இருந்தால் அவர்கள் தங்கள் own architecture work குறையும். Mentoring-ஐ delivery goal-ஆக track பண்ணுங்கள், charity work ஆக அல்ல.

Failure mode: Mentoring என்பது one-way lecture ஆக மாறும். அப்போது engineer passive ஆகி, "சொல்லுங்க, நான் பண்ணிக்கிறேன்" mode-ல் இருப்பார்.

## 6. Practical Example

Enterprise-ல RAG pipeline delivery.

New engineer-க்கு vector database, embedding model, retrieval logic எல்லாம் தெரியும். ஆனால் production-ல latency spike ஆகும்போது எங்கே debug பண்ணுவது தெரியாது.

Mentor 30 நிமிடம் சொல்லிக்கொடுக்காமல், incident simulation செய்ய சொல்கிறார்: "Retrieval latency 800ms ஆகிறது. Metrics எங்கே பார்ப்பீர
