# Quantization

> **Learning Path:** AI / LLM Foundations
> **Section:** 10.3.7 — Model patterns

## 1. Problem

உங்களிடம் ஒரு LLM service இருக்கு. Production-ல deploy பண்ணும்போது மூன்று விஷயங்கள் உடனே painful ஆகும்:

* **Memory**: ஒரு 7B model FP16-ல ~14GB VRAM. 70B model என்றால் 140GB+. ஒரு single GPU-ல ஏறாது.
* **Latency & Throughput**: Bigger model = slower inference, அதிக cost per token.
* **Cost**: GPU instance cost. A100, H100 எல்லாம் பணம்.

Model accuracy குறையாமல், இதை குறைக்க முடியுமா? அதுதான் quantization-ன் core problem.

## 2. Mental Model

Quantization என்பது model-ன் weights மற்றும் activations-ஐ **high precision float-ல இருந்து low precision integer-க்கு மாற்றுவது**.

Analogy: நீங்கள் ஒரு photo-வை 24-bit color இலிருந்து 8-bit color-க்கு குறைக்கிறீர்கள். File size குறையும், quality கொஞ்சம் மாறும். அதே மாதிரி model numbers-ஐ குறைவான bits-ல represent பண்ணுவது.

Mental model: **Precision vs Memory vs Speed trade-off**. Bits குறைத்தால் memory குறையும், inference வேகமாகும், ஆனால் information loss வரும்.

## 3. How It Works

Model training-ல weights FP16 / BF16 / FP32-ல இருக்கும். Inference-ல அவை மிக அதிக precision தேவையில்லை.

Quantization process:
* **Post-training quantization**: Trained model-ஐ எடுத்து, weights-ஐ scale பண்ணி INT8 / INT4-க்கு map செய்வது.
* **Quantization-aware training**: Training-லேயே quantization noise-ஐ simulate பண்ணி train செய்வது. Accuracy loss குறைவு.

Key idea: `weight_quantized = round(weight / scale)`. Scale ஒரு small float. Inference-ல dequantize பண்ணாமலே INT kernels-ல compute பண்ணலாம்.

Common levels:
* **INT8**: ~2x memory reduction. Accuracy loss குறைவு.
* **INT4 / NF4**: 4x memory reduction. Small models-ல fine.
* **GPTQ, AWQ**: Per-channel scaling, sensitive weights-ஐ protect பண்ணும். Practical industry standard.

## 4. Architectural Reasoning

Quantization useful ஆகும் போது:

* **Edge / on-device**: Phone, laptop, car. VRAM limited.
* **High throughput serving**: Same GPU-ல அதிக concurrent requests.
* **Cost optimization**: Cheaper GPU-ல பெரிய model ஓட்டுவது.
* **Multi-tenant LLM service**: ஒரு GPU-ல பல models.

Alternatives:
* Model distillation - smaller model train பண்ணுவது. Better accuracy but training cost உண்டு.
* Pruning - zero out weights. Sparsity hardware support தேவை.
* Smaller base model - 7B instead of 70B. Capability loss அதிகம்.

Architect choose quantization when: Model capability தேவை, ஆனால் hardware budget கட்டுப்பாடு. Accuracy degradation acceptable.

## 5. Trade-offs

**Memory vs Accuracy**: Bits குறைய bits, perplexity increase ஆகும். INT4-ல ஒரு குறிப்பிட்ட threshold-க்கு கீழே hallucination அதிகரிக்கும்.

**Speed vs Quality**: INT kernels வேகமானவை. ஆனால் calibration data தேவை. Bad calibration = distribution shift.

**Operational complexity**: Quantized model-க்கு separate evaluation, monitoring தேவை. INT8 vs INT4 performance கலந்து பார்க்க வேண்டும்.

Failure mode: Aggressive quantization + out-of-distribution prompt = catastrophic output degradation. Financial / medical RAG-ல risky.

## 6. Practical Example

Enterprise RAG system: 70B Llama model, retrieval + generation. Requirement: p95 latency < 800ms, cost per 1k tokens < $0.02.

Option A: FP16 on 2x A100. Latency ok, cost high.
Option B: AWQ INT4 on 1x A100. Memory ~35GB, fits single GPU. Throughput 2.5x increase. Evaluation shows ROUGE / answer relevance 3-4% drop, acceptable for internal support bot.

Decision: Use INT4 quantized model for production serving, keep FP16 checkpoint for evaluation and sensitive queries. Monitoring-ல output quality drift-ஐ track பண்ணி fallback logic வைக்க.

## 7. Reasoning Challenge

உங்களிடம் 2 use cases உள்ளன:
1. Internal code assistant, 1M tokens/day, latency sensitive இல்லை.
2. Customer-facing chatbot, 50M tokens/day, latency critical, cost sensitive.

இரண்டுக்கும் 70B model தேவை. GPU budget limited. Quantization strategy என்ன வேறுபடும்? INT8 vs INT4? ஏன்?

## 8. Key Takeaways

* Quantization என்பது precision குறைத்து memory & speed gain பண்ணும் architectural lever.
* Problem ஆரம்பிக்கிறது deployment constraints-ல: VRAM, cost, throughput.
* INT8 பாதுகாப்பானது, INT4 aggressive. Trade-off தெளிவாக measure பண்ண வேண்டும்.
* Quantization ஒரு hardware & serving decision, model quality decision அல்ல.
