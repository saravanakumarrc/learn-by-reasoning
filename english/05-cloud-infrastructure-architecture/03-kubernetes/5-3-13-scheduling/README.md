# Scheduling

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.3.13 — Kubernetes

**Scheduling in Kubernetes**

### 1. The problem

You have a cluster of nodes with finite CPU, memory, GPU, and failure domain capacity. You have hundreds to thousands of Pods arriving continuously, each with resource requests, constraints, and placement preferences.

Place them where they will run, start quickly, and stay running. Doing it by hand does not scale, and doing it naively creates hot nodes, cold nodes, noisy neighbor problems, and violations of business constraints like "don't put both replicas in the same AZ".

The problem is not just bin packing. It is constrained, distributed placement under uncertainty with continuous churn.

### 2. Mental model

The scheduler is a matchmaker, not a placement engine.

It does not move running Pods. It only decides *where* a pending Pod can bind first time, given the current state of Nodes.

Think: **Filter -> Score -> Bind**. Filter removes illegal nodes, score ranks the legal ones, bind commits.

### 3. How it works

The kube-scheduler watches the API server for Pods in `Pending`. For each Pod it runs:

```mermaid
flowchart LR
    P[Pending Pod] --> F[Filter: Predicates]
    F --> |legal nodes| S[Score: Priorities]
    S --> B[Bind to best Node]
    B --> R[Pod Scheduled]
```

Filter is hard constraints: resource requests <= allocatable, nodeSelector, nodeAffinity hard requirement, taints/tolerations, PodTopologySpread, volume zone constraints, inter-pod affinity/anti-affinity hard rules.

Score is soft preferences: spread across nodes/Zones, balance resource utilization, prefer nodes with existing related Pods, prefer fewer Pods per node, custom scoring plugins.

The scheduler is centralized per cluster by default. It is pluggable via Scheduler Framework: filter plugins, score plugins, and bind plugins. The decision is made synchronously then the Pod is bound via an update to the API server.

Scheduling is eventually consistent: the scheduler sees a point-in-time snapshot of Nodes and Pods. If state changes during scheduling, the Pod can become unschedulable and be retried.

### 4. Architectural reasoning

Scheduling exists to decouple *what* to run from *where* to run it.

When it helps:
* Heterogeneous hardware: GPU, high-memory nodes, arm/x86
* Failure domain isolation: spread replicas across zones/racks
* Resource efficiency: pack workloads to avoid over-provisioning
* Policy enforcement: compliance, cost, latency SLOs via topology

Alternatives you would consider:
* Static placement: manual node assignment. Works for tiny clusters, fails at scale and churn.
* External orchestrator: Nomad, Mesos. Different trade-offs, not Kubernetes-native.
* Custom scheduler per workload: build a dedicated scheduler for latency-critical or GPU workloads. You lose default operability and gain control.

Choose default scheduler when you want general purpose placement with standard constraints. Choose custom scheduler or scheduler extender when you have a dominant workload class with a placement objective the default cannot express well, e.g., bin packing for GPU fragmentation or co-location for low-latency inference.

### 5. Trade-offs and failure modes

* **Optimality vs latency.** Better scoring takes longer. Scheduler can become a bottleneck under high churn. Default is fast enough for most clusters; large bursts cause scheduling latency.
* **Centralization.** Single scheduler is simple but a single point of contention. Mitigated by multiple scheduler instances with different queues, but then you add complexity.
* **Filter vs score confusion.** Architects put hard requirements in scores and wonder why Pods are unschedulable. Hard constraints must be filters; preferences belong in scores.
* **Starvation and deadlock.** Over-constrained Pods with affinity to nodes that never have capacity will sit Pending forever. Anti-affinity + limited nodes = deadlock.
* **Resource requests vs limits.** Scheduler uses requests. If requests are set too low, you get placement but runtime OOM/CPU throttle. If set too high, you waste capacity.

Failure modes to watch: scheduling queue backlog, pending Pods with no events, thrashing due to frequent node pressure evictions causing rescheduling storms.

### 6. Example

Enterprise ML serving: GPU inference Pods need NVIDIA A100, 16GB GPU memory, and must be spread across 3 AZs for HA. Batch training Pods can tolerate preemption and want to pack tightly to maximize GPU utilization.

Architectural decision:
* Node taint `gpu=true:NoSchedule`, toleration on inference Pods.
* Hard nodeAffinity for GPU nodes.
* PodTopologySpread for inference replicas across zones.
* Separate scheduler named `batch-scheduler` with a custom scoring plugin that prefers nodes with the most free GPU memory to reduce fragmentation.
* Requests set to actual steady-state usage, limits to burst.

Result: inference gets predictable placement and failure isolation, batch gets efficient bin packing, both share cluster without interference.

### 7. Reasoning challenge

You have 10 nodes per zone, 3 zones. A Deployment with 25 replicas and `topologySpreadConstraints` `maxSkew:1` across zones. Also a `podAntiAffinity` requiring replicas not share the same node.

Can this Deployment ever become fully scheduled? What changes would you make?

### 8. Key takeaway

* Scheduling is constrained placement, not load balancing. The scheduler decides initial binding only.
* Filter for hard constraints, score for preferences. Mixing them creates unschedulable or unpredictable systems.
* Placement policy is architecture: affinity, anti-affinity, topology spread, taints/tolerations express reliability, performance, and cost goals.
* Central scheduler scales surprisingly far, but high churn, over-constraining, and bad requests/limits are the real failure modes.

You should be able to reason: given a workload's reliability and performance constraints, what placement policy expresses it, and what scheduling failure mode will bite you first.
