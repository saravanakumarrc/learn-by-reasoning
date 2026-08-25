# Aggregates

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.3.9 — 3. Application architecture

**Aggregates**

### 1. The problem

You have a cluster of related domain objects that must stay consistent together. An Order has OrderItems, a total, a status, and a payment. If you update them independently, you get partial writes, race conditions, and invalid states: a cancelled order with new items, a total that doesn't match items, etc.

You need a transactional boundary that is smaller than the whole database and larger than a single row. And you need a place to enforce business invariants.

Without a boundary, you either:
* Lock everything with a big database transaction, which doesn't scale and couples services
* Accept eventual consistency everywhere and write compensating logic for every invariant

### 2. Mental model

An aggregate is a **consistency boundary**. Think of it as a single unit of work with one owner.

The aggregate root is the entry point. All changes to the cluster go through the root, and the root guarantees invariants before the change is accepted. Entities inside the aggregate can reference each other, but nothing outside should hold a direct reference to an internal entity.

```
graph TD
    Client --> AR[Aggregate Root]
    AR --> E1[Entity]
    AR --> E2[Entity]
    AR --> VO[Value Object]
    AR -. enforces invariants .-> State
    Repository -->|load/save whole graph| AR
```

### 3. How it works

* **Aggregate Root:** One entity per aggregate. It owns the lifecycle of children and exposes behavior, not setters.
* **Invariant enforcement:** Business rules like `Order.canCancel()` or `Account.withdraw()` are methods on the root. They check the whole graph before mutating.
* **Repository boundary:** A repository loads the entire aggregate for a unit of work, applies changes via the root, then persists the whole graph. No partial updates to children from outside.
* **Identity:** Children have identity only within the aggregate. The root's ID is the aggregate ID.

This gives you a single place to reason about consistency.

### 4. Architectural reasoning

Use an aggregate when:
* A group of objects must be kept consistent at the same time
* The invariant spans multiple entities
* You want a clear transactional boundary in a domain model

Alternatives:
* **Anemic model + service layer:** Invariants live in services. Easy to write, hard to enforce. Invariants leak across services over time.
* **Eventual consistency + sagas:** Good for cross-service relationships. Accept that consistency is delayed and compensate. Use when aggregates cross bounded context boundaries.
* **One big transaction:** Simple, but creates contention and prevents scaling out.

Decision rule: Model aggregates around business transactions, not tables. The aggregate is the unit of consistency, not the unit of persistence.

### 5. Trade-offs and failure modes

* **Size vs contention.** A large aggregate = more data loaded per transaction, higher lock contention, slower reads/writes. Keep aggregates small and cohesive.
* **Chattiness.** Clients that need only a small part of the aggregate still load the whole graph. Use read models for queries.
* **Cross-aggregate references.** Do not hold direct references between aggregates. Use IDs only. If you need cross-aggregate coordination, use domain events or sagas, not in-memory references.
* **Distributed trap.** Aggregates are a single-process consistency boundary. If you try to make an aggregate span microservices, you reintroduce distributed transactions.

### 6. Example

E-commerce Order aggregate:
Root: `Order`
Children: `OrderItem[]`, `ShippingAddress`, `Payment`
Invariant: `Order.total == sum(items)` and `status` transitions are valid: `Pending -> Paid -> Shipped`, never `Shipped -> Pending`.

All mutations go through `Order.addItem()`, `Order.pay()`, `Order.cancel()`. The repository loads the Order graph, the root validates, then persists. A separate read model serves the order list page.

### 7. Reasoning challenge

You have a `BankAccount` aggregate with `Transaction` entities. Business wants to enforce a daily withdrawal limit across all accounts for a user, and also per account. 

Is the daily limit an invariant of the `BankAccount` aggregate? If not, where does it belong and what consistency model do you need?

### 8. Key takeaway

* An aggregate is a consistency boundary, not a performance optimization.
* The root enforces invariants; children are private implementation details.
* Keep aggregates small, cohesive, and free of cross-aggregate references.
* Use read models for queries, aggregates for writes.
