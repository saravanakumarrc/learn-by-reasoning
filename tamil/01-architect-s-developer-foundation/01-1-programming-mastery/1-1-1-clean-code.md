# Clean code

> **Learning Path:** Architect's Developer Foundation
> **Section:** 1.1.1 — 1. Programming mastery

### 1. Problem

நீங்க ஒரு team-ல 2 வருஷம் பழைய codebase-ஐ touch பண்ணும்போது நடக்கும் வலி நினைவிருக்கா?

ஒரு simple bug fix செய்யணும். File open பண்ணீங்க. 400 lines ஆன function. Variable names `data`, `temp`, `x`. Comments இல்லை. அடுத்த function-க்குள்ள இன்னொரு function call, அது இன்னொரு module-க்குள்ள போகுது. என்ன பண்றதுன்னு புரியாம 2 மணி நேரம் trace பண்ணிட்டு இருக்கீங்க. 

Feature add பண்ணணும்னா, எங்க மாற்றணும் என்பதே தெரியல. ஒரு change பண்ணினா வேற இடத்துல break ஆகுது. Code review-ல எல்லாரும் "இது என்ன பண்றது?"ன்னு கேக்குறாங்க. 

இதுக்கு காரணம் code work ஆகுது, ஆனா *understand ஆகல*. 

இந்த வலி தான் clean code தேவைப்படுத்தியது.

### 2. Mental Model

Clean code என்பது pretty formatting இல்லை. இது **cognitive load-ஐ குறைக்கறது**.

Code எழுதுறதை விட, code-ஐ படிக்கறது 10x அதிகம். அடுத்த வருஷம் நீங்களே இதை திரும்ப படிக்கும்போது, அல்லது வேற engineer படிக்கும்போது, intent உடனே தெரியணும்.

Mental model simple:
> Code should read like a spec, not a puzzle.

ஒரு function-ஐ பார்த்ததுமே, *என்ன பண்றது, ஏன் பண்றது, எப்படி fail ஆகும்* என்பது தெரியணும்.

### 3. How It Works

இதுக்கு ஒரு magic formula இல்லை. சில reasoning principles தான்.

**Name matters.** `process()` vs `processRefund()`. முதல் name-ல intent இல்லை. இரண்டாவது உடனே domain-ஐ சொல்லுது.

**Small and focused.** ஒரு function ஒரே வேலை பார்க்கணும். `getUser`, `validateUser`, `saveUser` என்று பிரிந்தால், அவற்றை test பண்ணலாம், reuse பண்ணலாம். 200 line monster function-ல ஒரு bug fix பண்ணினால் side effect தெரியாது.

**Boundaries clear ஆக இருக்கணும்.** ஒரு module என்ன responsibility எடுத்துக்குது என்பது தெளிவா இருக்கணும். `PaymentService` database access, validation, notification எல்லாம் சேர்த்து பண்ணக்கூடாது. அது hidden coupling உருவாக்கும்.

**Error and edge case explicit ஆக இருக்கணும்.** Silent fail, magic boolean return எல்லாம் பிறகு production-ல வெடிக்கும். Fail fast, fail loud.

இது எல்லாம் syntax rule இல்லை. இது communication rule.

### 4. Architectural Reasoning

Clean code என்பது individual developer style issue இல்லை. இது architectural leverage.

எப்போது critical ஆகும்?
* Team size > 1, especially remote/async
* Codebase lifetime > 6 months
* System-ல change rate அதிகம்

அப்போது code என்பது *artifact* இல்லை. இது *interface* between engineers across time.

Alternative என்ன? Workable but unreadable code. அது short term-ல வேகமா தெரியும். Long term-ல change cost exponential ஆகும்.

Architect ஆக நீங்க choose பண்ணுவது:
* Naming conventions consistent ஆ?
* Function size bounded ஆ?
* Module boundaries domain-ஐ reflect பண்ணுதா?

இது coding standard enforcement இல்லை. இது change cost-ஐ control பண்ணற decision.

### 5. Trade-offs

Clean code-க்கு விலை இருக்கு.

**Time now vs time later.** Clean ஆக எழுதுவது initial implementation-ஐ slow பண்ணும். ஆனா 3rd change-ல ROI தெரியும்.

**Simplicity vs Abstraction.** Over-abstraction வேற வலி. `AbstractFactoryProvider` போட்டு simple logic-ஐ மறைக்கக் கூடாது. Abstraction தேவைப்படும் complexity வந்த பிறகு தான்.

**Consistency vs Local optimum.** ஒரு file-ல நீங்க perfect clean code எழுதினாலும், rest of codebase அப்படி இல்லைன்னா, integration painful ஆகும். Team level convention முக்கியம்.

Failure mode: Clean code என்ற பெயரில் premature refactoring. Feature still unstable, requirements changing daily. அப்போது over-cleaning waste.

### 6. Practical Example

Payment refund flow.

Bad:
```python
def proc(d):
    if d['s'] == 'ok':
        x = db.get(d['id'])
        if x:
            x['a'] -= d['v']
            db.save(x)
            return True
```

இதை படிச்சவன் என்ன நடக்குதுன்னு யூகிக்கணும்.

Clean:
```python
def process_refund(order_id, amount):
    order = get_order(order_id)
    if not order.is_payable():
        raise InvalidRefund()
    
    order.apply_refund(amount)
    save_order(order)
    emit_refund_event(order_id)
```

இப்போ intent clear. Testable. `apply_refund` என்ற business rule ஒரே இடத்துல இருக்கு. ஒரு வருஷம் கழிச்சு வந்தவனுக்கு எங்க மாற்றணும்னு தெரியும்.

இது working code இல்லை. இது *maintainable system*.

### 7. Reasoning Challenge

உங்க team-ல ஒரு legacy `UserService` இருக்கு. அது 1500 lines. Authentication, profile update, email sending,
