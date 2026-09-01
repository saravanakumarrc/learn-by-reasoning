# Human evaluation

> **Learning Path:** AI Evaluation
> **Section:** 18.1.4 — Evaluation

### 1. Problem

உங்க team ஒரு LLM-based agent-ஐ build பண்ணிட்டீங்க. Unit tests pass ஆகுது. Automated metrics - BLEU, ROUGE, accuracy - எல்லாம் நல்லா இருக்கு.

Production-க்கு போனதும் user சொல்றார்: "Answer is technically correct but tone is rude", "It hallucinates in Tamil mixing", "It gives correct info but too verbose for a customer support use case".

Automated metrics எதுவும் இதை catch பண்ணல. Why?

Because metrics can measure what is measurable, not what matters. Quality, safety, usefulness, factual correctness in real context - இதை எல்லாம் numbers மட்டும் decide பண்ண முடியாது.

இங்கதான் human evaluation தேவைப்படுது.

### 2. Mental Model

Human evaluation என்பது **ground truth for subjective quality**.

Automated evaluation = fast, cheap, consistent. Human evaluation = slow, expensive, but captures nuance, intent, real-world utility.

Think of it like this: A code review. Static analysis tool can catch style issues. But only a senior engineer can say "இந்த design புரியாது, இங்க coupling அதிகம்".

Human evaluation is your senior reviewer for LLM outputs.

### 3. How It Works

Practically, human evaluation என்பது structured judging.

1. **Task definition**: What exactly we judge? Correctness? Helpfulness? Tone? Safety?
2. **Sampling**: Random or stratified sample of real prompts and outputs. Production traffic-ல இருந்து sample எடுப்பது best.
3. **Annotation UI**: Judges-க்கு prompt, output A/B, rubric கொடுக்கணும். Bias குறைக்க randomize order, hide model name.
4. **Rubric**: Clear criteria with scale. Ex: 1-5 for factual correctness, 1-5 for relevance.
5. **Inter-rater agreement**: Same sample-ஐ 2-3 judges பார்த்து consistency check பண்ணணும். Kappa score பார்க்கலாம்.
6. **Aggregation**: Per-model scores, error categories.

For RAG / agent systems, evaluation often includes: Did it cite correct source? Did it hallucinate? Did it follow tool use correctly?

### 4. Architectural Reasoning

Human evaluation useful ஆகும் போது:

* New capability launch பண்ணும்போது baseline set பண்ண
* Automated metric மற்றும் real user satisfaction mismatch இருக்கும்போது
* Safety, brand tone, cultural nuance முக்கியமான domain-ல
* Model version upgrade decision-க்கு final gate

Alternatives:
* **Offline automated metrics** - fast but blind to nuance
* **Online A/B with user engagement** - real signal but noisy, slow, and can't diagnose why
* **LLM-as-judge** - cheap proxy, but inherits biases

Architect choose human evaluation when decision cost is high. Model change cost lakhs per month, reputation risk உண்டு. அப்போ $ few thousand for human eval is cheap insurance.

### 5. Trade-offs

**Quality vs Cost**: Human eval accurate ஆனா expensive and slow. 1000 samples × 2 judges = real time.

**Consistency vs Nuance**: Judges disagree. Need training, rubric refinement. Too rigid rubric kills nuance.

**Coverage vs Depth**: Full production set-ஐ evaluate பண்ண முடியாது. Sampling bias வரும். Stratified sampling by intent, language, risk level தேவை.

**Freshness**: Model updates fast, human eval lags. Need a hybrid loop: automated screening → human eval on high-risk deltas.

Failure mode: Bad rubric = garbage judgments. Untrained judges = noise. No blinding = brand bias.

### 6. Practical Example

Enterprise customer support agent for Tamil + English mixed queries.

Automated metric: Exact match of entities = 92%. Looks good.

Human eval setup:
* 300 real anonymized tickets sample
* Rubric: 1) Factual correctness 2) Resolution completeness 3) Tone politeness 4) Language appropriateness
* 3 trained annotators, blinded to model version

Result: Model A scores higher on correctness but tone is robotic, users escalate. Model B slightly lower correctness but higher resolution completeness and tone. Business chooses B.

Without human eval, you would have shipped Model A and increased churn.

### 7. Reasoning Challenge

உங்க RAG system-க்கு retrieval quality பெரிய issue. You have two retrieval strategies: A - high recall, more docs; B - high precision, fewer docs.

Automated metric: MRR and Recall@k both improve with A.

But human judges say answers from A are more verbose, sometimes contradictory because of extra docs. B answers are concise and trustworthy.

Model upgrade செய்யறீங்களா? அப்படி இல்லைனா என்ன hybrid approach பார்ப்பீங்க? Trade-off என்ன?

### 8. Key Takeaways

* Human evaluation exists because some quality dimensions cannot be reduced to numbers.
* Use it for high-stakes decisions, safety, tone, and real usefulness - not for every nightly run.
* Good rubric + trained judges + blinding = reliable signal. Without this, noise > signal.
* Treat human eval as part of architecture loop: sample → judge → error taxonomy → fix → re-evaluate.
