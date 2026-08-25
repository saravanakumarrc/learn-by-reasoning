# Normalization

> **Learning Path:** Data Architecture
> **Section:** 3.2.2 — Data architecture

**Normalization**

### 1. The problem

A single business fact gets stored in multiple places.

In an orders table you store customer name, address, phone on every order row. Update the address once, forget one row, now you have two truths. Delete the last order for a customer and you lose the customer entirely. Insert an order for a new product before the product record exists and you create orphan data.

These are update, delete and insert anomalies. They come from redundancy and from mixing different types of facts in the same table.

### 2. Mental model

Normalization is separating *what a thing is* from *how things relate*.

Think of it as removing duplication of meaning. A customer's address belongs to the customer, not to each order they placed. An order line belongs to the relationship between an order and a product.

The goal is one authoritative place for each fact.

### 3. How it works

Normalization is the process of applying functional dependencies to decompose tables.

* **1NF:** No repeating groups. One value per cell, atomic columns. You can't store multiple phone numbers in one column.
* **2NF:** No partial dependency. Non-key attributes must depend on the whole primary key. In `OrderItems(order_id, product_id, quantity, product_price)` product_price depends only on product_id, not the whole key.
* **3NF:** No transitive dependency. Non-key attributes must depend only on the key. In `Customers(id, name, city, tax_rate)` tax_rate depends on city, not directly on id.

Result is a set of tables linked by foreign keys.

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    PRODUCTS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--o{ ORDER_ITEMS : has
    CUSTOMERS {
        customer_id PK
        name
        address
    }
    ORDERS {
        order_id PK
        customer_id FK
        order_date
    }
    ORDER_ITEMS {
        order_id FK
        product_id FK
        quantity
        unit_price
    }
    PRODUCTS {
        product_id PK
        name
        unit_price
    }
```

### 4. Architectural reasoning

Normalization helps when the system is write-heavy and correctness matters.

* **When it helps:** OLTP systems, transactional apps, systems with frequent updates to shared reference data. Banking, CRM, inventory. You want one source of truth and minimal anomalies.
* **What it solves:** Data integrity, reduced storage waste from duplication, predictable updates.
* **Alternatives:** Denormalization, star schemas, document stores. You trade integrity for read speed and simplicity.

Decision rule: Normalize first for logical correctness, denormalize later for performance where proven by measurement.

### 5. Trade-offs and failure modes

* **Read cost.** Normalized data requires joins. A single order summary can need 4-5 tables. This is fine for OLTP, painful for analytical queries.
* **Over-normalization.** Splitting into too many tiny tables creates join explosion, hurts operability and developer productivity. Normalization is not maximization.
* **Write overhead.** More tables = more foreign key checks, more transactions.
* **Failure mode:** Treating normalization as a moral rule. In high-read, append-only workloads like analytics or event sourcing, denormalized or columnar stores are the right choice. Normalization does not automatically equal good architecture.

### 6. Example

E-commerce order system.

Denormalized: `orders(order_id, customer_name, customer_address, product_name, quantity, price)`. Change address requires updating every past order row.

Normalized:
* `customers` holds address once
* `orders` references customer_id
* `order_items` references order_id and product_id
* `products` holds current price

Update address = one row in `customers`. Historical order price is preserved in `order_items` via snapshot, not live reference.

For a reporting dashboard that needs daily revenue by region, you would build a separate read model or materialized view, not force ad-hoc joins on the normalized OLTP tables.

### 7. Reasoning challenge

You are designing a platform for a retailer with 10M daily orders and a real-time recommendation engine that needs user profile + last 20 orders + product catalog in <50ms.

Do you keep the profile and orders fully normalized in Postgres for the serving path? What do you change, and where does normalization stay?

### 8. Key takeaway

* Normalization exists to eliminate redundancy and anomalies, not to make tables pretty.
* Normalize for write correctness and integrity in transactional domains; denormalize for read performance in analytical domains.
* The architect's job is choosing where the boundary lives, not applying normal forms blindly.
* Over-normalization hurts latency and simplicity; under-normalization hurts correctness.
