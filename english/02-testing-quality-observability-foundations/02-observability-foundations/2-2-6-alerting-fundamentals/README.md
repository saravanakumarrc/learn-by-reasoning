# Alerting fundamentals

> **Learning Path:** Testing, Quality & Observability Foundations
> **Section:** 22.2.6 — Observability foundations

### The problem

You have observability: metrics, logs, traces. You can see what happened after it happens. The problem is you don't want to be looking at dashboards all day, and you don't want to find out about an outage from customers.

You need a mechanism that converts a changing system state into a timely, actionable human response. Without it, detection latency is bounded by how often someone happens to look, and response is random.

Constraints that shape alerting:
* **Signal must be rare and important.** You can't alert on every anomaly.
* **Latency matters.** The alert must fire before damage grows.
* **Actionability.** If a human gets paged, they must be able to do something meaningful now.
* **Noise kills trust.** False positives train people to ignore alerts.

### Mental model

An alert is not a metric. It is a contract: *if this condition is true for long enough, a human must be interrupted*.

Think of it as a closed loop:
`Symptom → Detection → Decision → Notification → Action → Verification`

The goal is not more information. The goal is reducing time to *corrective action* for a small set of failure modes that matter.

### How it works

At its core, alerting is periodic evaluation of a condition over a time window.

```
Metrics/Logs/Traces → Rule Evaluator → Alert Manager → Routing/Dedup → Notification → Human
```

The evaluator runs on a pull or push interval. A rule is: `expression, for: duration, labels`. Example: `rate(http_errors[5m]) > 0.05 for 2m`.

If the condition holds for the full `for` duration, the alert fires. The `for` clause is critical: it filters transient spikes.

The Alert Manager then handles:
* **Deduplication and grouping.** One alert per incident, not per replica.
* **Routing.** Who gets paged now vs who gets a Slack tomorrow.
* **State management.** Firing, pending, resolved. Resolved alerts close the loop.
* **Inhibition.** Suppress downstream alerts when root cause is known.

### Architectural reasoning

When it helps:
* SLO violations that require immediate remediation.
* Safety or security conditions: data loss, auth failures, money moving incorrectly.
* Availability: service down, critical dependency failing.

What problem it solves vs dashboards/logs:
* Dashboards are for exploration. Alerts are for intervention.
* Logs are for forensics. Alerts are for prevention.

Alternatives and when to choose them:
* **On-call dashboards / SLO dashboards.** Use when you need human judgment, not automation. Good for ambiguous conditions.
* **Automated remediation.** Auto-scale, circuit break, self-heal. Use when action is safe and deterministic. Alert only if automation fails.
* **Anomaly detection.** Useful for unknown unknowns, but high false positive rate. Needs tuning and human-in-the-loop before paging.

Decision rule: alert only if the condition is *actionable now by an on-call engineer*, and the cost of missing it exceeds the cost of paging.

### Trade-offs and failure modes

* **Alert fatigue vs missed incidents.** More alerts = more noise = ignored pages. Fewer alerts = blind spots. The real metric is signal-to-noise ratio, not alert count.
* **Sensitivity vs stability.** Short `for` and low thresholds catch fast but flap. Long `for` and high thresholds are stable but late. You trade detection latency for false positives.
* **Granularity.** Per-instance alerts are precise but noisy. Aggregated alerts are quiet but can hide partial outages.
* **Flapping and thundering herd.** A flapping alert causes repeated pages. Grouping and inhibition prevent it.
* **Alert on symptoms, not causes.** Alerting on high latency is good. Alerting on every pod restart is noise unless it maps to an SLO.
* **Stale alerts.** If an alert never fires or always fires, it's dead code. Alert hygiene is operational work.

### Example

Payment service SLO: 99.9% of requests < 500ms over 30 days.

You don't alert on `p99 > 500ms`. You alert on SLO burn rate.

Burn rate > 14.4x over 1h = page now. Burn rate > 6x over 6h = warning Slack.

This ties alerting to business impact, not raw metrics. It gives you time budget semantics: you can tolerate a spike if you have budget left.

Architecture:
`Prometheus metrics → Recorded rules for latency & error rate → Alertmanager with routes: critical → PagerDuty, warning → Slack → Runbook link in alert annotation`.

The runbook is required. Without steps, the alert is not actionable.

### Reasoning challenge

You have a microservice with 50 replicas. CPU spikes on one replica cause occasional 5s latency bursts for 30s, then recover. Error rate stays <0.1%. Your dashboard shows it.

Do you alert on `max(cpu) > 90%` or on `p99 latency > 1s for 5m`? What `for` duration would you pick, and who gets paged?

### Key takeaway

* Alerting exists to convert system state into timely human action, not to report interesting metrics.
* Design alerts from SLOs and business impact, not from raw signals. Use `for` duration and burn rate to trade latency for stability.
* An alert must be actionable now, owned, and have a runbook. If it doesn't, it's noise.
* Operate alerting as a product: measure false positive rate, mean time to acknowledge, and alert churn; prune ruthlessly.
