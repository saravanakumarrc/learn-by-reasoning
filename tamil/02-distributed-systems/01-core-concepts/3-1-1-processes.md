# Processes

> **Learning Path:** Distributed Systems
> **Section:** 3.1.1 — Core concepts

### 1. Problem

உங்களிடம் ஒரு monolith application இருக்கு. Order, payment, inventory, notification எல்லாம் ஒரே code base-ல, ஒரே process-ல ஓடுது.

ஒரு நாள் notification service-ல memory leak வந்து process crash ஆகுது. என்ன ஆகும்? Order-ம் payment-ம் எல்லாம் down.

அடுத்து traffic spike வருது. Payment-க்கு மட்டும் scale பண்ணணும். ஆனா முழு monolith-ஐயும் duplicate பண்ணி scale பண்ணனும். Inventory idle-ஆ இருந்தாலும் resources waste.

இதுதான் problem. ஒரே process-ல எல்லாம் சேர்த்து வைக்கும்போது failure, scaling, deployment எல்லாம் கட்டுப்படுத்த முடியாம போகுது.

> What goes wrong if we don't have process boundaries?

### 2. Mental Model

Process என்பது independent execution unit. தனக்கென்று memory space, state, execution context உண்டு. 

Thread-க்கு shared memory உண்டு. Process-க்கு இல்லை. ஒரு process crash ஆனாலும் அது மற்ற process-ஐ affect பண்ணாது.

Distributed system-ல ஒவ்வொரு node-ல ஓடும் ஒவ்வொரு service-ம் practically ஒரு process அல்லது process group. அவை network மூலம் மட்டுமே பேசும். Shared memory இல்லை.

Analogy: ஒரு restaurant-ல ஒவ்வொரு station-மும் தனித்தனியாக இயங்கும். Grill station-ல தீ விபத்து வந்தாலும் cash counter நிற்காது.

### 3. How It Works

OS level-ல process என்பது independent address space. இரண்டு process-க்கு இடையே data போகணும்னா message passing தான் வழி. Local-ல socket, pipe; distributed-ல TCP/IP, HTTP/gRPC.

Process boundary-ல state copy ஆகாது. Reference share பண்ண முடியாது. நீங்கள் communicate பண்ணணும் என்றால் serialize செய்து send பண்ண வேண்டும்.

இதனால்:

* Failure isolation உண்டு
* Independent lifecycle உண்டு. ஒன்றை restart பண்ணலாம், மற்றதை தொடாமல்
* Independent scaling, deployment, resource allocation சாத்தியம்

### 4. Architectural Reasoning

Process boundary எப்போது வேண்டும்?

* **Fault containment**: Critical path-ஐ non-critical work-ல இருந்து பிரிக்கும்போது. Payment process crash ஆனால் search process ஓட வேண்டும்.
* **Scaling constraint வேறுபடும் போது**: Read traffic 10x, write traffic 2x. Different process-களை வெவ்வேறு scale பண்ணலாம்.
* **Team ownership**: Order team, Payment team வேறு வேறு release cycle வைத்திருக்கும் போது.

Alternatives என்ன?
* Threads / in-process modules: Low latency, shared memory, ஆனால் crash contagion உண்டு.
* Single process multi-module: Fast communication, ஆனால் coupling அதிகம்.

Architect-ஆ choose பண்ணுவது எப்போது? Process boundary cost ஏற்றுக்கொள்ளும் அளவுக்கு independence value இருக்கும்போது.

### 5. Trade-offs

**Isolation vs Latency**
Process boundary தாண்டி message போக network hop, serialization, deserialization வரும். Same process-ல function call நானோ seconds. Cross process RPC milliseconds ஆகலாம். Latency அதிகரிக்கும்.

**Consistency vs Availability**
Shared memory இல்லாததால் distributed state maintain பண்ண transaction hard ஆகும். Two-phase commit, saga போன்ற patterns வரும். Strong consistency கிடைக்காமல் போகலாம்.

**Operational complexity**
Process அதிகமானால் monitoring, logging correlation, deployment orchestration, failure modes அதிகரிக்கும். Kubernetes, service mesh போன்ற tooling தேவைப்படும்.

Important failure mode: Process crash ஆனால் in-flight requests drop ஆகும். Idempotency, retry, timeout, dead letter queue போன்ற mechanisms தேவை.

### 6. Practical Example

E-commerce checkout flow.

`API Gateway` -> `Order Service` process -> `Payment Service` process -> `Inventory Service` process -> `Notification Service` process

ஒவ்வொன்றும் தனி process, தனி container, தனி database.

Order Service payment complete event-ஐ publish பண்ணும். Notification Service அதை consume பண்ணும்.

Payment Service crash ஆனால் Order Service pending state-ல இருக்கும். Circuit breaker திறந்து fallback காட்டும். மற்ற services ஓடும்.

Scale பண்ணும்போது Black Friday-ல Payment Service-ஐ 20 replicas, Notification Service-ஐ 3 replicas என்று வெவ்வேறாக scale பண்ணலாம்.

```
Client --> Order Service
Order Service --RPC--> Payment Service
Order Service --event--> Inventory Service
Payment Service --event--> Notification Service
```

Process boundary தான் service boundary ஆக மாறுகிறது.

### 7. Reasoning Challenge

உங்களிடம் ஒரு real-time pricing engine இ
