# Denormalization

> **Learning Path:** Data Architecture
> **Section:** 4.2.3 — Data architecture

## 1. Problem

நார்மலைஸ் பண்ணிய relational database-ல ஒரு realistic scenario.

`users`, `products`, `orders`, `order_items`, `addresses` என 5 tables இருக்கு. User-ன் order history page-க்கு வேண்டியது: order date, total amount, product name, price at purchase time, shipping address.

Normalized schema-ல இது 4-5 joins. Traffic குறைவாக இருக்கும்போது பிரச்சனை இல்லை. Black Friday-ல 10k RPS வரும்போது அதே query 800ms - 2s ஆகிறது. DB CPU spike ஆகிறது. Index எல்லாம் வைத்தும் joins-ன் cost குறையவில்லை.

இப்போது கேள்வி: Read speed-க்காக data-வை duplicate பண்ணலாமா? அதன் விலை என்ன?

இதுதான் denormalization-ன் root problem.

## 2. Mental Model

Normalization = write consistency-க்காக data-வை split பண்ணுவது.
Denormalization = read speed / simplicity-க்காக data-வை duplicate பண்ணுவது.

நீங்கள் write complexity-வை அதிகரித்து read path-வை cheap ஆக்குகிறீர்கள். 

ஒரு mental model: normalized DB என்பது single source of truth. Denormalized view என்பது pre-computed read model. Source-of-truth மாறும்போது read model-ஐ update செய்ய வேண்டும்.

## 3. How It Works

Database level-ல:

* Normalized: `orders(order_id, user_id, ...)` + `order_items(order_id, product_id, qty)` + `products(product_id, name, price)` ... join செய்து read.
* Denormalized: `order_summary(order_id, user_name, shipping_address, items_json, total_amount_at_purchase)` 

Product name, price at purchase time போன்றவற்றை order create ஆகும்போதே snapshot எடுத்து store பண்ணுவது. இனி order history read என்பது single table scan, zero join.

NoSQL / document store-ல இது natural. Relational-ல இதை `materialized view` அல்லது application-level denormalized table-ஆக செய்யலாம்.

```
Order created
   |
   v
Write to normalized tables for consistency
   |
   v
Async / synchronous write to order_summary for fast reads
```

## 4. Architectural Reasoning

Denormalization useful ஆகும் போது:

* **Read heavy, write light**: 95% read, 5% write workload.
* **Join heavy read path**: 3+ joins தேவைப்படும் முக்கிய queries.
* **Read latency SLA strict**: <100-200ms வேண்டும், user-facing page.
* **Eventual consistency acceptable**: Product name மாறினால், பழைய order-ல பழைய name தான் தேவை.

Alternatives:
* Read replica + better indexing → helps but joins இன்னும் இருக்கும்
* Cache layer with Redis → hit rate, invalidation complexity
* Materialized view → database managed denormalization, refresh cost உண்டு

Architect ஏன் தேர்வு செய்கிறார்? Join cost-ஐ eliminate செய்து, read path-ஐ predictable ஆக்குவதற்கு. Operational cost குறைவு, DB load குறைவு.

## 5. Trade-offs

1. **Write amplification**: ஒரு product name மாறினால், அது எங்கெங்கு duplicate ஆகி இருக்கிறது என்று update செய்ய வேண்டும். அல்லது snapshot approach எடுத்து historical data-வை touch செய்யாமல் விடுவது.

2. **Consistency risk**: Source table update ஆனது denormalized copy-ல reflect ஆக தாமதமாகலாம். Race condition, partial failure வரும். Idempotent update, outbox pattern தேவை.

3. **Storage cost**: Data duplicate ஆகிறது. Modern cloud-ல storage cheap, but backup, replication cost உயரும்.

4. **Complexity of change**: Schema evolve ஆகும்போது duplicate columns எல்லாவற்றையும் migrate செய்ய வேண்டும்.

Failure mode: Denormalized table update fail ஆனால் read stale ஆகும். User-க்கு தவறான price தெரியும். அதனால் critical financial data-க்கு denormalization-ஐ கவனமாக பயன்படுத்த வேண்டும்.

## 6. Practical Example

E-commerce order history.

Normalized schema-ல dashboard query:

```sql
SELECT o.id, u.name, p.name, oi.qty, a.city
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON oi.order
