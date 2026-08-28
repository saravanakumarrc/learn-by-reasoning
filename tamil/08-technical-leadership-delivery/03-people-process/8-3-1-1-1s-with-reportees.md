# 1:1s with reportees

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.3.1 — People & process

# 1:1s with reportees

## Problem

நீங்கள் tech lead / engineering manager. Team-ல 6-8 engineers. Jira-ல tickets close ஆகுது, standup-ல "on track" என்கிறார்கள். ஆனால் delivery slow ஆகுது, code review-ல quality drop ஆகுது, ஒரு senior engineer இரண்டு வாரமாக quiet ஆக இருக்கார்.

இதை standup-ல பிடிக்க முடியுமா? Slack-ல பிடிக்க முடியுமா? No.

Standup என்பது team sync. 1:1 என்பது manager-reportee இடையேயான calibration channel. 

Problem என்னவென்றால், technical issues வெளியே தெரியும். People issues, career blockers, process friction, trust issues silent-ஆக accumulate ஆகும். அதை catch பண்ண நமக்கு dedicated, safe space தேவை.

## Mental Model

1:1 என்பது status update meeting அல்ல. அது **feedback loop**.

ஒரு distributed system-ல health check போல. Metrics பார்த்தால் போதாது, logs மற்றும் traces பார்க்க வேண்டும். Reportee-வின் context, motivation, blockers, growth intent அவர்கள் சொல்லாமல் தெரியாது.

Mental model: **Reportee owns agenda, manager owns listening and action.**

## How It Works

Cadence: weekly 30-45 min stable. Month end-ல 60 min career check.

Structure simple:

1. **Check-in**: "இந்த வாரம் எப்படி போயிட்டு இருக்கு? Energy level எப்படி இருக்கு?"
2. **Blockers**: Technical, process, people. என்ன உங்களை slow பண்ணுது?
3. **Work**: Priorities clear-ஆ? Scope realistic-ஆ? Overcommit இருக்கா?
4. **Growth**: Skill வளர்க்க வேண்டியது என்ன? Career path பற்றி என்ன நினைக்கிறீர்கள்?
5. **Manager support**: நான் என்ன support பண்ண முடியும்?

Notes எடுக்கவும், action items track பண்ணவும். Same notes next 1:1-ல review.

1:1 confidential. Performance rating discussion-க்கு மட்டும் அல்ல, growth conversation-க்காக.

## Architectural Reasoning

When 1:1 useful ஆகும்?

- New reportee first 90 days
- Delivery pressure அதிகம் இருக்கும் quarter
- Team restructuring, re-org
- Engineer disengaged signs: missed deadlines, low PR quality, less participation

Constraints:

- Manager time limited. 8 reportees × 45 min = 6 hrs/week
- Reportee may not open up immediately
- If manager uses it for status, trust break ஆகும்

Alternatives:

- Async check-in via doc: cheap, but no nuance
- Team retro: good for process, not personal growth
- Skip 1:1: short term gain, long term attrition, silent failure

Decision: 1:1 என்பது operational overhead மாதிரி தெரியும். ஆனால் இது early warning system. Small cost now vs big cost later.

## Trade-offs

**Time vs Insight**: 1:1 time cost உண்மையானது. ஆனால் இது தவறான assumption-ஐ early catch பண்ணும். அதனால் rework குறையும்.

**Psychological safety vs Evaluation fear**: Reportee performance review பற்றி பயந்தால் honest ஆக மாட்டார். Manager must separate coaching from evaluation. 1:1-ல punishment இல்லை.

**Manager bias**: Manager தனது agenda push பண்ணினால் 1:1 reportee-வின் meeting ஆக மாறும். Agenda ownership flip பண்ண வேண்டும்.

Failure mode: 1:1 becomes "What did you do this week?" status report. அப்போது engineer standup-ல சொன்னதை repeat பண்ணுவார், value zero.

## Practical Example

உங்களிடம் payment service team இருக்கு. Senior engineer Arjun. Last 2 sprints-ல PR throughput குறைந்து விட்டது. Standup-ல சொல்வது "still working".

1:1-ல Arjun சொல்கிறார்: "New microservices pattern கத்துக்க வேண்டி இருக்கு, ஆனால் deadline pressure-ல time இல்லை. Tech lead-க்கு என் confusion கேட்க தயக்கம்".

இது தெரிந்ததும் manager என்ன செய்யலாம்? Pairing session schedule, scope trim, learning budget allocate.

இல்லாமல் இருந்தால்? Arjun quiet quit, quality drop, eventually attrition. Cost >> 45 min.

## Reasoning Challenge

உங்களிடம் 2 junior engineers இருக்கிறார்கள். இருவரும் same tech stack-ல work செய்கிறார்கள். ஒருவர் confident, proactive. இன்னொருவர் always waiting for instructions.

நீங்கள் 1:1-ல என்ன கேள்விகள் கேட்பீர்கள்? Manager support-ஐ எப்படி customize பண்ணுவீர்கள்? Generic advice கொடுக்காமல், ஒவ்வொருவருக்கும் வேறு approach எப்படி?

## Key Takeaways

- 1:1 என்பது status meeting
