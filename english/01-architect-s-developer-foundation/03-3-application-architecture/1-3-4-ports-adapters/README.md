# Ports & adapters

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.3.4 — 3. Application architecture

**Ports & Adapters**

### 1. The problem

Your domain logic starts clean. Then it needs to persist to Postgres, expose an HTTP API, send events to Kafka, call Stripe, and log to CloudWatch.

Soon the business rules for `PlaceOrder` are interwoven with SQL queries, HTTP serialization, and SDK calls. Changing a database or swapping a payment provider means touching core logic. Tests need a real DB or you end up mocking frameworks.

The constraint is not just testability. It's **independence of rate of change**. Business rules change slowly and deliberately. Infrastructure changes fast, by vendor, compliance, and scale.

You need a way to keep the core stable while allowing the edges to move.

### 2. Mental model

Think of the application as an island. The domain core contains business rules and use cases. Ports are the defined sockets on the island's shore. Adapters are the docks and cables that plug external systems into those sockets.

The core never knows about HTTP, Postgres, or Stripe. It only knows about the port interface it defines.

```mermaid
flowchart LR
    subgraph Core
        D[Domain / Use Cases]
        P[Ports - interfaces]
    end
    D --> P
    P --> A1[HTTP Adapter]
    P --> A2[DB Adapter]
    P --> A3[Payment Adapter]
    A1 -.-> Ext1[Clients]
    A2 -.-.-> Ext2[(Postgres)]
    A3 -.-.-> Ext3[Stripe/Adyen]
```

Dependencies point inward. Infrastructure depends on core, never the reverse.

### 3. How it works

A port is an interface owned by the core that describes a capability.

* Driving port: `PlaceOrder`, `GetUser`. The application drives the outside world.
* Driven port: `OrderRepository`, `PaymentGateway`, `EventPublisher`. The outside world drives the application.

The core defines the port contract. Adapters implement it.

```ts
// Core defines the port
interface PaymentPort {
  charge(amount: Money, card: Card): Promise<Result>
}

// Adapter implements it
class StripeAdapter implements PaymentPort { ... }
class AdyenAdapter implements PaymentPort { ... }

// Use case only knows the port
class PlaceOrder {
  constructor(private payment: PaymentPort) {}
  async run(...) {
    await this.payment.charge(...)
  }
}
```

No framework code in the core. No business logic in the adapter.

### 4. Architectural reasoning

When it helps:
* You need to test business logic without infrastructure. Ports are trivial to fake.
* You anticipate swapping implementations: Stripe -> Adyen, Postgres -> DynamoDB, REST -> gRPC.
* You have multiple delivery mechanisms for the same use case: web, CLI, worker.

What it solves vs layered architecture:
Layered architecture still couples layers to specific technologies via implicit contracts. Ports & adapters makes the contract explicit and owned by the core. You can replace an entire layer without touching the core.

Alternatives:
* Direct integration: faster to build, collapses under change.
* Service layer with dependency injection: good, but often still leaks framework types into core.
* Hexagonal/Clean Architecture is the formalization of ports & adapters.

Decision rule: Use it when the cost of future change to external systems exceeds the cost of indirection today. For a throwaway script, don't. For a core domain service that will live years, do.

### 5. Trade-offs and failure modes

* **Indirection tax.** You write interfaces and adapters for things you may never swap. Small services can become over-engineered with 3 layers for a simple CRUD.
* **Leaky ports.** If the port interface is shaped by the adapter, you get infrastructure concerns leaking into core. Example: `PaymentPort.chargeWithStripeId()` is a leak. The port should speak domain language.
* **Adapter proliferation.** Teams create an adapter per use case instead of per capability, leading to duplication.
* **Testing illusion.** You can test core in isolation, but integration tests between ports and real adapters are still required. Don't skip them.

The most common failure is designing ports after the adapter exists. Design the port from the use case first.

### 6. Example

AI inference service.

Core use case: `ClassifyDocument(doc) -> Classification`.

Ports defined by core:
* `ModelPort.infer(text): Prediction`
* `StoragePort.storeResult(id, classification)`

Adapters:
* `OpenAIAdapter implements ModelPort`
* `VertexAdapter implements ModelPort`
* `S3Adapter implements StoragePort`
* `PostgresAdapter implements StoragePort`

Product decides to move from OpenAI to a self-hosted model for cost. Core unchanged. Only the adapter wiring changes. Tests for classification logic run against a fake `ModelPort` with no API calls.

### 7. Reasoning challenge

You have a billing service that currently calls Stripe SDK directly inside the `CreateInvoice` use case. You need to add support for a test payment provider in CI and eventually Adyen in EU. 

Would you introduce a `PaymentPort` now, or wait until you actually need Adyen? What would you put in the port interface to avoid leaking Stripe types, and what is the minimal adapter you can ship today?

### 8. Key takeaway

* Ports & adapters exists to isolate stable business logic from volatile infrastructure by inverting dependencies.
* Core defines ports, adapters implement them. Dependencies point inward.
* Use it when change of external systems is likely and core correctness matters more than initial speed.
* Beware leaky ports and unnecessary indirection; design ports from domain needs, not from the adapter you have.
