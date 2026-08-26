# Profiling

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.13 — 1. Programming mastery

## Problem

உங்கள் service ஓடிக்கொண்டிருக்கிறது. புதிய feature release பண்ணியதும் p99 latency 200ms-ல இருந்து 800ms ஆகி விட்டது. CPU usage, memory usage, DB query time எல்லாம் normal-ஆக தெரிகிறது. Metrics சொல்கிறது *what* slow ஆகிறது என்று, ஆனால் *why* என்று சொல்லவில்லை.

இதை logs போட்டு கண்டுபிடிக்க முயற்சித்தால் நீங்கள் ஏற்கனவே சந்தேகிக்கும் இடத்தில் மட்டுமே பார்க்கிறீர்கள். உண்மையான bottleneck வேறு இடத்தில் இருக்கலாம். இதுதான் profiling தேவைப்படும் இடம்.

## Mental Model

Profiler என்பது system-க்கு X-ray எடுப்பது போன்றது.

Metrics உங்களுக்கு fever உள்ளது என்று சொல்லும். Tracing உங்களுக்கு எந்த service-ல் delay ஆகிறது என்று சொல்லும். Profiler உங்களுக்கு **code-ல் எந்த function, எந்த line, எந்த allocation** அதிக நேரத்தை செலவழிக்கிறது என்று காட்டும்.

அதாவது, "எங்கே நேரம் கரைகிறது" என்பதை data-வுடன் காட்டுவது.

## How It Works

இரண்டு முக்கிய வழிகள்:

**Sampling profiler** : குறிப்பிட்ட interval-ல், எந்த code stack-ல் CPU இருக்கிறது என்று snapshot எடுக்கும். Overhead குறைவு, production-ல் பாதுகாப்பானது. Flame graph, call graph போன்ற visualization கிடைக்கும்.

**Instrumentation profiler** : Function enter/exit-ல் hook போட்டு exact time, call count, allocation count measure செய்யும். Accurate ஆனால் overhead அதிகம்.

CPU profiler, memory profiler, allocation profiler, wall-clock profiler என்று வகைகள் உண்டு.

CPU profiler பார்க்கிறது hot path எது. Memory profiler பார்க்கிறது leak இருக்கிறதா, எங்கே அதிக allocation நடக்கிறது. Allocation profiler பார்க்கிறது GC pressure-க்கு காரணம் என்ன.

## Architectural Reasoning

Profiler எப்போது தேவை?

* Unknown unknown performance issue இருக்கும்போது. Metrics normal ஆனால் user experience மோசமாக இருக்கிறது.
* Latency budget-ஐ மீறும் போது, ஆனால் root cause தெரியவில்லை.
* CPU/memory உயர்ந்திருக்கிறது, ஆனால் எந்த component-க்கு என்று தெரியவில்லை.
* Refactor செய்யும் முன், baseline எடுக்க வேண்டும்.
* Production incident postmortem-ல்.

Architect-ஆக நீங்கள் profiling-ஐ debugging tool அல்ல, design feedback loop-ஆக பார்க்க வேண்டும். ஒரு service-ன் cost, latency, scalability எல்லாம் hot path-உடன் தொடர்புடையது.

## Trade-offs

* **Overhead vs Accuracy.** Sampling cheap ஆனால் rare events miss ஆகலாம். Instrumentation precise ஆனால் production-ல் பயன்படுத்த முடியாது.
* **Signal vs Noise.** Profiler நிறைய data தரும். Wrong question கேட்டால் time waste. எந்த hypothesis-க்கு profile செய்கிறீர்கள் என்பது முக்கியம்.
* **Production safety.** Attach profiler production-ல் செய்யும்போது pause, lock contention வரலாம். Many teams profiling-ஐ canary அல்லது staging-ல் மட்டுமே செய்கிறார்கள்.
* **Sampling bias.** CPU-bound code மட்டும் தெரியும். I/O wait, lock contention, GC pause போன்றவை CPU profiler-ல் தெரியாமல் போகலாம். அதற்கு wall-clock profiler அல்லது event-based profiling தேவை.

Every profiling decision creates a trade-off with observability cost.

## Practical Example

ஒரு Python RAG service. Embedding generation + vector search + LLM call pipeline. p99 latency 3s ஆகியுள்ளது.

Metrics: API latency high. Tracing: vector DB call 200ms, LLM call 1.8s. மீதி 1s எங்கே போகிறது?

CPU sampling profiler ஓடினால் flame graph-ல் `json.dumps` மற்றும் `pydantic model validation` பெரிய block-ஆக தெரிகிறது. ஒவ்வொரு request-லும் 50KB context-ஐ serialize/deserialize செய்கிறீர்கள், அதுவும் ஒவ்வொரு hop-லும்.

Decision: Serialization-ஐ lazy செய்ய, அல்லது binary format-க்கு மாற, அல்லது validation-ஐ hot path-ல் குறைக்க.

Profiler இல்லாமல் நீங்கள் DB-ஐ scale செய்ய முயற்சித்திருப்பீர்கள். அது பணம் வீண்.

## Reasoning Challenge

உங்களிடம் Java microservice இருக்கிறது. p99 latency peak hours-ல் 2s ஆகிறது. CPU 30% மட்டுமே. Memory steady. GC logs normal. Tracing-ல் DB latency normal.

நீங்கள் என்ன profile செய்வீர்கள்? CPU profiler போதுமா? Wall-clock profiler தேவையா? அதற்கு என்ன hypothesis இருக்கிறது?

## Key Takeaways

* Profiling என்பது *where time goes*
