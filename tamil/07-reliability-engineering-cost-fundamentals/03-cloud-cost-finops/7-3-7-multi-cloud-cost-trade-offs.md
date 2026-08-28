# Multi-cloud cost trade-offs

> **Learning Path:** Reliability Engineering & Cost Fundamentals
> **Section:** 7.3.7 — Cloud cost / FinOps

## 1. Problem

உங்கள் company ஒரே cloud-ல, சொல்லுங்க AWS-ல மட்டும் 3 வருஷமா ஓடுது. Engineering-க்கு வேலை நல்லா போகுது. ஆனா Finance team கிட்ட இருந்து மெயில் வருது: "இந்த quarter bill 40% அதிகம். எதுக்கு?"

நீங்க பார்த்தா:
- Data transfer bill அதிகரிச்சிருக்கு, egress cost தான் killer.
- On-demand compute-ல 24/7 ஓடுற workloads-க்கு overpay பண்றீங்க.
- ஒரு region-ல price hike வந்ததும் எதுவும் பண்ண முடியல. Vendor-ஐ மாற்ற முடியாது.
- Spot instance இல்ல, reserved capacity இல்லன்னா cost unpredictable ஆகுது.

இப்போ "multi-cloud use பண்ணினா செலவு குறையுமா?"ன்னு கேள்வி வருது. ஆனா உண்மையிலேயே multi-cloud என்பது free saving இல்லை. அது ஒரு trade-off.

**What problem painful enough?** Single cloud-ல cost lock-in, pricing powerless, data gravity, egress tax. Cost optimize பண்ணணும் ஆனா complexity அதிகமாகும்.

## 2. Mental Model

Cloud cost-ஐ ஒரு electricity tariff மாதிரி பாருங்க. ஒரே provider-கிட்ட நீங்க 24/7 peak rate-க்கு வாங்குறீங்க. ஆனா வேற provider-கிட்ட off-peak rate, cheaper renewable, வேற region-ல tariff குறைவு இருக்கலாம்.

Multi-cloud cost trade-off என்பது:
**Workload-ஐ right cloud, right region, right pricing model-க்கு move பண்ணி செலவு குறைக்கலாம். ஆனா அதுக்கு data movement, operational complexity, tooling cost அதிகரிக்கும்.**

Cost arbitrage உண்மையானது. ஆனா அது free இல்லை.

## 3. How It Works

Cost trade-off practical-ஆ மூன்று இடத்துல வரும்:

**1. Workload placement by price/performance**
Compute intensive batch jobs-ஐ spot/preemptible instances உள்ள cloud-ல வைக்கலாம். Storage-heavy cold data-ஐ cheaper object storage உள்ள provider-க்கு move பண்ணலாம். AI training-க்கு GPU price வெவ்வேறு cloud-ல வெவ்வேறு.

**2. Data locality & egress avoidance**
Users Europe-ல இருந்தா, EU region compute வச்சா latency குறையும், transfer cost குறையும். Multi-cloud என்பது data-ஐ அருகில் வைக்கும்.

**3. Contract & commitment arbitrage**
Reserved instances, savings plans, committed use discounts ஒரு cloud-ல lock பண்ணிட்டா, மற்ற cloud-ல on-demand use பண்ணி peak-ஐ balance பண்ணலாம்.

Implementation-ல FinOps team cost visibility, tagging, showback முதலில் செய்யும். பிறகு workload classification: **price-sensitive, latency-sensitive, data-sensitive**.

## 4. Architectural Reasoning

Multi-cloud for cost useful ஆகும் போது:

- **Workload தனித்து இருக்கும்.** Stateless batch jobs, analytics, ML training போன்றவை எளிதாக move ஆகும்.
- **Egress cost உங்கள் bill-ல பெரும் பங்கு.** Cross-region transfer விலை $0.08/GB இருக்கும் போது, data-ஐ அருகில் வைப்பது செலவு குறைக்கும்.
- **Pricing volatility உள்ளது.** ஒரு cloud-ல GPU price hike ஆனால், மற்ற cloud-ல run பண்ண முடியும்.

Choose பண்ணாதீங்க போது:

- **Tight coupling, low latency.** Service mesh-ல microservices ஒன்னோட ஒன்னு 1ms-க்குள் பேசணும். Multi-cloud network latency அதிகம்.
- **Data gravity.** 50TB database-ஐ மாற்றுவது transfer cost + downtime = சேமிப்பை விட அதிகம்.
- **Team size சிறியது.** Multi-cloud ops overhead-ஐ handle பண்ண மனிதர் இல்லை.

## 5. Trade-offs

**Saving vs Complexity.** 
Multi-cloud உண்மையிலேயே 10-20% saving கொடுக்கும். ஆனா monitoring, CI/CD, IAM, networking, cost attribution-ஐ இரண்டு மூன்று platform-ல synchronize பண்ணணும். Team cognitive load அதிகரிக்கும்.

**Egress cost vs Availability.**
Cloud A-ல compute, Cloud B-ல storage வைத்தால் saving தெரியும். ஆனா cross-cloud data transfer-ல latency + egress bill திரும்ப வந்து கடிக்கும். Data gravity என்பது உண்மையான செலவு.

**Standardization vs Optimization.**
Cost optimize பண்ண ஒவ்வொரு workload-க்கும் வெவ்வேறு cloud. இது FinOps tooling, Terraform modules, observability-ஐ fragment
