# AI Solution Architect Learning Path — இந்த Curriculum ஏன் இப்படி Shape ஆயிருக்கு

## Goal-ஐ திரும்ப சொல்றேன்

இந்த curriculum இருக்குறது **reasoning ability** build பண்றதுக்காக, memorize பண்ண glossary
ஆக இல்ல. நீங்களே சொன்ன வார்த்தையில், target outcome இது:

> "Exact rule நினைவு இல்லன்னாலும், அதுல இருக்கிற forces எனக்கு புரியும். Let me reason
> through the problem."

கீழ இருக்கிற ஒவ்வொரு phase-உம் இந்த test வைச்சு படிக்கணும். ஒரு phase தன் வேலையை
முடிச்சிருச்சுன்னா, அதுல இருக்கிற ஒரு trade-off-ஐ first principles-லேர்ந்து explain பண்ண
முடியும்போது தான், அதுல இருக்கிற topic list-ஐ recite பண்ணும்போது இல்ல.

## ஐந்து stage progression

Product vision-ல இருக்கிற ஐந்து stage-ஆ phases group பண்ணப்பட்டிருக்கு. Boundaries soft-ஆ
இருக்கு, hard gate இல்ல — சில later-numbered phases (Cloud, Security) already Solution-Architect
depth கொண்டிருக்கு, Phase 9-ம் intentional-ஆவே ஒரு short capstone, ஒரு நீண்ட stage இல்ல:

| Stage | Phases |
|---|---|
| Developer | 1-2 |
| Senior Developer | 3-4 |
| Technical Lead | 5-8 |
| Solution Architect | 9 (capstone) |
| AI Solution Architect | 10-25 |

## ஏன் இந்த order

இந்த curriculum-ஐ reorganize பண்ணும்போது மூணு ordering principles apply பண்ணப்பட்டது:

1. **முடிஞ்ச வரைக்கும் forward references இல்ல.** ஒரு topic-க்கு அதோட prerequisites
   இல்லாம அது introduce ஆகாது. Distributed systems (3), data architecture (4)-க்கு முன்னாடி
   வருது, ஏன்னா consistency problems முதலில் databases-ல தெரியுது, ஆனா அது cause ஆவது
   distributed-systems physics-ஆல. Tool calling (14), agents (15)-க்கு முன்னாடி வருது,
   ஏன்னா ஒரு agent structurally ஒரு tool-calling loop தான்.

   ரெண்டு exceptions மட்டும் இருக்கு, அவரவர் phase README-ல flag பண்ணப்பட்டிருக்கு:
   **AI-specific data** (Phase 4-க்குள்ள) மற்றும் **AI security** (Phase 6-க்குள்ள) —
   இவை natural-ஆ அவங்க non-AI siblings கூட சேர்ந்திருக்கிறதால, Phase 10+, Phase 15+-ல
   full-ஆ click ஆகாதுன்னு தெரிஞ்சுக்கூட early-ஆ preview பண்ணப்பட்டிருக்கு. முதல் தடவை
   பாக்கும்போது ஒரு skim-ஆ treat பண்ணுங்க, later ஒரு deliberate second pass plan பண்ணுங்க.

2. **Evaluation, reliability extend பண்ணப்படுது, ஒரே தடவைக்கு bolt-on பண்ணப்படலை.**
   Phase 2, ordinary software-க்கு testing, observability கத்துக்கொடுக்குது; Phase 19
   (LLMOps), Phase 18 (AI Evaluation) அதே reflexes-ஐ AI-specific failure modes-க்கு extend
   பண்ணுது, கடைசில முழு discipline-ஐயும் scratch-லேர்ந்து introduce பண்றதுக்கு பதிலா.
   Cost-க்கும் (Phase 7 → Phase 20), reliability-க்கும் (Phase 7 → Phase 21) இதே pattern.

3. **ரெண்டு system-design capstones், ஒண்ணு இல்ல.** Phase 9, AI involve ஆகாம ஒரு
   traditional system-ஐ end-to-end design பண்ணச் சொல்லுது — Phase 1-8-ஐ actually நீங்க
   internalize பண்ணினீங்கன்னு proof, AI ஒரு extra layer complexity சேர்க்குறதுக்கு முன்னாடி.
   Phase 24, AI-ஓட கூட அதே exercise-ஐ repeat பண்ணுது. Phase 9 கஷ்டமா இருந்தா, Phase 24
   தேவைக்கு மிச்சம் கஷ்டமா இருக்கும்.

## Gaps, honest-ஆ சொல்றேன்

ரெண்டு phases-க்கு (21 — AI Reliability, 24 — AI System Design), ஒரு section-க்கு
(25 — The ultimate learning progression) tracker-ல இன்னும் topics define பண்ணல.
அவங்க README-ல என்ன missing-ன்னு சொல்லியிருக்கு. இந்த curriculum ஒரு living document,
finished document இல்ல — ஒரு topic இல்லன்னா 'தேவை இல்ல'-ன்னு treat பண்ணாம, போகப்போக
extend பண்ணுங்க.

## இந்த READMEs-ஐ எப்படி use பண்றது

ஒவ்வொரு phase folder-க்கும் ஒரு `README.md` இருக்கு — **ஏன் அந்த phase இருக்கு, sequence-ல
அது எங்க sit பண்ணுது, அந்த phase முடிச்ச பிறகு answer பண்ண முடிற ஒரு reasoning question
என்ன**-ன்னு explain பண்ணுது. ஒவ்வொரு section folder-க்கும் ஒரு shorter `README.md` இருக்கு —
அந்த section என்ன cover பண்ணுது, ஏன் அப்படி group பண்ணப்பட்டிருக்குன்னு. Topics ஆரம்பிக்குறதுக்கு
முன்னாடி phase README-ஐ படிங்க — இதுதான் connective tissue, இல்லன்னா இது isolated bits of
information மாதிரி feel ஆகும்.
