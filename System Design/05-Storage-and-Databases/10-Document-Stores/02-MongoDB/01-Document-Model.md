> [!info] MongoDB stores JSON objects — called documents — instead of rows. No fixed schema. Two documents in the same collection can have completely different fields, different nesting, different arrays. The database stores whatever you give it.

## The problem with SQL for variable data

You're building a Flipkart-style product catalog. You start with a simple table:

```sql
CREATE TABLE products (
  id          INT PRIMARY KEY,
  name        VARCHAR(255),
  description TEXT,
  price       DECIMAL
);
```

Now add shoes — they need sizes. `ALTER TABLE ADD COLUMN sizes VARCHAR`. But laptops don't have sizes, they have RAM and CPU. TVs have resolution. Cameras have megapixels.

```sql
ALTER TABLE products ADD COLUMN sizes VARCHAR;      -- null for everything except shoes
ALTER TABLE products ADD COLUMN ram_gb INT;          -- null for everything except laptops
ALTER TABLE products ADD COLUMN resolution VARCHAR;  -- null for everything except TVs
ALTER TABLE products ADD COLUMN megapixels INT;      -- null for everything except cameras
```

Your table is now mostly nulls. Every new product category means another ALTER TABLE. At scale, ALTER TABLE on a live table with 100M rows locks the table and takes hours.wh

This is the **schema-on-write** problem — SQL forces you to define the shape before you write the data.

---

## What MongoDB does instead

MongoDB uses **schema-on-read** — no shape defined upfront. You store what you have, query what you need.

```json
// Shoe
{
  "product_id": 101,
  "name": "Nike Air Max",
  "price": 8999,
  "sizes": ["6", "7", "8", "9", "10"],
  "specs": { "weight": "300g", "material": "mesh" }
}

// Laptop
{
  "product_id": 202,
  "name": "MacBook Pro",
  "price": 129900,
  "specs": { "ram_gb": 16, "cpu": "M3 Pro", "storage_gb": 512 }
}

// TV
{
  "product_id": 303,
  "name": "Samsung QLED",
  "price": 54999,
  "specs": { "resolution": "4K", "size_inches": 55, "refresh_rate_hz": 120 }
}
```

All three live in the same `products` collection. Different shapes, no nulls, no schema change needed when you add a new category.

---

## The document structure

```
Database
  └── Collections  (like SQL tables — but no fixed schema)
        └── Documents  (like SQL rows — but JSON, any shape)
              └── Fields  (like SQL columns — but per-document, not per-table)
```

A document is just a JSON object. Fields can be:
- Flat values: `"name": "Nike Air Max"`
- Nested objects: `"specs": { "weight": "300g" }`
- Arrays: `"sizes": ["6", "7", "8"]`
- Arrays of objects: `"images": [{ "url": "front.jpg", "type": "main" }]`

---

## What you give up

MongoDB's flexibility comes at a cost — **no schema enforcement**. SQL gives you:

```sql
NOT NULL        → MongoDB: application must check
FOREIGN KEY     → MongoDB: no referential integrity, orphaned documents possible  
UNIQUE          → MongoDB: opt-in index, not enforced by default
CHECK constraint → MongoDB: doesn't exist
```

In SQL the database is the last line of defence against bad data. In MongoDB your application code is. If a bug in your code writes a document without a required field, MongoDB accepts it silently.

> [!important] This is why MongoDB is wrong for financial data, order records, anything where data integrity is non-negotiable. The application enforcing integrity is not the same as the database enforcing it.
