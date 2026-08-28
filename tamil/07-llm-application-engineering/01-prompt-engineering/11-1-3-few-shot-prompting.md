# Few-shot prompting

> **Learning Path:** LLM Application Engineering
> **Section:** 11.1.3 — Prompt engineering

## 1. Problem

உங்களுக்கு ஒரு LLM கிடைச்சிருக்கு. Zero-shot-ல் simple instruction கொடுத்தா சில சமயம் வேலை செய்யும். ஆனா real application-ல format கண்டிப்பா வேணும்.

> "ஒரு user query-ஐ sentiment-ஆக classify பண்ணு: positive / negative / neutral"

Model சில சமயம் explanation கொடுக்கும், சில சமயம் தமிழில் பதில் கொடுக்கும், சில சமயம் format மாறும். Production-ல இதை parse பண்ண முடியாது.

Problem என்ன? **Model-க்கு உங்கள் domain-ன் expectation தெரியாது.** Style, format, nuance எல்லாம் missing.

இப்போ நீங்கள் fine-tune பண்ணலாம். ஆனா அது expensive, slow, மாற்றத்துக்கு hard. ஒரே task-க்கு ஒரே model வேண்டாம்.

இங்கே தான் few-shot வருகிறது.

## 2. Mental Model

Few-shot prompting = **Model-க்கு உதாரணங்களை காட்டி, "இப்படி behave பண்ணு" என்று காட்டுவது.**

நீங்கள் ஒரு junior engineer-க்கு ஒரு task கொடுக்கும்போது, definition மட்டும் சொல்லாமல் 2-3 examples காட்டுவீர்கள். அவர் pattern புரிந்துகொள்வார். அதேதான் LLM-க்கும்.

Zero-shot = instruction மட்டும்.
Few-shot = instruction + 2-5 example input-output pairs.

Model தானாக generalise பண்ணும். Context window-ல இருக்கும் examples pattern-ஐ கற்றுக்கொள்கிறது.

## 3. How It Works

Prompt structure simple:

```
Task: ...
Format: ...
Examples:
Input: X1
Output: Y1
Input: X2
Output: Y2

Input: X_new
Output:
```

Model, examples-ல இருந்து format, style, decision boundary எல்லாவற்றையும் infer பண்ணும்.

Important point: Example quality > quantity. 3 good diverse examples, 10 random examples-ஐ விட சிறந்தது.

## 4. Architectural Reasoning

எப்போ few-shot useful?

* **Format enforcement தேவை:** JSON output, structured fields, classification labels
* **Domain nuance உள்ளது:** ஒரு bank-ல "dispute" என்றால் ஒரு meaning, e-commerce-ல வேறு meaning
* **Low latency, no training:** Fine-tune பண்ணாமல் quick iteration வேண்டும்
* **Small data:** 3-5 examples மட்டுமே உள்ளது

Alternatives:

* **Zero-shot + stronger instruction:** சில சமயம் போதும். ஆனால் consistency குறைவு.
* **Few-shot with CoT:** Reasoning steps காட்டலாம். ஆனால் latency & token cost அதிகம்.
* **Fine-tuning / LoRA:** High volume, stable pattern-க்கு best. ஆனால் cost, maintenance உள்ளது.
* **RAG:** Knowledge தேவைப்படும் போது. Few-shot style கற்றுக்கொடுக்காது.

Architect-ஆக நீங்கள் தேர்வு செய்ய வேண்டியது: **Consistency vs Cost vs Maintainability.** Few-shot என்பது cost-ஐ தியாகம் செய்து consistency-ஐ கொண்டு வரும் shortcut.

## 5. Trade-offs

**1. Consistency vs Prompt size**
Examples அதிகம் சேர்த்தால் pattern better. ஆனால் context window fill ஆகும், latency & cost increase. Token cost linear-ஆ வளரும்.

**2. Overfitting to examples**
Model examples-ஐ memorize பண்ணி, real input-க்கு generalize பண்ண தவறும். உதாரணங்கள் diverse ஆக இருக்க வேண்டும்.

**3. Fragility**
Small wording change in examples-ல கூட output மாறும். Prompt versioning தேவை.

**4. Security / Leakage**
Examples-ல sensitive data வைத்தால் அது prompt-ல expose ஆகும். Production-ல real PII use பண்ணக்கூடாது.

Failure mode: Example bias. உங்கள் 3 examples எல்லாம் positive sentiment-ல இருந்தால், model neutral-ஐ தவறாக classify பண்ணும்.

## 6. Practical Example

Enterprise support ticket classification.

Task: Ticket-ஐ `billing`, `technical`, `account` என classify செய்து JSON output.

Zero-shot output unpredictable.

Few-shot prompt:

```
Classify the support ticket into one of: billing, technical, account.
Output JSON only: {"category":"...","confidence":"high|medium|low"}

Examples:
Input: "I was charged twice for my subscription this month"
Output: {"category":"billing","confidence":"high"}

Input: "App crashes when I try to upload a file"
Output: {"category":"technical","confidence":"high"}

Input: "Can't reset my password, link expired"
Output: {"category":"account","confidence":"medium"}

Input: "My invoice amount is wrong"
Output:
```

இங்கே model format, category boundary, confidence level style எல்லாம் கற்றுக்கொள்கிறது.

Production-ல நீங்கள் examples-ஐ dynamically select பண்ணலாம்: user query-க்கு nearest examples-ஐ embedding search-ல எடுத்து prompt-ல சேர்க்கலாம். இதை dynamic few-shot என்கிறோம்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு RAG agent உள்ளது. User question-க்கு answer கொடுக்கும்போது citation format கண்டிப்பாக வேண்டும்: `Answer + [doc_id]`. Zero-shot-ல 60% time format miss ஆகிறது.

உங்களிடம் 5000 historical Q&A pairs உள்ளன. ஆனால் latency strict ஆக 800ms வரை மட்டுமே.

Few-shot use பண்ணுவீர்களா? எத்தனை examples? Static ஆக வைப்பீர்களா, dynamic ஆக select பண்ணுவீர்களா? ஏன்?

## 8. Key Takeaways

* Few-shot = examples மூலம் behavior teach செய்வது. Fine-tune இல்லாமல் pattern transfer.
* Example quality and diversity > quantity. Format மற்றும் style இரண்டும் தெளிவாக இருக்க வேண்டும்.
* Trade-off எப்போதும் token cost, latency, consistency மூன்றுக்கும் இடையே.
* Production-ல prompt versioning, example sanitization, evaluation set-ல consistency test அவசியம்.
* Few-shot என்பது architecture decision, not just prompt trick.
