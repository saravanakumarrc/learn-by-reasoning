# Prompt versioning

> **Learning Path:** LLM Application Engineering
> **Section:** 11.1.6 — Prompt engineering

## 1. Problem

உங்கள் LLM application production-ல் ஓடுகிறது. நேற்று வரை user query-க்கு சரியாக பதில் கொடுத்த prompt இன்று வித்தியாசமாக behave பண்ணுகிறது.

Product team கேட்கிறது: "ஏன் output quality குறைந்தது?"
You கண்டுபிடிக்க வேண்டும்:
- எந்த prompt version இப்போது run ஆகிறது?
- எந்த change எப்போது deploy ஆனது?
- எந்த version-ல் quality நல்லா இருந்தது?

இல்லாவிட்டால் நீங்கள் blind ஆக இருப்பீர்கள். Prompt-ஐ மாற்றினீர்கள், ஆனால் அது rollback பண்ண முடியாது. A/B test பண்ண முடியாது. Audit-க்கு என்ன மாற்றம் நடந்தது என்று சொல்ல முடியாது.

> What goes wrong if we don't have this? Reproducibility இல்லை, debugging இல்லை, safe rollout இல்லை.

## 2. Mental Model

Prompt versioning என்பது code versioning-க்கு ஒத்தது.

Code-ல் `git commit`, branch, tag வைக்கிறோம். Prompt-லும் அதே தேவை.

ஒரு prompt என்பது இனி static string அல்ல. அது:
- template
- system instruction
- few-shot examples
- tools definition
- parameters like temperature, top_p
- input schema

இவை எல்லாம் சேர்ந்து ஒரு **versioned artifact** ஆக மாற வேண்டும்.

Mental model: Prompt = Config + Code. Deploy பண்ணும் போது version pin செய்ய வேண்டும். Production traffic-ஐ version A vs version B என்று route செய்ய முடிய வேண்டும்.

## 3. How It Works

Minimum viable versioning:

**1. Prompt as data, not hardcoded**
Prompt-ஐ code-க்குள் string literal ஆக வைக்காதீர்கள். DB / config store / artifact registry-ல் வைக்கவும்.

**2. Version identifier**
ஒவ்வொரு prompt-க்கும் immutable ID + version. ex: `customer_support_v3.2.1`

**3. Metadata**
- author, created_at, prompt_text, examples, params
- model binding: இந்த prompt எந்த model-க்கு என்று
- tags: use-case, language

**4. Routing**
Request வரும்போது `prompt_version` ஐ select செய்யவும். Default version + override by user group, tenant, experiment.

**5. Observability**
ஒவ்வொரு completion-க்கும் log செய்யவும்: prompt_version, model, input_hash, output, latency, cost.

இது பின்னர் evaluation-க்கு உதவும்.

## 4. Architectural Reasoning

**எப்போது useful?**
- Prompt-ஐ தொடர்ந்து iterate செய்யும்போது
- Multiple teams same prompt-ஐ use செய்யும்போது
- Production rollback தேவைப்படும்போது
- Compliance / audit தேவைப்படும்போது

**Constraint it addresses:** Non-determinism + rapid iteration.

Code deploy க்கு 2 வாரம் எடுக்கலாம். Prompt tweak க்கு 2 நிமிடம். அந்த speed-ஐ safe ஆக்க versioning தான்.

**Alternatives:**
- Hardcoded prompts in code → fast to start, impossible to manage
- Prompt in feature flag system → simple rollout, but no history/audit
- Full prompt management platform → LangSmith, PromptLayer, etc. → good for scale

**Architect choose எப்போது?** முதல் production incident வந்ததும். அல்லது 2 engineers prompt-ஐ மாற்றும் போது conflict ஆகும் போது.

## 5. Trade-offs

**Version proliferation vs stability**
அதிக version வைத்தால் test செய்ய கடினம். ஒரே version-ஐ நீண்ட நேரம் வைத்தால் innovation slow.

**Storage cost vs reproducibility**
ஒவ்வொரு prompt run-ஐயும் log செய்வது expensive. ஆனால் debugging-க்கு தேவை.

**Centralized registry vs decentralized**
Centralized என்றால் governance நல்லா இருக்கும், speed குறையும். Decentralized என்றால் team autonomy, drift வரும்.

**Failure mode:** Wrong version pinned to production. Model upgrade பண்ணினால் prompt compatibility break ஆகலாம். Version drift between dev and prod.

## 6. Practical Example

Enterprise RAG chatbot for support.

`system_prompt_v1` → "Answer only from context"
Quality okay, but too restrictive.

`system_prompt_v2` → add few-shot examples for refusal handling
Quality up, latency up.

நீங்கள் prompt versioning + feature flag செய்கிறீர்கள்:
- 10% traffic → v2
- 90% traffic → v1
- Log prompt_version, user_satisfaction_score

2 நாள் பிறகு v2-ல் satisfaction 12% up. ஆனால் cost 8% up.

இப்போது நீங்கள் decide செய்யலாம்: rollout to 100% அல்லது refine v2.1.

Incident வந்தால்: `customer_support_v2.0.3` to `v2.0.4` rollback in 30 seconds.

## 7. Reasoning Challenge

உங்களிடம் 3 tenants உள்ளன: Enterprise A, B, C. அவர்களுக்கு வெவ்வேறு tone வேண்டும். உங்கள் team weekly prompt iteration பண்ணுகிறது.

ஒரே prompt repo வைத்து எப்படி versioning செய்வீர்கள்? Tenant-specific override வேண்டுமா? Model version மாறும் போது prompt version-ஐயும் bump செய்ய வேண்டுமா? ஏன்?

## 8. Key Takeaways

- Prompt-ஐ code மாதிரி treat செய்யுங்கள். Version, pin, rollback செய்யுங்கள்.
- Version = prompt text + examples + parameters + model binding. ஒன்று மாறினாலும் version bump.
- Observability இல்லாமல் versioning அர்த்தமில்லை. Prompt version-ஐ log செய்யுங்கள்.
- Every prompt change creates trade-off between quality, cost, latency, safety. Versioning அதை measurable ஆக்கும்.
