# Ingress

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.4 — Kubernetes

## Problem

உங்கள் cluster-ல் 10 microservices ஓடுது. எல்லாம் `ClusterIP Service`-க்குள் இருக்கு. அதாவது pod-கள் private IP-ல் மட்டுமே reachable.

இப்போ external user க்கு `api.example.com` வழியா `order-service` போகணும், `web.example.com` வழியா frontend போகணும். Mobile app ஒரு வேறு path-க்கு போகணும்.

வழக்கமான தீர்வு என்ன?
ஒவ்வொரு service-க்கும் ஒரு LoadBalancer Service. அது ஆகும், மெதுவாக scale ஆகும், cloud cost ஏறும். ஒவ்வொரு service-க்கும் TLS certificate manage பண்ணணும்.

இந்த வலியிலிருந்துதான் Ingress வந்தது.

> ஒரு entry point, பல services-க்கு routing, TLS termination, host/path rules ஒரே இடத்தில்.

## Mental Model

Ingress = cluster-க்கு வரும் traffic-க்கான reverse proxy / front door.

நினைத்துக்கொள்ளுங்கள்: ஒரு அலுவலக கட்டிடத்தில் ஒரே main gate இருக்கு. Security guard வெளியே வருபவரின் badge / request பார்த்து, எந்த floor, எந்த room க்கு அனுப்புவது என்று decide பண்ணுகிறார்.

Ingress controller தான் அந்த guard. Ingress resource தான் routing rules book.

Controller: NGINX, Traefik, HAProxy, AWS ALB Controller போன்றவை. Kubernetes API-யை watch பண்ணி, rules வந்ததும் backend proxy-யை configure செய்கின்றன.

## How It Works

நீங்கள் ஒரு Ingress resource create செய்கிறீர்கள்:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  tls:
  - hosts: [api.example.com]
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /orders
        pathType: Prefix
        backend:
          service:
            name: order-service
            port: {number: 80}
```

Ingress controller இதை பார்த்து, NGINX config generate செய்து reload செய்யும்.

Flow:

```mermaid
graph LR
User -->|HTTPS| Cloud LB
Cloud LB --> Ingress Controller
Ingress Controller -->|host/path| Service A
Ingress Controller -->|host/path| Service B
Service A --> Pod A
Service B --> Pod B
```

Controller cluster-ல் Deployment-ஆக ஓடும். அதற்கு external access கொடுக்க NodePort அல்லது LoadBalancer Service தேவை. அதன் பின்னால் எல்லா service-களும் இருக்கின்றன.

## Architectural Reasoning

**எப்போது Ingress தேவை?**

* Multiple services-க்கு external access தேவை, ஆனால் ஒவ்வொன்றுக்கும் தனி LoadBalancer வேண்டாம்.
* Host-based routing / path-based routing தேவை.
* TLS termination ஒரே இடத்தில் centralize பண்ண வேண்டும்.
* Canary, A/B routing, rate limiting போன்ற L7 features வேண்டும்.

**மாற்று வழிகள்:**

* **LoadBalancer Service per service**: Simple, but cost + IP limit. L4 மட்டுமே.
* **NodePort + external LB**: Manual config, maintainability குறைவு.
* **Service Mesh Gateway**: Istio Gateway, Linkerd. Ingress-க்கும் மேல் fine-grained mTLS, observability தேவைப்பட்டால்.

அதனால் decision: வெளி உலகத்திலிருந்து வரும் HTTP/HTTPS traffic-க்கு L7 routing தேவை என்றால் Ingress. உள் cluster service-to-service L4/ mTLS வேண்டுமென்றால் Service Mesh.

## Trade-offs

* **Single point of failure / blast radius**: Controller down ஆனால் எல்லா external traffic-ம் போகாது. அதனால் controller-ஐ multi-replica, different nodes-ல் spread செய்ய வேண்டும்.
* **L7 vs L4**: Ingress HTTP/HTTPS மட்டுமே. gRPC, TCP, UDP க்கு TCP Ingress அல்லது separate Service தேவை.
* **Controller implementation differences**: NGINX Ingress annotation rich. Traefik dynamic. AWS ALB controller annotation வேறு. Porting கஷ்டம்.
* **TLS management**: Certificate renewal, secret sync. Cert-Manager போன்ற operator உதவும். ஆனால் secret rotate பண்ணும்போது controller reload lag வரலாம்.
* **Observability**: Ingress controller logs, metrics முக்கியம். Backend service error-ஐ Ingress 502/504-ஆக மாற்றும். Debugging complex ஆகும்.

## Practical Example

Enterprise e-commerce:

* `api.example.com/orders` → order-service
* `api.example.com/payments` → payment-service
* `web.example.com` → frontend

ஒரே Ingress controller, ஒரே TLS secret `example.com` wildcard.

Canary release: `/orders` traffic-ன் 10% `order-service-v2` க்கு அனுப்ப.

Rate limit: payment path-க்கு per IP limit.

இதனால் external LB ஒன்று போதும், cost குறையும், certificate ஒரே இடத்தில்.

## Reasoning Challenge

உங்களுக்கு 3 environments இருக்கு: dev, staging, prod. எல்லாம் ஒரே cluster-ல் namespace isolate செய்யப்பட்டுள்ளன.

இப்போது external access தேவை:

* `api.dev.example.com` → dev namespace
* `api.staging.example.com` → staging namespace
* `api.example.com` → prod namespace

ஒரு team Ingress controller-ஐ maintain செய்ய விரும்புகிறது, ஆனால் ஒவ்வொரு namespace team-க்கும் தனியாக route சேர்க்க உரிமை கொடுக்க வேண்டும்.

இங்கே IngressClass + RBAC எப்படி வடிவம
