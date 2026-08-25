# Phase 15: Agentic AI

**Stage:** AI Solution Architect

## Why this phase exists here

Builds directly on tool calling — structurally, an agent is a loop that plans, calls tools, and observes results. This is also where Phase 6's AI security concepts (prompt injection, excessive agency) stop being abstract and become concrete; worth revisiting that section now.

## The question this phase should leave you able to answer

> Do you actually need a full agent here, or would a deterministic workflow do the same job more reliably?

## Sections in this phase
- **[Agent fundamentals](01-agent-fundamentals/README.md)** — Perception, reasoning, planning, and action as an explicit, inspectable loop.
- **[Agent patterns](02-agent-patterns/README.md)** — ReAct, planner/executor, supervisor — named shapes for that loop, so you can pick one on purpose instead of inventing your own each time.
- **[Agent state](03-agent-state/README.md)** — How an agent survives interruption, a crash, or a task that spans days.

---
[← Back to curriculum overview](../README.md)
