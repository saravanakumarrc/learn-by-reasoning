# AI Solution Architect Learning Path — Why This Curriculum Is Shaped This Way

## The goal, restated

This curriculum exists to build **reasoning ability**, not a memorized glossary. The target
outcome, in your own words:

> "I don't remember the exact rule, but I understand the forces involved. Let me reason
> through the problem."

Every phase below should be read with that test in mind. A phase has done its job when you
can explain a trade-off from first principles, not when you can recite its topic list.

## The five-stage progression

Phases are grouped into the five stages from the product vision. The boundaries are soft,
not hard gates — some later-numbered phases (Cloud, Security) already carry Solution-Architect
depth, and Phase 9 is intentionally a short capstone rather than a long stage:

| Stage | Phases |
|---|---|
| Developer | 1-2 |
| Senior Developer | 3-4 |
| Technical Lead | 5-8 |
| Solution Architect | 9 (capstone) |
| AI Solution Architect | 10-25 |

## Why this order

Three ordering principles were applied when this curriculum was reorganized:

1. **No forward references where avoidable.** A topic isn't introduced until its prerequisites
   exist. Distributed systems (3) comes before data architecture (4) because consistency
   problems show up in databases first, but are caused by distributed-systems physics.
   Tool calling (14) comes before agents (15) because an agent is, structurally, a tool-calling
   loop.

   Two exceptions remain, flagged in their own phase READMEs: **AI-specific data** (inside
   Phase 4) and **AI security** (inside Phase 6) are previewed early because they belong
   naturally with their non-AI siblings, even though they won't fully click until Phase 10+
   and Phase 15+ respectively. Treat first contact with those two sections as a skim, and
   plan a deliberate second pass later.

2. **Evaluation and reliability are extended, not bolted on once.** Phase 2 teaches testing
   and observability for ordinary software; Phase 19 (LLMOps) and Phase 18 (AI Evaluation)
   extend those same reflexes into AI-specific failure modes, rather than introducing the
   entire discipline from scratch at the end. Same pattern for cost (Phase 7 → Phase 20) and
   reliability (Phase 7 → Phase 21).

3. **Two system-design capstones, not one.** Phase 9 asks you to design a traditional
   system end-to-end with no AI involved — proof you've actually internalized Phases 1-8
   before AI adds another layer of complexity on top. Phase 24 repeats the exercise with AI
   in the mix. If Phase 9 is hard, Phase 24 will be much harder than it needs to be.

## Known gaps, honestly

Two phases (21 — AI Reliability, 24 — AI System Design) and one section (25 — The ultimate
learning progression) don't have topics defined yet in the tracker. Their READMEs note what's
missing. This curriculum is a living document, not a finished one — extend it as you go rather
than treating the absence of a topic as "not needed."

## How to use these READMEs

Every phase folder has a `README.md` explaining **why the phase exists, where it sits in the
sequence, and the one reasoning question that phase should leave you able to answer.** Every
section folder has a shorter `README.md` explaining what that section covers and why it's
grouped the way it is. Read the phase README before starting its topics — it's the connective
tissue that keeps this from feeling like isolated bits of information.
