# ArgoCD

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.4.4 — Platform engineering

## The problem

You have Kubernetes clusters in prod, stage, and dev. Teams ship manifests via CI pipelines that `kubectl apply` to clusters. Over time you get:

* Drift: someone fixes a pod manually with `kubectl`, the change is invisible in Git
* No audit: who changed what, when, and why is scattered in CI logs
* Slow rollback: you need to find the right commit and re-push
* Multi-cluster sprawl: each team has its own scripts, secrets in pipelines

The constraint is not just automation, it's **declarative, auditable, observable control** of live state with Git as the single source of truth.

## Mental model

ArgoCD is a continuous reconciliation loop, not a deployment pipeline.

Think of it as a thermostat for your cluster: Git holds the desired temperature, the cluster is the room, ArgoCD constantly reads both and applies heat/cool until they match. It is pull-based: ArgoCD watches Git, not the other way around.

```mermaid
flowchart LR
    Dev[Developer commit to Git] --> Repo[Git Repo - Desired State]
    Repo --> ArgoCD[ArgoCD App Controller]
    ArgoCD -->|compare| K8s[Kubernetes Cluster - Live State]
    K8s -->|status| ArgoCD
    ArgoCD -->|apply / prune| K8s
```

No manual push to the cluster. Changes flow in one direction: Git → ArgoCD → Cluster.

## How it works

An `Application` CRD declares what repo, path, and target cluster an app should live in. ArgoCD's controller:

1. Watches the repo for changes
2. Renders manifests from that path, often via Helm or Kustomize
3. Compares desired manifests to live resources via Kubernetes API
4. Syncs differences, with options for auto-sync, sync waves, and resource hooks

Sync is declarative and auditable. The UI shows out-of-sync, drift, and history per app. RBAC can be delegated so teams can only manage their own apps.

## Architectural reasoning

**When it helps**
* Platform engineering with many teams and clusters. GitOps gives self-service with guardrails.
* Need for drift detection and automated remediation.
* Multi-cluster promotion: same app definition, different clusters/overlays.

**Alternatives**
* Push CI/CD: Git commit triggers pipeline that `kubectl apply`s. Faster to initial deploy, but drift is invisible and rollback is pipeline-dependent.
* Flux: also GitOps, similar reconciliation model. ArgoCD tends to be chosen for its UI, app-of-apps pattern, and more mature multi-cluster UX. Flux is lighter and more Kubernetes-native.

Choose ArgoCD when you want pull-based reconciliation, strong Git as source of truth, and an explicit control plane for apps rather than hiding it in CI.

## Trade-offs and failure modes

* **Git as source of truth is a constraint.** Emergency fixes must go via Git or be reverted. This is good for audit, bad for break-glass speed unless you design exceptions.
* **Sync conflicts.** Two teams edit the same repo path, or someone applies out-of-band. ArgoCD will fight the change until Git is corrected.
* **Blast radius.** Auto-sync with prune can delete resources not declared in Git. Misconfigured apps of apps can cascade changes.
* **Secrets.** Git shouldn't contain secrets. You need external secret operators or sealed secrets, adding complexity.
* **Observability gap.** ArgoCD shows sync status, not application health. You still need metrics and logs.

Failure mode to watch: split-brain during network partition. ArgoCD can't see the cluster, so it reports unknown. On reconnect it may revert manual fixes, which is correct for GitOps but surprising in an incident.

## Example

Platform team runs ArgoCD in a management cluster. Each dev team owns a folder `apps/team-a/service/` in a mono-repo.

Application CRD:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: team-a-service
spec:
  project: team-a
  source:
    repoURL: https://github.com/org/platform.git
    path: apps/team-a/service
    targetRevision: main
  destination:
    server: https://stage.api
    namespace: team-a
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Dev merges PR → ArgoCD detects → syncs to stage. Promoting to prod is a PR that changes `destination.server`. Audit trail is Git history + ArgoCD events. Platform controls what projects can deploy where via ArgoCD RBAC.

## Reasoning challenge

You have 50 microservices across 3 clusters. Platform wants self-service but must prevent direct cluster access. A team needs an emergency hotfix at 2am and Git review will take 30 minutes.

Would you allow out-of-band `kubectl` edits with ArgoCD self-heal disabled for that app, or require a fast-track Git merge with auto-sync? What failure mode does your choice create?

## Key takeaway

* ArgoCD implements continuous reconciliation: Git desired state vs cluster live state, automatically converged.
* Pull-based GitOps gives auditability, drift detection, and declarative promotion at the cost of slower emergency changes.
* It solves multi-team, multi-cluster control, not just deployment automation.
* Design for break-glass, secrets handling, and app-of-apps boundaries early; otherwise GitOps becomes a bottleneck.
