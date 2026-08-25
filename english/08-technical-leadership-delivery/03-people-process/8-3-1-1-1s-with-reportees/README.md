# 1:1s with reportees

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 24.3.1 — People & process

### 1:1s with reportees

**The problem**

A manager can't scale attention by broadcast. Standups, Slack, and sprint reviews give visibility into *what* is being done. They give almost no signal on *how* the person is doing, what is blocking them personally, and whether the work matches their growth.

As team size grows, information asymmetry increases. The reportee knows the risks, frustrations, and career intent. The manager only sees output. Without a private channel, problems become visible late: attrition, disengagement, misalignment, or technical debt created by someone stretched too thin.

Ad-hoc chats are noisy and reactive. Group forums are unsafe for personal topics. Async updates are efficient but lack trust building.

**Mental model**

Think of a 1:1 as a private control loop for a human system component.

```
mermaid
flowchart LR
    R[Reportee state: work, blockers, energy, growth] --> A[1:1 input]
    M[Manager context: org priorities, risks, opportunities] --> A
    A --> D[Decision / support / unblock]
    D --> R
```

The goal is not status transfer. Status already exists elsewhere. The goal is to detect drift early and adjust trajectory.

The owner of the agenda is the reportee. The manager owns the framing, psychological safety, and follow-through.

**How it works**

Essential mechanism, not a template.

* Cadence: 30-60 min weekly for new / high-risk reportees, bi-weekly for stable. Frequency is a trade-off with manager time.
* Agenda driven by reportee, sent 24h before. Manager adds 1-2 org context items max.
* Structure: 70% reportee, 30% manager. Start with check-in, then blockers, then growth/career.
* Notes are minimal and action-oriented. Decisions and commitments are recorded, not transcripts.
* Consistency > perfection. Same time, same place, protected.

What it is not: a performance review, a 1:1 status meeting, or therapy.

**Architectural reasoning**

When it helps:
* You are leading engineers with autonomy. Work quality depends on context and motivation, not just tickets.
* You need early warning on attrition risk, burnout, or skill mismatch.
* You are making resourcing decisions that require understanding capacity and interest.

Alternatives:
* **Async updates**: cheaper, good for tracking deliverables. Loses nuance and trust.
* **Group 1:1s / team meetings**: scales, but suppresses personal issues.
* **Skip-levels only**: catches systemic issues, misses individual calibration.

Choose 1:1s when the cost of a missed signal > cost of manager time. For senior ICs with high autonomy, less frequent but deeper is better. For new hires, junior engineers, or people in transition, weekly is the default.

**Trade-offs and failure modes**

* Manager time is expensive and non-scalable. Too many 1:1s dilutes depth. Cap total manager 1:1 hours at ~30-40% of week.
* Status creep. The meeting becomes a rehash of Jira. Fix by requiring reportee to bring only blockers and decisions, not updates.
* Manager dominates. Signal degrades to a lecture. Fix by starting with "What do you want to cover?" and timeboxing.
* No follow-through. Trust collapses if action items die. The manager must close the loop next week.
* False intimacy. 1:1s can create expectations of mentorship you can't sustain. Be explicit about scope.

The biggest failure mode is treating 1:1s as HR compliance instead of a feedback system. If you can't articulate what decision it enables, cancel it.

**Example**

Platform team, 8 engineers, 2 managers.

Manager A runs weekly 30-min 1:1s, reportee-owned agenda, notes in a shared doc with only action items. One engineer mentions repeated context switching between incident response and feature work. Over three weeks the pattern emerges. Manager re-negotiates on-call rotation and shields engineer for a 2-week feature sprint. Output stabilizes and attrition risk drops.

Manager B runs ad-hoc chats and relies on Slack. Same engineer quits with one week's notice citing burnout. Signal was present but never captured.

**Reasoning challenge**

Your senior engineer is high performing but has stopped speaking up in 1:1s. They send a one-line agenda: "nothing much". Their output is fine. Do you:
a) Reduce cadence to free time,
b) Push harder for blockers,
c) Change the framing and explicitly probe for growth/career signals?

What trade-off are you making?

**Key takeaway**

* 1:1s exist to reduce information asymmetry and detect drift early, not to track status.
* Reportee owns agenda, manager owns safety and follow-through.
* Consistency and action closure matter more than perfect structure.
* Scale by cadence and depth, not by eliminating the channel.
