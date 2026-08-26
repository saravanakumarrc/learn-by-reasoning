# Network failures

> **Learning Path:** Distributed Systems
> **Section:** 3.1.6 — Core concepts

## 1. Problem

நீங்க ஒரு distributed system design பண்ணிக்கிட்டு இருக்கீங்க. Order Service, Payment Service, Inventory Serviceன்னு மூணு service-கள். Order Service Payment Service-க்கு HTTP call பண்ணி payment confirm பண்ணும்.

Local-ல எல்லாம் சரியா வேலை செய்யும். Production-ல network வழியா call போகும் போது என்ன ஆகும்?

Network packet drop ஆகலாம். Switch hang ஆகலாம். Service B slow ஆகலாம். GC pause, CPU spike, network partition வரலாம். Result என்ன? Request hang ஆகும். Client-க்கு response போகாது. Timeout ஆகும்.

இதை ignore பண்ணினா system ஒரே call fail ஆனதும் மொத்த flow-ம் fail ஆகும். Retry பண்ணா duplicate payment ஆகும். Retry பண்ணலைன்னா user-க்கு false failure காட்டும்.

இதுதான் network failures-ஐ design பண்ண வைக்கும் problem.

## 2. Mental Model

Network-ஐ reliable ஆ assume பண்ணாதீங்க.

Distributed systems-ல ஒரு basic mental model இருக்கு: **The network is unreliable**. Latency unpredictable, packets lost, connections reset, partitions happen.

இதை ஒரு post office மாதிரி நினைச்சுக்கோங்க. நீங்க letter அனுப்பினீங்க. அது தொலைஞ்சு போகலாம், late ஆ வரலாம், duplicate ஆ வரலாம், ஆனா deliver ஆனதா உங்களுக்கு confirm கிடைக்காமலும் போகலாம்.

இந்த uncertainty-தான் architecture decisions-ஐ drive பண்ணுது.

## 3. How It Works

Network failure எப்படி present ஆகும்?

* **Timeout**: Service B respond பண்ணாம இருக்கு. Client wait பண்ணிட்டு இருக்கு. இதுவே resource leak.
* **Connection reset / dropped**: TCP connection முறிஞ்சு போகும். Client-க்கு error வரும்.
* **Slow network / latency spike**: Request complete ஆகும் ஆனா user experience-க்கு மிகவும் slow.
* **Network partition**: Service A-க்கும் Service B-க்கும் இடையே network cut. இரண்டும் ஒன்னோட ஒன்னு பேச முடியாது.
* **Partial failure**: Request reach ஆகும், processing ஆகும், response path-ல fail ஆகும். Server process பண்ணிடுச்சு ஆனா client-க்கு தெரியாது.

முக்கியமானது: Failure visible ஆகும் போது மட்டுமல்ல, invisible ஆகும் போதும் problem. Server processed ஆனா client-க்கு response போகலைன்னா?

## 4. Architectural Reasoning

Network failure-க்கு ஒரே solution இல்லை. Design choice-கள் failure-ஐ எப்படி handle பண்ணுறோம் என்பதைப் பற்றியது.

* **Timeout set பண்ணுங்க**: Infinite wait பண்ண கூடாது. Service call-க்கு reasonable timeout வையுங்க. Timeout value என்பது SLA, downstream latency distribution, retry policy-யை பொறுத்து வரும்.
* **Retry with backoff**: Transient failure-க்கு retry பண்ணலாம். ஆனா blind retry பண்ணா retry storm வரும். Exponential backoff + jitter பயன்படுத்துங்க.
* **Idempotency**: Retry பண்ணினாலும் duplicate side effect வரக்கூடாது. Payment request-ஐ idempotent key-ஓட அனுப்புங்க. Server same key வந்தா duplicate process பண்ணாம return பண்ணும்.
* **Circuit breaker**: Downstream repeatedly fail ஆனா, அதுக்கு call பண்ணுவதை தற்காலிகமா stop பண்ணுங்க. Fast fail, resource waste தடுக்க.
* **Graceful degradation**: Critical path-க்கு மட்டும் call பண்ணுங்க, non-critical-ஐ skip பண்ணி partial response கொடுங்க.

```
Client -> Service A -> Service B
               |
           Timeout?
               v
           Retry -> Idempotent
               v
           Circuit Open?
```

இது ஒரு failure-aware request flow.

## 5. Trade-offs

**Timeout short vs long**
Short timeout = fast failure, better user experience, but false positives அதிகம். Long timeout = fewer false failures, ஆனா caller threads pool exhaust ஆகும், latency cascade ஆகும்.

**Retry vs No retry**
Retry improves availability for transient failures. ஆனா retry பண்ணினா load அதிகரிக்கும், duplicate risk வரும். Idempotency இல்லாம retry ப
