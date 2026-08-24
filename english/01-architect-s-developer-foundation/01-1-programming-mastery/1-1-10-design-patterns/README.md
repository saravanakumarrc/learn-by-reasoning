# Design patterns

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.10 — 1. Programming mastery

### The problem

You build the same solution repeatedly with different names. One team needs flexible payment processing, another needs pluggable pricing rules, another needs to decouple UI from domain events. Each time you end up reinventing the same structural trade-offs: how to vary behavior without scattering conditionals, how to create objects without coupling callers to concrete types, how to keep components decoupled while still communicating.

The constraint is not lack of code skill. It is communication and repeatability under change. Without a shared vocabulary, teams re-solve the same forces differently, creating inconsistency, hidden coupling, and brittle code that breaks on the next requirement.

Design patterns exist to name those recurring forces and the proven trade-offs that resolve them.

### Mental model

A pattern is not a code template. It is:

**Context + Forces → Solution with Consequences**

Context: where you are, e.g. many algorithms for one task.
Forces: flexibility vs complexity, decoupling vs indirection, reuse vs readability.
Solution: a structure for organizing code to resolve the forces.
Consequences: what you gain and what you pay for.

Think of patterns as architectural shorthand. When an architect says "Strategy", the team understands: behavior is encapsulated and interchangeable, selection is externalized, and we accept extra indirection for testability.

### How it works

Use patterns only after you can name the forces.

1. Identify the problem: what varies, what is stable, who creates objects, who needs notification.
2. List forces: change frequency, team boundaries, performance, testability.
3. Map to a pattern family, not a specific class diagram.
   * Creational: who constructs and when. Factory, DI container.
   * Structural: how components compose. Adapter, Decorator.
   * Behavioral: how objects collaborate. Strategy, Observer, Command.
4. Choose based on trade-offs, not familiarity.
5. Implement minimally to resolve the forces.

### Architectural reasoning

Patterns help when change is expected in a specific dimension.

* **Strategy** helps when you have one interface with multiple interchangeable algorithms. You get testable policies and no giant switch.
* **Factory / Dependency Injection** helps when object creation has constraints: lifetimes, configuration, test doubles. You decouple construction from use.
* **Observer / Event** helps when producers and consumers must evolve independently and you need loose temporal coupling.
* **Adapter** helps when integrating bounded contexts with incompatible contracts.

Alternatives always exist: inline conditionals, inheritance, service locators. Patterns are chosen because they make the trade-off explicit.

```
flowchart LR
    RequirementChange[Changing requirement] --> Forces[Forces: flexibility vs complexity]
    Forces --> Decision{Choose structure}
    Decision -->|Vary algorithm| Strategy[Strategy]
    Decision -->|Vary construction| Factory[Factory/DI]
    Decision -->|Vary communication| Observer[Observer/Event]
    Strategy --> Tradeoffs[More indirection, better testability]
    Factory --> Tradeoffs
    Observer --> Tradeoffs
```

### Trade-offs and failure modes

The important trade-offs an architect remembers:

* **Indirection cost.** Patterns add abstractions. You pay in readability, stack depth, and cognitive load.
* **Premature generality.** Applying a pattern before the forces exist creates dead abstractions.
* **Pattern fetishism.** Naming a pattern does not make a design good. The forces must justify it.
* **Leaky boundaries.** Behavioral patterns like Observer can become implicit coupling through events if contracts are not owned.

Failure mode: using Singleton for global config because it is easy. You gain convenience, you lose testability, lifecycle clarity, and safe scaling.

### Example

Enterprise payment processing with multiple providers.

Forces: new providers appear, each with different auth, retry, and response shape. Business rules for fees change per region. Core order logic must not change.

Decision: Strategy for provider execution, Factory for provider creation from config, Adapter to normalize provider responses to internal model.

Result: adding a provider = new strategy + registration, no changes to order flow. Tests inject fake strategies. The trade-off is extra interfaces and wiring.

### Reasoning challenge

You need a service that routes LLM calls to different providers. Providers differ in auth, rate limits, retries, and output schema. Product wants to A/B test providers per tenant and to swap providers without redeploy.

Do you reach for Strategy, Factory, Adapter, or all three? What forces make each appropriate, and what is the first thing that would break if you used a single static class with if-else?

### Key takeaway

* Patterns name forces, not code. Learn the forces first.
* Choose patterns to make a specific kind of change cheap, not to be clever.
* Every pattern buys flexibility with indirection. Pay only when you need it.
* At architecture level, patterns are about team communication and predictable evolution, not class diagrams.
