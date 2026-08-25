# Distillation

> **Learning Path:** AI / LLM Foundations
> **Section:** 6.3.8 — Model patterns

**Distillation: making a big model’s behavior run small**

### 1. The problem

You have a capable LLM. It is accurate, but it is too expensive to run where you need it.

Constraints show up together:
* **Latency / throughput:** 70B+ models need multiple GPUs for <500ms responses
* **Cost:** $0.01 per request at scale becomes millions per month
* **Footprint:** cannot fit on edge device, mobile, or single inference node
* **Privacy / compliance:** data cannot leave VPC / on-prem boundary
* **Reliability:** large model is non-deterministic and hard to control for internal tools

You do not need the teacher’s full capacity. You need *most* of its behavior, on a cheaper substrate.

### 2. Mental model

Distillation is apprenticeship, not compression.

A large teacher model generates examples of its behavior. A smaller student model learns to imitate that behavior, not just the ground truth labels.

The student is smaller, faster, cheaper. The goal is to transfer the *distribution* of good outputs, not copy parameters.

### 3. How it works

The core loop is data generation + supervised fine-tuning.

```mermaid
flowchart LR
    Teacher[Large Teacher Model] -->|prompts + soft targets / traces| DistillData[Distillation Dataset]
    DistillData --> Train[Student Training: KL / cross-entropy on soft labels]
    Train --> Student[Small Student Model]
    Student -. evaluation -> Teacher
```

Essentially:
* **Response distillation:** Teacher answers a curated prompt set. Student trains on teacher outputs as targets. Common for instruction following.
* **Logit distillation:** Teacher produces softened logits with temperature >1. Student learns to match the distribution, not just argmax. Captures relative preferences.
* **Feature distillation:** Intermediate representations are aligned. Used less in LLMs, more in vision.

Training cost is dominated by teacher inference to build the dataset, then standard SFT of the student.

### 4. Architectural reasoning

When it helps:
* You need model quality close to teacher but with 3-10x smaller size
* You control the domain: internal support, coding assistant, classification
* You can afford an offline data generation pass

Alternatives:
* **Quantization / pruning:** Keeps same model, reduces bits/weights. Cheaper to deploy, minimal accuracy loss, but size reduction is bounded.
* **Train smaller from scratch:** Full control, no teacher bias, but expensive and often underperforms.
* **Speculative decoding / routing:** Keep big model but make it faster. Does not reduce footprint.

Decision rule: Distill when you need a *behaviorally similar* small model and you have a good teacher + representative data. Quantize when you just need cheaper inference of the same model.

### 5. Trade-offs and failure modes

* **Capacity gap.** Student cannot learn what it cannot represent. Distilling 70B → 350M often fails on complex reasoning. Expect diminishing returns below ~1-3B for general tasks.
* **Teacher bias transfer.** Hallucinations, style, and safety flaws are copied. You inherit the teacher’s failure modes.
* **Evaluation mismatch.** Student may match teacher on distillation set but degrade on out-of-domain prompts. Needs hold-out evaluation, not just teacher agreement.
* **Data cost.** Generating high-quality distillation data is expensive and needs careful prompt coverage. Bad prompts = bad student.
* **Loss of diversity.** Soft targets collapse modes. Student can become over-confident and less creative.

### 6. Example

Enterprise customer support in finance.

Teacher: 70B frontier model, good at policy adherence and nuanced reasoning. Runs in central GPU cluster.
Constraint: Support agents need <200ms responses, data must stay on-prem, and per-request cost must be <$0.0005.

Architecture: Generate 2M prompts from historical tickets + synthetic edge cases. Teacher produces answers with reasoning traces. Distill to a 3B student, fine-tuned on-prem. Student runs on single A10G per region.

Result: ~92% teacher agreement on golden set, 5x lower latency, 8x lower cost, data never leaves VPC.

### 7. Reasoning challenge

You have a 32B model that passes your quality bar for code review comments. You need to deploy it to 10k developer laptops with 8GB RAM.

Options: 4-bit quantization to ~16GB → still too big. Distill to 1.5B. Or keep 32B server-side with streaming.

What do you choose, and what do you measure before deciding to distill?

### 8. Key takeaway

* Distillation solves cost/latency/privacy constraints by transferring behavior from a large teacher to a small student.
* It is an architectural choice about *where* intelligence lives, not just compression.
* Success depends on domain coverage, student capacity, and teacher quality.
* Trade-off is accuracy for size and operational simplicity, with risk of copying teacher flaws and failing on tail cases.

You should leave knowing when distillation is the right lever versus quantization, routing, or keeping the teacher.
