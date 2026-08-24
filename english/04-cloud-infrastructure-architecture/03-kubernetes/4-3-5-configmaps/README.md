# ConfigMaps

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.3.5 — Kubernetes

**ConfigMaps**

### 1. The problem

You ship containers. The same image must run in dev, staging, and prod. If configuration is baked into the image at build time you need a different image per environment. That violates immutable artifacts and slows delivery.

You also have ephemeral pods. When a pod dies and is rescheduled it must get the same configuration without rebuilding. Hard-coding config in a Deployment manifest works for a few env vars, but it pollutes the manifest, is hard to audit, and mixes code lifecycle with config lifecycle.

The constraint is 12-factor: config is separate from code, and in Kubernetes it must be separate from the Pod spec.

### 2. Mental model

A ConfigMap is a named key-value bundle stored by the control plane, not by your app. Think of it as a small file system or environment variable set that lives in the cluster and can be attached to pods.

Same image, different ConfigMap per namespace/environment. The pod reads config from the cluster, not from the image.

### 3. How it works

A ConfigMap is an API object stored in etcd. It can be mounted as a volume, so files appear under `/etc/config`, or injected as env vars via `envFrom`.

```mermaid
flowchart LR
    CM[(ConfigMap)] -->|volume mount| P[Pod]
    CM -->|envFrom| P
    P --> D[Deployment]
    D -->|uses same image| P
```

Updates to the ConfigMap update the volume files in running pods eventually, but do not automatically restart containers. The pod spec references the ConfigMap by name, not by value.

### 4. Architectural reasoning

When it helps:
* Non-sensitive, environment-specific settings: feature flags, log level, endpoints, time zone, service URLs.
* Same container image across environments. ConfigMap per namespace gives you dev/staging/prod without rebuilds.
* Configuration that changes less frequently than code but more frequently than releases.

What it solves: decouples config lifecycle from image lifecycle and from the Deployment manifest.

Alternatives:
* Bake config into image. Simple, but rebuild per env, violates immutability.
* Put config directly in Pod spec as env vars. Works for small values, becomes unmanageable and leaks config into GitOps.
* Secrets for sensitive data. ConfigMap is explicitly not for secrets.
* External config service like Consul/etcd. More powerful for dynamic config, adds operational complexity and network dependency.

Choose ConfigMap when you want Kubernetes-native, declarative config that is versioned with the cluster and does not need a sidecar.

### 5. Trade-offs and failure modes

* **Not secret safe.** ConfigMaps are stored unencrypted in etcd by default and visible via `kubectl`. Never put passwords, tokens, or keys there. Use Secrets with encryption at rest.
* **Update propagation is lazy.** Volume mounts are updated ~1 minute later, env vars are immutable for the container lifetime. If you need instant hot-reload you need a reload sidecar or rolling restart.
* **Size and blast radius.** Large ConfigMaps increase pod startup time and etcd load. Keep them small. One ConfigMap per logical concern, not a monolith.
* **Coupling to cluster.** Config lives in Kubernetes, so moving workloads out of the cluster requires migration. Also, changing a ConfigMap is a cluster change, not an app change — guard it with RBAC and GitOps.

Common failure: putting secrets in ConfigMaps because it's convenient, then exposing them in logs. Another: expecting env vars to update without restart.

### 6. Example

A payment API runs the same image in all environments. Non-sensitive routing config varies.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: payment-api-config
data:
  LOG_LEVEL: info
  FEATURE_NEW_CHECKOUT: "true"
  PAYMENT_PROVIDER_URL: https://provider.internal
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: api
        image: payment-api:v1.2.3
        envFrom:
        - configMapRef:
            name: payment-api-config
        volumeMounts:
        - name: config
          mountPath: /etc/app
      volumes:
      - name: config
        configMap:
          name: payment-api-config
```

Dev namespace has its own ConfigMap with `LOG_LEVEL: debug` and a different provider URL. No image rebuild.

### 7. Reasoning challenge

You need to rotate a database password. You currently store it in a ConfigMap mounted as an env var. What is the architectural issue, and what is the minimal correct change?

*Hint: consider secret management, pod restart semantics, and whether env vars can be updated in place.*

### 8. Key takeaway

* ConfigMap exists to separate non-sensitive configuration from immutable container images and from Pod specs.
* Use it for environment-specific, non-secret config that can be attached declaratively to pods.
* Never use it for secrets. Updates are not instantaneous for env vars; volume mounts update eventually but require app-level reload awareness.
* The decision is about lifecycle boundaries: code vs config vs secrets, and how much dynamic behavior you need versus Kubernetes-native simplicity.
