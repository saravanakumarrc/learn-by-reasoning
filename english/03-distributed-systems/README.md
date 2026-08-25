# Phase 3: Distributed Systems

**Stage:** Senior Developer

## Why this phase exists here

The moment a system crosses a process boundary, the failure modes change completely. This is the single biggest mental-model shift in the whole curriculum — most bad architecture comes from treating a distributed call like a local function call.

## The question this phase should leave you able to answer

> Why can't we just add a try/catch and call it done, the way we did in Phase 1?

## Sections in this phase
- **[Core concepts](01-core-concepts/README.md)** — The physics of distributed systems — CAP, consensus, ordering, partial failure. These are constraints you design around, not techniques you apply.
- **[Messaging](02-messaging/README.md)** — How decoupled components actually communicate in practice — the backbone that event-driven architecture, and later agent-to-agent communication, both build on.

---
[← Back to curriculum overview](../README.md)
