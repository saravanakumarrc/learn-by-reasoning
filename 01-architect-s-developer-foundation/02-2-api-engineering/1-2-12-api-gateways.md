# API gateways

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.12 — 2. API engineering

## The problem

You have 20-40 microservices behind you. Clients are mobile apps, web frontends, partners, and internal teams.

What problem appears?

* Clients must discover the right service, handle retries, know versions, and deal with different protocols.
* Each service now needs to re-implement auth, rate limiting, logging, request validation, and TLS termination.
* You want to change routing, deprecate v1, or move a service without forcing every client to change.

Centralizing that complexity in the services creates duplication and coupling. Scattering it in clients creates fragility.

An API Gateway is the architectural answer to **north-south traffic** at scale.

## Mental model

Think of it as a front door and a traffic cop, not a business logic layer.

All external requests enter through one logical entry point. The gateway authenticates, shapes, and routes to the right backend. It never contains domain logic; it only enforces cross-cutting concerns.

```mermaid
flowchart LR
    C[Client] --> G[API Gateway]
    G --> A[AuthN/Z]
    G --> R[Rate Limit]
    G --> S1[Service A]
    G --> S2[Service B]
    G --> S3[Service C]
    S1 -.-> DB1[(DB)]
    S2 -.-. DB2[(DB)]
```

## How it works

The essential mechanism is thin, stateless request processing:

* **Routing & composition**: Path/host based routing, and optionally aggregation of multiple backend calls into one response for a client.
* **Protocol & format translation**: HTTP/REST to gRPC, JSON to Avro, etc.
* **Cross-cutting policy**: AuthN/Z, rate limiting, throttling, request validation, caching, request/response transformation.
* **Observability**: Logging, metrics, distributed tracing at the edge.

It sits in front of services. Services stay focused on domain logic.

## Architectural reasoning

**When it helps**

* Many external clients need a stable contract while backends change.
* You need a single place for security, rate limiting, and versioning.
* You want to expose a subset of internal services to partners with different SLAs.

**What it solves**

* Decouples client contract from service topology.
* Avoids duplicating non-functional concerns in every service.
* Provides a choke point for governance and observability.

**Alternatives**

* **Client-side service discovery + direct calls.** Works for small systems, fails at scale with duplicated policy and client complexity.
* **Service Mesh.** Handles east-west traffic between services: mTLS, retries, observability. It does not replace an edge gateway for external clients.
* **Backend for Frontend.** A per-client gateway that composes services. Useful when clients have very different needs, but adds more layers.

Choose a gateway for external ingress. Choose a mesh for internal service-to-service. Often both.

## Trade-offs and failure modes

* **Latency and hot spot.** Every request passes through it. Poorly sized gateway adds p99 latency and becomes a bottleneck.
* **Single point of failure.** If the gateway goes down, everything is unreachable. Must be deployed multi-zone/active-active with health checks.
* **Coupling risk.** Teams start putting business logic in the gateway because it is convenient. That creates a hidden monolith.
* **Thundering herd / amplification.** A gateway that fans out to 5 services for one request can overload backends if not rate limited properly.
* **Config drift.** Routing rules, auth policies, and versions live in gateway config. Without CI/CD for config, you get outages.

## Example

E-commerce mobile app.

Mobile client calls `api.shop.com/checkout`. The gateway:

1. Validates JWT, extracts tenant and user tier.
2. Checks rate limit per user tier.
3. Routes `/checkout` to `checkout-service v2`, but routes internal calls for legacy partners to `checkout-service v1`.
4. Aggregates calls to `pricing-service` and `inventory-service` to build one response.
5. Logs request id and latency for tracing.

Services receive a clean, authenticated request and never see the client.

## Reasoning challenge

You have an internal platform with 50 microservices needing mTLS, retries, and per-service metrics between them. You also have 3 external partner APIs.

Do you put a single API Gateway in front of everything, including internal service-to-service calls? Why or why not?

## Key takeaway

* API Gateway exists to centralize edge concerns and decouple clients from service topology, not to host business logic.
* Use it for north-south ingress; use service mesh for east-west.
* The biggest risks are latency, SPOF, and creeping business logic into the edge.
* Design it as stateless, horizontally scalable, and config-driven with strict change control.
