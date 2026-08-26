# Test doubles: mocks, stubs, fakes

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 2.1.3 — Testing strategy

# Problem

நீங்க ஒரு payment service எழுதுறீங்க. அது `PaymentGateway` API-ஐ call பண்ணி charge செய்யுது. Unit test எழுதும்போது உண்மையான gateway-ஐ call பண்ண முடியுமா?

முடியாது. அது slow, flaky, rate limited, cost ஆகும். Test data create பண்ணணும், network fail ஆகலாம். CI pipeline எல்லா run-க்கும் external call போகக் கூடாது.

இன்னொரு பக்கம், real dependency-ஐ கொண்டு test பண்ணா அது integration test ஆகிடும். நீங்க இப்போ business logic-ஐ தனியாக verify பண்ண முடியாது.

இந்த pain தான் test double-ஐ கண்டுபிடிக்க வச்சது. Real dependency-க்கு பதில், test-க்கு மட்டும் வேலை செய்யும் ஒரு stand-in வேணும்.

# Mental Model

Test double என்பது ஒரு real component-ன் substitute. அதன் interface-ஐ மட்டும் பின்பற்றும், ஆனால் behavior-ஐ நாம் கட்டுப்படுத்த முடியும்.

முக்கியமான மூன்று வகை:

**Stub**: Input கொடுத்தா pre-defined output தரும். "What do you return?" என்பதை மட்டும் கவனிக்கும்.

**Fake**: Real implementation போலவே வேலை செய்யும், ஆனால் lightweight. In-memory database, fake payment gateway போல.

**Mock**: Behavior-ஐ expect பண்ணி verify பண்ணும். "Did you call this method with these arguments, எத்தனை முறை?" என்று check பண்ணும்.

எளிமையாக: Stub = data provider, Fake = working imitation, Mock = behavior verifier.

# How It Works

System Under Test - SUT என்பது நீங்க test பண்ணும் code. அது ஒரு dependency-ஐ use பண்ணுது.

Production-ல: `SUT -> Real PaymentGateway -> Network -> External Service`

Test-ல: `SUT -> Test Double -> No network`

Test double அதே interface-ஐ implement பண்ணும். Test code set up பண்ணும்போது அதன் behavior-ஐ configure பண்ணலாம்.

Stub-ஐ set up பண்ணும்போது: `when paymentGateway.charge() then return success`

Mock-ஐ set up பண்ணும்போது: `expect paymentGateway.charge to be called once with amount=100`

Fake-ஐ set up பண்ணும்போது: in-memory `FakeDatabase` create பண்ணி, CRUD operations உண்மையாக வேலை செய்யும்.

# Architectural Reasoning

Test double-ஐ எப்போ use பண்ணணும்?

**Unit test**-ல SUT-ன் logic மட்டும் isolate பண்ண வேணும். External boundary-ஐ cut பண்ணணும். அப்போ stub/fake/mocks உதவும்.

**Integration test**-ல real dependency-ஐ வேணும். Test double பயன்படாது.

Decision flow:

- Logic correct-ஆ? Business rule, validation, calculation -> Stub/Fake
- Interaction correct-ஆ? Did we call downstream service with right params? -> Mock
- Whole flow work-ஆ? -> Real dependency, integration test

Architect-க்கு முக்கியம்: Test double-ன் usage scope. Over-mocking செய்தால் test உண்மையான contract-ஐ verify பண்ணாது. Under-mocking செய்தால் test flaky ஆகும்.

# Trade-offs

**Speed vs Reality**: Test double fast, deterministic. ஆனால் real behavior-ஐ capture பண்ணாது. Fake database ACID guarantee தராது.

**Isolation vs Integration risk**: Mock உங்க code isolate பண்ணும். ஆனால் interface மாறினால் test break ஆகும், production break ஆகாமல் இருக்கலாம்.

**Maintainability**: Mock heavy tests brittle. Implementation detail-க்கு strongly coupled. Refactor செய்தால் mocks update பண்ண வேண்டும்.

**Cognitive load**: Team எல்லாரும் எந்த double எப்போ use பண்ணணும் என்பதை தெளிவாக புரிஞ்சிருக்கணும். இல்லன்னா test suite confusing ஆகும்.

Failure mode: Mock expect பண்ணினது, SUT மாறி different call pattern பண்ணுது. Test fail ஆகும், ஆனால் production work ஆகும். இது false signal.

# Practical Example

Order service-ல `InventoryService.checkStock()` call பண்ணி order place பண்ணுறீங்க.

Unit test for `OrderService.placeOrder()`:

Stub use பண்ணி:
`inventoryStub.checkStock("item1") -> true`

நீங்க business logic மட்டும் test பண்ணுறீங்க: stock இருந்தா order create ஆகுதா?

Fake use பண்ணி:
`FakeInventory` with in-memory map. Multiple items, stock decrement simulate பண்ணலாம்.

Mock use பண்ணி:
Expect `inventoryService.checkStock` called once with "item1", and `paymentService.charge` called once with correct amount.

இங்கே integration test-ல நீங்க real inventory service-ஐ point பண்ணி, network, latency, error handling test பண்ணுவீங்க. Test double இல்லாமல்.

# Reasoning Challenge

உங்க service 3 downstream dependencies உள்ளது: `UserDB`, `EmailService`, `AnalyticsService`.

`placeOrder` flow: user validate -> email send -> analytics event emit.

இதுல unit test எழுதும்போது எந்த dependency-க்கு stub, fake, mock use பண்ணுவீங்க? ஏன்? எந்த dependency-ஐ real-ஆ விடுவீங்க?

# Key Takeaways

- Test double-ன் நோக்கம் speed, isolation, determinism.
