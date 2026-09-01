# Model registry

> **Learning Path:** Enterprise AI Architecture
> **Section:** 23.1.5 — Enterprise patterns

## 1. Problem

உங்களிடம் ஒரு enterprise AI system இருக்கு. 3 teams, 5 models, 2 environments.

Team A `recommendation-v3` deploy பண்ணினாங்க. Team B `recommendation-v3` use பண்ணி training செய்தாங்க. Production-ல ஓடுறது `recommendation-v3.2` தான்.

இப்போ production-ல error வந்துட்டு. எந்த model artifact ஓடுது? எந்த training data-ல இருந்து பிறந்தது? Hyperparameters என்ன? Code version எது? Preprocessing pipeline எது?

எல்லாம் Slack messages, S3 folder names, notebook files-ல scattered-ஆ இருக்கு.

Model ஒன்னு update ஆனா, அதை reproduce பண்ண முடியாது. Rollback பண்ணணும்னா எந்த artifact எடுக்கணும் தெரியாது. Compliance audit கேட்டா, "இந்த model எப்படி build ஆச்சு"ன்னு சொல்ல முடியாது.

இதுதான் painful problem. Model ஒரு code-ல இல்ல, ஒரு artifact + data + config + environment-ன் combination.

## 2. Mental Model

Model registry ஒன்னு **single source of truth for model artifacts** மாதிரி.

Git repo code-க்கு செய்யுறதை, model-க்கும் செய்யணும். Versioning, metadata, lineage, promotion, access control.

எளிமையா சொன்னா: Model-க்கு package manager + release manager + audit log.

Model ஒன்னு build ஆனதும் registry-ல register ஆகும். அதுக்கு immutable version கிடைக்கும். அதே version தான் training, staging, production-ல reference ஆகும்.

## 3. How It Works

ஒரு model training pipeline முடிந்ததும்:

1. **Register**: Model artifact `.pt/.safetensors`, tokenizer, config JSON registry-ல upload ஆகும்.
2. **Metadata capture**: Model name, version, training dataset version, code commit hash, hyperparameters, metrics `accuracy`, `latency`, `drift`, owner team.
3. **Stage**: Model-க்கு stage set பண்ணுவோம் — `staging`, `production`, `archived`.
4. **Promotion**: Staging-ல validation pass ஆனா, promotion workflow மூலம் production stage-க்கு move.
5. **Serving reference**: Serving service model registry-ல இருந்து specific version-ஐ pull பண்ணி serve பண்ணும்.

Registry basically ஒரு catalog + artifact store. Artifact store S3/GCS, catalog ஒரு DB. MLflow Model Registry, Weights & Biases Registry, Hugging Face Hub, Azure ML Model Registry இதே pattern.

## 4. Architectural Reasoning

எப்போ தேவை?

* Multiple teams same model family use பண்ணும்போது.
* Production model reproduce, rollback தேவைப்படும்போது.
* Model governance, compliance, audit தேவைப்படும்போது.
* A/B test, canary, champion-challenger pattern வேண்டும்போது.

Constraint இது address பண்ணும்: **Reproducibility + Consistency + Accountability**.

Alternatives?

* S3 folder per model + README. Cheap, but no governance, no atomic promotion.
* Git LFS. Versioning இருக்கும், ஆனால் metadata, stage, lineage இல்ல.
* Manual spreadsheet. Scale ஆகாது.

Architect choose பண்ணுவான் registry-ஐ, system-ல model என்பது first-class artifact என்று treat பண்ணும்போது. Model deployment என்பது `docker image tag` மாதிரி deterministic ஆக இருக்கணும்.

## 5. Trade-offs

**Centralization vs latency.** Registry ஒன்னு central point ஆகும். Serving startup-ல artifact pull slow ஆகலாம். Solution: registry-ல reference மட்டும் வைத்து, artifact cache in region.

**Strict governance vs velocity.** Promotion gates, approvals வைத்தால் speed குறையும். Too loose ஆனால் bad model production-க்கு போகும். Trade-off: automated tests + policy as code.

**Metadata completeness vs overhead.** Dataset version, feature store version, prompt template version எல்லாம் capture பண்ணணும். ஆனால் engineers fill பண்ண மாட்டாங்க. Enforce via pipeline hooks.

**Failure modes.** Registry down ஆனால் new deployment block ஆகும். Registry-ல corrupted metadata வந்தால் wrong model serve ஆகும். Artifact store and registry DB separate failure domain-ல வைக்கணும். Version immutability must be enforced.

## 6. Practical Example

Enterprise RAG system. Two models: `embedding-v2`, `reranker-v1`.

Training pipeline run ஆகி, new `embedding-v3` train ஆச்சு. MLflow registry-ல register ஆச்சு. Metadata: trained on `corpus-2026-08-01`, code commit `a3f9c1`, MRR 0.42.

Model stage = `staging`. RAG service staging environment-ல `embedding-v3` point பண்ணி evaluation run ஆச்சு. Latency +12ms.

Result ok. Promotion approval via PR. Promotion script `embedding-v3` stage `production` ஆக்கும். Serving service pull request merge ஆனதும், rollout starts with canary 10%.

Audit time-ல: production-ல எந்த model ஓடுது? Registry query: `embedding-v3` version 3.2.1. Full lineage traceable.

Rollback தேவைப்பட்டால், registry-ல `embedding-v2` production stage-க்கு promote பண்ணி 2 minutes-ல rollback.

## 7. Reasoning Challenge

உங்களிடம் 4 teams இருக்கு. ஒவ்வொருவரும் தங்கள் own model registry instance வைத்துள்ளனர். Central platform team ஒரு unified registry கட்ட முன்மொழிகிறது.

Centralize பண்ணுவதால் என்ன pros/cons வரும்? உங்கள் organization-ல team autonomy vs governance எந்த balance choose பண்ணுவீர்கள்? Model promotion policy எப்படி வைப்பீர்கள்?

## 8. Key Takeaways

* Model registry-ன் core value reproducibility and governance, not just storage.
* Model version = artifact + metadata + lineage. எல்லாம் ஒன்னா தான் version ஆகணும்.
* Promotion workflow தான் staging to production-ன் safety net.
* Registry centralize பண்ணும்போது operability and compliance improve ஆகும், ஆனால் latency, coupling trade-off உண்டு.
* Every model in production must be traceable back to data, code, and metrics via registry.
