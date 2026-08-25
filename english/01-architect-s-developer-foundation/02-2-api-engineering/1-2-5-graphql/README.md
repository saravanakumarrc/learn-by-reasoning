# GraphQL

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.2.5 — 2. API engineering

### The problem

REST forces the API designer to decide the shape of every response in advance.

You end up with:
* **Over-fetching:** Mobile client needs `user.id` and `name`, gets `email`, `profile`, `orders` too.
* **Under-fetching:** Needs `user` + `orders.items.price`, makes 3 round trips.
* **Versioning churn:** New field needed? Add `/v2/` or duplicate endpoints.
* **Frontend coupling:** Backends must anticipate every client data need.

The constraint is real: producers and consumers evolve at different speeds, and network is expensive. The problem is not CRUD, it's *data shaping*.

### Mental model

GraphQL inverts control. Instead of the server deciding the shape, the client declares exactly what it needs in a single request.

Think of it as a typed query language over your domain model. One endpoint, one schema, client-driven selection set.

```mermaid
flowchart LR
    Client -->|POST /graphql { query }| Gateway
    Gateway --> Schema
    Schema --> ResolverA[Resolver]
    Schema --> ResolverB[Resolver]
    ResolverA --> Service1[(Service)]
    ResolverB --> Service2[(Service)]
```

### How it works

Essential mechanism, not feature list:

* **Schema:** A single source of truth describing types, fields, and types. `type User { id, name, orders: [Order] }`
* **Query language:** Client sends a declarative query. Server validates against schema.
* **Resolvers:** Per-field functions that map the abstract graph to real services/databases.

Example:
```graphql
query {
  user(id: "123") {
    name
    orders(last: 5) { total }
  }
}
```
Server executes only those resolvers, returns exactly that shape. No extra endpoints.

### Architectural reasoning

When it helps:

* **Multiple heterogeneous clients** - web, mobile, internal tools all consume same backend with different data needs.
* **Frontend autonomy** - Product teams can add fields without backend release.
* **Evolving UIs** - Feature flags for fields, no version explosion.

Alternatives:
* **REST** - Predictable caching, simple. Best for public, stable resources and HTTP cacheability.
* **gRPC** - Efficient, strongly typed, best for service-to-service.
* **tRPC / schema-first REST** - Type safety without GraphQL complexity.

Choose GraphQL when *client data shape variability* is the primary constraint, not raw throughput.

### Trade-offs and failure modes

* **Caching is hard.** REST URLs are naturally cacheable. GraphQL uses one URL with a POST body. You need persisted queries, query hashing, or a CDN-aware layer. Without it, you lose HTTP caching.
* **N+1 and resolver abuse.** Client asks for `users { orders { items { seller } } }`. Naive resolvers = query explosion. You need DataLoader batching, query complexity analysis, and depth limiting.
* **Operational complexity.** Schema is a contract. Changes are breaking if you remove fields. You need schema registry, versioned evolution, and monitoring of query cost.
* **Over-privileging client.** Clients can request expensive graphs. Must enforce authorization per field and cost limits.

Failure mode to remember: GraphQL feels cheap to the client, expensive to the server. An unguarded endpoint becomes a DDoS vector.

### Example

Enterprise e-commerce platform. Web, iOS, Android, and partner portal share one backend.

REST would require `/users`, `/users/{id}/orders`, `/orders/{id}/items` and versioned expansions for each client.

With GraphQL: one schema. Mobile requests minimal fields for list view. Web requests full profile + recommendations. Partner requests pricing fields only if authorized.

Frontend ships independently. Backend adds `user.preferences` field once, all clients opt-in when ready. No `/v2` needed.

### Reasoning challenge

You are designing an AI Solution Architect for a high-traffic public API with strict SLAs and heavy CDN caching requirements. Product wants rapid UI iteration.

Do you start with GraphQL, REST, or a hybrid? What guardrails would you put in place if you choose GraphQL?

### Key takeaway

* GraphQL solves client-driven data shaping and reduces round trips, not CRUD.
* One endpoint + schema + resolvers gives frontend autonomy at the cost of server complexity.
* Choose it for many clients with different data needs and rapid UI evolution; avoid it when caching, simplicity, and service-to-service efficiency dominate.
* Architect for cost control: query complexity limits, persisted queries, DataLoader, field-level auth.
