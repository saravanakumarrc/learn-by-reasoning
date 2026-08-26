# Test data management

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.1.9 — Testing strategy

## 1. Problem

உங்க team-ல microservices இருக்கு. Integration test ஓடனும். CI pipeline ஒவ்வொரு PR-க்கும் ஓடணும்.

இப்போ என்ன பண்றீங்க? Production DB-ல இருந்து ஒரு dump எடுத்து staging-க்கு restore பண்றீங்க.

அப்புறம் என்ன ஆகுது?

* Tests flaky ஆகுது. ஒரு test ஒரு row-ஐ expect பண்ணுது, மறுநாள் data மாறியிருக்கு.
* Data size பெருசு. Restore எடுக்க 40 நிமிஷம். CI slow ஆகுது.
* PII leak ஆகும் risk. Customer name, PAN, phone எல்லாம் test logs-ல வந்துடுது. GDPR audit-ல பிரச்சனை.
* ஒரு developer local-ல run பண்ணும்போது அவனுக்கு தேவையான data மட்டும் இல்ல, முழு prod clone வேணும்.

Test data-ஐ manage பண்ணாம விட்டா, test reliability, speed, compliance மூணும் போயிடும்.

## 2. Mental Model

Test data management = **test data-ஐ product மாதிரி treat பண்ணுவது**.

Production data copy அல்ல. நீங்கள் control பண்ணும், version பண்ணும், reproducible ஆக்கும் ஒரு dataset.

Core idea: **ஒரு test-க்கு தேவையான minimal, deterministic data மட்டும், right shape-ல, right isolation-ல**.

Realism vs Safety trade-off-ஐ manage பண்ணுவது தான் வேலை.

## 3. How It Works

நடைமுறையில் 3 layer வரும்.

**Data classification & masking**
Prod data-வை எடுக்கும்போது PII fields-ஐ mask/anonymize பண்ணு. Name → `User_1234`, Email → `user1234@test.local`. Referential integrity காக்கணும்.

**Synthetic data generation**
Real data distribution-ஐ பார்த்து fake data generate பண்ணு. Faker libraries, data factories. `account_balance` realistic range-ல இருக்கணும், ஆனா real customer இல்ல.

**Data as code**
Seed scripts, fixtures, data factories-ஐ git-ல வை. Test setup-ல `db.seed()` பண்ணும்போது ஒரே data எப்போவும் கிடைக்கும். Environment-க்கு தகுந்த dataset.

ஒரு simple flow:

```mermaid
graph LR
Prod[(Prod DB)] --> Mask[Masking / Anonymization]
Synth --> Synthetic Generator
Mask --> TestEnv[Test Environments]
Synth --> TestEnv
TestEnv --> CI/CD
```

Data lifecycle-உம் இருக்கு: create → use → destroy. Test run முடிஞ்சதும் data clean பண்ணனும்.

## 4. Architectural Reasoning

இது useful ஆகும் போது:

* Compliance constraint இருக்கும் போது. PII ஐ test env-க்கு கொண்டு போக முடியாது.
* Test isolation வேணும் போது. ஒரு test மற்றொரு test-ஐ affect பண்ணக்கூடாது.
* Speed வேணும் போது. Small deterministic dataset = fast CI.

Alternatives:
* **Prod clone + manual mask** - realistic ஆனா maintenance costly, human error.
* **Fully synthetic** - safe, fast ஆனா edge cases miss ஆகலாம்.
* **Golden datasets** - curated small set, versioned. பல team-க்கும் common.

Architect எப்போ எதை தேர்வு பண்ணுவார்?
Low risk domain, e.g. catalog service → synthetic போதும்.
High risk domain, e.g. fraud detection → masked prod sample + synthetic mix.

Decision driver: **risk, realism need, cost to maintain**.

## 5. Trade-offs

**Realism vs Privacy**
Real data realistic bugs காட்டும். ஆனா privacy breach risk. Masking பண்ணினாலும் correlation attack வரலாம்.

**Maintenance vs Reproducibility**
Data as code எழுதுவது initial effort அதிகம். ஆனா flaky test குறையும். Prod dump எளிது, ஆனா unstable.

**Shared vs Per-team data**
Central test data service கொடுத்தால் consistency வரும். ஆனா bottleneck ஆகும், change slow ஆகும். Team own data-ஐ create பண்ணினால் autonomy வரும், divergence வரும்.

Failure mode: Masking incomplete ஆகி real PII test logs-ல leak ஆகுது. அல்லது synthetic data too clean ஆகி production edge cases catch ஆகாம போகுது.

## 6. Practical Example

Banking app. Accounts, transactions, KYC.

Integration test-ல fraud rule test பண்ணணும். `amount > 50000 and new_device and night_time`.

Prod data copy use பண்ண முடியாது. PAN, phone leak ஆகும்.

Solution: 
1. Prod-ல இருந்து schema மட்டும் எடு.
2. Data factory use பண்ணி 200 synthetic accounts generate பண்ணு. Distribution: 70% normal, 20% suspicious pattern, 10% edge.
3. Seed script-ஐ git-ல வை. CI ஓடும்போது fresh DB create பண்ணி seed பண்ணு.
4. Test data version 1.2 tag பண்ணு. Fraud rule மாற
