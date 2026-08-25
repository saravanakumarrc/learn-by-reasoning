# Processes

> **Learning Path:** Distributed Systems
> **Section:** 2.1.1 — Core concepts

### The problem

You need a system that keeps working when parts fail, scales independently, and can evolve without redeploying everything.

A single process with shared memory solves none of that. One bug can corrupt shared state, one slow request blocks all threads, one crash takes down the whole service. In a network, you also can't assume two nodes see the same time, the network is reliable, or that a peer is still alive.

You need a unit of computation that is *isolated*, can fail on its own, and communicates explicitly. That unit is the process.

### Mental model

Think of a process as an autonomous worker with its own memory, lifecycle, and mailbox. It does work, it has local state, and it talks to other workers by sending messages. It has no shared memory with its peers.

Analogy that helps: a kitchen brigade. Each chef owns their station, their ingredients, and their tools. They don't reach into each other's pans. They coordinate by passing plates. If the pastry chef burns a dessert, the grill station keeps running.

In distributed systems theory, a process is the fundamental active entity: it executes sequentially, maintains state, and communicates via asynchronous message passing. The system is the set of processes plus the network between them.

### How it works

The essential mechanism is isolation + explicit communication.

Isolation: each process has its own address space and failure domain. A crash is contained. The OS or container runtime enforces this boundary.

Communication: processes interact via messages over a channel. In practice that is RPC, HTTP/gRPC, message queue, or raw TCP. There is no shared memory. That forces all state sharing to be explicit, versioned, and observable.

Lifecycle is local: start, run, crash-stop. The system as a whole is partially synchronous: messages can be delayed, reordered, lost. There is no global clock.

```mermaid
flowchart LR
    A[Process A\nlocal state] -->|message| B[Process B\nlocal state]
    B -->|message| C[Process C\nlocal state]
    A -. unreliable network .-> B
    B -. unreliable network .-> C
```

The model is: processes are independent, failures are independent, communication is the only coupling.

### Architectural reasoning

Processes exist to give you failure containment and independent evolution.

**When it helps**
* You need fault isolation. A memory leak or panic in one service must not kill the others.
* You need independent scale and deploy. Order service scales with traffic, inventory service scales with stock updates.
* You need team ownership boundaries. Process boundaries map to teams and blast radius.

**Alternatives**
* Threads in one process: cheap communication via shared memory, but no failure isolation. One segfault kills all.
* Shared database as coupling: cheap consistency, but creates a single point of failure and a scaling bottleneck.
* Monolith: simple to reason about, fast internal calls, terrible for partial failure and independent release.

Choose process boundaries where the cost of a network call is justified by the gain in isolation, independent lifecycle, and scalability.

### Trade-offs and failure modes

**Isolation vs latency.** Message passing is orders of magnitude slower than in-process calls. You pay in latency and operational complexity for resilience.

**Failure detection is hard.** A process can be slow, partitioned, or dead. You cannot distinguish a crashed process from a slow network without timeouts and heartbeats. That leads to the classic failure detector problem.

**State ownership.** With isolated processes, state must live somewhere. You either replicate it, accept single-writer, or make it event-sourced. There is no free lunch: consistency now trades with availability.

**Common failure modes**
* Crash-stop: process dies, stops sending. Detectable eventually.
* Message loss / duplication: at-least-once vs at-most-once semantics.
* Partial partitions: two processes think they are both leaders.

Design for these by making processes idempotent, stateless where possible, and using explicit acknowledgements and retries.

### Example

An e-commerce checkout flow.

`API Gateway` -> `Order Process` -> `Payment Process` -> `Inventory Process` -> `Notification Process`

Each runs as a separate deployable process, possibly on different nodes.

Order creates a pending order and emits `OrderCreated`. Payment listens, charges card, emits `PaymentSucceeded`. Inventory reserves stock on that event. Notification sends email after both succeed.

If Payment crashes, Order and Inventory keep running. When Payment recovers it replays its queue. No shared memory, no coordinated lock. The failure is contained to one domain.

### Reasoning challenge

You have a pricing service that is read-heavy and a pricing-rules service that is updated rarely but must be consistent with inventory.

Do you co-locate pricing reads and rules in the same process, or keep them separate? What happens to latency, deployment risk, and consistency when a bad rules update ships?

Consider the blast radius of a buggy rules deploy versus the cost of an extra network hop on every price read.

### Key takeaway

* A process is an isolated unit of computation with local state that communicates explicitly. It is the basic building block for fault containment in distributed systems.
* Processes exist because you want independent failure, scaling, and deployment, not because you want performance.
* Design process boundaries around failure domains and team ownership, not around code reuse.
* Expect partial failure, unreliable messages, and no global clock. Build idempotency, timeouts, and explicit state machines into every process.
