# Load testing

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.1.7 — Testing strategy

## 1. Problem

Prod-ல release பண்ணின சில மணி நேரத்தில் traffic spike வருது. 100 RPS-ல சரியாக இருந்த API, 1000 RPS வந்த உடனே latency ஏற ஆரம்பிக்குது. p99 200ms-ல இருந்து 5s ஆகுது. Timeouts, 5xx errors வருது. DB connection pool exhaust ஆகுது. Autoscaling trigger ஆகும் முன்னாடியே users fail ஆகி போயிடறாங்க.

இது ஏன் நடக்குது? Dev மற்றும் staging-ல எல்லாம் வேலை செய்யுது. அங்கே load இல்லை. Real traffic pattern, concurrent users, sustained load எதுவும் simulate பண்ணல.

Load testing இல்லாமல் என்ன ஆகும்? Bottleneck-ஐ production-ல கண்டுபிடிக்கிறோம். அதாவது customer-கிட்ட கண்டுபிடிக்கிறோம். அது cost, reputation, incident.

## 2. Mental Model

Load testing என்பது production-ஐ போல ஒரு controlled traffic-ஐ உருவாக்கி, system எப்படி behave பண்ணும் என்பதை முன்கூட்டியே பார்ப்பது.

இது unit test இல்லை. Correctness test இல்லை. System-ன் performance characteristics-ஐ பார்ப்பது: throughput எவ்வளவு வரை stable இருக்கும், latency எப்போது degrade ஆகும், எங்கே resource saturation வரும்.

முக்கியமானது breaking point-ஐ கண்டுபிடிப்பது, அதற்கு முன்னால் safe operating range-ஐ define பண்ணுவது.

## 3. How It Works

Load generator → target system → metrics.

Load generator virtual users உருவாக்கும். அவங்க real user போல request அனுப்புவாங்க. முக்கிய knobs:

* **Virtual users / concurrency**: எத்தனை பேர் ஒரே நேரத்தில்
* **RPS**: requests per second
* **Ramp-up**: load-ஐ எவ்வளவு மெதுவாக ஏத்துறது
* **Duration**: sustained load எவ்வளவு நேரம்
* **Think time**: request-க்கு இடையில் realistic pause

நாம் measure பண்ணுவது:

* Latency percentiles: p50, p95, p99
* Error rate, timeout rate
* Throughput: successful RPS
* Resource utilization: CPU, memory, DB connections, queue length
* Saturation point: எங்கே latency அதிகரிக்க ஆரம்பிக்குது

Load test என்பது pass/fail இல்லை. Data collect பண்ணி architecture decision எடுக்க.

## 4. Architectural Reasoning

Load testing useful ஆகும் போது:

* New service launch, scale up plan, SLA commitment உள்ளது
* Bottleneck கண்டுபிடிக்க வேண்டும்: DB, cache, downstream API
* Capacity planning: எத்தனை instances வேண்டும், connection pool size என்ன
* Change impact: DB index மாற்றம், new library, autoscaling config

Constraint it addresses: latency budget, availability, cost efficiency.

Alternatives என்ன?

* Production monitoring மட்டும்: real but risky, you learn after damage
* Benchmarking single component: useful but misses system interaction
* Chaos testing: resilience பார்க்கும், load அல்ல

ஆர்க்கிடெக்ட் choose பண்ணுவது ஏனெனில் load test கொடுக்கும் confidence-ஐ production incident கொடுக்காது. Trade-off தெரிந்து design செய்ய முடியும்.

## 5. Trade-offs

* **Realism vs Cost**: Production-like data, traffic pattern, warm cache வேண்டும். அது expensive. Oversimplified test கொடுக்கும் false confidence.
* **Test environment parity**: Staging prod போல இல்லை என்றால் results misleading. Data size, network latency, DB load வேறுபடும்.
* **Synthetic load vs real traffic**: Synthetic repeatable ஆன
