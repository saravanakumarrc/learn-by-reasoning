# Planner

> **Learning Path:** Agentic AI
> **Section:** 11.2.2 — Agent patterns

**Planner**

### 1. The problem

LLMs are good at one-step reasoning, bad at reliable multi-step execution.

Give a model: "Onboard a new enterprise customer, provision resources, run compliance check, send welcome kit." It will often hallucinate steps, skip dependencies, or get lost mid-way. The problem isn't intelligence, it's lack of persistent structure.

Constraints that force a solution:
* **Goal → steps gap.** High-level intent must be decomposed into tool calls with ordering and dependencies.
* **Context limits.** Long tasks exceed context, so the model forgets earlier decisions.
* **Error recovery.** One tool fails, the whole chain collapses without replanning.
* **Observability.** You need an auditable plan, not hidden chain-of-thought.

### 2. Mental model

Planner = strategist, not executor.

It takes a goal and produces an explicit plan: a sequence or DAG of sub-tasks with preconditions, tools, and expected outputs. Execution is separate and feeds results back to the planner for monitoring and replanning.

Analogy: project manager writes the Gantt chart, engineers execute tasks and report blockers. The manager updates the plan.

### 3. How it works

```
flowchart LR
    Goal --> Planner[Generate Plan]
    Planner --> Plan[Steps + Dependencies]
    Plan --> Executor[Execute Step N]
    Executor --> Result
    Result --> Monitor{Success?}
    Monitor -->|Yes| NextStep
    Monitor -->|No / Drift| Planner
    NextStep --> Executor
```

Essential loop:
1. **Decompose.** Planner outputs structured plan, e.g. JSON with steps, inputs/outputs, tool needed.
2. **Validate.** Light validator checks plan completeness, required parameters, dependency cycles.
3. **Execute.** Executor runs one step with tool use, returns observation.
4. **Monitor & Replan.** If step fails, output is unexpected, or goal state changes, planner revises remaining steps.

The plan is explicit and inspectable, not buried in CoT.

### 4. Architectural reasoning

**When it helps**
* Multi-step tasks with dependencies: research → synthesize → act.
* Tasks needing different tools or agents per step.
* Need for auditability and human-in-the-loop approval of plan.
* Long horizons where replanning is cheaper than failing silently.

**Alternatives**
* ReAct / Chain-of-Thought: interleaves reasoning and acting per step. Good for short, exploratory tasks, bad for complex ordering.
* Reflexion: improves via self-critique after execution, but still lacks upfront structure.
* Single-shot prompting: cheapest, most brittle.

Choose Planner when the cost of a wrong step > cost of planning overhead. Choose ReAct when the task is open-ended and you want the model to discover steps.

### 5. Trade-offs and failure modes

* **Plan brittleness.** LLM hallucinates non-existent tools or impossible preconditions. Mitigate with tool registry grounding and schema validation.
* **Over-planning.** Planner spends tokens generating a perfect plan for a simple task. Keep plan granularity at the right level; allow dynamic refinement.
* **Plan drift.** World changes during execution. Without monitoring, plan becomes stale. You need a feedback loop, not one-shot planning.
* **Latency and cost.** Planning + validation + execution is more expensive. Budget for it.
* **Separation complexity.** Planner-executor split adds orchestration. You need state management for plan, context, and partial results.

### 6. Example

Enterprise customer onboarding.

Goal: "Onboard Acme Corp, tier Gold."

Planner generates:
1. Verify contract signed → CRM lookup
2. Provision tenant in multi-tenant platform → infra tool
3. Run compliance questionnaire → form tool, requires step 1
4. Create billing profile → billing API, requires step 1
5. Send welcome kit → email tool, requires 2,3,4

Executor runs step 1, succeeds. Step 2 fails due to quota. Monitor triggers replanning: add "request quota increase" before retry. Plan updates, execution continues.

Without planner, model might provision before contract verification, or forget billing.

### 7. Reasoning challenge

You are building an AI agent to triage support tickets and resolve them.

Option A: ReAct loop that reads ticket, picks a tool, acts, repeats until done.
Option B: Planner that first creates a plan with steps, then executes with replanning on failure.

Ticket volume is high, 80% are simple password resets. 20% are multi-step escalations requiring human approval mid-flow.

Which pattern do you use, and where would you draw the boundary between planner and direct execution?

### 8. Key takeaway

* Planner exists to make multi-step goals explicit, orderable, and auditable.
* Separate planning from execution to enable validation, monitoring, and replanning.
* Use it when dependencies, tool diversity, and failure recovery matter more than raw latency.
* The biggest risks are hallucinated steps and stale plans; ground plans and close the feedback loop.
* Architectural decision: Planner buys reliability and observability at the cost of complexity and tokens.
