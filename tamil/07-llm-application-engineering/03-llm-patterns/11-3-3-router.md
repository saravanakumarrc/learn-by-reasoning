# Router

> **Learning Path:** LLM Application Engineering
> **Section:** 11.3.3 — LLM patterns

## 1. Problem

உங்க LLM application-ல ஒரே model எல்லா query-க்கும் use பண்ணுறீங்க.

Simple FAQ-க்கு கூட expensive model use ஆகுது. Cost ஏறுது.
Latency high ஆகுது.
Complex reasoning தேவைப்படும் query-க்கு small model தவறான பதில் தருது.

இப்போ என்ன problem?
One size fits all என்பது வேலை செய்யாது. Cost, latency, quality எல்லாம் trade-off ஆகுது.

What goes wrong if we don't have routing? 
நீங்க எல்லாத்துக்கும் GPT-4o போல expensive model-ஐ run பண்ணினால் cost கட்டுப்படியாகாது. சின்ன model-ஐ மட்டும் use பண்ணினால் quality drop ஆகும்.

அப்போ தேவை: **query-வை பார்த்து சரியான model-க்கு அனுப்புவது.**

## 2. Mental Model

Router என்பது traffic police மாதிரி.

Request வருது. அதோட complexity, sensitivity, cost budget, latency requirement பார்த்து, அதை சரியான model-க்கு forward பண்ணுது.

ஒரு distributed system-ல service mesh-ல traffic route பண்ணுற மாதிரிதான். ஆனால் இங்கே destination என்பது model.

## 3. How It Works

Router ஒரு lightweight classifier-ஆக வேலை செய்யும்.

Input prompt வரும்போது:

1. **Feature extraction**: length, intent, domain, tools தேவையா, reasoning depth
2. **Routing policy**: rule-based or learned
3. **Dispatch**: Model A / Model B / Model C க்கு அனுப்பு
4. **Fallback**: Model fail ஆனால் retry / degrade

Simple rule-based: 
`if prompt contains "code" → code model`
`if prompt < 100 tokens and FAQ → small cheap model`
`if user = premium → large model`

Learned router: Small classifier model prompt-ஐ read பண்ணி, எந்த model best என்பதை predict பண்ணும். இதை offline evaluation data-ல train பண்ணலாம்.

## 4. Architectural Reasoning

Router useful ஆகும் போது:

- Multiple models இருக்கும் போது: e.g., `tiny model for classification`, `medium model for general chat`, `large model for reasoning`, `specialized model for finance/legal`
- Cost constraint இருக்கும் போது. 80% queries simple, 20% complex
- Latency SLO வேறுபடும் போது. Real-time chatbot vs async report generation
- Availability / redundancy வேண்டும் போது. Primary model down ஆனால் fallback

Alternatives என்ன?
- Always use one large model: simple, but expensive and slow
- Always use one small model: cheap, but quality drop
- Client side routing: app code decides. Works for small scale, but logic scattered

Architect ஏன் router choose பண்ணுவார்?
Decoupling. Model selection logic ஒரே இடத்தில். New model add பண்ணும்போது app-ஐ மாற்ற வேண்டாம். A/B test பண்ணலாம். Cost control பண்ணலாம்.

## 5. Trade-offs

**Routing accuracy vs overhead.** Router தப்பா route பண்ணினால் quality பாதிக்கும். Router-ஐ run பண்ணுவதே latency சேர்க்கும். So router itself should be cheap and fast.

**Complexity.** Now you have model fleet to manage, monitoring, fallback logic. Operability கூடும்.

**Consistency.** Same query வந்தால் வெவ்வேறு model-க்கு போகலாம். Output style மாறும். User experience inconsistent ஆகலாம். Session stickiness தேவைப்படலாம்.

**Observability தேவை.** எந்த query எந்த model-க்கு போனது, cost, latency, quality ஒவ்வொன்றும் track பண்ணனும். இல்லை என்றால் router blind ஆகும்.

Failure mode: Router itself fails → no traffic. So router should be stateless, redundant, with default safe route.

## 6. Practical Example

Enterprise support chatbot.

Flow:
User query → Router → 

- Intent = "reset password" → tiny intent classifier model + knowledge base retrieval. Cost ~ $0.0001
- Intent = "billing dispute" → medium model with tool call to CRM
- Intent = "technical troubleshooting with logs" → large reasoning model
- User tier = Enterprise + prompt contains PII → route to private hosted model

Router rule:
```
if sentiment = angry and intent = billing → large model + human escalation flag
if prompt length > 1000 tokens → large context model
else → small model
```

Result: Average cost per query 60% குறையும். P95 latency குறையும். Quality for complex cases improve ஆகும்.

## 7. Reasoning Challenge

உங்களிடம் 3 models இருக்கு: `tiny 3B` cheap, `medium 70B` balanced, `large 405B` expensive.

Traffic: 10k RPM. 70% simple FAQ, 20% general chat, 10% complex reasoning.

Cost budget திடீரென 30% cut ஆகுது. Latency SLO 2s.

Router policy-ஐ எப்படி மாற்றுவீர்கள்? Fallback எப்படி design பண்ணுவீர்கள்? Quality drop ஆகும் போது எப்படி detect பண்ணுவீர்கள்?

## 8. Key Takeaways

- Router என்பது cost, latency, quality-க்கு இடையே trade-off-ஐ manage பண்ணும் architectural control plane
- Query characteristics பார்த்து model fleet-க்கு route பண்ணுவது, one-size-fits-all-ஐ தவிர்க்கும்
- Router தப்பு பண்ணினால் cost save ஆகும் ஆனால் quality போகும். So router-ஐ monitor & evaluate பண்ணனும்
- Every routing decision creates new failure modes: inconsistency, added latency, operational complexity

இதை use பண்ணும்போது யோசிக்க வேண்டியது: **எந்த signal-ல routing பண்ணுவது, எப்போ fallback பண்ணுவது, cost save ஆகுதா quality பாதிக்கலையா என்பதை எப்படி தெரிந்து கொள்வது?**
