# PARTIAL — Privacy

> Reason: Ollama reached num_predict
> num_predict: 32768

## 1. Problem

நீங்கள் ஒரு AI feature build பண்ணுறீங்க. User-ஆடு தன் profile, transaction history, chat history கொடுத்து "இதுக்கு summary கொடு"ன்னு கேட்கிறார்.

அந்த prompt-ஐ நீங்கள் OpenAI, Anthropic, Gemini மாதிரி third-party LLM API-க்கு அனுப்புறீங்க. Request போய் response வந்துடும். ஆனா அந்த data-க்கு என்ன ஆகும்?

Provider-ன் terms-ல் prompt data log ஆகும், abuse detection-க்கு store ஆகும், ஒரு குறிப்பிட்ட காலம் வரை retain ஆகும், சில models-ல் training data-வாக பயன்படுத்தப்படலாம். நீங்கள் உங்கள் user-க்கு promise பண்ணிய privacy ஒரே API call-ல் break ஆகிறது.

இதே problem fine-tuning-லயும், RAG-லயும் இருக்கு. User-ன் private document-ஐ vector database-ல் embed பண்ணி, அதை LLM-க்கு context-ஆக கொடுக்கும்போது அந்த document cloud provider-க்கு தெரியும்.

> What problem became painful enough? **Data leaves your trust boundary and you lose control over retention, access and usage.**

## 2. Mental Model

Privacy-க்கு model selection-ல் core mental model ஒன்னுதான்: **Trust boundary.**

On-prem / self-hosted model = data உங்கள் VPC-க்குள்ளேயே இருக்கு. Network egress இல்லை.
Cloud managed API = data internet வழியாக provider-க்கு போகிறது. Provider உங்கள் data custodian ஆகிறார்.

Model capability முக்கியம், ஆனா privacy constraint இருந்தா அது selection-ஐ override பண்ணும்.

## 3. How It Works

Model provider-ஆடு பொதுவாக மூன்று விஷயங்களை செய்வார்கள்:

* **Prompt logging for ops and abuse:** Latency, error debugging, safety filtering
* **Retention policy:** 30 days, 7 days, zero-retention option
* **Training usage:** Default-ல் allow பண்ணியிருப்பார்கள். Opt-out தருவார்கள்.

Enterprise tier-ல் நீங்கள் Zero Data Retention / Data Processing Addendum, SOC2, ISO27001, GDPR compliance கேட்கலாம். ஆனா அது legal assurance, technical guarantee இல்லை.

Self-hosted open-weight model, e.g., Llama, Mistral self-hosted on Kubernetes, என்றால் prompt உங்கள் infrastructure-ல் தங்கும். Model weights உங்கள் control-ல். ஆனா operational complexity உங்களுடையது.

## 4. Architectural Reasoning

Model selection privacy lens-ல் பார்க்கும்போது constraints இவை:

* **Data sensitivity:** PII, PHI, financial records, trade secrets, internal code
* **Compliance:** GDPR, HIPAA, DPDP Act India, data residency requirements
* **Data lifecycle:** Prompt-ஐ long-term store பண்ணக்கூடாது. Real-time use மட்டும்
* **User expectation:** User explicit consent இல்லாமல் third party-க்கு data போகாது

இதற்கு options:

1. **Cloud managed LLM API with DPA + zero-retention** - fastest to ship, best capability
2. **Private cloud / VPC deployment** - provider managed infra, but isolated network
3. **Self-hosted open model on-prem / private cloud** - full control, higher ops cost
4. **Hybrid:** Public model for non-sensitive, private model for sensitive paths

Architect முடிவு எடுக்கும்போது கேட்க வேண்டியது: இந்த data எப்படி classify ஆகிறது? அதை external LLM-க்கு அனுப்பினால் business risk என்ன? Legal fine மட்டுமல்ல, reputational risk.

## 5. Trade-offs

**Privacy vs Capability:** Top-tier proprietary models திறமையானவை. Open models catch up பண்ணுது, ஆனா capability gap இருக்கு. Sensitive data-க்கு சற்று குறைவான capable model-ஐ accept பண்ணுவீர்களா?

**Privacy vs Cost & Ops:** Self-hosted என்றால் GPU cost, MLOps team, model serving, scaling, patching எல்லாம் உங்கள் பொறுப்பு. Cloud API pay-per-token. 10x cheaper operationally.

**Privacy vs Latency:** On-prem inference network latency குறைவு. ஆனா cold start, load balancing நீங்கள் manage பண்ணணும்.

**Privacy vs Fine-tuning:** Private data-உடன் fine-tune பண்ண வேண்டுமென்றால் cloud provider-ன் fine-tuning pipeline-ல் data upload ஆகும். அது permanent training influence ஆகலாம். Self-hosted fine-tuning மட்டுமே safe.

Failure mode: Team privacy requirement-ஐ மறந்து development-ல் cloud API use பண்ணி, production-க்கு வந்த பிறகு compliance audit-ல் fail ஆகிறது. Migration expensive.

## 6. Practical Example

ஒரு bank customer support chatbot. User கேட்கிறார்: "என் last 3 transactions என்ன? அதுக்கு summary கொடு".

இங்கே data = PII + financial. GDPR scope.

Option A: Prompt-ஐ அப்படியே OpenAI API-க்கு அனுப்புவ
