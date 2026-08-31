# Resources

> **Learning Path:** Tool Calling & AI Interfaces
> **Section:** 14.2.4 — MCP

## 1. Problem

ஒரு LLM agent-க்கு external world-ஐ access பண்ணணும். Tools மூலம் function call பண்ணலாம். ஆனால் agent-க்கு context தேவைப்படும்போது என்ன செய்வது?

உதாரணமா, user கேட்கிறார்: "என்னுடைய கடந்த வார sales report-ஐ காட்டு". Agent-க்கு அந்த report எங்கே இருக்கு தெரியாது. File path தெரியாது. Database schema தெரியாது.

Tool calling என்பது action. Resources என்பது data access. 

MCP-ல் ஒரு LLM ஒரு server-உடன் connect ஆகும்போது, அந்த server என்ன tools கொடுக்கிறது, என்ன resources expose பண்ணுகிறது என்பதை discover பண்ண முடியும்.

Resources என்பது agent-க்கு read-only access கொடுக்கும் URLs / data handles. இது file, database row, API endpoint, memory snapshot போன்றவையாக இருக்கலாம்.

**Problem ஆகிறது:** Agent எப்போது, எந்த resource-ஐ read பண்ண வேண்டும் என்று முடிவு செய்ய, அது அந்த resource-இன் existence மற்றும் schema பற்றி தெரிந்திருக்க வேண்டும். மேலும் resource list dynamically மாறும்.

## 2. Mental Model

MCP Resources = Agent-க்கான **readable references**.

Tool = "இதை செய்".
Resource = "இதை பார்".

ஒரு library catalog போல நினைக்கலாம். Tools என்பது librarian-கள் புத்தகத்தை கொண்டு வந்து தருவார்கள். Resources என்பது catalog-ல் இருக்கும் book references. Agent முதலில் catalog-ஐ list பண்ணி, எந்த book தேவை என்று தேர்வு செய்கிறது.

MCP server ஒரு Resource Template கொடுக்கலாம்: `file://reports/{date}.pdf`. Agent இதை expand செய்து concrete URI-ஐ read பண்ணலாம்.

## 3. How It Works

MCP protocol-ல் server initialization-ல் இது list ஆக வரும்:

`resources` - static list of URIs
`resource_templates` - parameterized URIs

Agent இதை discover பண்ணி `resources/list` call பண்ணும். பிறகு `resources/read` மூலம் specific URI-ஐ fetch பண்ணும்.

Server side-ல் resource என்பது URI + MIME type + optional description. Agent client அதை fetch செய்து content-ஐ LLM context-ல் inject செய்யும்.

Important point: Resource content என்பது tool output-ஐ போல structured அல்ல. இது raw data. Agent அதை படித்து reasoning செய்யும்.

## 4. Architectural Reasoning

எப்போது Resources தேவை?

* Agent-க்கு large, read-heavy context தேவைப்படும்போது. உதாரணம்: company docs, knowledge base, user files.
* Real-time data snapshot தேவைப்படும்போது. Dashboard metrics, current inventory.
* User-ன் personal data எப்போதும் accessible ஆக இருக்க வேண்டும்.

Tool calling vs Resource reading:

Tool = action with side effects, parameters, validation.
Resource = idempotent read, no side effects.

ஒரு architect ஏன் Resources-ஐ expose பண்ணுவார்?

1. **Discovery**: Agent தானாகவே available data-ஐ கண்டுபிடிக்க முடியும். Hardcoding பண்ண தேவை இல்லை.
2. **Caching**: Resource content-ஐ client cache பண்ணலாம். Tool call எப்போதும் fresh.
3. **Security boundary**: Read-only access கொடுக்கலாம். Agent எதையும் மாற்ற முடியாது.

Alternatives: Agent-க்கு direct file system access, vector database query tool. ஆனால் அது tight coupling. MCP Resources decoupling கொடுக்கிறது.

## 5. Trade-offs

**1. Context size vs latency**
Resource content பெரியதாக இருந்தால் LLM context window-ஐ fill பண்ணும். Agent எல்லாவற்றையும் read பண்ணாமல் relevant portion மட்டும் read பண்ண வேண்டும். இதற்கு resource templates + filtering தேவை.

**2. Freshness vs cache**
Resource-ஐ poll பண்ணுவது expensive. Server `resource_updated` notification கொடுக்கலாம். ஆனால் அது complexity add பண்ணும்.

**3. Security & privacy**
Agent-க்கு read access கொடுப்பது என்பது sensitive data leak ஆகலாம். URI scheme, access control, tenant isolation முக்கியம். `file:///etc/passwd` போன்ற open access கொடுக்கக்கூடாது.

**4. Schema ambiguity**
Resource என்பது raw bytes. Agent-க்கு அது JSON-ஆ, PDF-ஆ, CSV-ஆ என்று தெரிய வேண்டும். MIME type மற்றும் description தெளிவாக இருக்க வேண்டும். இல்லையெனில் agent hallucinate செய்யும்.

Failure mode: Agent தவறான resource-ஐ read பண்ணி தவறான conclusion எடுக்கும். Resource list மிகப்பெரியதாக இருந்தால் agent overwhelmed ஆகும்.

## 6. Practical Example

Enterprise RAG setup:

MCP server `company-docs` expose பண்ணுகிறது:

* `resource://docs/handbook` - MIME: text/markdown
* `resource_template://docs/tickets/{id}` - MIME: application/json

User கேட்கிறார்: "நான் last sprint-ல raise பண்ணிய ticket-ஐ காட்டு".

Agent முதலில் `resources/list` பண்ணி templates-ஐ பார்க்கும். அது ticket resource template இருப்பதை காணும். User profile resource-ல் last sprint tickets list-ஐ படிக்கும். அதிலிருந்து ticket id-ஐ extract செய்து `resource://docs/tickets/12345` ஐ read பண்ணும்.

Tool இல்லாமல் resource மூலம் agent தானாகவே data fetch பண்ணி reasoning செய்யும்.

## 7. Reasoning Challenge

உங்களிடம் ஒரு MCP server இருக்கிறது. அது 10,000 user files-ஐ resources ஆக expose பண்ணுகிறது. Agent ஒரு query-க்கு எல்லா files-ஐயும் list பண்ணி read பண்ண முயற்சிக்கிறது. Context window overflow ஆகிறது, latency அதிகமாகிறது.

இங்கே architect ஆக நீங்கள் என்ன செய்வீர்கள்? Resources-ஐ எப்படி design பண்ணுவீர்கள்? Tool-ஐ use பண்ண வேண்டுமா, resource template-ஐ மாற்ற வேண்டுமா?

## 8. Key Takeaways

* Resources என்பது MCP-ல் read-only data access. Tools என்பது actions.
* Agent discovery மூலம் dynamic resource list-ஐ பயன்படுத்தி context-ஐ build செய்யும்.
* Resource templates மூலம் parameterized data access சாத்தியம்.
* Read access கொடுக்கும்போது security, freshness, context size trade-off-ஐ manage பண்ண வேண்டும்.
* Architecture-ல் Resources = data boundary, Tools = action boundary.

இது ஏன் தேவை என்று புரிந்தால், agent-க்கு data எப்போது expose பண்ண வேண்டும், எப்போது tool-ஆக wrap பண்ண வேண்டும் என்பதை நீங்கள் தேர்வு செய்ய முடியும்.
