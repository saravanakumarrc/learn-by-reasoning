# Pods

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.3.1 — Kubernetes

**Pods**

### The problem

Containers are lightweight isolated processes. A real service is rarely one process. A web app needs the app container, a proxy, a logger, a metrics exporter. Those components need to:
- Start together and stop together
- Share network and storage with near-zero latency
- Be scheduled as one unit on the same node
- Fail as one unit

If Kubernetes scheduled individual containers, you'd have to guarantee co-location, shared networking, and shared lifecycle manually. That is brittle and expensive to operate.

The need is an atomic scheduling and lifecycle unit that can host multiple cooperating containers.

### Mental model

A Pod is a logical host. Think of it as a lightweight VM abstraction with one network identity and one storage namespace.

All containers in a Pod share the same network namespace = same Pod IP, same localhost, same ports. They share volumes mounted at the same paths.

If you need two processes to act like they are on the same machine, put them in the same Pod. If they are independent services, put them in different Pods.

```
mermaid
flowchart LR
    Node[Node]
    Pod[Pod IP 10.1.2.3]
    C1[app container]
    C2[sidecar proxy]
    C3[log shipper]
    Pod --> C1
    Pod --> C2
    Pod --> C3
    C1 <--> C2
    C1 <--> C3
    Node --> Pod
```

One IP per Pod, not per container. All containers see each other on `localhost`.

### How it works

Kubernetes schedules Pods, not containers. The kubelet on the node runs the containers inside a Pod sandbox.

Essentials:
* **Shared network**: one IP, one network namespace. Containers communicate over localhost.
* **Shared storage**: volumes mounted into the Pod are visible to all containers in the Pod.
* **Coordinated lifecycle**: containers start in order defined by init containers, then app containers start together. Restart policy applies to the Pod.
* **Atomic unit**: scaling a Deployment scales Pods. A Pod dies, all its containers die together.

This enables the sidecar pattern: a main app container plus helpers that need tight coupling, like an Envoy proxy, a service mesh sidecar, a log forwarder, or an init container that waits for a DB migration before the app starts.

### Architectural reasoning

When to use one Pod:

* Components must be co-located on the same node for performance or security.
* Components need to share a local filesystem or in-memory network.
* You want one lifecycle and one failure domain for tightly coupled processes.

When NOT to use one Pod:

* Components are independently scalable, have different failure domains, or different resource requirements. Put them in separate Pods and communicate over the network.
* You want independent rollout, autoscaling, or deployment cadence.

Best practice: **one main container per Pod**. Multi-container Pods are for helpers, not for microservices. The rule of thumb is: if you would run them as separate Deployments in production, they belong in separate Pods.

Alternatives: run helpers as separate containers on the node via DaemonSets, or as separate services with network calls. Both increase latency and operational complexity versus a sidecar.

### Trade-offs and failure modes

* **Shared fate**: a crashlooping sidecar restarts the whole Pod. A noisy neighbor container can starve the app of CPU/memory inside the same cgroup.
* **Scaling granularity**: you scale the whole Pod. You cannot scale the app container independently from its sidecar.
* **IP overhead**: one IP per Pod. For very high density, this creates routing table and CNI pressure. Some clusters use IP-per-Pod with a proxy; others use IP reuse.
* **Lifecycle coupling**: updates to sidecar require Pod restart, which restarts the app. Use read-only helpers or init containers where possible.
* **Not a process manager**: Pods are not for running multiple independent apps. Kubernetes will not manage process supervision inside a container.

Operational note: Pods are ephemeral. Never store durable state on a Pod's local filesystem. Use PersistentVolumes for state, and treat Pods as cattle.

### Example

An enterprise API service behind a service mesh:

* `app` container: the business logic
* `envoy` sidecar: ingress/egress with mTLS and retries
* `log-forwarder` container: tails stdout and ships to central logging

All three share the Pod network. Envoy sees the app on `localhost:8080`. The log-forwarder sees the same stdout. They start together, die together, and move together when the Pod is rescheduled. If you needed independent scaling of logging, you'd move it out to a DaemonSet or a separate pipeline.

### Reasoning challenge

You have a Java app that needs:
1. A JVM metrics exporter on port 9100
2. A log shipper that tails files from `/var/log/app`
3. An Envoy sidecar for outbound mTLS

Do you put all three helpers in the same Pod as the app, or split them? What changes if the metrics exporter must be scaled independently to reduce scrape load?

Think about coupling, blast radius, and scaling.

### Key takeaway

* Pods exist to give tightly coupled containers a shared network, storage, and lifecycle, and to provide a single scheduling unit.
* One main container per Pod is the default; multi-container Pods are for helpers with shared fate.
* Pod IP is per Pod, not per container. Design for ephemeral Pods, not persistent hosts.
* Shared fate is the core trade-off: you gain locality and simplicity, you lose independent scaling and failure isolation.
