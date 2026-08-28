# Definition of done

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.1.6 — Code & delivery practices

## Problem

நீங்கள் 8 பேர் கொண்ட team-ஐ lead பண்ணுறீங்க. Sprint review வந்துச்சு. Product Owner சொல்றார்: "இந்த story done தானே?" Developer சொல்றார்: "Code merge ஆயிடுச்சு, done." QA சொல்றார்: "Test cases எழுதல, edge cases check பண்ணல." DevOps சொல்றார்: "Prod-ல deploy பண்ணல, monitoring இல்ல."

யாருக்கும் "done" என்றால் என்னன்னு ஒரே definition இல்ல. இதனால என்ன ஆகும்?

Work பாதியில் நின்னு போகும். Rework வரும். அடுத்த sprint-ல இதே story-க்கு bug fix வரும். Release-க்கு முன் last minute firefighting. Team trust குறையும்.

இந்த pain தான் Definition of Done வர காரணம்.

## Mental Model

Definition of Done என்பது ஒரு checklist இல்ல. அது team-க்குள் ஒரு **shared contract**.

> ஒரு work item-ஐ நாம் "done" என்று சொல்லும்போது, அது எந்த quality bar-ஐ cross பண்ணியிருக்கணும் என்பதை தெளிவாக்குவது.

Done என்பது code written இல்ல. Done என்பது **value safely delivered** என்ற நிலை.

## How It Works

Team ஒன்று கூடி, அந்த team-ன் context-க்கு ஏற்ற quality bar-ஐ define பண்ணும். அது transparent ஆக visible இருக்கும். எல்லா story, task, bug-க்கும் அதே bar apply ஆகும்.

ஒரு typical Definition of Done:

- Code complete & peer reviewed
- Unit tests written & passing
- Integration tests passing
- Code merged to main via CI/CD
- Deployed to staging & validated
- Acceptance criteria verified by PO
- Documentation / runbook updated
- Monitoring & alerting in place
- No critical / high tech debt left

இது team decide பண்ணும். Startup team-க்கும் enterprise team-க்கும் வித்தியாசம் இருக்கும்.

இந்த checklist-ஐ Jira, board-ல visible ஆக வச்சுக்கலாம். Done என்று mark பண்ணுறதுக்கு முன் checklist tick ஆகணும்.

## Architectural Reasoning

இது எதை solve பண்ணுது?

**Ambiguity & handoff friction.** Developer, QA, DevOps, Product எல்லாருக்கும் ஒரே expectation. Handoff இல்லாமல் flow ஆகும்.

**Quality as habit, not heroics.** Review, test, deploy எல்லாம் last minute-ல அல்ல, story வாழ்க்கை முழுக்க நடக்கும்.

**Flow & predictability.** "Done" என்பது binary. இது WIP reduce பண்ணும், sprint commitment reliable ஆகும்.

Alternatives? 
- Ad-hoc definition per person. -> Chaos.
- Manager decides done. -> Bottleneck.
- No definition. -> Rework & trust loss.

Definition of Done-ஐ choose பண்ணுறது team maturity, risk tolerance, release cadence-ஐ பொறுத்தது. High-risk financial service-ல Definition of Done கடுமையாக இருக்கும். Internal tool prototype-ல சற்று light ஆக இருக்கலாம்.

## Trade-offs

**Strict vs fast.** Checklist அதிகமானால் cycle time increase ஆகும். Too loose ஆனால் tech debt accumulate ஆகும். Balance தேவை.

**Standardization vs context.** ஒரே Definition of Done எல்லா team-க்கும் பொருந்தாது. Platform team vs feature team வித்தியாசம் வேண்டும். Over-standardization kills autonomy.

**Automation dependency.** Definition of Done-ல CI/CD, test automation இருந்தால், அது process-ஐ enforce பண்ணும். Manual checklist trust-ஐ நம்பி இருக்கும், அது fail ஆகும்.

Failure mode: Checklist-ஐ tick box ஆக்கி விடுவது. People game the system. "Test written" என்று fake test வைப்பது. அதனால Definition of Done-ஐ review செய்து evolve பண்ண வேண்டும்.

## Practical Example

ஒரு enterprise payment service-ல refund API add பண்ணுறீங்க.

Definition of Done இல்லாமல்: Developer code push பண்ணார். PO happy. Prod-ல deploy பண்ணும்போது idempotency இல்லாமல் double refund ஆகும். Monitoring இல்லாமல் failure தெரியாது. Rollback செய்ய முடியாது.

Definition of Done உடன்: 
- Idempotency key test உள்ளதா?
- Chaos test - network timeout-ல என்ன நடக்கும்?
- Alert for refund failure rate?
- Runbook update ஆச்சா?

Done என்று mark பண்ணுறதுக்கு முன் இது எல்லாம் செய்ய வேண்டும். Release safe ஆகும்.

## Reasoning Challenge

உங்கள் team microservices-ஐ Kubernetes-ல deploy பண்ணுது. Feature flag use பண்ணுறீங்க. இப்போ ஒரு new feature-க்கு Definition of Done-ல "Deployed to prod" வைக்கலாமா, "Flag enabled for 10% users" வைக்கலாமா? 

எந்த bar தேர்வு செய்வீர்கள்? ஏன்? அதனால் என்ன trade-off வரும்?

## Key Takeaways

- Definition of Done
