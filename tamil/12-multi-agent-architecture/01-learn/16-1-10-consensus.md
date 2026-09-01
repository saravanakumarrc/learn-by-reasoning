# Consensus

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.10 — Learn

## 1. Problem

நீங்கள் multi-agent system பண்ணுகிறீர்கள். Agent A ஒரு decision எடுக்கிறது, Agent B அதே decision எடுக்க வேண்டும். Network இருக்கிறது, node crash ஆகலாம், message தாமதமாகலாம் அல்லது duplicate ஆகலாம்.

என்ன ஆகும்?

ஒரு agent தன்னுடைய state-ஐ update பண்ணிவிட்டது, இன்னொரு agent அதை காணவில்லை. இரண்டு agents ஒரே resource-க்கு conflict ஆகும் முடிவு எடுக்கிறது. System-க்கு ஒரே source of truth இல்லை.

Distributed system-ல் இது painful ஆகும். Multi-agent architecture-ல் இது fatal ஆகும்.

**Consensus என்றால் என்ன?** ஒரு குழுவான nodes சேர்ந்து, network failure, crash, message loss இருந்தும், ஒரு common value அல்லது decision-ல் உடன்படுவது.

Problem தெளிவு: **Byzantine அல்லது non-Byzantine failure இருக்கும்போது, யார் உண்மையான state?**

## 2. Mental Model

Consensus-ஐ ஒரு meeting-ஆக நினைக்கலாம்.

5 engineers conference call-ல் இருக்கிறார்கள். Network lag உள்ளது. ஒருத்தர் "deploy செய்வோம்" என்கிறார். எல்லாரும் அதை ஒப்புக்கொண்டார்களா என்பதை எப்படி உறுதி செய்வது?

தேவைப்படுவது மூன்று properties:

* **Agreement:** எல்லாரும் ஒரே value-ஐ ஏற்க வேண்டும்
* **Validity:** ஒப்புக்கொள்ளப்பட்ட value ஒரு participant-ஆல் propose செய்யப்பட்டதாக இருக்க வேண்டும்
* **Termination:** Correct processes இறுதியில் decide செய்ய வேண்டும்

Multi-agent system-ல் இது: ஒரு plan, ஒரு task assignment, ஒரு state transition, எல்லா agents-மும் ஒரே மாதிரி பார்க்க வேண்டும்.

## 3. How It Works

Consensus-க்கு basic idea: **propose, exchange, decide**.

ஒரு leader அல்லது coordinator ஒரு proposal அனுப்புகிறது. Nodes அதை accept / reject செய்கின்றன. Quorum அடைந்தால் commit ஆகிறது.

Paxos, Raft போன்ற algorithms இதை formalize செய்கின்றன.

Raft-ல் முக்கியமான concept: **leader election + log replication**.

Leader தேர்ந்தெடுக்கப்படுகிறது. Leader-க்கு clients ஆர்டர் கொடுக்கின்றன. Leader அதை followers-க்கு replicate செய்கிறது. Majority acknowledge ஆனதும் commit. New leader வந்தால் log consistency maintain செய்யப்படுகிறது.

Multi-agent context-ல்: agents தங்களுக்குள் ஒரு shared decision log maintain செய்கிறார்கள். யார் என்ன action எடுக்க வேண்டும் என்பதற்கு ஒரு agreed order இருக்கிறது.

## 4. Architectural Reasoning

Consensus எப்போது தேவை?

* Agents ஒன்றுக்கொன்று dependent tasks செய்யும்போது
* Shared state update செய்யும்போது
* Coordination required ஆக இருக்கும்போது, e.g., resource allocation, plan merging

Constraint-ஐ பாருங்கள்:

* Network partition ஆகலாம்
* Node crash ஆகலாம்
* Agents slow ஆக இருக்கலாம்

Options:

* **Central coordinator:** Simple, ஆனால் single point of failure. Coordinator down ஆனால் system halt.
* **Gossip / eventual consistency:** Fast, ஆனால் temporary disagreement உண்டு.
* **Consensus protocol:** Strong consistency, availability trade-off.

ஏன் consensus தேர்வு செய்வது? ஏனெனில் agent decisions idempotent இல்லை. ஒரு action இரண்டு முறை execute ஆனால் harm உண்டு. Payment, inventory update, robot movement போன்றவற்றில் தவறு கூடாது.

## 5. Trade-offs

1. **Consistency vs Availability:** CAP theorem. Network partition இருக்கும்போது, consensus system availability-ஐ sacrifice செய்து consistency-ஐ தக்க வைக்கும். Leader down என்றால் election நடக்கும் வரை system unavailable.

2. **Latency vs Safety:** Consensus ஒவ்வொரு decision-க்கும் round trip தேவை. 3 nodes-க்கு majority 2, network RTT இருமடங்காகும். Real-time agent coordination-க்கு கடினம்.

3. **Complexity vs Correctness:** Raft simple ஆக தெரியும், implementation-ல் edge cases நிறைய. Leader failover, log divergence, split brain avoid செய்ய வேண்டும்.

Failure modes:

* **Split brain:** இரண்டு leader ஆகி விட்டால் divergent state.
* **Stalled election:** Network partition-ல் leader தேர்ந்தெடுக்க முடியாமல் deadlock.
* **Byzantine agent:** Consensus assume செய்யும் honest nodes. Agent malicious ஆகவோ buggy ஆகவோ இருந்தால், standard consensus போதாது.

## 6. Practical Example

Enterprise workflow orchestration.

உங்களிடம் 3 planning agents உள்ளன: SalesAgent, InventoryAgent, FinanceAgent. ஒரு bulk order வந்தது.

SalesAgent "accept order" என்கிறது. InventoryAgent "stock உள்ளது" என்கிறது. FinanceAgent "credit check passed" என்கிறது.

ஆனால் இவர்கள் asynchronous-ஆக communicate செய்கிறார்கள். யார் முதலில் commit செய்வது?

Consensus layer ஒரு distributed log maintain செய்கிறது: `Order-123 → PROPOSE → ACCEPT`. Majority of agents sign off செய்த பிறகே order confirmed ஆகிறது. ஒரு agent crash ஆனாலும் log replay செய்து மற்ற agents state-ஐ rebuild செய்ய முடியும்.

இல்லாவிட்டால் Sales confirm செய்துவிட்டு Inventory reject செய்யும். Customer-க்கு inconsistent promise.

## 7. Reasoning Challenge

உங்களிடம் 7 autonomous agents உள்ளன. அவர்கள் ஒவ்வொரு 100ms-க்கு ஒரு முறை joint plan update செய்ய வேண்டும். Network latency ~50ms. ஒரு agent crash ஆகலாம்.

Consensus பயன்படுத்தினால் எந்த பிரச்சனை வரும்? Alternative என்ன?

*Latency budget-க்குள் majority quorum கிடைக்குமா? Availability vs freshness trade-off எப்படி handle செய்வீர்கள்?*

## 8. Key Takeaways

* Consensus என்பது failure இருந்தும் agreement உறுதி செய்வது, அல்லது speed.
* Multi-agent system-ல் shared decision, plan ordering, resource allocation-க்கு consensus தேவைப்படும்.
* Raft/Paxos போன்ற protocols leader election + log replication மூலம் agreement achieve செய்கின்றன.
* Trade-off: strong consistency கிடைக்கும், ஆனால் latency அதிகரிக்கும், availability குறையும், complexity அதிகரிக்கும்.
* Byzantine failures இருந்தால் classic consensus போதாது; extra verification தேவை.
