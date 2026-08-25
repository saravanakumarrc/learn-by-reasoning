# CDN

> **Learning Path:** Cloud & Infrastructure Architecture
> **Section:** 4.1.6 — Cloud fundamentals

**The problem**

You have a single origin in us-east-1. A user in Sydney requests a 2 MB image. The request must travel ~20,000 km, do 3-4 TCP round trips, suffer slow-start, and compete for origin bandwidth with every other global user. Latency is 300-600 ms and your origin CPU/bandwidth scales linearly with global traffic.

Constraints are physical: speed of light, TCP handshake cost, origin capacity, and egress cost. You cannot move the origin closer to everyone, and you cannot make light faster.

**Mental model**

A CDN is a distributed cache with smart routing. It puts copies of your content on the internet, close to users, and serves them from there. Think of it as a reverse proxy farm that you don't operate, whose job is to absorb the long tail of reads and hide the origin.

**How it works**

Requests hit the nearest Point of Presence via anycast DNS. The edge checks its cache using your cache-control policy. Hit = serve from RAM/disk in <50 ms. Miss = fetch from origin, cache it, then serve.

```mermaid
flowchart LR
    C[Client Sydney] --> E[CDN Edge PoP Sydney]
    E -->|Cache Hit| C
    E -->|Cache Miss| O[Origin us-east-1]
    O --> E
    E --> C
```

Essential mechanisms:
* **Edge caching:** static assets, and cacheable API responses, stored in PoPs worldwide.
* **Origin shielding:** one regional cache absorbs repeated misses instead of hammering origin.
* **Invalidation & TTL:** you control freshness via `Cache-Control`, `ETag`, surrogate keys. The CDN respects it.
* **Dynamic acceleration:** TCP/HTTP optimization, connection pooling to origin, TLS offload.

**Architectural reasoning**

When it helps:
* High read:write ratio content served to a geographically dispersed audience.
* Origin is a bottleneck for latency-sensitive reads.
* You need surge absorption for viral spikes.

What it solves: reduces tail latency, reduces origin egress and compute, improves availability by decoupling user-facing traffic from origin.

Alternatives:
* Multi-region active-active origins. Solves latency but costs 3-5x to run and replicate state. Good for low-latency write workloads.
* Client-side caching only. Limited control and no global distribution.
* Edge compute without caching. Useful for personalization, but doesn't remove origin load.

Choose CDN when the bottleneck is distribution of largely read-only data, not write consistency.

**Trade-offs and failure modes**

* **Freshness vs speed.** Longer TTL = better hit rate, worse staleness. Invalidation is eventually consistent and costly. You must design for cache.
* **Cache stampede / thundering herd.** A popular object expires, thousands of edges fetch origin simultaneously. Mitigate with stale-while-revalidate, origin shielding, request coalescing.
* **Cache poisoning.** Bad response cached globally. Requires strict origin validation and purge controls.
* **Cost model shift.** You pay per egress at edge, often cheaper than origin egress, but cache misses still cost origin bandwidth.
* **Security surface.** Edge is a new trust boundary. You must sign URLs, set `Vary` correctly, and avoid caching user-specific responses.

CDN does not help write latency or strong consistency. It makes eventual consistency cheaper.

**Example**

Enterprise SaaS dashboard. Static JS/CSS/images are immutable with content hashes, cached for 1 year. API responses like `/api/config` are cached for 60s with `stale-while-revalidate=30`. The origin runs in two regions for writes. 85% of user requests never reach origin, origin egress drops 70%, p95 page load in APAC goes from 1.8s to 220ms. Purging happens via surrogate key on deploy, not per URL.

**Reasoning challenge**

You run a flash-sale e-commerce site. Product detail pages are personalized per user, prices change every 5 minutes, and traffic spikes 50x for 10 minutes. Do you put the HTML behind a CDN? What would you cache and for how long, and what would you leave origin-only?

**Key takeaway**

* CDN exists to move reads closer to users and shield the origin from global demand, not to make writes faster.
* Architecture is cache policy first, infrastructure second. Design your objects and TTLs for the cache you want.
* Use it for high-read, low-mutability content and as surge protection; do not use it to hide a poorly designed origin.
* The main risks are staleness, invalidation complexity, and accidentally caching private data.
