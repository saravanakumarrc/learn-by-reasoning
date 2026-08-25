# Reserved vs spot instances

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 23.3.1 — Cloud cost / FinOps

## The problem

On-demand cloud compute is priced for flexibility: pay per hour, start and stop instantly. That flexibility is expensive, especially for steady, predictable workloads that run 24/7.

Cloud providers have a different problem: they must build capacity ahead of demand and want predictable utilization. If they can sell you capacity in advance, they can discount it. If you have workloads that can tolerate interruption, they can sell you excess capacity that would otherwise go unused.

Reserved vs Spot is the economic solution to both problems.

## Mental model

Think of capacity as housing.

**Reserved instances = lease.** You commit to a term, 1 or 3 years, for a specific instance type in a specific region. You pay upfront or monthly, get a ~40-70% discount vs on-demand, and the capacity is guaranteed for you.

**Spot instances = hotel overbooking.** The provider has spare capacity. You bid for it at a discount, often 60-90% off on-demand. You can be evicted with short notice when the provider needs the capacity back.

On-demand is the nightly rate with no commitment.

## How it works

**Reserved.** You reserve a specific size and type. You can choose payment model, but you are committing to pay for that capacity regardless of use. Modern offerings like Savings Plans abstract the instance type, giving more flexibility. The discount comes from the commitment.

**Spot.** The provider runs an auction against its spare capacity. Your instances run until price > your max bid or capacity is needed. You get a 2 minute termination notice on AWS, similar on GCP/Azure. No commitment, no guaranteed capacity.

## Architectural reasoning

The decision is not about cost alone, it's about workload tolerance.

Use Reserved when:
* You have a stable baseline that will run for months. Serving, databases, core API tiers.
* Predictability and SLA matter more than marginal cost. You need the instance to exist.

Use Spot when:
* Work is fault-tolerant and interruptible. Batch jobs, CI runners, model training, data processing.
* You can checkpoint, queue work, and scale out. If one node disappears, another picks up.

The architect's pattern is a mix: Reserved for the baseline you can't lose, Spot for the elastic headroom you can lose.

## Trade-offs and failure modes

**Cost vs availability.** Reserved saves money but locks you into instance type/region and term. If demand drops, you still pay. Spot saves money but can disappear at any time.

**Interruption risk.** Spot termination is not a failure, it's a design constraint. Jobs must be idempotent, short, and checkpointed. Stateful services, in-memory caches, and long-running transactions cannot run on Spot.

**Operational complexity.** Spot requires automation: auto-replacement, checkpointing, queue-based work distribution, graceful shutdown on termination notice. Reserved requires capacity planning: right-sizing, term selection, and avoiding over-commitment.

**Hidden cost.** Chasing Spot savings with constant bidding and instance churn can increase engineering time and failure surface. Reserved can become waste if you over-provision.

## Example

An ML platform with two workloads:

* Serving: real-time inference API on GPU. Must be always on, low latency, SLA bound. Runs on Reserved instances with a small on-demand buffer for spikes.
* Training: nightly hyperparameter sweeps and fine-tuning. Jobs take hours, can be checkpointed to S3, and can be retried. Runs on Spot fleet with a fallback to on-demand if Spot capacity is low.

The architecture is cheaper and still reliable because each tier matches its tolerance to the pricing model.

## Reasoning challenge

You have a nightly ETL that must finish by 6am local time, processes 10TB, and can be parallelized across 50 workers. It currently runs on on-demand. Spot prices in your region are usually 70% lower but have had 3 interruptions per month in the last quarter.

Would you move it to Spot? What would you need to change first?

## Key takeaway

* Reserved buys predictable capacity at a discount in exchange for commitment. Use it for baseline, critical workloads.
* Spot buys cheap excess capacity in exchange for interruption risk. Use it for stateless, checkpointable, retryable work.
* Cost optimization is an architecture decision, not a billing setting. Match pricing model to fault tolerance and operational control.
* The best FinOps design is a portfolio: Reserved for the floor, Spot for the elastic ceiling, on-demand for the spikes you can't predict.
