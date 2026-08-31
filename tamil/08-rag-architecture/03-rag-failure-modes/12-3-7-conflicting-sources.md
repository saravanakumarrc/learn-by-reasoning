# Conflicting sources

> **Learning Path:** RAG Architecture
> **Section:** 12.3.7 — RAG failure modes

## 1. Problem

உங்க RAG system ஒரு user கேள்விக்கு பதில் தரணும். Same query-க்கு ஒரு source சொல்லுது "Interest rate 7.2%". இன்னொரு source சொல்லுது "Interest rate 8.5%". இன்னொரு source சொல்லுது "As of 2024, rate is 7.2%".

இப்போ LLM-க்கு மூன்று chunks கொடுத்தா, அது என்ன பண்ணும்? 

சில சமயம் முதல் source-ஐ தேர்ந்தெடுக்கும். சில சமயம் இரண்டையும் கலந்து ஒரு முடிவு எடுக்கும். சில சமயம் "According to sources, rate is 7.2% to 8.5%"ன்னு vague பதில் தரும்.

இது user-க்கு trust-ஐ குறைக்கும். Finance, legal, medical RAG-ல இது critical failure.

> **What goes wrong if we don't have this?** Hallucination-க்கு அடுத்தபடியாக, conflicting sources-ஐ முறையாக handle பண்ணாம விட்டால், model நம்பகத்தன்மை இழக்கும், முரண்பட்ட பதில்கள் வரும், audit-ல explain பண்ண முடியாது.

## 2. Mental Model

Conflicting sources என்பது retrieval-ல வந்த data-ல உண்மை வேறுபாடு இருப்பது அல்ல. அது **contextual conflict** ஆக இருக்கலாம்.

மூன்று வகை conflict:

1. **Factual conflict**: Same entity, different value. Interest rate 7.2% vs 8.5%
2. **Temporal conflict**: Value changed over time. 2022-ல 7.2%, 2025-ல 8.5%
3. **Scope conflict**: Different audience/condition. Personal loan 8.5%, home loan 7.2%

RAG-ல retriever எல்லாவற்றையும் fetch பண்ணும். LLM-க்கு கொடுத்துட்டா, model-க்கு source-ஐ rank பண்ணும் logic இல்லை.

## 3. How It Works

Retrieval ஆனதும் நமக்கு top-k chunks கிடைக்கும். அவற்றில் conflict இருந்தால், அது LLM-க்கு தெரியாது.

Typical pipeline:

Query → Retriever → Ranked chunks → Context builder → LLM → Answer

Conflict handling இங்கே இரண்டு இடத்தில் செய்யலாம்:

**Pre-generation**: Retrieval அப்புறம் conflict detection செய்து, context-ஐ clean பண்ணுவது.
**Post-generation**: Answer generate ஆன பிறகு citation-ஐ validate பண்ணி, contradiction flag போடுவது.

## 4. Architectural Reasoning

இந்த problem எப்போ painful ஆகும்?

- Multiple knowledge bases merge ஆன போது: internal wiki + external web + product docs
- Time-sensitive data: prices, rates, policies
- Multi-author content: sales team vs engineering docs

Options:

**A. Single source of truth enforce பண்ணு.** Retrieval-க்கு முன் source priority define பண்ணு. Ex: Internal DB > Official docs > Web.
Trade-off: Simpler, but new sources add பண்ண கஷ்டம்.

**B. Conflict detection layer வை.** Chunks-ல metadata compare பண்ணி conflict score கணக்கிடு. timestamp, source authority, provenance.
Trade-off: More accurate, but pipeline complex ஆகும்.

**C. LLM-க்கு conflict-ஐ explicitly கொடு.** Prompt-ல "If sources conflict, mention both and explain". 
Trade-off: Quick fix, but model inconsistent.

Architect-க்கு தேர்வு: System-ன் correctness requirement-ஐ பார்க்கணும். Finance/legal-ல A or B. Internal Q&A-ல C போதும்.

## 5. Trade-offs

**Authority vs Recency**: ஒரு authoritative source பழையதாக இருக்கலாம். Recent source less authoritative ஆக இருக்கலாம். எது prioritize?

**Coverage vs Precision**: top-k ஐ அதிகப்படுத்தினால் conflict அதிகம் வரும். குறைத்தால் missing info.

**Transparency vs Confidence**: User-க்கு conflict-ஐ சொல்லி "two sources say different things"ன்னு கொடுக்கலாம். அது honest ஆனால், user experience குறையும்.

**Operational cost**: Conflict detection-க்கு extra embedding, metadata store, re-ranking logic தேவை. Small team-க்கு over-engineering ஆகலாம்.

Failure mode: LLM மிகவும் confident-ஆக தவறான source-ஐ pick பண்ணும். Citation hallucinations.

## 6. Practical Example

Enterprise RAG for bank policy.

Sources:
- `policy_2023.pdf` : FD interest 7.2%
- `policy_2025.pdf` : FD interest 8.5%
- `website FAQ` : FD interest 7.2% as of Jan 2024

Query: "What is current FD interest rate?"

Good architecture:

Retriever returns 3 chunks. Pre-generation layer metadata-ல `published_date` பார்க்கும்.

Conflict resolver logic:
```
if same entity and different value:
  pick latest timestamp with source_authority >= threshold
  keep older source as "historical reference"
```

Context builder LLM-க்கு கொடுக்கும்:
```
Current rate: 8.5% [policy_2025.pdf, published 2025-03-01]
Previous rate: 7.2% [policy_2023.pdf, published 2023-01-15]
```

LLM answer: Current rate 8.5% and cite. If user asks about 2023, then show old rate.

Alternative: If no timestamp, route to human review or ask clarifying question.

## 7. Reasoning Challenge

உங்களிடம் RAG system இருக்கு. Two sources:
- Internal CRM notes: customer tier = Gold, last updated 2021
- Support chat transcript: customer tier = Platinum, last updated 2024

User query: "What discount should I apply for this customer?"

Discount depends on tier. இங்கே என்ன architecture தேர்வு செய்வீர்கள்? Conflict-ஐ எப்படி handle பண்ணுவீர்கள்? Recency எடுக்கலாமா, authority எடுக்கலாமா? User-க்கு என்ன பதில் கொடுப்பீர்கள்?

## 8. Key Takeaways

- Conflicting sources என்பது retrieval problem அல்ல, reasoning + provenance problem
- Timestamp, source authority, scope metadata இல்லாமல் RAG production ready ஆகாது
- Conflict-ஐ hide பண்ணாதே, detect பண்ணி explicit ஆக manage பண்ணு
- Every conflict resolution strategy creates a new trade-off between recency, authority, and transparency
