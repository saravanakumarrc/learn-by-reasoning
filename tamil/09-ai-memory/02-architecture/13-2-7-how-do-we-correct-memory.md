# How do we correct memory?

> **Learning Path:** AI Memory
> **Section:** 13.2.7 — Architecture

## 1. Problem

உங்கள் AI agent கடந்த வாரம் கற்றுக்கொண்டது: "user-க்கு coffee ஆர்டர் செய்யும்போது default-ஆ sugar குறைவாக வேண்டும்". 

இப்போது user சொல்கிறார்: "இல்லை, sugar அதிகமாக வேண்டும்". 

Memory-ல இருப்பது பழைய தகவல். Agent அதை தொடர்ந்து use பண்ணினால் என்ன ஆகும்? Hallucination இல்லை, wrong personalization.

இன்னொரு case: RAG system-ல vector database-ல outdated document embed ஆகி இருக்கு. Source document update ஆனது, ஆனால் embedding மாறவில்லை. 

**Problem:** Memory என்பது append-only அல்ல. It needs to be corrected, merged, forgotten, and versioned. 

What goes wrong if we don't have correction? Stale facts, conflicting memories, drift, privacy violation.

## 2. Mental Model

Memory correction என்பது ஒரு write operation அல்ல. It's a **conflict resolution process**.

Think of memory as a distributed database with multiple writers: user, agent inference, external source, feedback loop.

Correction means:
1. Identify which memory is stale / wrong
2. Decide what the new ground truth is
3. Update all derived representations consistently
4. Keep audit trail

Analogy: git history. நீங்கள் ஒரு file-ல தவறு செய்தீர்கள். `git commit --amend` பண்ணுவது போல, memory-யும் rewrite செய்ய முடியாது, you need a new version and deprecate old.

## 3. How It Works

Architecture-ல 3 layers இருக்கும்:

**Source of Truth Layer:** Raw facts where it came from. User utterance, verified document, admin override.

**Memory Store Layer:** Vector DB, graph DB, relational table. இங்கே embeddings, entities, relations store ஆகும்.

**Correction Controller:** இது ஒரு service. இது incoming correction signal-ஐ receive செய்து, impact analysis பண்ணி, update propagate செய்கிறது.

Flow:
User says correction → Intent extraction → Identify affected memory keys / entities → Retrieve current memory version → Conflict resolution policy apply → Write new version with metadata `corrected_at`, `supersedes_id` → Invalidate / re-embed related vectors → Notify downstream consumers.

## 4. Architectural Reasoning

When this becomes useful? 
- Long-running agents with persistent user memory
- RAG with mutable knowledge base
- Multi-agent system where agents learn from each other

Constraint it addresses: **consistency over time**.

Alternatives:
* **Overwrite in place:** Simple, but audit trail இல்லை, rollback முடியாது.
* **Append-only with new version:** Safe, but query time-ல latest version find செய்ய வேண்டும்.
* **Separate correction log:** Event sourcing style. Rebuild memory from log when needed.

Architect might choose append-only versioning with a `valid_from / valid_to` window. Because AI memory needs explainability: "Why did you change your mind?" என்று user கேட்டால் answer வேண்டும்.

## 5. Trade-offs

* **Correctness vs Availability:** Strong correction requires locking / validation. Real-time agent-க்கு latency வரும். Eventual consistency choose செய்யலாம்.
* **Granularity vs Cost:** Entity level correction cheap. Whole conversation re-embed செய்வது costly. Where to draw boundary?
* **Automation vs Human-in-the-loop:** Auto-correction from user feedback fast, but false positive ஆகலாம். Sensitive data-க்கு human approval வேண்டும்.
* **Storage growth:** Every correction creates new version. Vector DB-ல duplicate embeddings grow. TTL / compaction தேவை.

Failure modes:
- Partial update: Entity update ஆனது, but related relation update ஆகவில்லை → inconsistent graph.
- Stale cache: API gateway cache old memory serve பண்ணுது.
- Feedback loop: Agent wrong prediction → writes to memory → later correction uses that wrong memory as source.

## 6. Practical Example

Enterprise support agent with long-term customer memory.

Memory schema: `user_profile` table + `vector_memories` table with columns: `entity_id`, `content`, `embedding`, `source`, `version`, `valid_to`.

User says: "My address is no longer Chennai, it's Bangalore".

Correction controller:
1. Identify `entity_id = user_address`. Current version v3 valid.
2. Write v4 with new address, `supersedes_id=v3`, `valid_from=now`.
3. Update relational DB.
4. Re-embed user profile summary vector, delete old vector, insert new.
5. Emit `memory_corrected` event to notification service.

Next time agent searches memory, query filters `valid_to IS NULL`. Old address automatically invisible.

## 7. Reasoning Challenge

உங்களிடம் RAG system இருக்கு. Source document update ஆனதும், அந்த document-ன் embedding stale ஆகிறது. 10M documents உள்ளன. Full re-embedding cost அதிகம். 

ஒரு user கேள்விக்கு பதில் தவறாக வருகிறது, அவர் correction சொல்கிறார். 

இங்கே memory correction-க்கு நீங்கள் என்ன architecture தேர்வு செய்வீர்கள்? Immediate re-embed அனைத்தையும் செய்வீர்களா? Selective invalidation + lazy re-embed பண்ணுவீர்களா? ஏன்?

## 8. Key Takeaways

* Memory correction என்பது overwrite அல்ல, versioned conflict resolution.
* Source of truth, memory store, correction controller என 3-layer separation தேவை.
* Append-only versioning auditability கொடுக்கும், query complexity அதிகரிக்கும்.
* Every correction creates propagation problem: embeddings, cache, downstream agents.
* Trade-off: correctness vs latency vs storage cost.
