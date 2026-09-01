# Independent state

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.14 — Learn

### 1. Problem

உங்களிடம் 3 agents இருக்கு: `OrderAgent`, `InventoryAgent`, `PricingAgent`.

ஒரு user order place பண்ணும்போது, மூன்றும் ஒன்றாக run ஆகணும். இப்போ இவை மூன்றும் ஒரே shared memory / global state-ஐ பார்த்து முடிவு எடுக்கிறது.

என்ன நடக்கும்?
- `PricingAgent` price-ஐ update பண்ணும் நேரத்தில் `OrderAgent` அதே price-ஐ read பண்ணி wrong total calculate பண்ணும்.
- ஒரு agent crash ஆனால் மற்ற agents-க்கு state inconsistent ஆகும்.
- ஒரு agent-ன் bug மற்ற agent-ஐயும் break பண்ணும்.
- Testing கஷ்டம். ஒரு agent-ஐ மாற்றினால் எல்லாவற்றையும் test பண்ண வேண்டும்.

**Pain point:** Agents tightly coupled ஆகி விடுகிறது. ஒன்றின் failure மற்றதை பாதிக்கிறது. Scale பண்ண முடியாது.

### 2. Mental Model

Independent state என்றால் ஒவ்வொரு agent-க்கும் **தனக்கு தேவையான state மட்டும் தனியாக** இருக்கும்.

Shared global brain இல்லை. தேவைப்பட்டால் மட்டும் explicit communication மூலம் state-ஐ share பண்ணுவார்கள்.

அனாலகி: ஒரு team-ல் ஒவ்வொரு engineer-க்கும் தனி laptop, தனி repo. நீங்கள் ஒரு document share பண்ணனும்னா explicit-ஆ share பண்ணனும். யாரோட hard disk crash ஆனாலும் மற்றவருக்கு பாதிப்பு இல்லை.

### 3. How It Works

ஒவ்வொரு agent-க்கும்:

- **Own state store:** local DB, file, memory, or external service it owns.
- **Own lifecycle:** start, stop, restart independently.
- **Explicit interface:** இன்னொரு agent-டோடு பேச முடியும் மட்டும் API / message queue / event மூலம்.
- **No direct access:** Agent A நேரடியாக Agent B-ன் internal state-ஐ read/write பண்ணாது.

State flow:
`Agent A` has event → publishes to bus → `Agent B` subscribes → updates its own copy of state.

ஒரு agent-ன் state change என்பது அதன் சொந்த decision. மற்ற agent-கள் அதை தெரிந்து கொள்ள வேண்டுமானால் அவை message receive பண்ணி தங்களுக்கு தேவையானதை update செய்து கொள்ளும்.

### 4. Architectural Reasoning

**எப்போது useful?**
Multi-Agent system-ல் agents வெவ்வேறு responsibility, வெவ்வேறு scale, வெவ்வேறு failure tolerance கொண்டிருக்கும்போது.

**எந்த constraint-ஐ address பண்ணும்?**
- Coupling
- Blast radius
- Independent deployment
- Team autonomy

**Alternatives:**
- Shared state store: ஒரே database / Redis. எளிது ஆனால் tight coupling.
- Central orchestrator: ஒரு brain எல்லா state-ஐயும் வைத்திருக்கும். Single point of failure.
- Independent state: ஒவ்வொருவரும் தனியாக.

Architect ஏன் independent state தேர்வு செய்வார்? ஏனெனில் agents evolve independently. `PricingAgent` ஒரு நாள் machine learning model-க்கு மாறலாம். அதன் state format மாறலாம். `OrderAgent` அதனால் பாதிக்கப்படக்கூடாது.

### 5. Trade-offs

**Pros**
- Fault isolation: ஒரு agent down ஆனாலும் மற்றவை run ஆகும்.
- Independent scaling: `OrderAgent` traffic அதிகம் → scale it alone.
- Team velocity: ஒவ்வொரு team தன் agent-ஐ தனியாக deploy பண்ணலாம்.
- Clear boundaries.

**Cons / Trade-offs**
- **Eventual consistency:** Agents ஒரே நேரத்தில் same state-ஐ பார்க்க மாட்டார்கள். Stale read வரலாம்.
- **Duplication:** ஒவ்வொரு agent-க்கும் தனியாக state copy வேண்டும். Storage cost.
- **Coordination complexity:** Transaction across agents கஷ்டம். Two-phase commit போன்றது வேண்டும்.
- **Observability:** System-wide view கிடைக்க கஷ்டம். Correlation ID, tracing தேவை.

Important failure mode: Agent A தனது state-ஐ update பண்ணிவிட்டு message publish பண்ணும் முன் crash ஆனால் Agent B update ஆகாது. Idempotency மற்றும் at-least-once delivery தேவை.

### 6. Practical Example

Enterprise RAG system.

3 agents:
- `RetrieverAgent`: user query → vector database-ல் search → relevant chunks.
- `RerankerAgent`: chunks-ஐ re-rank.
- `GeneratorAgent`: final answer generate.

Shared state இருந்தால் எல்லா agent-ம் ஒரே session store-ஐ use பண்ணும். ஒரு agent slow ஆனால் எல்லாம் slow.

Independent state-ல்:
`RetrieverAgent` தன் query cache-ஐ வைத்திருக்கும்.
`RerankerAgent` தன் model weights மற்றும் ranking scores-ஐ தனியாக வைத்திருக்கும்.
`GeneratorAgent` தன் conversation history-ஐ தனியாக வைத்திருக்கும்.

Communication: `RetrieverAgent` → event `documents_retrieved` → `RerankerAgent`. `RerankerAgent` → event `documents_reranked` → `GeneratorAgent`.

ஒரு agent upgrade செய்யலாம். Generator-ஐ LLM v2-க்கு மாற்றினாலும் Retriever பாதிக்காது.

### 7. Reasoning Challenge

உங்களிடம் `FraudAgent`, `RiskAgent`, `ApprovalAgent` இருக்கு. ஒரு transaction வரும்போது மூன்றும் evaluate பண்ணி decision தர வேண்டும். Business requirement: decision atomic-ஆக இருக்க வேண்டும். அதாவது மூன்றும் agree பண்ணினால் மட்டும் approve.

Independent state-ஐ keep பண்ணிக்கொண்டு atomic decision-ஐ எப்படி achieve பண்ணுவீர்கள்? Trade-off என்ன?

### 8. Key Takeaways

- Independent state = loose coupling, fault isolation, independent deployment.
- Agents communicate via explicit events/messages, not shared memory.
- Consistency eventual ஆகும். Coordinationக்கு extra pattern தேவை.
- Every architectural solution creates a trade-off: isolation vs consistency.
