# Helm

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.4.2 — Platform engineering

## 1. பிரச்சனை

நீங்க platform team-ல இருக்கீங்க. 30 teams Kubernetes-ல deploy பண்ணணும்.

ஒரு service-க்கு Deployment, Service, ConfigMap, Secret, Ingress, HPA, ServiceMonitor — இப்படி 8-10 YAML files. dev, staging, prod-க்கு values மாறும்: replica count, resource limits, image tag, DB host.

இப்போது என்ன ஆகுது?

* `kubectl apply -f` பண்ணி மறந்துட்டா drift வரும்
* ஒரு field மாறினா எல்லா environments-லயும் copy-paste
* Rollback எப்படி? `git log`-ல தேடி பழைய yaml-ஐ திரும்ப apply பண்ணணும்
* Team A ஒரு மாதிரி எழுதுது, Team B இன்னொரு மாதிரி எழுதுது. Standard இல்ல

இதுதான் painful. Manual manifest management scale ஆகாது.

## 2. Mental Model

Helm என்பது Kubernetes-க்கான package manager.

Linux-ல `apt install nginx` பண்ணுவது மாதிரி, Helm-ல `helm install myapp ./chart` பண்ணுவது.

Core idea: **templates + values + versioned release**.

ஒரு Chart = ஒரு application அல்லது infrastructure component-ன் reusable package. அதுக்குள்ள Kubernetes manifests templates-ஆ இருக்கும். Deploy time-ல values-ஐ fill பண்ணி, ஒரு Release-ஆ create பண்ணும்.

## 3. How It Works

Chart structure:

```
mychart/
  Chart.yaml      # name, version, dependencies
  values.yaml     # default values
  values-prod.yaml
  templates/
    deployment.yaml
    service.yaml
```

`templates/deployment.yaml`-ல Go template இருக்கும்:

```yaml
replicas: {{ .Values.replicaCount }}
image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
```

`helm install` பண்ணும்போது:
1. values.yaml + override values merge ஆகும்
2. templates render ஆகி final manifests generate ஆகும்
3. அந்த manifests Kubernetes API-க்கு apply ஆகும்
4. Helm release-ஐ track பண்ணும்

Upgrade, rollback எல்லாம் release history-ல இருந்து நடக்கும்.

```
flowchart LR
A[values.yaml] --> C[Chart templates]
B[helm install/upgrade] --> C
C --> D[Kubernetes API]
D --> E[Release v1,v2...]
E --> F[helm rollback]
```

## 4. Architectural Reasoning

Helm பிரச்சனைக்கு வரும்போது useful ஆகும்:

* **Repeatability**: Same chart, different values for dev/staging/prod
* **Versioning**: Chart version 1.2.3, app version 0.4.1 — both tracked
* **Upgrade safety**: `helm upgrade --atomic --history` பண்ணி failed ஆனா auto rollback
* **Standardization**: Platform team base chart கொடுக்கும், teams அதை extend பண்ணும்

Alternatives என்ன?
* **Raw manifests**: Simple, but no templating, no versioning
* **Kustomize**: Overlay based, good for small variations, templating limited
* **Helm**: Full templating + packaging

Architect decision: Team self-service வேணும், multi-env parity வேணும், மேலும் chart-ஐ reuse பண்ணணும் என்றால் Helm தேர்வு. Kustomize போதுமானதாக இருந்தால், அதன் complexity குறைவு.

## 5. Trade-offs

* **Abstraction leak**: Template logic complex ஆனால் debug கஷ்டம். Render ஆன output-ஐ பார்க்காமல் apply பண்ணுவது risk
* **State management**: Helm release state Kubernetes-ல secret-ஆ store ஆகும். Cluster wipe ஆனால் history போகும். GitOps + Helm பயன்படுத்தும்போது drift issues வரும்
* **Secret handling**: Helm-ல Secret-ஐ plaintext values-ல வைக்க கூடாது. External Secrets / Sealed Secrets தேவை
* **Upgrade risk**: Template change பண்ணி upgrade பண்ணினால், implicit changes வ
