# Secrets

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.6 — Kubernetes

## 1. Problem

உங்க app ஒரு database-ஐ connect பண்ணணும். அல்லது third-party API-க்கு call பண்ணணும். இதுக்கு username, password, API key, TLS cert வேணும்.

இதை Deployment yaml-ல hardcode பண்ணினா என்ன ஆகும்?
Git repo-ல போயிடும். CI log-ல போயிடும். Image layer-ல போயிடும். யாராவது `kubectl get pod -o yaml` பார்த்தாலே தெரிஞ்சிடும்.

Production-ல secret மாறணும். அப்போ image rebuild பண்ண முடியாது. Manifest மாறினாலும் rollout செய்யணும். Audit trail இல்ல.

இந்த pain தான் Kubernetes Secret வந்த reason.

## 2. Mental Model

Kubernetes Secret என்பது **sensitive data-வை API object ஆக store பண்ணி Pod-க்கு கொண்டு போகும் mechanism**.

இது secret manager இல்ல. இது vault இல்ல. இது encrypted safe இல்ல. இது வெறும் distribution மற்றும் access control.

Mental model: etcd-ல ஒரு object-ஆ வைக்கறோம். அதை API server மூலம் படித்து, kubelet Pod-க்கு mount பண்ணி கொடுக்கிறோம்.

Security வரை: Base64 encoding மட்டுமே. Encryption at rest என்பது cluster-level feature. RBAC தான் gatekeeper.

## 3. How It Works

Secret create பண்ணது ரொம்ப simple:

```bash
kubectl create secret generic db-creds --from-literal=password=SuperSecret123
```

இது `Opaque` type secret-ஆ etcd-ல create ஆகும். Value Base64-ல store ஆகும்.

Pod-ல use பண்ண இரண்டு வழி:

**Env var ஆக:**
```yaml
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-creds
      key: password
```

**File ஆக mount:**
```yaml
volumeMounts:
- name: secret-vol
  mountPath: /etc/secrets
  readOnly: true
volumes:
- name: secret-vol
  secret:
    secretName: db-creds
```

Mount ஆனது tmpfs-ல் நடக்கும். Pod delete ஆனதும் போய்விடும். File permission 0440 ஆக set பண்ணலாம்.

API server -> kubelet -> Pod flow மட்டுமே நடக்கும். Secret data rest of cluster-க்கு expose ஆகாது, RBAC இருந்தால்.

## 4. Architectural Reasoning

Secret எப்போது useful?

* Pod start ஆகும்போது தேவையான credential தேவை.
* ConfigMap-க்கு போட முடியாத sensitive data.
* Same secret பல Pod-களுக்கு share பண்ணணும்.

Alternative என்ன?

* Hardcode in image: build time secret leak. Rotate செய்ய முடியாது.
* ConfigMap: plaintext. அதுவும் same risk.
* External secret manager: HashiCorp Vault, AWS Secrets Manager, external-secrets operator. இது production grade.

ஏன் architect இதை தேர்வு பண்ணுவான்?
Kubernetes native. No external dependency. Small scale-க்கு போதும். Dev/test-க்கு போதும்.

ஆனால் constraint: Secret data etcd-ல store ஆகும். etcd backup எடுத்தால் secret backup-ம் எடுக்கப்படும். அதனால் etcd encryption at rest must be on. Audit log must be on.

## 5. Trade-offs

**Base64 is not encryption.** `kubectl get secret -o yaml` பண்ணினால் decode பண்ணி படிக்கலாம். API access உள்ளவன் பார்த்துவிடலாம்.

**Env var leak.** `/proc/<pid>/environ` மூலம் பார்க்க முடியும். Container runtime log-ல வந்துவிடும். File mount பாதுகாப்பானது.

**Rotation painful.** Secret update ஆனாலும் running Pod-க்கு auto update ஆகாது. Volume mount 1 minute கழித்து refresh ஆகும். Env var refresh ஆகாது. Pod restart தேவை. Zero downtime rotation-க்கு sidecar or external operator தேவை.

**Secret sprawl.** Namespace-க்கு namespace secret copy பண்ணுவாங்க. Drift வரும். Who owns secret? Audit கடினம்.

**Access control.** RBAC இல்லாமல் cluster admin யார் வேண்டுமானாலும் secret படிக்கலாம். Default service account-க்கு read access இருந்தால் risk.

## 6. Practical Example

E-commerce app. Payment service-க்கு Stripe secret key தேவை. DB service-க்கு password தேவை.

நீங்கள் `payment-secret` ஒன்று create பண்ணி, payment Deployment-ல file mount செய்வீர்கள்.

App start ஆகும்போது `/etc/secrets/stripe_key` file-
