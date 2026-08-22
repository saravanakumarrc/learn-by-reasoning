# Registries

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.2.4 — Containers

### 1. The problem

You have containerized your app. The image is now the unit of deployment. How do you get that immutable artifact from a build machine to hundreds of worker nodes, reliably, securely, and repeatedly?

Constraints appear immediately:
* Images are large, layered binaries. You can't email them.
* Nodes are ephemeral. They must pull on demand.
* Teams need a single source of truth for what image is running in prod.
* You need versioning, access control, and auditability without baking images into VMs.

Without a registry, you end up with ad-hoc file servers, shared volumes, or copying images manually. That breaks reproducibility and scales poorly.

### 2. Mental model

A container registry is a content-addressable package store for OCI images. Think of it like npm PyPI for containers.

You push an image once, reference it by name:tag or digest, and any node can pull it. The registry deduplicates layers across images, so 100 services sharing `alpine:3.19` download one copy.

### 3. How it works

Build produces layers + manifest. Push uploads layers by digest, registry stores manifest mapping tag -> digest.

```mermaid
flowchart LR
    CI[CI Build] -->|push| REG[Registry]
    REG -->|pull| K8s[Orchestrator Nodes]
    K8s -->|run| Pod[Container]
```

Pull is a manifest fetch then parallel layer download. The digest is immutable; a tag is mutable pointer.

OCI spec makes this portable: Docker Hub, ECR, GCR, Harbor, Artifactory all speak same wire protocol. Authentication is token-based, often via IAM or OIDC.

### 4. Architectural reasoning

**When it helps:** Any containerized workload in CI/CD or orchestrated environments. It decouples build from deploy and enables immutable deployments.

**Alternatives considered:**
* Bake image into VM/golden AMI. Works for small scale, fails for rapid iteration and rollbacks.
* Git LFS / object store. Stores blobs but lacks manifest, tagging, signing, and policy controls.
* Peer-to-peer distribution. Faster in theory, adds operational complexity.

**Why registry wins:** Centralized distribution + versioning + policy enforcement. You get a single place to scan, sign, and gate images before they reach production.

Decision pattern: Public registry for base images, private registry for internal images. Pull-through cache in clusters to reduce egress and latency.

### 5. Trade-offs and failure modes

* **Availability is a deployment dependency.** If registry is down, new pods can't start. Design for multi-AZ, regional replication, and high availability. Use image pull secrets with retries and local cache.
* **Mutable tags are a risk.** `latest` moves. Architects pin to digests in production manifests.
* **Rate limits and egress cost.** Public registries throttle anonymous pulls. Private registries charge for storage and egress. Large clusters can hit limits during rolling updates.
* **Supply chain security.** Registry is an attack surface. Needs image signing, vulnerability scanning, and admission control. A compromised base image propagates everywhere.
* **Layer sprawl.** Poor layer caching and huge images increase pull time and startup latency.

Failure mode to remember: A bad push with a retagged `prod` overwrites the image in flight. Mitigate with immutable tags and promotion workflows.

### 6. Example

Enterprise bank with 3 regions. CI builds service image, pushes to Harbor in primary region with signing enabled. Harbor replicates to ECR in each region. Kubernetes uses imagePullSecrets + pull-through cache DaemonSet.

Deployment flow: PR merge -> build -> test image -> sign -> promote tag `v1.2.3` to `stable` -> ArgoCD deploys digest-pinned manifest. If primary registry fails, regional replica serves pulls. Vulnerability scan gates promotion.

This gives audit trail, air-gapped fallback, and controlled rollout.

### 7. Reasoning challenge

You have a global app with clusters in US and EU. Pulls from a single US registry add 400ms+ latency and high egress cost to EU nodes. Do you:
A) Mirror the registry in EU and use geo-routing
B) Enable a pull-through cache in each cluster
C) Both

What are the trade-offs of your choice on consistency vs cost vs operational overhead?

### 8. Key takeaway

* A registry exists to make container images distributable, versionable, and governable artifacts.
* Use immutable digests for production, mutable tags for promotion.
* Registry availability is deployment availability. Replicate, cache, and monitor it like a critical dependency.
* Security is not optional: sign, scan, and enforce policy at the registry boundary.

You should now be able to reason about where to place registries, how to harden them, and what breaks when they fail.
