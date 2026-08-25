# Docker

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.2.1 — Containers

**Docker**

### 1. The problem

You ship working code. It runs on your laptop. It fails in CI. It fails in production.

The problem is not the code. It is *environment drift*. Different OS versions, library versions, environment variables, system dependencies, and manual setup steps make "it works on my machine" a real architectural risk.

Constraints you face:
* Reproducible builds across dev, test, and prod
* Fast, isolated startup for scaling
* Decoupling app dependencies from host OS
* Consistent deployment artifact

VMs solve isolation but are heavy and slow to boot. Bare metal is fast but not portable. You need a lighter isolation boundary that still packages dependencies.

### 2. Mental model

A container is a standardized, immutable shipping box for an application and its runtime dependencies.

Think of it as a process with its own filesystem view, network namespace, and resource limits, running on a shared kernel. No hypervisor, no full guest OS.

Image is the read-only blueprint. Container is the running instance of that blueprint.

### 3. How it works

Essential mechanism, not feature list:

* **Image layers:** Dockerfile instructions build a layered read-only filesystem. Layers are cached and reused. This gives you immutable, versioned artifacts.
* **Namespaces:** Linux namespaces isolate PID, network, mount, user. Each container sees its own process tree and network stack.
* **Cgroups:** Control groups limit and account CPU, memory, IO per container.
* **Union filesystem:** Read-only image layers + thin writable layer for runtime writes.

Flow:

```mermaid
flowchart LR
    Dev[Developer + Dockerfile] --> Image[Image]
    Image --> Registry[(Registry)]
    Registry --> Runtime[Container Runtime]
    Runtime --> Container[Container<br/>App + Libs + Config]
    Container --> Host[Shared Host Kernel]
```

The runtime enforces isolation, you get portability because the image bundles just enough OS bits for the app to run.

### 4. Architectural reasoning

When it helps:
* **Immutable deployments.** You build once, promote the same image through environments. Reduces "works here not there" failures.
* **Density and speed.** Containers start in seconds vs minutes for VMs. Good for autoscaling and batch jobs.
* **Dependency isolation for microservices.** Each service carries its own runtime, no host-wide library conflicts.

Alternatives:
* **VMs:** Stronger isolation, full OS. Choose when you need multi-tenant strong isolation or different kernels. Pay in size and boot time.
* **Bare metal / system packages:** Max performance, zero overhead. Choose when you control the entire fleet and need bare-metal optimization.
* **Serverless / Functions:** Further abstraction. Choose when you want no ops for lifecycle.

Decision rule: Use containers when you need portable, reproducible packaging with fast start/stop and you can tolerate sharing a kernel.

### 5. Trade-offs and failure modes

* **Security boundary is weaker than VM.** Containers share kernel. A kernel exploit or privileged container escape compromises host. Never run untrusted workloads on same host without hardening.
* **State is a trap.** Containers are ephemeral by design. Writing to local filesystem is lost on restart. Architects push state to external volumes, databases, object storage.
* **Image bloat and drift.** Unpinned base images, copying whole repos, and layer sprawl increase size and attack surface. Leads to slow pulls and larger blast radius.
* **Observability gap.** You see container metrics, not necessarily app health. Health checks and logging must be explicit.
* **Complexity moves up.** You solve dependency hell but now manage orchestration, networking, secrets, and image lifecycle.

### 6. Example

Enterprise ML inference service.

Requirement: Deploy Python model v1 and v2 side-by-side, scale each independently, roll back instantly.

Architecture: Each version builds a Docker image with `python:3.11-slim`, model weights, and inference server. Image pushed to registry. Orchestrator runs containers behind a service mesh. Model weights mounted as read-only volume from object storage.

Result: Same artifact runs on dev laptop, CI, staging, prod. Rollback = change image tag. No host Python version conflicts.

### 7. Reasoning challenge

You have a CPU-bound, single-tenant analytics job that processes large datasets and must run for hours with direct access to NVMe storage.

Would you containerize it, or run it on bare metal/VM? What changes if the job must be multi-tenant and run in a shared cluster?

Consider startup time vs isolation vs data locality vs security.

### 8. Key takeaway

* Containers solve environment reproducibility and deployment speed, not compute efficiency or strong isolation.
* The image is the unit of delivery and versioning; the container is ephemeral runtime.
* Prefer stateless containers with externalized state, secrets, and config.
* The real architectural value is immutable infra and fast, repeatable rollouts, not Docker as a tool.

You should be able to reason about when container overhead is worth it, where the security boundary ends, and what must stay outside the container.
