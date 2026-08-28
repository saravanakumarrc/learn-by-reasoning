# Task breakdown & estimation

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.1.4 — Code & delivery practices

# Task breakdown & estimation

## 1. Problem

Product manager வர்றார்: “Mobile app-ல payment feature add பண்ணுங்க, 2 வாரத்தில் வேண்டும்.”

Team “சரி”ன்னு சொல்லுது. ஏன்னா தெரியலை. 2 வாரம் கழித்து integration stuck, compliance approval pending, retry logic இல்லை, test data இல்லை. 2 மாதம் ஆகுது.

இது ஏன் நடக்குது? வேலை ஒரே பெரிய blob-ஆ இருக்கு. யார் என்ன செய்யணும், எவ்வளவு நேரம், என்ன dependencies இருக்கு என்பது தெளிவில்லை. Estimate என்பது guess ஆக மாறும்.

Task breakdown & estimation இல்லாமல் வரும் pain: missed deadline, scope creep, team burnout, rework, stakeholder mistrust.

## 2. Mental Model

Breakdown என்பது complexity-ஐ visible ஆக்குவது. Estimation என்பது uncertainty-ஐ quantify பண்ணுவது.

ஒரு house கட்டுவதை நினைத்து பாருங்கள். “வீடு கட்டு”ன்னு சொல்ல மாட்டீர்கள். Foundation, plumbing, electrical, finishing என்று பிரிப்பீர்கள். அப்போதுதான் யார் என்ன செய்வார்கள், எவ்வளவு material தேவை என்பது தெரியும்.

Software-லும் அதே. ஒரு feature என்பது ஒரு black box. அதை independently deliver செய்யக்கூடிய, test செய்யக்கூடிய, Definition of Done உள்ள work units-ஆக உடைக்கிறோம்.

## 3. How It Works

Breakdown-ன் rule simple: **decompose until you can reason about it**.

1. Feature -> Epic -> Story -> Task
2. ஒரு story எப்போது ready? Clear acceptance criteria, no hidden dependencies, one team member can own it.
3. Definition of Done set பண்ணுங்கள்: code, review, test, observability, docs.

Estimation technique எல்லாம் perfect prediction கிடையாது. Uncertainty-ஐ communicate பண்ணுவதற்கு.

* Relative sizing: story points, T-shirt sizes S/M/L. Absolute hours இல்லாமல் compare பண்ணுவது.
* Planning Poker: team-ஆக discuss பண்ணி consensus கிடைக்கும்.
* 3-point estimate: optimistic, most likely, pessimistic -> எதிர்பாராத risk-ஐ capture பண்ணும்.

Mechanism முக்கியமில்லை. முக்கியம்: estimate என்பது conversation, not a number.

## 4. Architectural Reasoning

இது எப்போது useful? Multiple services, cross-team dependencies, delivery cadence தேவைப்படும்போது.

Constraint-ஐ பாருங்கள்: latency to market, team cognitive load, coordination cost.

Fine-grained breakdown கொடுக்கும்:
* Parallel work possible
* Risk early visible ஆகும்
* Delivery incremental ஆகும்

Coarse breakdown கொடுக்கும்:
* Less overhead
* Faster planning

Architect ஆக நீங்கள் choose பண்ண வேண்டியது: system boundary எங்கே? ஒரு task independent-ஆ deploy ஆகுமா? அதற்கு data dependency உண்டா? அப்படி இருந்தால் breakdown depth அதிகம் வேண்டும்.

Alternative: top-down waterfall estimate. அது assumption-ஐ hide பண்ணும். Agile breakdown & iterative estimation uncertainty-ஐ surface பண்ணும்.

## 5. Trade-offs

1. **Granularity vs overhead.** மிகவும் fine-ஆக உடைத்தால் planning meeting எல்லாம் task management ஆக மாறும். மிகவும் coarse ஆக இருந்தால் risk invisible ஆகும்.
2. **Accuracy vs speed.** 3-point estimate சரியாக வராது, ஆனால் directionally correct ஆக இருக்கும். Perfect estimate பின்னாடி chase பண்ணினால் delivery stall ஆகும்.
3. **Optimism bias.** Engineers underestimate. Estimation without buffer = commitment to failure.
4. **Estimation creates accountability.** ஒரு number கொடுத்தால் அதை defend செய்ய வேண்டும். அதனால் team estimate-ஐ avoid பண்ண முயற்சிக்கும். அது toxic.

Failure mode: estimate-ஐ commitment ஆக treat பண்ணி, reality change ஆனால
