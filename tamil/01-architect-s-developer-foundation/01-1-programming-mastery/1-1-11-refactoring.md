# Refactoring

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.11 — 1. Programming mastery

## Problem

உங்கள் team 5 வருடம் பழைய codebase-ஐ maintain பண்ணுது. ஆரம்பத்துல ஒரு feature 2 நாள்ல வந்தது. இப்போ அதே மாதிரி மாற்றம் செய்ய 2 வாரம் ஆகுது. ஏன்?

Code-ஐ புரிஞ்சுக்கவே 3 நாள் ஆகுது. ஒரு line மாற்றினா இன்னொரு இடத்துல bug வருது. New joiner-க்கு onboarding நீளுது. Code review-ல "இதை தொடாதீங்க" என்று சொல்லும் பகுதிகள் அதிகரிக்கின்றன.

இது வளர்ந்த business need-ஆல வருவது அல்ல. Code base depreciate ஆகுறதால வருது. இந்த pain வந்தப்போதான் refactoring தேவைப்படுது.

## Mental Model

Refactoring என்பது feature இல்லை. இது **interest payment** மாதிரி.

நீங்கள் வேகமாக code எழுதினீர்கள், shortcuts எடுத்தீர்கள். அந்த debt-க்கு இப்போ interest கட்ட வேண்டும். Refactor பண்ணும்போது external behavior மாறாமல், internal structure-ஐ மட்டும் improve பண்றீர்கள்.

முக்கியமான mental model: **Code is a living asset, not a one-time artifact.** Asset depreciate ஆகும், maintenance தேவை.

## How It Works

Refactoring என்பது big rewrite இல்லை. Small, safe steps.

1. **Safety net முதலில்.** Tests இருக்கா? இல்லைன்னா, முதல்ல characterization tests எழுதுங்கள். இப்போதைய behavior என்னன்னு capture பண்ணுங்கள். இல்லாம refactor பண்ணுவது blindfolded-ல car drive பண்ணுவது மாதிரி.
2. **Small steps.** ஒரு function-ஐ extract பண்ணுங்கள், ஒரு duplication அகற்றுங்கள். Commit பண்ணுங்கள். Green build திரும்ப வரட்டும்.
3. **Behavior unchanged.** Refactor-க்கு பிறகு existing tests எல்லாம் pass ஆகணும். API contract, database schema external interface மாறக்கூடாது.
4. **Understand before touch.** ஏன் இந்த code இப்படி இருக்குன்னு reasoning பண்ணுங்கள். Hidden assumption இருக்கலாம்.

இது craftsmanship இல்லை. Operabilityக்கு தேவையான discipline.

## Architectural Reasoning

Refactor எப்போ useful?

* **Change cost அதிகரிக்கும் போது.** அடுத்த 3 features எல்லாம் அதே messy module-ஐ தொட வேண்டும் என்றால், முதலில் அதை clean பண்ணுவது cheaper.
* **Risk அதிகரிக்கும் போது.** Production incident வந்தப்போது root cause தெரியாமல் அலையறீங்கன்னா, coupling அதிகம்.
* **Team velocity குறையும் போது.** New developer productivity 2 weeks ஆகுதுன்னா, knowledge silo + code complexity இரண்டும் காரணம்.

Refactor vs Rewrite என்ற தேர்வு முக்கியம். Rewrite என்பது control தரும், ஆனால் business க்கு zero value கொடுக்கும் காலம். Refactor என்பது incremental value protect பண்ணும்.

ஒரு architect இதை எப்படி decide பண்ணுவார்? Constraint பார்ப்பார்: deadline, risk tolerance, test coverage, team size. Test coverage குறைவாக இருந்து deadline tight ஆ இருந்தால், refactor-ஐ பெரிதாக்கக்கூடாது. Strategic seams உருவாக்குவதில் focus பண்ணுங்கள்.

## Trade-offs

**Short term slowdown vs long term speed.** Refactor sprint-ல feature delivery குறையும். ஆனால் அடுத்த 6 மாதம் velocity double ஆகும். Stakeholder-க்கு இதை explain பண்ணுவது கடினம்.

**Risk of introducing bugs.** Tests இல்லாமல் refactor பண்ணினால் regression வரும். அதனால் safety net cost முதலில் வரும்.

**Scope creep.** "சரி clean பண்ணிட்டோம், இப்போ feature-ம் மாத்திடலாம்" என்று refactor scope விரிந்து விடும். Refactor-ல behavior change mix பண்ணாதீர்கள். Separate commits.

**Operability vs elegance.** Perfect clean architecture வேண்டும் என்று over-engineer பண்ணினால் complexity அதிகரிக்கும். Refactor என்பது enough clarity, not perfection.

## Practical Example

Enterprise order service. `OrderService.create()`-ல payment validation logic, inventory check, discount calculation எல்லாம் ஒரே 400 lines function-ல இருக்கு. API layer-லயும் worker-லயும் duplicate validation இருக்கு.

Problem: discount rule மாற்ற வேண்டும். மூன்று இடத்துல மாற்ற வேண்டும். Test இல்லை. ஒரு மாற்றம் மற்ற இடத்துல break ஆகும்.

Refactor approach:
* முதலில் integration tests உருவாக்குங்கள், current behavior capture.
* Payment validation-ஐ `PaymentValidator` class-க்கு extract பண்ணுங்கள்.
* Discount calculation-ஐ pure function-ஆக பிரித்து unit tests எழுதுங்கள்.
* API & worker இரண்டும் அதே validator-ஐ call பண்ணும்.

Behavior மாறவில்லை, ஆனால் இனி discount rule மாற்ற 1 file மட்டும் தொட வேண்டும். Onboarding time குறைந்தது.

## Reasoning Challenge
