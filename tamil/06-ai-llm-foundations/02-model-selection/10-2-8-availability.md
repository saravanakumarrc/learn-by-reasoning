# Availability

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.2.8 — Model selection

## 1. Problem

உங்கள் AI product-ல் ஒரு LLM service இருக்கு. User prompt அனுப்பினால் response வரணும். 

ஒரு நாள் OpenAI API timeout ஆகுது. அடுத்த நாள் model rate limit hit ஆகுது. அடுத்த வாரம் provider region down ஆகுது. User-க்கு response இல்லை. 

இங்கே பிரச்சனை என்ன? Correctness இல்லை. Availability இல்லை.

Model selection-ல் நாம் accuracy, cost, latency பார்க்கிறோம். ஆனால் availability-ஐ பார்க்காவிட்டால், best model கூட உங்கள் system-க்கு dead.

**"What goes wrong if we don't have this?"** System uptime இருந்தாலும் user request fail ஆகும். Business impact ஆகும்.

## 2. Mental Model

Availability என்பது simple: **requested service-ஐ, requested time-ல், requested performance-ல் கொடுக்க முடியுமா?**

LLM context-ல் availability என்பது 3 layers:

* **Provider availability**: API up-ஆ? rate limit, outage, maintenance?
* **Model availability**: அந்த model உங்களுக்கு accessible-ஆ? quota, region lock?
* **Your system availability**: fallback இருக்கா? retry logic work ஆகுதா? timeout சரியா set பண்ணியிருக்கீங்களா?

Availability = uptime * reliability of access.

## 3. How It Works

Availability-ஐ உறுதி பண்ண, architects usually do:

**Redundancy**: Multiple providers / models. OpenAI fail ஆனால் Anthropic / local model-க்கு failover.

**Graceful degradation**: Heavy model fail ஆனால் smaller, cheaper model-க்கு switch. Response quality கொஞ்சம் குறையும், ஆனால் service down ஆகாது.

**Circuit breaker + retry with backoff**: Transient failure-க்கு immediate retry செய்யாமல், exponential backoff + jitter. Provider overload ஆவதை தடுக்கும்.

**Timeout budget**: LLM call-க்கு max latency set பண்ணு. Timeout ஆனால் fast fallback model-க்கு போ.

**Capacity planning**: Peak traffic-ல் rate limit hit ஆகாமல், token quota, concurrent request limit-ஐ முன்கூட்டியே பார்த்து plan பண்ணு.

## 4. Architectural Reasoning

Model selection-ல் availability ஏன் முக்கியம்?

ஒரு production RAG / agent system-ல், model என்பது external dependency. Database போல உனக்கு control இல்லை.

Constraint: User expects <2s response. Provider P99 latency 3s. அப்போ உனக்கு option என்ன?

Alternatives:

1. Single best model, hope it stays up
2. Primary + secondary provider
3. Tiered models: fast cheap model for simple queries, strong model for complex
4. Hybrid: Cloud LLM + on-prem small model for failover

அர்சிடெக்ட் choose பண்ணுவது: **business criticality vs cost**.

Banking chatbot-க்கு availability > cost. E-commerce product description generation-க்கு cost > availability.

Decision driver: **SLA**. 99.9% availability வேண்டுமா? அப்போ single provider போதாது.

## 5. Trade-offs

**Availability vs Cost**: Multi-provider setup cost double ஆகும். Redundant quota maintain பண்ணணும்.

**Availability vs Latency**: Failover logic add பண்ணினால், health check + routing overhead வரும். First attempt fail ஆனால் retry-ல் latency increase ஆகும்.

**Availability vs Consistency**: Different models give different output style. Fallback model-க்கு response tone மாறும். User experience inconsistent ஆகும்.

**Availability vs Complexity**: Circuit breaker, fallback routing, model router maintain பண்ணுவது operational overhead. Small team-க்கு over-engineering ஆகும்.

Failure mode முக்கியம்: Cascading failure. Primary fail ஆனதும் எல்லா traffic-யும் secondary-க்கு போனால், secondary-ம் overload ஆகி down ஆகும். அதனால் load shedding தேவை.

## 6. Practical Example

Enterprise support agent.

Design:
* Primary: `gpt-4.1` for complex reasoning, 100 RPM quota
* Secondary: `claude-3.5` for same quality, different provider
* Fallback: `llama-3.1-8b` on-prem for simple FAQ, always up

Flow:
User query -> Router -> Check primary health + rate limit -> Call primary with 2s timeout -> Timeout / 5xx -> Circuit breaker opens -> Try secondary -> Fail -> Serve from fallback with disclaimer.

Monitoring: Provider error rate, latency P95/P99, quota utilization.

Result: Provider outage-லும் service down ஆகாது. Cost increase ~30% ஆனால் SLA meet ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG chatbot இருக்கு. Peak hour-ல் 500 RPS வரும். ஒரே provider-ன் rate limit 1000 TPM. Model latency P95 1.5s. 

Business requirement: 99.5% availability, cost must stay low.

நீங்கள் single model use பண்ணலாமா? அல்லது model router + tiering வேண்டுமா? 

ஏன்? Timeout, retry, fallback எப்படி design பண்ணுவீர்கள்? Trade-off என்ன?

## 8. Key Takeaways

* Availability என்பது model accuracy இல்லை, service accessible-ஆ இருப்பது.
* Single provider = single point of failure. Production-ல் redundancy தேவை.
* Model selection-ல் latency, quota, region availability-ஐ SLA-வோடு compare பண்ணு.
* Failover, circuit breaker, graceful degradation இல்லாமல் availability guarantee பண்ண முடியாது.
* Every availability improvement adds cost and complexity. Choose based on business criticality.
