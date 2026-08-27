# Scheduling

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 5.3.13 — Kubernetes

## Problem

உங்களிடம் 200 node-கள் இருக்கு. ஒவ்வொன்றிலும் CPU, memory, GPU, zone, instance type வேறுபடும். மேலே 2000 pod-கள் schedule ஆக வேண்டும். Autoscaler ஒவ்வொரு நிமிடமும் புது pod-களை உருவாக்கும்.

மானுவலாக எந்த pod-ஐ எந்த node-ல் போடுவது என்று முடிவு பண்ண முடியாது. ஒரு pod-க்கு 4 CPU வேண்டும் என்றால் 2 CPU உள்ள node-ல் போட்டால் என்ன ஆகும்? ஒரு critical service-ஐயும் batch job-ஐயும் ஒரே node-ல் போட்டால் noisy neighbor பிரச்சனை வரும். ஒரு zone down ஆனால் அந்த zone-ல் மட்டும் pod-கள் இருந்தால் availability போய்விடும்.

இந்த placement decision-ஐ தானாக, policy-க்கு ஏற்ப, resource fit ஆகும் வகையில் எடுக்க வேண்டும். அதுதான் Kubernetes scheduler-ன் வேலை.

## Mental Model

Scheduler = matchmaker + traffic police.

Matchmaker: pod-ன் resource request, node selector, affinity, taint/toleration போன்ற constraints-க்கு ஏற்ற node-களை கண்டுபிடிக்கும்.

Traffic police: ஒரு node-ல் ஏற்கனவே அதிக load இருந்தால் அங்கே போடாமல் spread பண்ணும். Priority, preemption போன்ற policy-களை enforce பண்ணும்.

நீங்கள் *where* என்று சொல்லாமல் *what constraints* என்று சொல்கிறீர்கள். Scheduler அதை satisfy செய்யும்.

## How It Works

ஒரு pod unschedulable ஆக pending-ல் இருக்கும். kube-scheduler அதை கண்டுபிடிக்கும்.

**Filter → Score → Bind** என்ற flow.

1. **Filter / Predicates**: எல்லா node-களையும் filter பண்ணி feasible set-ஐ குறைக்கும்.
   - resources fit ஆகுமா? requests vs allocatable
   - taints/tolerations match ஆகுமா?
   - nodeSelector, affinity/anti-affinity, topologySpreadConstraints satisfy ஆகுமா?
   - pod topology, volume zone constraints?

2. **Score / Priorities**: feasible node-களுக்கு score கொடுக்கும்.
   - LeastRequestedPriority: குறைவாக பயன்படுத்தப்பட்ட node-க்கு அதிக score
   - BalancedResourceAllocation: CPU/memory balanced ஆக இருக்கும் node-க்கு score
   - NodeAffinityPriority, TaintTolerationPriority...

Score அதிகமான node தேர்ந்தெடுக்கப்பட்டு kubelet-க்கு Bind செய்யப்படும்.

இது plugin based scheduler framework-ல் இயங்குகிறது. Custom scheduler, scheduler extender பயன்படுத்தி வெளியே logic எழுத முடியும்.

## Architectural Reasoning

Scheduler உங்களுக்கு என்ன கொடுக்கிறது?

**Decoupling**: Pod definition-ல் placement logic கலக்காமல் இருக்கும். Application team resource request, affinity மட்டும் கொடுக்கும்.

**Constraint as code**: Taints, tolerations, nodeSelector, topology spread மூலம் business constraint-களை declarative ஆக வைக்கலாம்.

**Scale**: 10k node-களில் pod-கள் scale ஆகும்போது human decision impossible. Scheduler continuous reconciliation செய்யும்.

எப்போது default scheduler போதுமானது? General workloads, standard resource constraints உள்ள போது.

Custom scheduling தேவைப்படும்போது? GPU time-slicing, specific hardware, strict latency SLO, multi-tenant fairness, cost optimization based on spot instances.

## Trade-offs

**Scheduling speed vs placement quality**: Scheduler ஒவ்வொரு pod-க்கும் எல்லா node-களையும் evaluate செய்யும். Node count அதிகரிக்கும் போது scheduling latency அதிகரிக்கும். அதற்காக heuristic scoring பயன்படுத்துகிறோம், optimal solution கிடைப்பதில்லை.

**Bin packing vs spread**: Pack பண்ணினால் resource utilization அதிகம், ஆனால் node failure ஆனால் அதிக pod-கள் பாதிக்கும். Spread பண்ணினால் fault tolerance நன்றாக இருக்கும், ஆனால் cluster utilization குறையும்.

**Preemption cost**: PriorityClass மூ
