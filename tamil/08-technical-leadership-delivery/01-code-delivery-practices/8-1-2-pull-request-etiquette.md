# Pull request etiquette

> **Learning Path:** Technical Leadership & Delivery
> **Section:** 8.1.2 — Code & delivery practices

## 1. Problem

உங்க team-ல ஒரு developer 3 வாரமா ஒரு feature மேல வேலை பண்ணிட்டு இருக்கார். ஒரே branch-ல, 2,500 lines மாற்றம். Directly PR open பண்ணார்.

Reviewer-க்கு என்ன தெரியும்? எதை மாற்றினார், ஏன் மாற்றினார், எப்படி test பண்ணார் என்பது தெரியாது. Diff-ஐ பார்த்தால் கண் சொருகுது. CI fail ஆகுது. Comments வருது, author fix பண்ணி force push பண்ணுது. 5 நாள் review-க்கு அப்புறம் merge பண்ணும்போது main-ல merge conflict.

இதுவே திரும்ப திரும்ப நடந்தால் என்ன ஆகும்?
Reviewer context switch கொடுக்க மாட்டார். PR stale ஆகும். Main unstable ஆகும். Release delay ஆகும். Team trust குறையும்.

Pull request etiquette என்பது code-ஐ சுத்தமாக எழுதுவது மட்டும் இல்லை. Reviewer-க்கு முடிவெடுக்கும் சுமையை குறைக்கும் ஒரு communication protocol.

## 2. Mental Model

PR-ஐ ஒரு code dump ஆக பார்க்காதீங்க. PR என்பது ஒரு **request for permission to change shared state**.

Main branch என்பது team-ன் shared truth. நீங்க அதை மாற்றுவதற்கு முன், ஒரு reviewer-க்கு மூன்று விஷயங்களை உறுதியாக கொடுக்க வேண்டும்:

1. What changed and why
2. How you verified it is safe
3. What risk remains

இதை சிறிய, தெளிவான story-ஆக சொன்னால் reviewer yes சொல்வார். பெரிய, குழப்பமான dump-ஆக சொன்னால் reviewer block பண்ணுவார்.

## 3. How It Works

நல்ல PR etiquette என்பது ஒரு flow:

`feature branch -> small commits -> push -> PR open -> description + tests -> CI green -> review -> small iterations -> merge`

Key behaviors:
* **Branch per concern.** ஒரு PR-க்கு ஒரே logical change.
* **Description first.** Title clear, summary short, why needed, how to test.
* **Self review.** நீங்க தான் முதல் reviewer. Diff-ஐ உங்க கண்ணால் ஒரு முறை பார்க்கவும்.
* **Green CI before review request.** Flaky test-ஐ reviewer மேல தள்ளாதீங்க.
* **Respond fast.** Review comment வந்த 24 மணி நேரத்துக்குள் reply / fix.

## 4. Architectural Reasoning

ஏன் small PR?

Constraints உண்மையானவை: reviewer-க்கு limited cognitive budget, context switch cost உயர்ந்தது, main-ன் stability critical.

Options:
* Large PR: less overhead of creating PRs, context retained.
* Small PR: higher overhead, but faster review, less risk.

Architect ஆக நீங்க தேர்வு பண்ணுவது என்ன? Review-ன் throughput-ஐ maximize பண்ண வேண்டும். Review time பெரும்பாலும் PR size-க்கு proportional. 200 lines PR ஒன்றுக்கு 20 நிமிடம் review பண்ணலாம். 2000 lines PR ஒன்றுக்கு 4 மணி நேரம் ஆகும், அதுவும் incomplete.

ஆக small PR = higher review velocity, lower defect escape rate.

## 5. Trade-offs

* **Size vs completeness.** ஒரு feature ஐ பிரிக்கும் போது intermediate state broken ஆகலாம். Feature flag அல்லது WIP branch உபயோகித்து அதை manage பண்ணுங்க.
* **Speed vs thoroughness.** Hotfix-க்கு fast merge வேண்டும். அதற்கு fast track review process வேண்டும், அதை bypass பண்ணி etiquette குறைக்கக்கூடாது.
* **Automation vs human review.** CI checks, lint, unit tests பல விஷயங்களை catch பண்ணும். ஆனால் design trade-off, business logic, coupling போன்றவற்றை human தான் பார்க்க முடியும். PR description-ஐ மோசமாக எழுதினால் human review value குறையும்.
* **Failure mode.** Stale PR. 2 வாரம் review இல்லாமல் இருந்தால் base branch மாறி போய் merge conflict mountain ஆகும். அதை தவிர்க்க frequent rebase / keep PR small.

## 6. Practical Example

Payment service-ல refund flow மாற்றம் தேவை. Developer இதை மூன்று PR-ஆக பிரித்தார்:

1. `Add refund_reason field to DB and API` - migration + tests, no behavior change.
2. `Backend validation and service logic for refund_reason` - unit tests + integration tests.
3. `Update UI form and docs` - frontend change.

ஒவ்வொரு PR-க்கும் description-ல்: problem statement, linked ticket, test steps, rollback plan.

Reviewer 30 நிமிடத்தில் approve பண்ணினார். CI green. Merge conflict இல்லை. Production deploy safe.

ஒரே PR-ஆக வந்திருந்தால
