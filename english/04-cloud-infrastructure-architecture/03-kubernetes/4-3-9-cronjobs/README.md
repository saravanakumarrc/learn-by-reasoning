# CronJobs

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.3.9 — Kubernetes

**CronJobs**

### 1. The problem

You need batch work to run periodically inside a Kubernetes cluster: ETL at 2am, certificate rotation daily, log compaction hourly, model retraining nightly.

Constraints:
* The work is short-lived, not a long-running service
* It must be reliable, observable, and run on the cluster's compute
* You don't want an external host with cron calling `kubectl` and managing secrets
* You don't want an always-on service polling a clock

Options are: external cron, a daemonset polling, or letting the cluster itself be the scheduler.

### 2. Mental model

A CronJob is a time-based Job factory.

You declare *when* and *what*. The CronJob controller watches its own objects, creates a Job at the scheduled time, and the Job creates Pods to do the work. The CronJob itself never runs code.

```mermaid
flowchart LR
    CronJob[ CronJob object ] -->|schedule triggers| Controller
    Controller -->|creates| Job[ Job ]
    Job -->|creates| Pod[ Pod(s) ]
    CronJob -->|retains| History[ Job history ]
```

Think of it as Kubernetes owning the cron daemon, not your app.

### 3. How it works

The essential mechanism is small:
* CronJob spec defines a cron schedule, a pod template, and policies for concurrency and history
* The CronJob controller reconciles every ~1 minute. When the schedule matches, it creates a new Job from the template
* The Job runs to completion, succeeds or fails, and is left for you to inspect

That's it. The important controls are:
* `concurrencyPolicy`: `Allow`, `Forbid`, `Replace` — what to do if previous run is still active
* `startingDeadlineSeconds`: fail if schedule was missed too long
* `successfulJobsHistoryLimit` / `failedJobsHistoryLimit`: how long to keep Job objects

No distributed locking, no exactly-once semantics. It is a best-effort scheduler.

### 4. Architectural reasoning

When it helps:
* Periodic, self-contained batch work that belongs to the cluster lifecycle
* Work needs cluster resources, secrets, and RBAC like any other workload
* You want the schedule versioned in Git with the workload

Alternatives:
* **External cron + kubectl**: works, but couples scheduling to an out-of-cluster host, secrets management, and network reachability
* **Always-on service with timer**: wastes resources, adds failure modes, and re-implements scheduling
* **Workflow engine like Argo Workflows**: better for DAGs, retries, and dependencies. Overkill for a simple cron.

Choose CronJob when the requirement is *run this container at this time*, not *coordinate a multi-step pipeline*.

### 5. Trade-offs and failure modes

* **Time is cluster time.** If nodes have clock skew or the controller is down during the trigger window, runs can be missed or late. `startingDeadlineSeconds` helps detect misses, not prevent them.
* **No overlap protection by default.** A long job can cause the next scheduled run to pile up. `Forbid` prevents overlap but can silently skip work.
* **Resource spikes.** A daily job that runs at 00:00 for every team creates thundering herd. Stagger or use a queue.
* **Observability is Job-level.** You get Pod logs and Job status, but no built-in alerting for missed runs. You need external monitoring.
* **No built-in idempotency.** If a Job is recreated due to controller restart, you can get duplicate runs. The job itself must be idempotent.

### 6. Example

Nightly feature store compaction.

A data team needs a Spark job to compact Parquet tables at 01:30 UTC, never overlap with the 01:30 ETL. They define a CronJob with `concurrencyPolicy: Forbid`, a resource request that fits the node pool, and `successfulJobsHistoryLimit: 3`. The CronJob lives in the same namespace as the data pipeline, uses the cluster's service account and image registry.

If the controller is down at 01:30, `startingDeadlineSeconds: 300` marks the Job as failed, which triggers an alert. The job itself is idempotent: it checks a watermark before compacting.

This is better than a VM cron because the job scales with the cluster, and better than a polling service because it costs zero when idle.

### 7. Reasoning challenge

You need an hourly aggregation that must not overlap, must survive pod eviction mid-run, and the result must be written exactly once.

Would you use a CronJob with `concurrencyPolicy: Forbid` and retry logic in the container, or move to a queue-driven worker with a scheduler? What changes if the aggregation takes 45 minutes on average?

### 8. Key takeaway

* CronJobs move time-based scheduling into the platform, not into apps or external hosts
* It is a Job factory, not a workflow engine. It guarantees *attempt*, not exactly-once
* Concurrency policy and history limits are architectural decisions, not tuning knobs
* If you need coordination, retries with backoff, or DAGs, prefer a workflow system over CronJob

You should be able to reason: does this work need a clock or a queue?
