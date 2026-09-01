# Parallel agents

> **Learning Path:** Multi-Agent Architecture
> **Section:** 16.1.8 — Learn

### 1. Problem

ஒரு complex task-ஐ ஒரே LLM agent பண்ணும் போது என்ன ஆகும்? 
உதாரணமா, ஒரு customer support ticket வருது. அதுக்கு நீங்க:
- ticket-ஐ classify பண்ணணும்
- relevant past tickets-ஐ retrieve பண்ணணும்
- refund policy-ஐ check பண்ணணும்
- response draft பண்ணணும்
- CRM-ல update பண்ணணும்

ஒரே agent இதையெல்லாம் sequential-ஆ செய்தால் latency அதிகம், ஒரு step fail ஆனால் முழு flow-மே stuck ஆகும். மேலும் ஒரே model context window-ல எல்லா tool call-ஐயும் manage பண்ண முடியாமல் hallucination வரும்.

What goes wrong if we don't have parallel agents? **Slow, brittle, single point of failure.**

### 2. Mental Model

Parallel agents = ஒரு task-ஐ independent sub-tasks-ஆ break பண்ணி, அதை multiple agents-ஐ parallel-ல run பண்ணுவது.

ஒரு orchestra conductor மாதிரி. Conductor overall plan-ஐ வைத்திருப்பார், ஆனால் violins, drums, piano எல்லாம் ஒரே நேரத்தில் வாசிக்கும். ஒன்றை காத்திருக்க வைக்காமல்.

இங்கே **Coordinator agent** plan பண்ணும், **Worker agents** parallel-ல execute பண்ணும்.

### 3. How It Works

1. **Decompose**: Coordinator task-ஐ independent pieces-ஆ பிரிக்கிறது.
2. **Dispatch**: Workers-க்கு sub-tasks assign ஆகிறது. இது fan-out.
3. **Execute in parallel**: ஒவ்வொரு agent தனது tool, RAG, model call செய்கிறது.
4. **Aggregate**: Results வந்தவுடன் Coordinator synthesize செய்து final output உருவாக்குகிறது. இது fan-in.

Key enabler: sub-tasks-க்கு **data dependency இல்லாமல்** இருக்க வேண்டும். A depends on B என்றால் parallel ஆகாது.

### 4. Architectural Reasoning

எப்போது useful?

- **Latency sensitive** tasks where multiple independent lookups தேவை. உதாரணமாக product research: price, reviews, specs, availability - இவை எல்லாம் ஒரே நேரத்தில் fetch பண்ணலாம்.
- **High throughput** batch processing. 1000 documents summarize பண்ணும்போது 10 agents-ஆ divide பண்ணலாம்.
- **Specialization**. ஒரு agent code review, ஒரு agent security scan, ஒரு agent performance analysis - ஒவ்வொருவரும் தனது system prompt / toolset உடன்.

Alternatives:
- **Single agent with sequential tool calls**: Simple, but slow and error prone.
- **Pipeline agents**: Strict order. Good for dependency உள்ள flow.
- **Parallel agents**: Speed and isolation.

ஏன் choose பண்ணுறோம்? Throughput and latency trade-off-க்கு. Coordinator complexity கூடும், ஆனால் wall-clock time குறையும்.

### 5. Trade-offs

**Speed vs Coordination Cost**: Parallel ஆனாலும் Coordinator-க்கு results-ஐ merge பண்ணும் complexity வரும். Conflicting outputs-ஐ resolve பண்ண வேண்டும்.

**Resource cost**: N agents = N times LLM calls. Cost and rate limits increase. Token usage கூடும்.

**Consistency**: Different agents different reasoning style இருந்தால் final answer inconsistent ஆகும். Need clear schema for output aggregation.

**Failure isolation**: ஒரு worker fail ஆனால் மற்றவர்கள் தொடரலாம். ஆனால் partial result-ஐ handle பண்ண வேண்டும். Timeout / retry policy தேவை.

### 6. Practical Example

Enterprise research agent.

User கேட்கிறார்: "Q3-ல எங்கள் top 3 competitors எப்படி pricing மாற்றினார்கள்?"

Coordinator plan:
- Agent A: Competitor X pricing history fetch + analyze
- Agent B: Competitor Y pricing history fetch + analyze
- Agent C: Competitor Z pricing history fetch + analyze

மூன்றும் parallel-ல run ஆகும். ஒவ்வொரு agent தனது RAG pipeline-ஐ use பண்ணி web, internal DB-ல இருந்து data எடுக்கும்.

30 sec-ல மூன்று results வரும். Coordinator அதை synthesize பண்ணி summary + chart தரும்.

இங்கே sequential ஆக இருந்தால் 90 sec. Parallel ஆக 30 sec + overhead.

### 7. Reasoning Challenge

உங்களிடம் ஒரு code review system உள்ளது. ஒவ்வொரு PR-க்கும் நீங்கள் செய்ய வேண்டியது:
1. Code quality check
2. Security vulnerability scan
3. Performance impact estimate
4. Test coverage check

இவை எல்லாம் independent. ஆனால் ஒரே PR-ல இருந்து data எடுக்க வேண்டும். 

இங்கே parallel agents use பண்ணலாமா? ஆமா / இல்லையா? 
அப்படியானால் எப்படி fan-out/fan-in design பண்ணுவீர்கள்? Timeout ஒரு agent 60 sec எடுத்தால் என்ன செய்வீர்கள்? 

*சிந்தியுங்கள். இதுதான் architect ஆக முடிவு எடுக்கும் திறன்.*

### 8. Key Takeaways

- Parallel agents என்பது **independent sub-tasks-ஐ parallel execute பண்ணி latency குறைக்கும்** pattern.
- Coordinator-க்கு decomposition + aggregation பொறுப்பு. Worker-களுக்கு specialization.
- Data dependency இல்லாத இடத்தில் மட்டுமே parallel பயனுள்ளது.
- Speed gain கிடைக்கும், ஆனால் cost, coordination complexity, consistency management அதிகரிக்கும்.
