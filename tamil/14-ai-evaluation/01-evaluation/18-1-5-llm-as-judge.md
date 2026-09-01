# LLM-as-judge

> **Learning Path:** AI Evaluation
> **Section:** 18.1.5 — Evaluation

## 1. Problem

நீங்கள் ஒரு RAG system அல்லது agent build பண்ணியிருக்கீங்க. Model output quality-ஐ எப்படி measure பண்ணுவது?

Human evaluation பண்ணலாம். ஆனால் 10k prompts-க்கு 3 annotators வச்சு label பண்ணுவது slow, expensive, inconsistent. Inter-annotator agreement-ம் குறையும்.

Automated metrics like BLEU, ROUGE, exact match எடுத்துக்கலாம். ஆனால் LLM output-க்கு semantic correctness, helpfulness, factuality, tone முக்கியம். BLEU அதை catch பண்ணாது.

இங்கே தான் pain வருது: **Evaluation-ஐ scale பண்ண முடியல, மற்றும் model improvement-ஐ fast feedback loop-ல track பண்ண முடியல.**

What goes wrong if we don't have this? Model tuning blind ஆகும், regression catch பண்ண முடியாது, production quality guarantee இல்லை.

## 2. Mental Model

LLM-as-judge என்பது ஒரு LLM-ஐ evaluator ஆக use பண்ணுவது.

நீங்கள் system output-ஐ ஒரு judge model-க்கு கொடுக்கிறீங்க. Criteria கொடுத்து, "இது எவ்வளவு good?" என்று score கொடுக்க சொல்கிறீங்க.

உதாரணமாக: Prompt + Reference answer + Model answer → Judge LLM → Score for correctness, completeness, style.

இது human evaluation-ன் reasoning pattern-ஐ mimic பண்ணும், ஆனால் automated and fast.

## 3. How It Works

Basic flow:

1. **Evaluation prompt design**: Judge-க்கு clear rubric கொடுக்கணும். உதாரணம்: "Rate 1-5 for factual accuracy. 5 = fully correct, no hallucination..."
2. **Input assembly**: task, reference / ground truth, candidate output.
3. **Judge inference**: Stronger model, often different family than candidate, used to reduce bias.
4. **Output parsing**: Score, reasoning, or pairwise preference.
5. **Aggregation**: Mean score, distribution, failure categories.

Variants:
* **Single score**: 1-5 rating
* **Pairwise**: A vs B, which is better?
* **Categorical**: hallucination yes/no, safety violation yes/no
* **Chain-of-thought judging**: Judge explains reasoning first, then scores → better reliability.

Important trick: Temperature 0, deterministic output. Few-shot examples with gold labels கொடுத்தால் consistency improve ஆகும்.

## 4. Architectural Reasoning

எப்போது useful?

* Offline evaluation: model version compare, prompt engineering iteration
* Online monitoring: production traffic sampling
* Red teaming / safety check
* RAG quality: answer groundedness, citation correctness

What constraint it addresses? **Evaluation throughput and cost vs human quality trade-off.**

Alternatives:
* **Human evaluation**: High fidelity, low scale, slow, expensive
* **Rule-based metrics**: Cheap, fast, but shallow
* **LLM-as-judge**: Medium cost, high scale, decent correlation with human

Why choose it? When you need fast feedback loop for iteration, and you can tolerate some judge bias.

Architectural decision point: Judge model selection. 
* Stronger model than candidate = better correlation
* Different family = reduce systematic bias
* Smaller model = cheaper for high volume, but less reliable

## 5. Trade-offs

**Correlation vs Cost**: Strong judge like GPT-4 class gives better human correlation, but cost per eval high. For 1M evals, cost matters.

**Bias**: Judge has its own preferences - length bias, style bias, brand bias. Long answers tend to score higher. It may favor its own training distribution.

**Self-preference**: Model tends to prefer its own outputs. Cross-model judging needed.

**Prompt sensitivity**: Rubric wording small change → score shift. Evaluation becomes unstable.

**Hallucination in judge**: Judge itself can hallucinate reasoning. Chain-of-thought + calibration helps but not eliminates.

**Security**: Judge sees production data. Data leakage risk if using external API.

## 6. Practical Example

Enterprise customer support chatbot.

You have 2 prompts: Prompt v1 and Prompt v2. Need to pick better one.

You collect 500 real user queries from last week. For each, you have:
* user query
* retrieved context
* chatbot answer from v1 and v2

You run LLM-as-judge with rubric:
1. Factuality vs context: 1-5
2. Helpfulness: 1-5
3. Conciseness: 1-5

Judge outputs scores and short reasoning. You aggregate.

Result: v2 scores higher on factuality +2%, but lower on conciseness. Business cares more about factuality → choose v2.

Later you run nightly regression check: sample 1k production responses, judge for hallucination. If hallucination rate > 2% → alert.

## 7. Reasoning Challenge

உங்களிடம் 20M messages per day இருக்கு. Real-time production monitoring வேண்டும். Human evaluation impossible. LLM-as-judge use பண்ண வேண்டும்.

Constraints: Latency < 100ms for monitoring path, cost budget tight, judge accuracy important.

இங்கே என்ன architecture தேர்வு செய்வீர்கள்? Full traffic-க்கு judge run பண்ணுவீர்களா? Judge model எந்த size? Synchronous or async? ஏன்?

## 8. Key Takeaways

* LLM-as-judge solves scale problem of human evaluation, not replaces human judgment completely
* Rubric quality and prompt design decide reliability more than judge model choice
* Judge bias, length bias, self-preference are real; calibrate with human spot checks
* Use it for iteration speed and regression detection, not as final ground truth

**One mental model to keep:** Judge is a cheap, fast proxy for human, with known biases. Architect the evaluation system around those biases, not ignore them.
