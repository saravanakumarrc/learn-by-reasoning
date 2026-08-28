# Cross-team coordination

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.2.4 — Incident & operational leadership

# Cross-team coordination

## 1. Problem

ஒரு production incident வந்தது. Payment service fail ஆகுது. Checkout timeout. 

Payment team சொல்றது: `gateway timeout` வருது, நாங்க healthy. 
Gateway team சொல்றது: downstream payment-க்கு request போகுது, response வரல. 
DB team சொல்றது: latency spike இருக்கு, connection pool full. 
Mobile team சொல்றது: user-க்கு error screen தெரியுது.

எல்லாரும் தங்கள் service-ல் சரியா இருக்குன்னு பார்க்கிறாங்க. ஆனால் user-க்கு பிரச்சனை தொடருது. Slack-ல 4 thread-ல பேச்சு. யார் என்ன decide பண்ணுறது தெரியல. On-call engineer-கள் எல்லாரும் busy.

**இங்கே painful ஆனது என்ன?** Single team-க்குள் fix பண்ண முடியல. Dependency chain-ல ஒரு point-ல தான் root cause இருக்கும். ஆனால் context fragmented ஆகி, communication slow ஆகி, MTTR நீளுது.

## 2. Mental Model

Cross-team coordination என்பது meeting அதிகமாக்குவது இல்லை. 

அது **shared context + clear interface + temporary unified decision making** ஆகும்.

ஒரு incident-ல ஒவ்வொரு team-மும் தன்னுடைய system boundary-க்குள் உண்மையை அறியும். Coordination என்பது அந்த உண்மைகளை ஒரே timeline-ல, ஒரே language-ல இணைப்பது.

Analogy: Surgery team. Surgeon, anesthetist, nurse எல்லாரும் தனித் தனி expertise. ஆனால் patient-க்கு ஒரே plan வேண்டும். அதை drive பண்ண ஒருவர் தேவை.

## 3. How It Works

Incident-ல coordination வேலை செய்ய 4 விஷயங்கள் போதும்.

**1. Incident Commander.** Technical decision-க்கு ஒரே owner. அவர் root cause hunt பண்ணுவது இல்லை, he orchestrates. Who has data? Who can rollback? Who needs info?

**2. Single source of truth channel.** ஒரே Slack/Teams channel. No parallel threads. Status updates, hypothesis, actions எல்லாம் அங்கே.

**3. Service boundaries documented.** அவசரத்தில் யார் என்ன own பண்ணுறாங்க என்பது தெரியணும். `payment-service -> payment-gateway -> db` flow clear ஆக இருக்கணும்.

**4. Pre-agreed interface.** Rollback procedure, feature flag kill switch, escalation path முன்னாடியே தெரிஞ்சிருக்கணும். Incident-ல negotiate பண்ண கூடாது.

## 4. Architectural Reasoning

இது எப்போ useful ஆகும்?

System distributed ஆகும்போது, ownership boundaries அதிகமாகும்போது. Monolith-ல ஒரு team போதும். Microservices + platform + data + infra என்று வளரும்போது coordination overhead வரும்.

Constraint என்ன? **Latency of information.** Incident-ல ஒவ்வொரு minute-க்கும் revenue, reputation cost.

Options:
- **Ad-hoc ping.** Fast ஆ start ஆகும். ஆனால் chaotic. Wrong assumption spread ஆகும்.
- **Formal war room.** Structured. ஆனால் overhead அதிகம். Small issue-க்கு overkill.
- **On-call rotation with clear runbook.** Good for known failure modes.

Architect முடிவு: Severity-க்கு ஏற்ப coordination model மாறும். SEV-1 = commander + war room. SEV-3 = async update.

Decision-ன் consequence: Coordination adds communication overhead. அதை balance பண்ண வேண்டும்.

## 5. Trade-offs

**Speed vs Correctness.** Quick rollback செய்தால் user impact குறையும். ஆனால் root cause mask ஆகலாம். Architect decide பண்ண வேண்டும்: first stabilize, then investigate.

**Centralization vs Autonomy.** Strong commander decision fast. ஆனால் team autonomy குறையும், blame culture வரும்.

**Transparency vs Noise.** All updates in one channel நல்லது. ஆனால் too much chatter decision-ஐ மறைக்கும். Role-based updates வேண்டும்: commander drives, owners report.

Failure mode: Coordination fails when ownership fuzzy. "நாங்க அதை own பண்ணல" என்று ஆரம்பித்தால் incident நீளும். இதை தடுக்க service ownership matrix, SLO, error budget clear ஆக இருக்க வேண்டும்.

## 6. Practical Example

Black Friday sale. Order service 500 errors.

Incident commander announce: `#incident-order-500`.

Timeline:
- T+0: Commander asks each team: last deploy? error rate? dependency health?
- T+5: Payment team says success rate 40%. Gateway team says DB latency p99 2s -> 8s.
- T+7: DB team confirms connection pool exhaustion, recent analytics query spike.
- T+10: Decision: kill analytics job via feature flag, increase pool temporarily.

No debate about who owns DB. Runbook says analytics can be paused without approval in incident.

After fix, post-mortem not blame, but question: why analytics query ran in prod peak? Coordination succeeded because pre-agreed kill switch existed.

## 7. Reasoning Challenge

உங்களிடம் 3 teams உள்ளன: API team, Data platform team, SRE.

காலையில் 9 AM-ல API latency spike. SRE கண்டுபிடித்தது: CPU high on data platform nodes. Data platform சொல்றது: batch job திட்டமிட்டபடி ஓடுது, நாங்க touch பண்ணல. API team சொல்றது: user impact இருக்கு, நாங்க cache increase பண்ணலாம்.

உங்களுக்கு Incident Commander role. முதல் 10 நிமிடத்தில் நீங்கள் என்ன முடிவு எடுப்பீங்க? Kill batch job? Scale API? Wait for data? ஏன்?

## 8. Key Takeaways

- Incident-ல வேகம் வருவது தகவல் தெளிவால், meeting அதிகமாக்குவதால் அல்ல.
- Coordination-க்கு தேவை: single commander, single channel, clear service boundaries.
- ஒவ்வொரு coordination model-க்கும் trade-off உண்டு: speed vs correctness, centralization vs autonomy.
- Pre-agreed interfaces, runbooks, kill switches தான் real coordination. Incident-ல negotiate பண்ணாதீங்க.
