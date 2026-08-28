# LoRA / PEFT

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.3.6 — Model patterns

## 1. Problem

உங்க team-க்கு ஒரு LLM தேவை. Support chatbot, internal knowledge search, code generation — எல்லாம் வேற வேற use-case.

Full fine-tuning பண்ணனும்னா என்ன ஆகும்?

* 7B model-க்கு 2-3 high-end GPUs, days of training time
* Every new customer, every new domain-க்கு ஒரு புது copy
* Model weights 14GB, 100 customers = 1.4TB storage
* Production-ல A/B test பண்ணவே முடியாது, rollback கஷ்டம்

**Pain point:** Base model generic. Domain-specific behaviour வேணும். ஆனால் full fine-tune பண்ணினா cost, time, operational complexity அதிகம்.

இதுக்காகதான் PEFT வந்தது. Parameter Efficient Fine Tuning.

## 2. Mental Model

Full fine-tuning = முழு model-ஐயும் மாற்றுவது.

PEFT = மாதிரி ஒரு பெரிய building-க்கு renovation பண்ணும்போது முழு building-ஐயும் இடிக்காம, குறிப்பிட்ட rooms-ல மட்டும் small adapter panels பொருத்துவது.

LoRA = Low Rank Adaptation. Model-ன் weight matrix W ஐ freeze பண்ணிட்டு, மாற்றம் ΔW = A × B என்று இரண்டு சின்ன low-rank matrices-ஆக கற்றுக் கொள்வது.

Base model பாதுகாப்பாக இருக்கு. Domain knowledge மட்டும் small adapter-ல capture ஆகும்.

## 3. How It Works

Base LLM-ன் weights frozen. Forward pass-ல:

`h = W x + (A B) x`

A ∈ R^{d × r}, B ∈ R^{r × k}, r << min(d,k)

Train பண்ணுவது A, B மட்டும். Trainable parameters 0.1-1% மட்டுமே.

Inference-ல இரண்டு வழி:

* Merge mode: W' = W + A B. One-time merge, latency same as base.
* Separate mode: adapter weights ரன்டைம்ல load, multiple adapters swap செய்யலாம்.

PEFT என்பது family. LoRA மிக popular. Alternatives: Adapter, Prefix Tuning, QLoRA.

QLoRA என்பது 4-bit quantization + LoRA. 7B model 4-bit-ல 4GB. Training consumer GPU-ல கூட possible.

## 4. Architectural Reasoning

**எப்போது LoRA useful?**

* Multi-tenant SaaS: ஒவ்வொரு customer-க்கும் தனி adapter, same base model.
* Rapid iteration: New domain data வந்ததும் hours-ல fine-tune.
* Resource constraints: 1 GPU-ல பல adapters train பண்ண முடியும்.
* Safety: Base model-ஐ மாற்றாமல் experiment பண்ணலாம்.

**Alternatives என்ன?**

* Full fine-tune: Best performance, but cost, storage, no sharing.
* Prompting / RAG: No training, but context window limit, consistency குறைவு.
* Instruct model + system prompt: Zero cost, ஆனால் deep domain behaviour வராது.

Decision flow:

```
Need domain style, tone, private data? → RAG enough? → Yes → RAG
                                           → No → LoRA
Need many variants per customer? → LoRA with adapter swapping
Need max quality, budget unlimited? → Full fine-tune
```

## 5. Trade-offs

* **Performance vs parameter efficiency:** LoRA full fine-tune-க்கு 95-99% performance தரும். Rank r அதிகமானால் gap குறையும், ஆனால் parameters அதிகம்.
* **Storage & switching cost:** Adapter size 10-100 MB. 1000 customers = ~50GB. Manageable. Runtime switch latency தேவைப்பட்டால் model reload overhead.
* **Catastrophic forgetting குறைவு:** Base capabilities retain ஆகும். ஆனால் very large domain shift-க்கு full fine-tune better.
* **Operational complexity:** Adapter versioning, routing, merge pipeline, evaluation drift. எந்த adapter எப்போது load ஆகிறது என்பதை track செய்ய வேண்டும்.

Failure mode: Rank too small → underfit. Training data low quality → adapter memorize noise. Inference-ல adapter merge மறந்தால் base model மட்டும் respond ஆகும்.

## 6. Practical Example

Enterprise support bot.

Base model = Llama 3 8B Instruct.

Customer A = Banking domain, formal tone, KYC policies.
Customer B = E-commerce, casual tone, return policy.

RAG-ல product catalog + policies வைத்தோம். ஆனால் tone, refusal style, jargon வேறுபடுகிறது.

Solution: Base model common. Two LoRA adapters: `adapter_banking`, `adapter_ecom`.

Request comes with `customer_id`. Router adapter load செய்கிறது.

Training: 5k examples per customer, QLoRA, 1x A10 GPU, 3 hours.

Inference: Merge during deployment, or keep adapters separate and hot-swap per request via vLLM with LoRA support.

Cost: Base model 1 copy. Adapters 2 x 80MB. No duplicate 16GB weights.

## 7. Reasoning Challenge

உங்களிடம் ஒரு 70B model உள்ளது. 50 enterprise customers. ஒவ்வொருவருக்கும் தனி fine-tune வேண்டும். VRAM 80GB per replica.

LoRA adapter per customer vs full fine-tune per customer vs RAG + system prompt?

Latency < 200ms, cost control முக்கியம், ஒவ்வொரு customer-க்கும் 10k private examples உள்ளன.

நீங்கள் எந்த architecture தேர்வு செய்வீர்கள்? Rank, merge strategy, serving model எப்படி design செய்வீர்கள்? என்ன trade-off ஏற்றுக்கொள்ள தயார்?

## 8. Key Takeaways

* LoRA என்பது full model-ஐ மாற்றாமல் small low-rank delta-ஐ கற்றுக்கொள்வது.
* Multi-tenant, fast iteration, low cost scenarios-ல PEFT தான் architecturally sensible.
* Adapter size tiny, storage & switching easy, ஆனால் performance ceiling full fine-tune-க்கு கீழே.
* Design decision என்பது quality vs cost vs operability. LoRA அந்த trade-off-ஐ shift செய்கிறது.
