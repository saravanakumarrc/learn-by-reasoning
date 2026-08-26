# CAP theorem

> **Learning Path:** Distributed Systems
> **Section:** 3.1.19 — Core concepts

## 1. Problem

உங்க service-க்கு users Chennai, Bangalore, US-ல இருக்காங்க. Latency குறைக்க 3 regions-ல database replicas வச்சிருக்கீங்க. Write ஒரு region-ல நடக்கும், read வேற region-ல நடக்கும்.

இப்போ network-ல packet loss வருது. Chennai மற்றும் Bangalore replicas ஒன்னோட ஒன்னு பேச முடியல. Partition ஆகிடுச்சு.

இந்த நேரத்தில் என்ன செய்வீங்க?
* Write accept பண்ணி, read கொடுக்கலாமா? 
* Read கொடுத்தால் stale data கொடுக்குமா?
* எல்லாத்தையும் reject பண்ணி error கொடுக்கலாமா?

இது தான் CAP theorem உருவான problem. Distributed system-ல network failure என்பது `when`, அல்ல `if` இல்லை.

## 2. Mental Model

CAP சொல்றது: ஒரு distributed system-ல **Consistency, Availability, Partition Tolerance** மூன்றையும் ஒரே நேரத்தில் perfect-ஆ guarantee பண்ண முடியாது. மூன்றில் இரண்டை மட்டுமே தேர்வு செய்ய முடியும்.

நிஜ உலகில் Partition Tolerance என்பது must-have. Network partition வராமல் இருக்க முடியாது. அதனால் உண்மையில் தேர்வு **Consistency vs Availability** தான்.

* **Consistency**: எல்லா nodes-லும் ஒரே நேரத்தில் ஒரே data தெரியும். Read எப்போதும் latest write-ஐ திருப்பி கொடுக்கும்.
* **Availability**: ஒவ்வொரு request-க்கும் system ஏதாவது response கொடுக்கும், success ஆகட்டும் failure ஆகட்டும். System down ஆகாது.
* **Partition Tolerance**: Network split ஆனாலும் system வேலை செய்யும்.

## 3. Architectural Reasoning

Partition தவிர்க்க முடியாது என்பதால், architect முடிவு இரண்டு பாதைகள்:

**CP - Consistency + Partition Tolerance**
Partition வந்தால், consistency காக்க கொஞ்சம் requests-ஐ reject பண்ணுவீங்க அல்லது wait பண்ணுவீங்க.
எ.கா., MongoDB primary-replica with strong consistency, or etcd, ZooKeeper.
Write போனால் quorum கிடைக்கணும். Quorum இல்லை என்றால் write fail. Read எப்போதும் up-to-date data.

**AP - Availability + Partition Tolerance**
Partition வந்தாலும் service available இருக்கணும். Consistency தளர்த்துவீங்க.
எ.கா., Cassandra, DynamoDB, MongoDB eventual consistency mode.
Write எந்த replica-லும் accept ஆகும். Data மெதுவாக sync ஆகும். Read சமயத்தில் stale data வரலாம்.

இது trade-off அல்ல, business requirement-ல இருந்து வரும் decision.

## 4. Trade-offs

**CP தேர்வு செய்யும் போது:**
* Pros: Data correctness உறுதி. Financial transactions-க்கு முக்கியம்.
* Cons: Partition time-ல availability குறையும். Timeout, errors அதிகம். Latency அதிகரிக்கும். Ops complexity அதிகம்.

**AP தேர்வு செய்யும் போது:**
* Pros: எப்போதும் up. Low latency. Scale சுலபம்.
* Cons: Temporary inconsistency. Last-write-wins conflict வரும். Replay / reconciliation logic தேவைப்படும்.

முக்கிய failure mode: AP system-ல split-brain write. Partition முடிஞ்சதும் எந்த value வைத்திருக்கிறது என்பது தெரியாது. Conflict resolution policy வேண்டும்.

## 5. Practical Example

**Payment service:** User balance update. இங்கே Consistency முக்கியம். ₹100 debit ஆனால் ₹100 தான் balance இருக்கணும். Partition வந்தால் write-ஐ block பண்ணுவீங்க. CP தேர்வு. Availability கொஞ்சம் குறைந்தாலும் சரி.

**Social feed / Product catalog:** User profile update ஒரு region-ல போய், மற்ற region-ல 2 விநாடி கழித்து தெரிந்தாலும் பரவாயில்லை. Feed எப்போதும் load ஆகணும். AP தேர்வு. Eventual consistency போதும்.

ஒரே company-க்குள்ளும் இரண்டும் இருக்கும். System boundary மாறும் போது CAP decision மாறும்.

## 6. Reasoning Challenge

உங்க e-commerce cart service-க்கு 3 region replicas உள்ளன. Black Friday-ல traffic spike. Inter-region network flaky ஆகிறது.

Requirement: User cart-ஐ add பண்ணும்போது எப்போதும் success response வேண்டும். Cart item 5-10 விநாடி கழித்து வேறு device-ல தெரிந்தால் பரவாயில்லை. Checkout time-ல தான் accurate cart வேண்டும்.

நீங்கள் CP எடுப்பீர்களா AP எடுப்பீர்களா? எந்த trade-off-ஐ accept பண்ணுவீங்க? Checkout-க்கு என்ன extra mechanism வேண்டும்?

## 7. Key Takeaways

* Partition Tolerance என்பது distributed system-ல non-negotiable. CAP தேர்வு உண்ம
