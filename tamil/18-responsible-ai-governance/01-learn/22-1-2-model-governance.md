# Model governance

> **Learning Path:** Responsible AI & Governance
> **Section:** 22.1.2 — Learn

## 1. Problem

உங்கள் team ஒரு LLM-based service-ஐ production-ல விட்டிருக்கு. Product team புது prompt வைக்குது, Data Science team fine-tune பண்ணி model version மாற்றுது, Ops team latency குறைக்கிறேன் என்று temperature மாற்றுது.

மூன்று வாரம் கழித்து customer கிட்ட harmful output வருது. யார் மாற்றினா? எந்த model version ஓடுது? எந்த prompt use ஆகுது? Audit-க்கு என்ன log இருக்கு?

இது வெறும் code quality இல்லை. Model governance என்பது **who can change what, when, and with what evidence** என்பதை control பண்ணுவது.

Without governance, நீங்கள் பெறுவது: silent model drift, unexplainable decisions, compliance risk, மற்றும் rollback-க்கு வழி இல்லாமல் போவது.

## 2. Mental Model

Model governance = **Lifecycle control + Accountability + Evidence**.

ஒரு model-ஐ ஒரு service போல் treat பண்ணுங்கள். அதற்கு version, owner, test, approval, monitoring, retirement இருக்க வேண்டும்.

Simple mental model: 
`Model Registry` is source of truth, `Policy` decides who can promote, `Lineage` tracks data → prompt → model → deployment, `Observability` tells you behavior changed.

## 3. How It Works

Practically, governance இது செய்கிறது:

* **Model Registry**: ஒவ்வொரு model artifact, fine-tune checkpoint, prompt version, config க்கும் immutable ID. MLflow, Weights & Biases Artifacts, or custom registry.
* **Versioning & Lineage**: Model build ஆனது எந்த dataset, evaluation set, hyperparameters, prompt template-ல் இருந்து வந்தது என்பது traceable.
* **Policy Gates**: Promotion என்பது manual review அல்லது automated checks-ஐ pass பண்ண வேண்டும். Eg: eval score drop < 2%, safety test pass, latency < 200ms.
* **Access Control**: Who can edit prompt, who can deploy to prod, who can read logs. RBAC + audit log.
* **Monitoring & Drift Detection**: Production-ல output distribution, latency, error rate, toxicity, hallucination proxy metrics track ஆகும். Drift ஆனால் alert.

இது ஒரு central control plane, not just a folder of files.

## 4. Architectural Reasoning

When does this become painful enough?

* Multiple teams touch same model/prompt
* Model output affects money, legal, safety
* You need to explain decision to regulator/auditor
* You need rollback in minutes, not hours

Alternatives:

* **Ad-hoc governance**: Confluence doc + Slack approval. Works for 1 model, 1 team. Fails at scale.
* **MLOps platform only**: CI/CD for model build but no policy/audit. You can deploy fast, but not safely.
* **Full governance platform**: Registry + policy + lineage + observability integrated.

Architect choose governance when **risk > speed**. Banking, healthcare, hiring, finance, customer-facing LLM.

## 5. Trade-offs

**Control vs Speed**: More gates = safer but slower iteration. Solution: environment tiers - dev auto-promote, staging gated, prod requires approval.

**Centralization vs Team autonomy**: Central registry helps audit, but teams want freedom. Trade-off solved via policy as code, not manual approval.

**Observability cost**: Logging every prompt/completion for audit is expensive. You need sampling, retention policy, PII redaction.

**Model immutability vs prompt flexibility**: Model frozen, but prompt can change frequently. Governance must version both separately and track combination.

Failure modes:

* Registry and production drift: registry says v3, production running v2 due to bad deploy. Need deployment signature check.
* Silent prompt change: Prompt changed in config without version bump. Need prompt-as-code with version control.
* Evaluation gap: Eval set stale, model passes gate but fails in real world. Need continuous eval on production data sample.

## 6. Practical Example

Enterprise RAG agent for internal support.

Architecture: 
`Prompt Registry` → `Model Registry` → `Deployment` with feature flag.

Flow:
1. Data team uploads new embeddings from updated KB. Artifact gets hash.
2. Prompt engineer proposes new system prompt v4.2 with safety guardrail.
3. CI runs eval suite: faithfulness, latency, safety tests on golden set. Score logged.
4. Policy engine checks: eval pass, owner approved, no PII in logs. Auto-promote to staging.
5. Staging runs 1% traffic shadow. Drift monitor compares output distribution.
6. Approval from Responsible AI owner → promote to prod. Audit log captures who, when, what artifact IDs.

Rollback: One command points service to previous model+prompt combo ID. Full lineage retrievable for audit.

## 7. Reasoning Challenge

உங்களிடம் customer-facing LLM chatbot இருக்கு. 3 product squads தங்கள் prompts-ஐ தினமும் மாற்றுகிறார்கள். Compliance audit-க்கு 6 மாத audit trail காட்ட வேண்டும். நீங்கள் முழு prompt logging-ஐ சேமிக்க முடியாது cost காரணமாக.

இங்கே என்ன governance controls வைப்பீர்கள்? Prompt versioning எப்படி கையாள்வீர்கள்? Logging-க்கு என்ன trade-off எடுப்பீர்கள்?

## 8. Key Takeaways

* Model governance என்பது model quality அல்ல, **change control + accountability** ஆகும்.
* Registry, lineage, policy gates, observability ஆகிய நான்கும் core pillars.
* Every change should be versioned, approved, observable, and reversible.
* Governance adds latency to deployment, but prevents silent failures and audit nightmares.
