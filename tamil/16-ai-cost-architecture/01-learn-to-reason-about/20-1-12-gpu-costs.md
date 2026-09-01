# GPU costs

> **Learning Path:** AI Cost Architecture
> **Section:** 20.1.12 — Learn to reason about

## 1. Problem

உங்க team-க்கு RAG pipeline build பண்ணியிருக்கீங்க. LLM inference-க்கு GPU வேணும். Prototype-ல ஒரு A100 ஓடினா fine.

Production-க்கு வந்ததும் user load பெருகுது. பகல்ல traffic high, இரவுல கிட்டத்தட்ட zero. ஆனால் GPU எப்பவுமே on-ஆ இருக்கு, ஏன்னா model load ஆக 30-60 seconds ஆகும். 

Invoice வந்ததும் shock ஆகும். **GPU hour cost** என்பது CPU hour cost-ஐ விட 10x-50x அதிகம். ஒரு விஷயம் தெரியும்: நீங்க pay பண்றது **compute-க்கு மட்டும் இல்ல, idle time-க்கும்**.

இங்கே painful question வரும்: Same quality-வை கொடுத்துட்டு cost-ஐ எப்படி குறைக்கறது? இது cost optimization இல்ல, **cost architecture** பிரச்சனை.

## 2. Mental Model

GPU cost-ஐ மூன்று பகுதியா பார்க்கணும்:

**1. Hardware cost** - எந்த GPU? H100 vs A100 vs L4 vs T4. Compute capability, memory size, price per hour.

**2. Utilization cost** - GPU எவ்வளவு நேரம் உண்மையா compute பண்ணுது. Batch size சின்னதா இருந்தா GPU idle ஆகும். Memory bandwidth idle ஆகும்.

**3. Operational cost** - Model loading time, cold start, autoscaling lag, over-provisioning for peak, data transfer.

Architect-ஆ நீங்க optimize பண்ணுவது hardware-ஐ மட்டும் இல்ல, **workload shape**-ஐ.

## 3. How It Works

Cloud provider billing model simple: `cost = GPU type rate per hour * hours used`. ஆனால் AI workload-க்கு cost drivers வேற.

**Inference**-ல cost = tokens processed / throughput. Throughput = batch size * sequence length / latency.

ஒரு request-க்கு GPU-வை 1 sec use பண்றீங்கன்னா, batching பண்ணி 32 requests ஒன்னா process பண்ணுனா effective cost per request 1/32 ஆகும்.

**Training / fine-tuning**-ல cost = total compute hours. Data size, model size, epochs, parallelism strategy.

முக்கியம்: GPU memory போதாமல் போனா, model-ஐ smaller GPU-க்கு fit பண்ண முடியாது. அப்போ அடுத்த tier GPU வாங்க வேண்டியிருக்கும். அதனால memory footprint தான் first constraint.

## 4. Architectural Reasoning

GPU cost-ஐ குறைக்கறதுக்கு ஒரே solution இல்ல. Constraint-ஐ புரிஞ்சுக்கணும்.

**Latency sensitive synchronous inference?** உதாரணம்: chatbot UI. User wait பண்ண மாட்டார். இங்கே low latency வேணும். Choice: smaller model on cheaper GPU with low batching, அல்லது larger model but high throughput with batching.

**Throughput sensitive batch inference?** உதாரணம்: nightly document embedding. இங்கே latency matter இல்ல. Choice: cheapest GPU that can hold model, max batch size, spot instances.

**Burst vs steady load?** Steady load-க்கு reserved instance / committed use discount. Burst load-க்கு on-demand + autoscaling.

Architectural options:
- **Model selection**: 70B model-க்கு பதில் 8B + RAG. Quality trade-off vs cost.
- **Quantization**: FP16 -> INT8 -> INT4. Same hardware-ல 2x-4x throughput.
- **Speculative decoding / distillation**: cheaper model draft, larger verify.
- **Caching**: embeddings, prompt cache. Repeated query-க்கு GPU use பண்ண வேண்டாம்.
- **Hybrid**: CPU for pre/post processing, GPU only for matmul.

Decision முடிவு: **What latency SLA can you tolerate?** அதுல இருந்து batch size, model size, GPU type decide ஆகும்.

## 5. Trade-offs

**Throughput vs Latency**: Batch size அதிகப்படுத்தினா throughput increase ஆகும், latency increase ஆகும். Interactive system-ல user experience போகும்.

**Model quality vs cost**: Larger model better quality, but cost exponential. 70B model-ஐ run பண்ண H100 தேவைப்படும். 7B model-ஐ L4-ல run பண்ணலாம். Cost ~10x difference.

**Consistency vs Savings**: Spot / preemptible instances 60-90% cheaper. ஆனால் interruption வரும். Training-க்கு okay, real-time inference-க்கு risky.

**Operational complexity vs savings**: Autoscaling, model offloading, dynamic batching setup பண்ண complex. ஆனால் idle GPU cost-ஐ குறைக்கும்.

Failure mode: Over-optimizing for cost and picking too small GPU -> OOM kill, requests fail, retry storm -> cost அதிகம்.

## 6. Practical Example

Enterprise search RAG system.

Peak hours: 9am-7pm, 200 requests/min. Off-peak: 20 requests/min.

Naive design: 4x A100 always on. Cost ~ $12/hr * 4 = $48/hr = ~$35k/month.

Reasoned design:
- Use quantized 8B model on 2x L4. L4 ~ $0.6/hr. Peak-ல 2 GPU batch size 16 use பண்ணி throughput meet பண்ணும்.
- Embedding & reranking CPU-ல.
- Response cache with Redis. 30% hit rate.
- Off-peak-ல autoscale to 1 GPU.
- Spot instance for batch embedding jobs.

Result: Effective cost ~ $6k/month. Quality loss minimal because RAG context சரியா இருக்கு.

இங்கே architectural decision: GPU cost-ஐ குறைக்க hardware-ஐ மட்டும் மாத்தல. Workload shape-ஐ மாத்தினோம்.

## 7. Reasoning Challenge

உங்களுக்கு 3 வகை workload இருக்கு:
1. Real-time chat, p95 latency < 800ms
2. Nightly document embedding, 2M docs/day
3. Weekly fine-tune, 500k examples

ஒரே GPU pool-ஐ use பண்ண வேண்டுமா? அல்லது workload-க்கு ஏத்த மாதிரி தனி architecture வைக்கலாமா? Cost, latency, operational complexity எப்படி trade-off பண்ணுவீங்க?

## 8. Key Takeaways

- GPU cost என்பது hardware price மட்டும் இல்ல, utilization, batching, idle time சேர்ந்தது.
- Latency SLA தான் GPU size, batch size, model choice-ஐ drive பண்ணும்.
- Quantization, caching, right-sizing model-ஐ முதல் optimize பண்ணு. Hardware upgrade கடைசி option.
- Burst workload-க்கு spot + autoscaling, steady workload-க்கு reserved capacity.
