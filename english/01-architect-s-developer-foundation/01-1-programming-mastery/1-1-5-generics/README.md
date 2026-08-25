# Generics

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.5 — 1. Programming mastery

### 1. The problem

You need one reusable data structure or service that works for many types, but you cannot lose compile-time type safety.

Before generics the options were:
* **Duplicate code** per type: `IntList`, `StringList`, `UserList`... maintenance nightmare
* **Use Object + casts**: one `List` holding `Object`, cast on every read. You get reuse, you lose safety.

The cast errors surface at runtime, in production, under load. For a library or platform component you cannot afford that.

The constraint is: **reuse code once, enforce type correctness at compile time**.

### 2. Mental model

Generics are *parameterized types*. You write a component once with a type parameter `T`, and the compiler creates a type-specific version for each use.

Analogy: a stencil. The stencil is the generic definition. `T` is the hole. You stamp it with `int`, `User`, `Event`. The shape of the stencil stays the same, the material changes.

### 3. How it works

Essentially:

```
GenericDefinition<T>  →  ConcreteType<X>
```

The compiler checks operations against `T` and rejects invalid ones before runtime. Implementation is shared.

Two important implementation models:
* **Type erasure, e.g. Java:** `T` is erased to its bound at runtime. You get one class file. No generic arrays, no `instanceof List<String>`.
* **Reified generics, e.g. C#:** `T` is preserved at runtime. You can do reflection on the concrete type.

You don't need the details, you need the consequence: erasure means you cannot create `new T[]` and you can get heap pollution via raw types.

### 4. Architectural reasoning

Generics enable reusable, type-safe abstractions.

When it helps:
* **Collections and containers** you already know
* **Repository / DAO / Service layers**: `Repository<T, ID>`, `PagedResult<T>`
* **Framework pipelines**: `Pipeline<Input, Output>`, `Validator<T>`
* **Domain modeling**: `Result<T, E>`, `Option<T>`, `Either<L,R>`

Alternatives and why you choose generics over them:
* **Duplication** → maintenance cost, drift
* **Dynamic / Object** → runtime errors, lost IDE support
* **Overloading** → combinatorial explosion

Decision rule: if you have the *same shape of behavior* with *different data types*, parameterize the type, not the code.

### 5. Trade-offs and failure modes

* **Readability cost.** `Map<K,V>` is fine. `Function<BiFunction<Optional<T>, Supplier<List<...>>>>` is not. Over-genericizing hurts maintainability.
* **Erasure pitfalls.** Java: you cannot instantiate `T`, you cannot do `new T[]`. Workarounds like `Class<T>` tokens add complexity.
* **Bounded wildcards confusion.** `List<? extends User>` vs `List<? super User>` is powerful but often misused, leading to APIs that are hard to call.
* **Leaky abstractions.** Generics don't make bad design good. A generic `Service<T>` with 12 type parameters is a smell for missing domain concepts.

### 6. Example

Enterprise payment platform. You need a generic, type-safe event store.

```java
interface EventStore<T extends DomainEvent> {
    void append(T event);
    List<T> readStream(String streamId);
}

class OrderEventStore implements EventStore<OrderEvent> { ... }
class PaymentEventStore implements EventStore<PaymentEvent> { ... }
```

One interface, compile-time guarantee that an `OrderEventStore` never returns a `PaymentEvent`. No casts, no duplication. The same pattern scales to `Repository<T>`, `Validator<T>`, `Mapper<S,T>`.

In TypeScript for AI pipelines, generics keep prompt contracts safe:

```ts
class PromptTemplate<TInput, TOutput> {
  render(input: TInput): TOutput { ... }
}
```

You reuse the template engine for classification, extraction, summarization without losing type information.

### 7. Reasoning challenge

You are designing a multi-tenant analytics SDK. Each tenant has its own `Metric` type with different fields, but the same aggregation logic: `groupBy`, `window`, `reduce`.

Do you create one generic `Aggregator<T extends Metric>` with type-safe projections, or a non-generic `Aggregator` that works on `Object` with runtime mapping?

What breaks if you choose wrong at 10M events/day?

### 8. Key takeaway

* Generics solve reuse vs type safety. Write once, use with many types, check at compile time.
* Use them for structural reuse: containers, repositories, pipelines, mappers. Not for hiding domain differences.
* Erasure vs reification changes what you can do at runtime. Design APIs accordingly.
* The cost is cognitive complexity. Prefer concrete types where possible, generic only where reuse is real and stable.

You should now be able to reason: *Is this a variation in type or in behavior?* If type, parameterize. If behavior, compose.
