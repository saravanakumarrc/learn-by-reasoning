# Snapshot testing

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.1.5 — Testing strategy

## 1. Problem

ஒரு React component-ஐ refactor பண்ணினீர்கள். Logic-ஐ மாற்றவில்லை, வெறும் internal implementation-ஐ clean பண்ணினீர்கள். ஆனால் அடுத்த deploy-ல் UI-ல் unexpected change வந்துவிட்டது.

இதை catch பண்ண test எழுதினீர்கள் என்றால் என்ன ஆகும்? 
`expect(component).toHaveText('Price: ₹199')` மாதிரி ஒவ்வொரு field-க்கும் assertion எழுதுவீர்கள். Component-ல் ஒரு label மாறினால், அல்லது ஒரு field கூடினால், அல்லது structure மாறினால், test-ஐ update பண்ண வேண்டும்.

பிரச்சனை என்ன? Small change-க்கு test-ஐயும் பெரியதாக பராமரிக்க வேண்டும். மறந்துவிட்டால் regression வந்துவிடும். மிகவும் கவனமாக இல்லாவிட்டால் test-ஐ update பண்ணி அமைதியாக pass ஆக விட்டுவிடுவீர்கள். அப்போ test-க்கு value இல்லை.

இதே பிரச்சனை API response shape-க்கும் உண்டு. ஒரு service ஒரு JSON-ஐ return பண்ணுகிறது. Version மாறும்போது ஒரு field நீக்கப்பட்டதா, type மாறியதா என்பதை எப்படி உறுதி செய்வது?

இந்த pain-தான் snapshot testing-க்கு காரணம்.

## 2. Mental Model

Snapshot testing என்பது **output-ஐ ஒரு முறை capture பண்ணி, அதன் பின் அதே output வருகிறதா என்று compare பண்ணுவது**.

Think of it as a photo of the output. Component render ஆன shape, API response JSON, generated config file, serialized state - எதுவாக இருந்தாலும், அதன் ஒரு frozen copy-ஐ வைத்துக்கொள்ளுங்கள்.

முதல் முறை test run-ல் snapshot create ஆகும். அடுத்த முறை அதே input கொடுத்தால் output மாறாமல் இருக்கிறதா என்று பார்க்கும். மாறினால் test fail ஆகும்.

இது assertion-ஐ எழுதும் workload-ஐ குறைக்கிறது. "என்ன மாறியது?" என்பதை diff-ஆக காட்டும்.

## 3. How It Works

Flow simple:

1. **Render / Execute**: Component-ஐ render பண்ணு அல்லது API handler-ஐ call பண்ணு.
2. **Serialize**: Output-ஐ string / JSON-ஆக மாற்று. React-ல் `react-test-renderer` tree-ஐ serialize பண்ணும்.
3. **Compare**: Serialized string-ஐ முன்பு save பண்ணிய snapshot file-ல் உள்ளதோடு compare பண்ணு.
4. **Update decision**: Match ஆனால் pass. Match இல்லை என்றால் fail. Developer update செய்ய விரும்பினால் `update snapshot` flag உடன் re-run.

Jest இதை default-ஆக செய்கிறது. Snapshot file-கள் `__snapshots__` folder-ல் வைக்கப்படும்.

Important point: Snapshot test input-ஐ மாற்றாமல் output மட்டும் மாறுகிறதா என்று பார்க்கிறது. Business logic test அல்ல.

## 4. Architectural Reasoning

Snapshot testing useful ஆகும் எங்கே?

* **UI component library / design system**: Component-ன் visual structure-ஐ regression இல்லாமல் காப்பாற்ற வேண்டும். Prop combinations அதிகம். ஒவ்வொன்றுக்கும் manual assertion எழுத முடியாது.
* **API contract / serialization shape**: ஒரு service-ன் response schema மாறும்போது downstream break ஆகுமா என்பதை early catch பண்ண.
* **Generated artifacts**: OpenAPI spec, Terraform plan output, codegen output போன்றவை unintentionally மாறாமல் பார்க்க.

Choose பண்ணும் reasoning: Output-ஐ முழுமையாக describe பண்ணுவது கடினம், ஆனால் output மாறினால் அது important ஆக இருக்கும். அப்போது snapshot-ஐ பயன்படுத்தலாம்.

Alternative: Property-based assertion, visual regression testing, contract testing. Snapshot என்பது cheap guardrail, not a replacement.

## 5. Trade-offs

**Safety vs Brittleness.** Snapshot உண்மையான regression-ஐ catch பண்ணும். ஆனால் legitimate change வந்தாலும் test fail ஆகும். Team-கள் `update snapshots` என்று blind-ஆக அழுத்த ஆரம்பித்தால், test-ன் value குறையும்.

**False sense of security.** Snapshot என்பது "output மாறவில்லை" என்பதை மட்டும் சொல்லும். "Output சரியாக உள்ளது" என்பதை சொல்லாது. Bad output-ஐயும் snapshot lock பண்ணலாம்.

**Maintenance cost.** Large repo-ல் snapshot files huge ஆகும். Git diff noisy ஆகும். CI slow ஆகும். Reviewer-கள் snapshot diff-ஐ புரிந்துகொள்ள வேண்டும்.

**Flaky serialization.** Date, UUID, timestamp போன்ற non-deterministic values snapshot-ஐ flaky ஆக்கும். அதை mock / strip பண்ண வேண்டும்.

Failure mode: Developer சோம்பலாக update அடித்த
