# ConfigMaps

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.5 — Kubernetes

## Problem

உங்க microservice ஒன்னு Docker image-ல build ஆகுது. அதுக்குள்ள DB host, API endpoint, log level, feature flag மாதிரி values hardcode பண்ணீங்க.

இப்போ dev, staging, prod என்று 3 environment இருக்கு. ஒவ்வொன்றுக்கும் DB host வேற, log level வேற.

என்ன பண்ணுவீங்க?

* Image-ஐ environment க்கு தகுந்த மாதிரி rebuild பண்ணி push பண்ணுவீங்களா?
* அல்லது Deployment yaml-ல நேரடியா env vars எழுதுவீங்களா?

முதல் option CI/CD-ஐ messy ஆக்கும். ஒரே codeக்கு 3 image tag.
இரண்டாவது option-ல config code-உடன் கலந்து போயிடும், Git history-ல sensitive value வந்து நிற்கும்.

இதுவே painful ஆகும்போது engineers config-ஐ image-ல இருந்து வெளியே எடுக்க ஆரம்பிச்சாங்க. அதுதான் ConfigMap-ன் root problem.

## Mental Model

ConfigMap = Kubernetes-ல இருக்கும் ஒரு config object.

இது application code-ஐ தொடாமல், non-sensitive configuration data-ஐ store பண்ணி, pod-க்கு கொடுக்கும் ஒரு abstraction.

Think of it as: **Image = what to run, ConfigMap = how to run in this environment**.

Code immutable, config mutable. Image build ஒரு முறை, ConfigMap-ஐ மாற்றினால் போதும்.

## How It Works

ConfigMap-ஐ ஒரு key-value map-ஆக create பண்ணுவீங்க.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: payment-service-config
data:
  LOG_LEVEL: info
  FEATURE_NEW_TAX: "true"
  API_ENDPOINT: https://api.internal/payment
```

Pod-க்கு இதை கொண்டு வர 2 வழி:

1. **envFrom / env**: ConfigMap-ல இருந்து env vars ஆக inject பண்ணுவது
2. **volume mount**: ConfigMap-ஐ files ஆக mount பண்ணுவது, `/etc/config` மாதிரி path-ல

உதாரணமாக volume mount:

Pod start ஆகும்போது kubelet ConfigMap data-ஐ tmpfs volume-ல files ஆக create பண்ணும். ConfigMap update ஆனால் mounted files auto update ஆகும். ஆனால் running process அதை reload பண்ணிக்கணும், இல்லன்னா restart தேவை.

Immutable ConfigMap வச்சு accidental overwrite-ஐ தடுக்கலாம்.

## Architectural Reasoning

**எப்போது useful?**

* Environment specific values: DB_HOST, REDIS_URL, feature flags
* Non-sensitive config: log level, timeout values, retry count, API base URL
* Config-ஐ GitOps-ல manage பண்ண வேண்டும், image rebuild இல்லாமல்

**Alternatives என்ன?**

* Config directly in Deployment yaml env: சிறிய setup-க்கு ஓகே, ஆனால் repeat ஆகும், version control கஷ்டம்
* ConfigMap vs Secret: Secret = base64 encoded, TLS cert, password மாதிரி sensitive data. ConfigMap plain text
* External config server: Consul, etcd, AWS Parameter Store. Multi-cluster, dynamic config, encryption வேண்டும்போது.

Architect choose பண்ணும்போது கேட்கும் கேள்வி:
Config code-உடன் couple ஆக இருக்கக் கூடாது. Team size சின்னதா இருந்தா ConfigMap போதும். Enterprise-wide dynamic config, audit, rotation வேண்டும்னா external system தேவை.

## Trade-offs

* **Security**: ConfigMap encrypt ஆகாது. etcd-ல plain text. Secrets க்கு நினைச்சு use பண்ணக்கூடாது.
* **Update semantics**: ConfigMap update ஆனாலும் pod auto restart ஆகாது. Volume mount file update ஆகும், ஆனால் app reload logic இருக்கணும். இல்லன்னா rolling restart தேவை.
* **Size limit**: ConfigMap 1Mi limit. பெரிய file, config dump வைக்க கூடாது.
* **Scope**: Namespace scoped. Cross namespace share கஷ்டம்.

Failure mode: ஒரு engineer ConfigMap-ல typo போட்டு DB_HOST-ஐ மாற்றினார். பழைய ConfigMap name-ஐ reference பண்ணிக்கொண்டிருந்த பல Deployment-கள் restart ஆகி outage வந்தது. Immutable + versioned name pattern use பண்ணாமல் இருந்தால் இது வரும்.

## Practical Example

Payment service-க்கு dev-ல LOG_LEVEL=debug, prod-ல LOG_LEVEL=warn.

நீங்க 3 ConfigMap create பண்ணுவீங்க:
`payment-config-dev`, `payment-config-staging`, `payment-config-prod`

Deployment-ல namespace க்கு ஏற்ப ConfigMap name மாறும். Image ஒன்றே.

Feature flag-க்கு: `FEATURE_NEW_TAX: "true"` ConfigMap-ல. Business
