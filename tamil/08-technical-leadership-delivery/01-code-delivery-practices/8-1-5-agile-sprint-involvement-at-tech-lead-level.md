# Agile/sprint involvement at tech-lead level

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.1.5 — Code & delivery practices

### Problem

ஒரு team-ல sprint planning நடக்குது. Product Owner user stories கொண்டு வர்றார். Team-ம் estimate போடுது. Sprint start ஆகுது. 2 வாரம் கழித்து பார்த்தால்:

* 50% story-கள் incomplete
* code review stuck ஆகியிருக்கு
* production-ல bug வந்திருக்கு
* tech debt-ஐ யாரும் touch பண்ண முடியல

Tech lead இருக்கார், ஆனா அவர் just coding பண்ணிட்டு இருக்கார். Sprint-ல அவர் கிட்ட impact இல்ல.

இதுதான் பிரச்சனை. Tech lead-ஐ senior developer-ஆ மட்டும் வைத்தால், delivery predictable ஆகாது.

**What goes wrong if we don't have this?** Planning unrealistic ஆகும், technical risk தெரியாம commit ஆகும், integration கடைசி நாளில் தெரியும், team alignment இருக்காது.

### Mental Model

Tech lead-ன் வேலை code எழுதுவது அல்ல. Tech lead என்பவர் **engineering reality-க்கும் business planning-க்கும் இடையே bridge**.

அவர் backlog-ஐ engineering lens-ல filter பண்ணுபவர். What is feasible, what is risky, what creates coupling, what will increase maintenance cost.

ஒரு sprint-ல tech lead involvement என்பது:

* **Technical compass** - direction சரியா?
* **Risk radar** - என்ன break ஆகும்?
* **Quality gate** - Definition of Done என்ன?
* **Team multiplier** - junior-களை unblock பண்ணுதல்

### How It Works

Sprint-ல tech lead involvement என்பது daily standup-ல கலந்து கொள்வது அல்ல. Timing முக்கியம்.

**Backlog Refinement:** Story split ஆகியிருக்கா? Acceptance criteria clear-ஆ? Hidden technical dependencies இருக்கா? Database migration வேணுமா? API breaking change வருமா? இதை tech lead early-ல catch பண்ணணும்.

**Sprint Planning:** Team capacity-ஐ tech lead புரிஞ்சிருப்பார். WIP limit, current production incidents, on-call load இதெல்லாம் factor. "இந்த story 3 points-க்கு போகாது, 5 points, ஏனென்றால் service mesh-ல retry logic சேர்க்கணும்" என்று realistic estimate வரணும்.

**Design & Review:** Complex story-க்கு light-weight design discussion. Tech lead 30 mins-ல architecture sketch பண்ணி, trade-off explain பண்ணி, team-ஐ align பண்ணுவார். Code review-ல quality bar set பண்ணுவார்.

**Delivery:** CI/CD pipeline healthy-ஆ? Test coverage? Rollback plan? Production deployment checklist? இது tech lead-ன் ownership.

### Architectural Reasoning

Tech lead ஏன் sprint-ல deep involvement வேண்டும்?

Constraint: Business wants speed, engineering wants reliability. இரண்டுக்கும் இடையில் tech lead தான் trade-off decide பண்ணுவார்.

Options:
1. Tech lead as IC only - fast individual output, but team bottleneck
2. Tech lead as manager only - process follows, technical quality drops
3. Tech lead as enabler - technical direction + coaching

Architect ஆக நீங்கள் choose பண்ணுவது option 3. Because scalability என்பது team scalability. One senior cannot be single point of failure.

Decision consequence: Tech lead-ன் coding time குறையும். அது okay. அவர் leverage அதிகம். One design decision saves 20 hours of rework.

### Trade-offs

**Speed vs Quality:** Tech lead strict definition of done வைத்தால் sprint velocity குறையும். ஆனா production incident குறையும். இதை balance பண்ணணும்.

**Autonomy vs Alignment:** Team-க்கு freedom கொடுத்தால் innovation வரும். ஆனா inconsistent architecture வரும். Tech lead periodic alignment செய்யணும், micromanage பண்ணக்கூடாது.

**Visibility vs Overhead:** Tech lead எல்லா story-லயும் comment போட்டால் bottleneck ஆகிடுவார். Focus on high-risk stories மட்டும். Not every PR review.

Failure mode: Tech lead review-க்காக wait பண்ணும் team. இதை avoid பண்ண, review SLA set பண்ணு, delegation பண்ணு.

### Practical Example

Enterprise payment service-ல quarterly goal: new refund flow launch.

Sprint planning-ல PO 5 stories கொண்டு வரார். Tech lead கேட்கிறார்:

* Refund flow depends on reconciliation service, அது இப்போ legacy DB-ல இருக்கு. Latency high.
* Payment gateway timeout handling இல்ல.
* No idempotency key in current API.

Tech lead proposes: sprint-ல 2 stories மட்டும் take பண்ணி, முதல் 3 days-ல spike பண்ணி feasibility confirm பண்ணுவோம். மற்ற 3 stories next sprint-க்கு shift.

Result: team didn't waste 2 weeks on blocked work. Architecture decision early-ல வந்தது. Production incident தவிர்க்கப்பட்டது.

### Reasoning Challenge

உங்கள் team-ல 20 developers. 3 microservices teams. Tech lead-க்கு daily standup-ல 15 PR-கள் review-க்கு வருது. Sprint planning-ல எல்லா story-க்கும் tech lead தான் design பண்ணுறார். Team velocity drop ஆகுது, tech lead burnout ஆகுது.

இங்கே என்ன problem? Tech lead involvement-ஐ எப்படி redesign பண்ணுவீர்கள்? யாருக்கு delegate பண்ணுவீர்கள்? என்ன trade-off accept பண்ணுவீர்கள்?

### Key Takeaways

* Tech lead-ன் value sprint planning மற்றும் refinement-ல தான் உருவாகும், coding hours-ல அல்ல
* Engineering reality-ஐ backlog-ல reflect பண்ணுவது tech lead-ன் core job
* High-risk technical decisions early-ல catch பண்ணு, late-ல அல்ல
* Quality gate, risk radar, team multiplier - இதுதான் sprint-ல tech lead-ன் 3 roles
* Involvement என்பது control அல்ல, enablement
