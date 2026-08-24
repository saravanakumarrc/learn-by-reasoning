# Jobs

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.3.8 — Kubernetes

### Jobs in Kubernetes

**The problem**
Kubernetes is built for long-running, always-on services. Deployments keep Pods up, restart them, and spread them across nodes.

What happens when you need work that *finishes*? A nightly ETL, a one-off DB migration, a model training run, a batch image resize. You want:
* run to completion, not forever
* restart on failure, but not infinitely
* a clear success/failure signal
* no orphaned Pods if the node dies

A plain Pod gives you none of that. A Deployment gives you forever.

**Mental model**
A Job is a controller for finite work. You declare *what* should be done and *how many times* it should succeed, not how to keep it alive.

Think of it as a work order, not a service. The Job controller creates Pods until the work is done, then stops managing them.

**How it works**

```mermaid
flowchart LR
    A[Job object] --> B[Job Controller]
    B --> C[Create Pod(s)]
    C --> D[Pod runs to completion]
    D --> E{Pod exited 0?}
    E -->|Yes| F[Count completion]
    E -->|No| G[Backoff & retry]
    F --> H{Completions reached?}
    H -->|Yes| I[Job Succeeded]
    H -->|No| C
```

Essential knobs:
* `completions` = how many successful Pods you need
* `parallelism` = max Pods running at once
* `backoffLimit` = max retries per Pod before Job fails
* `activeDeadlineSeconds` = hard timeout for the whole Job

The controller tracks Pod completions, not Pod liveness. When the count is reached, the Job is `Complete` and stops creating new Pods.

**Architectural reasoning**

When it helps:
* Batch processing with a clear end
* One-off migrations, backfills, cleanup
* Ephemeral compute like training or feature extraction
* Work that must be auditable and retriable

Alternatives:
* **Deployment** = keep running, self-healing service. Wrong for finite work.
* **CronJob** = a Job scheduler. It creates a Job on a schedule. Use CronJob for recurring batch, Job for one-off.
* **Pod + manual** = no retry, no completion tracking, no observability.

Choose Job when you need completion guarantees and bounded retries, not continuous availability.

**Trade-offs and failure modes**

* **Pods are not cleaned up by default.** Completed Pods linger. Set `ttlSecondsAfterFinished` or a finalizer to prune, or you leak objects and metrics.
* **BackoffLimit is per Pod, not total.** A Job with parallelism=10 and backoffLimit=6 can retry 60 times. That can blow up cost.
* **Node failure = restart.** Job restarts the Pod on a different node, but if the work is not idempotent you can get duplicates. Jobs assume at-least-once.
* **No rolling updates.** A Job is immutable in practice. To change spec you create a new Job.
* **Completion counting is subtle.** With `Indexed` completion mode each Pod gets an index and must succeed exactly once. Without it, the controller just counts successful exits. Use Indexed for parallel shards that must not re-run the same shard.

**Example**
Nightly user activity rollup.

A CronJob runs at 02:00, creates a Job with `parallelism: 4`, `completions: 4`. Each Pod processes a shard of users, writes results to object storage, exits 0. Job controller creates 4 Pods, restarts any that fail up to `backoffLimit: 3`, marks Job Succeeded when all 4 exit 0. Downstream DAG picks up the `Job.status.succeeded` condition as a gate.

If the ETL is changed to stream, you would replace Job + CronJob with a Deployment and Kafka consumers.

**Reasoning challenge**
You need to process 10M rows daily. Each Pod can handle 100k rows in ~10 minutes. The job must run exactly once per day, but you can manually re-run a failed day. You also need to be able to re-run a single failed shard without reprocessing the whole set.

Would you use a plain Job, Job with `completionMode: Indexed`, or CronJob + Job? What parallelism and backoff would you pick, and how do you avoid duplicate writes?

**Key takeaway**
* Jobs exist to give Kubernetes a way to run finite, retryable work to completion.
* Model Jobs as work orders with completions, not services with replicas.
* Use CronJob for recurrence, Job for one-off/batch, Deployment for long-running.
* Watch for Pod retention, non-idempotent retries, and completion semantics.
