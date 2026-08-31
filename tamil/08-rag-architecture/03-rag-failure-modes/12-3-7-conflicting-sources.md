# Conflicting sources

> **Learning Path:** RAG Architecture
> **Section:** 12.3.7 — RAG failure modes

## 1. Problem

உங்கள் RAG system ஒரு user question க்கு answer generate பண்ணுது. அதுக்காக retriever 3 documents கொண்டு வந்திருக்கு.

Document A: "Product X release date is 2024-01-15"
Document B: "Product X release date is 2024-03-10"
Document C: "Product X is planned for Q1 2024"

இப்போ LLM எதை நம்பி answer பண்ணும்? முதல் document ஐயா? average ஆக்குமா? அல்லது "Conflicting information found" என்று சொல்லுமா?

Real system-ல இது தினமும் நடக்கும். Source update ஆகாம இருக்கும், different teams different docs எழுதுவாங்க, old blog vs new release notes vs internal wiki. Retrieval ல top-k results எடுத்தால் conflicting facts கலந்து வரும்.

இப்படி conflicting sources இருந்தால் என்ன ஆகும்?
* Hallucination இல்லாமல், model பொய் சொல்லாமல் இருந்தாலும், அது முரணான தகவலை mix பண்ணி ஒரு uncertain answer கொடுக்கும்.
* User trust போய்விடும்.
* Financial / legal domain ல இது பெரிய risk.

Conflicting sources என்பது RAG failure mode இல்லை, data problem. ஆனால் RAG architecture இதை handle பண்ணாம விட்டால் system unreliable ஆகும்.

## 2. Mental Model

RAG என்பது "retrieve then generate". Retrieval என்பது relevance மட்டும் பார்க்கிறது, truthfulness அல்ல.

ஒரு question க்கு நீங்கள் 5 sources எடுத்தால், அவை ஒன்றுக்கொன்று agree பண்ணுதா, disagree பண்ணுதா என்பதை system தெரிந்து கொள்ள வேண்டும்.

Mental model: **Source Provenance + Versioning + Conflict Detection**.

ஒரு fact ஐ ஒரு source இல்லை, source + timestamp + authority + confidence உடன் பார்க்க வேண்டும்.

## 3. How It Works

Conflict எப்படி detect பண்ணுவது?

**Simple approach:** LLM ஐயே judge ஆக்குவது.
Retrieved chunks-ஐ prompt-ல போட்டு: "Do these sources agree on the release date? If conflict, list differences."

Problem: LLM itself inconsistent ஆக இருக்கும், and it adds inference cost.

**Better approach:** Structured extraction முன் செய்யுங்கள்.
Retrieval அப்புறம், each chunk-ல relevant fact-ஐ extract பண்ணி structured form-ல மாற்றுங்கள். உதாரணமாக release date field.

```
doc_id | fact_type | value | timestamp | source_type
A      | release_date | 2024-01-15 | 2024-01-10 | release_notes
B      | release_date | 2024-03-10 | 2024-02-01 | blog
```

இப்போ value mismatch தெரியும். இதை conflict detection layer பார்த்து flag பண்ணும்.

LLM generate செய்யும்போது, conflict இருந்தால்:
* Both values-ஐ cite பண்ணி present செய்யும்
* Or higher authority source-ஐ prioritize பண்ணும்
* Or user-க்கு "conflict detected, human review needed" என்று சொல்லும்

## 4. Architectural Reasoning

எப்போது இது useful ஆகும்?
* Enterprise knowledge base where multiple teams write docs
* Financial / medical / legal RAG where correctness matters
* System where data changes frequently

Constraint இது address பண்ணுவது: **Consistency vs Freshness vs Authority**.

Options:
1. **Last-write-wins**: timestamp மூலம் சமீபத்திய source எடு. Simple, ஆனால் wrong blog புதுசா இருந்தால் அது தவறானதாகும்.
2. **Authority-weighted**: source type-க்கு weight கொடு. Official release notes > internal wiki > community blog.
3. **Explicit conflict surface**: conflict இருந்தால் user-க்கு show பண்ணு, decision-ஐ user-க்கு விடு.
4. **Consensus threshold**: k sources-ல majority agree ஆனால் மட்டும் answer கொடு.

Architect choose பண்ணுவது depends on risk. Customer support bot-க்கு last-write-wins போதும். Contract clause extraction-க்கு explicit conflict surface தேவை.

## 5. Trade-offs

* **Detection cost vs accuracy**: LLM-based conflict detection flexible ஆனால் slow, non-deterministic. Structured extraction accurate ஆனால் schema maintain பண்ண வேண்டும்.
* **Automation vs human-in-the-loop**: Auto resolve பண்ணினால் fast ஆனால் wrong resolution risk உள்ளது. Human review safe ஆனால் latency அதிகம்.
* **Citation transparency**: எல்லா conflicting sources-ஐயும் cite பண்ணினால் user confused ஆகலாம். ஆனால் hide பண்ணினால் trust போகும்.
* **Freshness vs stability**: Newer source எப்போதும் correct இல்லை. Versioning இல்லாமல் vector DB-ல update பண்ணினால் old fact இன்னும் index-ல இருக்கும்.

Failure mode: Conflict detection இல்லாமல், LLM இரண்டு dates-ஐயும் combine பண்ணி "release date is around January to March 2024" போன்ற vague answer கொடுக்கும். அது technically wrong இல்லை, ஆனால் useless.

## 6. Practical Example

RAG for internal product knowledge.

Architecture:
Retriever -> top 10 chunks -> Conflict Detection Service -> LLM Generator

Conflict Detection Service:
* Extract fact: `release_date` using small LLM or regex
* Group by fact_type
* Compare values across sources
* Compute source authority score: release_notes=1.0, wiki=0.7, blog=0.5
* Compute recency score
* Final score = weighted sum

If variance > threshold, flag conflict.

Generator prompt:
```
You are given sources. Some conflict on release_date.
A says 2024-01-15, source=release_notes, date=2024-01-10
B says 2024-03-10, source=blog, date=2024-02-01
Prefer higher authority. Acknowledge conflict.
```

Answer will be: "According to official release notes dated 2024-01-10, release date is 2024-01-15. Note: a blog post dated 2024-02-01 mentions 2024-03-10."

## 7. Reasoning Challenge

உங்களிடம் ஒரு medical RAG system உள்ளது. Retriever ஒரு drug dosage க்கு 3 sources கொடுக்கிறது:
* FDA label 2023: 10mg
* Hospital guideline 2024: 20mg
* Research paper 2025: 15mg

User asks for recommended dosage. உங்கள் system எப்படி respond பண்ணும்? Auto resolve பண்ணுவீர்களா? Conflict-ஐ surface பண்ணுவீர்களா? ஏன்? Authority, recency, safety ஆகியவற்றை எப்படி balance பண்ணுவீர்கள்?

## 8. Key Takeaways

* Conflict என்பது retrieval quality problem அல்ல, provenance problem.
* RAG system-க்கு source metadata - timestamp, authority, version - கண்டிப்பாக தேவை.
* LLM-ஐ blindly generate விடாமல், conflict detection layer வைத்து facts-ஐ normalize செய்து பிறகு generate செய்யுங்கள்.
* Safety critical domains-ல auto resolution-க்கு பதில் explicit conflict surfacing தான் சரியான trade-off.
