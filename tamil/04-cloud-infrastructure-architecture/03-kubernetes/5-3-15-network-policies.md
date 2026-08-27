# Network policies

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.15 — Kubernetes

## 1. Problem

ஒரே Kubernetes cluster-ல் பல teams-ன் workloads ஓடுது. default-ஆ Kubernetes எல்லா pod-களுக்கும் எல்லா pod-களோடும் network traffic-ஐ allow பண்ணும்.

அதாவது `frontend` pod நேரடியா `payment-service` pod-ஐ ping பண்ண முடியும். `dev` namespace-ல் இருக்கும் ஒரு test pod production database pod-ஐ அணுக முடியும்.

இது ஏன் பிரச்சனை?
* ஒரு pod compromise ஆனால் lateral movement எளிது. Attacker ஒரு pod-ல இருந்து முழு cluster-ஐ scan பண்ணி உள்ளே போயிடலாம்.
* Multi-tenant cluster-ல team A team B-ன் service-ஐ தற்செயலா அணுகி மாற்றி விடலாம்.
* Compliance audit-ல "network segmentation இல்லை" என்று fail ஆகும்.

Firewall இல்லாத LAN மாதிரி இருக்கு. இந்த allow-all-ஐ கட்டுப்படுத்த ஏதாவது வேண்டும்.

## 2. Mental Model

NetworkPolicy என்பது **pod-level firewall** மாதிரி.

நீங்கள் pod-களுக்கு label கொடுக்கிறீர்கள், பிறகு சொல்கிறீர்கள்:
* இந்த pod-களுக்கு யார் **ingress** பண்ணலாம்?
* இந்த pod-கள் யாருக்கு **egress** பண்ணலாம்?

இது VLAN / security group-ன் fine-grained version. Namespace boundary அல்ல, label boundary.

## 3. How It Works

Kubernetes API-ல் `NetworkPolicy` resource இருக்கு. ஆனால் Kubernetes core அதை enforce செய்யாது. உங்கள் CNI plugin தான் enforce செய்யும். Calico, Cilium, Weave இவைகள்.

முக்கிய concept:

* **podSelector**: எந்த pod-களுக்கு இந்த policy apply ஆகும்.
* **policyTypes**: Ingress, Egress
* **from / to**: peer selection by podSelector, namespaceSelector, IPBlock.

Default behavior மிக முக்கியம்: **ஒரு namespace-ல NetworkPolicy இல்லையென்றால், எல்லா traffic-மும் allow**. ஒரு NetworkPolicy create செய்ததும், அந்த policy select செய்யும் pod-களுக்கு default deny ஆகி, policy-ல define செய்த rules மட்டுமே allow.

எளிய example:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-only
spec:
  podSelector:
    matchLabels: {app: order-service}
  policyTypes: [Ingress]
  ingress:
  - from:
    - podSelector:
        matchLabels: {app: frontend}
```

இது `order-service` pod-க்கு `frontend` label உள்ள pod-களில் இருந்து மட்டுமே traffic வர அனுமதிக்கும்.

## 4. Architectural Reasoning

NetworkPolicy எப்போது useful?

* **Blast radius குறைக்க**: compromised pod வெளியே spread ஆகாமல் தடுக்க.
* **Zero trust network**: service mesh இல்லாத சூழலில் முதல் layer isolation.
* **Compliance**: PCI, HIPAA போன்றவற்றில் network segmentation காட்ட.

Alternatives:
* **Service Mesh** - mTLS + L7 authorization. NetworkPolicy-க்கு மேல் layer. அதிக security ஆனால் complexity, latency, cost.
* **Namespace + node separation**: dev/prod வெவ்வேறு cluster/node. வேலை செய்யும் ஆனால் fine-grained இல்லை.
* **Cloud security groups / external firewall**: cluster exit/entry மட்டும் கட்டுப்படுத்தும்.

Decision: NetworkPolicy என்பது **lightweight, native, L3/L4** isolation. Service mesh வேண்டாம் என்றால் இது minimum.

## 5. Trade-offs

* **Security vs Operability**: Default deny போட்டால் முழு app down ஆகும். Database connection, monitoring, DNS, kube-dns-க்கு explicit allow வேண்டும். இதை மறந்தால் silent outage.
* **CNI dependency**: NetworkPolicy work செய்யும் என்பது CNI
