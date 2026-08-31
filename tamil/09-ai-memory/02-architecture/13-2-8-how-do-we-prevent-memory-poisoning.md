# How do we prevent memory poisoning?

> **Learning Path:** AI Memory
> **Section:** 13.2.8 — Architecture

## 1. Problem

உங்கள் AI agent-க்கு long-term memory இருக்கு. User conversations, past decisions, preferences, task results எல்லாம் memory-ல store ஆகுது.

பிரச்சனை என்ன? 

ஒரு தவறான தகவல் ஒரு முறை memory-க்குள் போய்விட்டால், அது திரும்ப திரும்ப reuse ஆகும். Agent அதை "உண்மை" என்று நம்ப ஆரம்பிக்கும். அதன் அடிப்படையில் புதிய decisions எடுக்கும்.

அதைத்தான் memory poisoning என்கிறோம்.

எடுத்துக்காட்டு: User தற்செயலாக தன் email-ஐ தவறாக சொல்கிறார். Agent அதை memory-ல save பண்ணிவிடுகிறது. பின்னர் அனைத்து follow-up emails-ம் தவறான address-க்கு போகின்றன. அல்லது ஒரு malicious prompt ஊடுருவி, "என் role என்னவென்றால்..." என்று system instruction-ஐ மாற்றும் data-வை memory-ல insert செய்துவிடுகிறது.

What goes wrong if we don't have this? Agent progressively unreliable ஆகும். Trust இழக்கும்.

## 2. Mental Model

Memory poisoning என்பது data quality problem அல்ல, **trust boundary problem**.

Memory என்பது external input-ஐ internal truth ஆக்கும் gateway. அந்த gateway-ல validation இல்லாமல் எதையும் உள்ளே விட்டால், poisoned data நிரந்தரமாகிவிடும்.

Think of memory as a database with a write path. Write path-ல யார் write பண்ணலாம், எப்படி validate செய்ய வேண்டும், எப்போது expire செய்ய வேண்டும் என்பதை control பண்ண வேண்டும்.

## 3. How It Works

Poisoning வரும் 3 main vectors:

1. **Bad user input**: User தவறாக சொன்னார், அல்லது social engineering மூலம் தவறான fact-ஐ plant செய்தார்.
2. **Tool / retrieval hallucination**: RAG pipeline தவறான document-ஐ retrieve செய்து, அதை memory-ல fact ஆக store செய்தது.
3. **Self-reinforcement loop**: Agent தன் முந்தைய output-ஐ திரும்ப படித்து, அதை ground truth என்று நம்பி மீண்டும் memory-க்கு write செய்யும்.

Prevention architecture என்பது 4 layers:

**Ingestion validation**: Memory-க்கு வரும் ஒவ்வொரு fact-க்கும் provenance tag இருக்க வேண்டும். Source யார்? User, tool, system? Confidence score என்ன?

**Write gate**: All writes go through a policy engine. Critical facts like PII, permissions, financial data - அவை explicit confirmation இல்லாமல் auto-save ஆகக்கூடாது.

**Separation of memory tiers**: 
- Short-term / session memory: ephemeral, low trust
- Long-term curated memory: validated, versioned
- Immutable system memory: role, policies

**Audit & revocation**: Memory entries immutable log + versioning. Poisoned entry-ஐ trace பண்ணி, invalidate பண்ணி, downstream effects-ஐ clean செய்ய முடிய வேண்டும்.

## 4. Architectural Reasoning

Memory poisoning-ஐ தடுக்க வேண்டும் என்றால், memory system-ஐ dumb key-value store ஆக பார்க்கக்கூடாது. அது trust-aware store ஆக வடிவமைக்க வேண்டும்.

எப்போது இது useful? 
- Agent long-term memory வைத்திருக்கும் போது
- Multi-user agents, shared memory இருக்கும் போது
- Autonomous agents tools-ஐ call செய்து results-ஐ memory-ல store செய்யும் போது

Alternatives:
- **No memory**: Poisoning இல்லை, ஆனால் personalization இல்லை
- **Blind write**: Simple, ஆனால் poisoned data permanent
- **Validated write with provenance**: சிறந்த trade-off

Architect choose பண்ணுவார் when consistency and safety > raw speed.

## 5. Trade-offs

**Validation vs Latency**: Every memory write-க்கு validation சேர்த்தால் round trips அதிகரிக்கும். Real-time agent-க்கு கஷ்டம்.

**Granularity vs Operability**: Fine-grained provenance, versioning கொடுத்தால் audit எளிது, ஆனால் storage மற்றும் query complexity அதிகரிக்கும்.

**Auto-curation vs User control**: Agent தானாக facts-ஐ summarize செய்து memory-ல வைக்கலாம். அது fast ஆனால் hallucination risk. Explicit user confirmation slow ஆனால் safe.

**Centralized memory vs per-user memory**: Centralized-ல cross-contamination risk. Isolation செய்தால் poisoning spread குறையும், ஆனால் shared knowledge குறையும்.

Failure mode: Validation logic itself compromised ஆகலாம். அதனால் validation rules-ஐ system memory-ல store செய்து, user-editable ஆக்கக்கூடாது.

## 6. Practical Example

Enterprise sales agent.

Architecture:
User conversation -> NLU -> Fact Extractor -> Write Gate -> Memory Store

Write Gate checks:
- Fact type = contact info? -> require user confirmation + source = user explicit
- Fact type = meeting outcome? -> source = calendar tool, confidence > 0.8
- Fact type = preference? -> allow auto-save but tag as low-confidence

Memory entry schema:
```
{
  id, 
  value, 
  source: {type: user|tool|system, id},
  confidence,
  ttl,
  verified: bool,
  version
}
```

User தற்செயலாக "என் budget $10k" என்று சொன்னார், ஆனால் உண்மையில் $100k. Agent அதை low-confidence preference ஆக store செய்யும். பின்னர் user explicitly confirm செய்யும் வரை agent அதை critical decision-க்கு use செய்யாது.

Poisoned entry detected ஆனால்? Audit log-ல source பார்த்து invalidate, அனைத்து dependent inferences-ஐ re-evaluate செய்யலாம்.

## 7. Reasoning Challenge

உங்களிடம் customer support agent இருக்கிறது. Agent ticket resolution-களை memory-ல store செய்து, future queries-க்கு reuse செய்கிறது. ஒரு junior agent தவறான workaround-ஐ ticket-ல type செய்தார். அது agent memory-க்கு போய்விட்டது. இனி agent அதே தவறான workaround-ஐ ஒவ்வொரு customer-க்கும் suggest செய்கிறது.

Memory poisoning-ஐ தடுக்க இங்கே என்ன control வைப்பீர்கள்? Write gate-ல என்ன policy வைக்கலாம்? Verified vs unverified memory-ஐ எப்படி separate செய்வீர்கள்?

## 8. Key Takeaways

- Memory என்பது trust boundary. Write path-ல validation இல்லாமல் memory-க்குள் எதையும் விடக்கூடாது.
- Provenance, confidence, verification status என்பவை memory entry-யின் முதல் class citizens.
- Poisoning-ஐ தடுக்க separation, gating, audit, revocation ஆகிய நான்கும் தேவை.
- Every architectural solution creates another trade-off: safety vs latency vs operability.
