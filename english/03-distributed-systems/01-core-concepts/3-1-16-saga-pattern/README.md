# Saga pattern

> **Learning Path:** Distributed Systems
> **Section:** 2.1.16 — Core concepts

**The problem**

You need a business transaction that spans multiple services, each with its own database. 
Create an order requires Payment to charge, Inventory to reserve stock, and Shipping to schedule delivery.

With a monolith you can wrap this in one ACID transaction. With distributed services you cannot. 
2PC can give atomicity but it couples services, blocks resources, and fails badly at scale.

The constraint is real: services must stay autonomous, available, and independently deployable. You also need consistency for the business outcome, not just per-service consistency.

So you need a way to make a multi-step business process succeed or fail without distributed locks.

**Mental model**

A Saga is a long-running business transaction composed of local transactions in each service, linked by compensating actions.

Think of booking a trip: you book flight, then hotel, then car. If the car fails, you cancel hotel and flight. You don't hold all three reservations open indefinitely waiting for a global commit.

The Saga makes the whole process eventually consistent. It commits step by step, and if a step fails it runs compensations backwards to undo what was already done.

**How it works**

Each step is a local transaction that changes state in one service and emits an event.

Two coordination styles exist:

*Orchestration*: a central saga orchestrator drives the steps and decides compensations.
*Choreography*: services listen to events and decide their own next step and compensation.

Essential mechanism is the same: for every forward action there is a compensating action.

```mermaid
sequenceDiagram
    participant C as Client
    participant O as Order Service
    participant P as Payment Service
    participant I as Inventory Service
    participant S as Shipping Service

    C->>O: Create Order
    O->>P: Reserve Payment
    P-->>O: Payment Reserved
    O->>I: Reserve Inventory
    I-->>O: Inventory Reserved
    O->>S: Schedule Shipping
    S-->>O: Shipping Scheduled
    O-->>C: Order Confirmed

    Note over O,P,I,S: If any step fails → run compensations in reverse
```

Forward: Reserve Payment -> Reserve Inventory -> Schedule Shipping
Compensation: Cancel Shipping -> Release Inventory -> Refund Payment

**Architectural reasoning**

When it helps: multi-service business processes that need eventual consistency, not immediate atomicity. Long running processes with human steps.

What it solves: eliminates distributed locks and cross-service transactions while keeping services autonomous. Allows independent scaling and deployment.

Alternatives:
* 2PC / XA: strong consistency, but coupling, blocking, poor availability.
* Monolith: simple, but loses autonomy and scale.
* Eventual consistency with manual reconciliation: cheaper, but error prone.

Choose Saga when you can tolerate temporary inconsistency and define meaningful compensations. Don't choose it when you need strict atomicity for financial settlement in the same millisecond, or when compensation is impossible or illegal.

**Trade-offs and failure modes**

Eventual consistency is the core trade-off. Users may see a partially completed order for a short window.

Compensation complexity grows with steps. Compensations must be idempotent and safe to retry. Some actions are not compensatable - e.g., sending an email can't be unsent.

Failure modes to design for:
* Partial failure: step succeeds, next fails. You must guarantee compensation runs.
* Compensation failure: the undo itself fails. You need a manual intervention path or a retry with escalation.
* Duplicate messages: at-least-once delivery means steps must be idempotent.
* Long sagas: state must be persisted and recoverable after crashes. Orchestrator state becomes critical.

Operational cost: you trade database coordination for application-level process management and observability.

**Example**

E-commerce order in microservices:

Order Service creates an order aggregate with status PENDING. It publishes OrderCreated.

Payment Service consumes it, charges card locally, publishes PaymentReserved. If charge fails, it publishes PaymentFailed.

Inventory Service reserves items, publishes InventoryReserved. If stock insufficient, publishes InventoryFailed.

On PaymentFailed or InventoryFailed, Order Service triggers compensations: cancel any reserved payment, release inventory. Final state is ORDER_CANCELLED.

All steps are local commits. The business invariant "order is either fully fulfilled or fully cancelled" is eventually enforced.

**Reasoning challenge**

You are designing a funds transfer between banks in different regions. Transfer must debit source account, credit destination account, and send notification. Debit is reversible for 24h, credit is not reversible once posted. Latency requirement is <2 seconds.

Would you use a Saga, and if so which coordination style? What is the failure risk you must accept?

**Key takeaway**

* Saga exists because distributed ACID is impractical at scale; you need business-level consistency instead of database-level.
* A Saga is a sequence of local transactions with compensating actions, not a distributed lock.
* Choose orchestration for visibility and control, choreography for loose coupling. Both accept eventual consistency.
* Design compensations first. If you cannot compensate safely, Saga is the wrong pattern.
