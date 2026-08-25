# Threads

> **Learning Path:** Distributed Systems
> **Section:** 2.1.2 — Core concepts

### The problem

A single execution path can do only one thing at a time. A web service that handles requests sequentially will block on the first slow I/O — a DB call, an HTTP fan-out, a lock — and every other client waits.

You need concurrency at the node level to meet latency and throughput targets, but you also need isolation and resource control. The problem is not "how to write code", it's how to model many independent units of work on one machine without paying the cost of a full process per request.

### Mental model

A thread is a lightweight execution context sharing an address space with other threads in the same process.

Think of a process as a kitchen. Threads are chefs working in the same kitchen, sharing the same knives, ingredients, and counters. They can work in parallel, but they must coordinate access to shared resources.

That shared memory is the key: cheap to create compared to a process, fast to communicate via memory instead of IPC, but also the source of coordination complexity.

### How it works

The OS scheduler maps threads to CPU cores. A thread pool pre-creates a bounded set of worker threads and reuses them.

```
flowchart LR
    Client --> LB[Load Balancer]
    LB --> S[Service Process]
    S --> TP[Thread Pool]
    TP --> W1[Worker Thread 1]
    TP --> W2[Worker Thread 2]
    TP --> Wn[Worker Thread N]
    W1 --> DB[(DB)]
    W2 --> Cache[(Cache)]
```

Request arrives → pulled from a queue → assigned to an idle worker → runs to completion or yields on blocking I/O → returns to pool.

For I/O-bound work the thread blocks in kernel, the scheduler runs another thread. For CPU-bound work threads truly run in parallel on multiple cores.

Modern runtimes add user-space scheduling: Go goroutines, Java virtual threads, async tasks. The mental model stays the same — logical concurrency — but the implementation changes who does the blocking and context switching.

### Architectural reasoning

Threads solve: handle many concurrent requests on one node with shared in-memory state.

When it helps:
* I/O-bound services where most time is spent waiting, not computing. Thread-per-request with a pool hides latency.
* Codebases that are naturally blocking and synchronous. Threads let you keep simple linear code without rewriting to async.
* Short-lived, shared state needs. One process, one cache, one connection pool, multiple workers.

Alternatives:
* Process per request: strong isolation, high overhead, poor memory sharing.
* Async event loop / non-blocking I/O: far higher concurrency per core, no blocking, but requires callback / async-await discipline and is painful for CPU work.
* Actor / message passing: avoids shared memory at cost of explicit message boundaries.

Why choose it: you want concurrency with shared memory and you can tolerate coordination overhead. The decision is about the cost model of your workload.

### Trade-offs and failure modes

* **Shared state = contention.** Locks, race conditions, deadlocks, and visibility issues appear. Correctness cost grows with thread count.
* **Scalability ceiling.** Each thread costs MBs of stack + kernel structures. Context switches grow with thread count. Typical sweet spot is tens to hundreds of threads per node, not tens of thousands.
* **Blocking amplifies.** One slow DB call holds a thread hostage. Under load the pool saturates, queue grows, latency spikes. This is the classic thread starvation failure.
* **Observability.** Stack traces are per-thread. Correlating a request across threads needs explicit context propagation.

Failure modes architects must remember: thread leak from unjoined workers, lock convoy under contention, priority inversion, and non-deterministic bugs that only appear under load.

### Example

An enterprise payment gateway needs <100ms p95 latency and must call 3 downstream services per request.

Design choice: fixed thread pool sized to CPU cores * ~2 for I/O wait. Each worker handles one request synchronously. Connection pools to downstream services are shared in-process, avoiding per-request connection churn.

At peak, pool saturates. Instead of spawning unbounded threads, the service sheds load via a bounded request queue and returns 503 with Retry-After. The shared in-memory rate limiter and circuit breaker are naturally centralized.

If the service were rewritten async, you could handle 10x more concurrent requests per node with less memory. But the team kept threads because existing business logic is blocking and the shared limiter would become harder to reason about.

### Reasoning challenge

You are designing an image thumbnail service. Workload: 1000 RPS, each request does 50ms of CPU-bound resizing then 10ms of S3 upload.

You have 16 cores per node. Would you use a classic thread pool, a larger pool, or move to an async worker model with a separate CPU worker pool? What breaks first and why?

### Key takeaway

* Threads enable safe concurrency within one process via shared memory; they are a local node primitive, not a distributed one.
* Choose threads when you need blocking, synchronous code and shared in-process state with moderate concurrency.
* The real cost is coordination, not creation: locks, contention, and pool saturation dominate operational risk.
* Scale concurrency with the workload: thread pools for I/O-bound, async/event loops for massive I/O concurrency, and dedicated CPU workers for compute-bound work.
