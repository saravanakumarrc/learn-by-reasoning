# PARTIAL — Model parameters

> Reason: Ollama reached num_predict
> num_predict: 32768

## Problem

உங்க team ஒரு customer support chatbot பண்ணுது. முதல்ல rules வச்சு போனீங்க. "refund" என்றால் இப்படி reply, "order status" என்றால் அப்படி reply.

ஒரு மாசம் ஓடினப்புறம் புது வார்த்தைகள், புது complaints, sarcasm, mixed Tamil-English வருது. Rules எழுதி முடியாது. 

அப்புறம் ஒரு LLM எடுத்து data மேல train பண்ண சொல்றாங்க. "இதுக்கு எவ்ளோ parameters வேணும்?" என்று கேட்கிறார்கள்.

இங்கே உண்மையான பிரச்சனை என்ன? மனுஷன் போல pattern கத்துக்கணும், எல்லா example-ஐயும் மனப்பாடம் பண்ணக்கூடாது. Data-வில் இருக்கும் உறவுகளை capture பண்ண ஒரு learnable representation வேண்டும். அதுதான் parameters.

## Mental Model

Parameters = model-ன் நினைவு செல்கள். ஒவ்வொரு parameter-ம் ஒரு weight. இது ஒரு dial மாதிரி, training time-ல data பார்த்து அதன் value மாறும்.

Parameter count = model-க்கு கொடுக்கப்பட்ட degrees of freedom. சிறிய dial set = சின்ன வீடு, பெரிய dial set = பெரிய வீடு. பெரிய வீட்டில் அதிக சாமான் வைக்கலாம், ஆனால் துடைக்கவும் அதிக நேரம்.

இது hyperparameter அல்ல. Hyperparameter = temperature, learning rate, batch size மாதிரி நீங்கள் set பண்ணுவது. Parameter = training மூலம் தானாக கற்றுக்கொள்ளும் weight.

## How It Works

LLM ஒரு function. Input tokens -> embeddings -> transformer layers -> output logits.

ஒவ்வொரு layer-லும் matrices உள்ளன. Q, K, V projection weights, feed-forward weights, layer norm scale. எல்லாம் சேர்ந்து parameters ஆகும்.

Training என்பது gradient descent மூலம் இந்த weights-ஐ சரி செய்வது. Loss குறையும் வரை dial-களை திருப்புவது.

ஒரு model-க்கு 7B parameters என்றால், அது 7 billion dials உள்ளது என்று அர்த்தம். அவை float16-ல் சுமார் 14 GB memory எடுக்கும். Inference-க்கு அந்த weights-ஐ முழுவதும் load செய்ய வேண்டும்.

## Architectural Reasoning

ஏன் parameter count முக்கியம்?

**Capacity vs Generalization.** அதிக parameters = அதிக capacity. Complex patterns, long context, nuance கத்துக்க முடியும். ஆனால் data குறைவாக இருந்தால் overfit ஆகும்.

**Quality vs Cost.** ஒரு 70B model 7B model-ஐ விட average quality-ல் சிறப்பாக இருக்கும், ஆனால் inference latency, GPU memory, cost அதிகம்.

எப்போது பெரிய model தேவை?
* Reasoning heavy tasks: code generation, multi-step planning
* Low data quality, need strong priors
* User experience முக்கியம், cost குறைவு முக்கியம் அல்ல

எப்போது சிறிய model போதும்?
* High throughput, low latency API
* Classification, reranking, intent detection போன்ற constrained tasks
* On-device / edge deployment
* Cost sensitive production

நீங்கள் எப்போதும் model-ஐ மட்டும் பார்க்கக்கூடாது. Architecture-ஐ பார்க்க வேண்டும். Small model + good RAG + tool use பெரும்பாலும் big model-ஐ விட சிறப்பாக வேலை செய்யும்.

## Trade-offs

**Quality vs Latency.** பெரிய model-ன் forward pass அதிக FLOPs. 70B model-க்க
