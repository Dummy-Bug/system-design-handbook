> [!info] The core problem
> ACID gives you atomicity within one database. But when a transaction spans multiple services, each with their own database, there is no single database to wrap a transaction around. This is the distributed transaction problem.


## The scenario

You're building Swiggy. A user places an order. Three things need to happen:

1. **Charge the user's payment card** → Payment Service → its own database
2. **Deduct the item from inventory** → Inventory Service → its own database
3. **Create the order** → Order Service → its own database

Each service is independent, each owns its own database.

Now imagine this sequence:

```
Step 1 — Payment Service charges card ✓
Step 2 — Inventory Service deducts stock ✓
Step 3 — Order Service tries to create order ✗ database is down
```

The user got charged. The restaurant pulled the item from inventory. But no order exists in the system. The user's money is gone and they get no food.

---

## Why ACID doesn't help here

Within a single database, you already know how to handle this — wrap everything in a transaction:

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 500 WHERE user_id = 1;
  UPDATE inventory SET stock = stock - 1 WHERE item_id = 42;
  INSERT INTO orders (user_id, item_id, status) VALUES (1, 42, 'confirmed');
COMMIT;
-- if anything fails → ROLLBACK → all three undo atomically
```

ACID gives you atomicity — all or nothing — within one database.

But here's the problem. Payment Service, Inventory Service, and Order Service each have their **own separate database**. There is no single database to wrap a transaction around. You cannot `BEGIN` and `COMMIT` across three different databases owned by three different teams.

> [!danger] ACID only works within one database
> The moment your transaction spans multiple services with separate databases, ACID cannot help you. There is no single coordinator to orchestrate a rollback across all three.

---

## The distributed transaction problem

You need a way to make all three steps either all succeed or all fail together — across service boundaries, across separate databases, over a network that can drop messages and crash at any point.

This is the **distributed transaction problem**. Two solutions exist:

- **2PC** — coordinate a true atomic commit across all databases using a central coordinator
- **Saga** — break the transaction into local steps, and if something fails, run compensating transactions to undo the previous steps

Both have trade-offs. Neither is free.
