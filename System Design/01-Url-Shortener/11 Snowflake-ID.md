[[05 Distributed Ids.pdf]] #snowflakeId  

Snowflake IDs were created to fix the **practical problems of UUIDs** while keeping their **global uniqueness**.

UUIDs are:

- Globally unique ✅
    
- Decentralized ✅
    
- But **long**, **random**, and **bad for indexing**
    

Snowflake IDs optimize for:

- Distributed systems
    
- High write throughput
    
- Time ordering
    
- Shorter, URL-friendly identifiers
    

---

## What is a Snowflake ID?

A **Snowflake ID** is a **64-bit integer** composed of multiple parts.

Classic structure (Twitter Snowflake style):

```
| 41 bits timestamp | 10 bits machine ID | 12 bits sequence |
```

Total = **63 bits** (1 bit unused for sign)

---

## Breakdown (important)

### 1. Timestamp (41 bits)

- Milliseconds since a custom epoch
    
- Allows:
    
    - Natural ordering by creation time
        
    - Efficient range queries
        
    - Easy pagination
        

41 bits ≈ **69 years** of timestamps

---

### 2. Machine / Worker ID (10 bits)

- Identifies the node generating the ID
    
- 10 bits = **1024 nodes**
    

This avoids collisions across:

- Machines
    
- Pods
    
- Data centers
    

---

### 3. Sequence number (12 bits)

- Counter per millisecond per node
    
- 12 bits = **4096 IDs per ms per node**
    

This supports **very high write throughput**.

---

## Example Snowflake ID

Decimal representation:

```
9223372036854775807
```

Binary representation (conceptual):

```
timestamp | machine | sequence
```

Important point:

- This is still **just a number**
    
- But it encodes **time + origin + order**
    

---

## Why Snowflake IDs are better than UUIDs

### 1. Time ordering (major win)

Snowflake IDs are:

- Monotonically increasing
    
- Naturally sorted by creation time
    

This fixes:

- Random index inserts (UUID problem)
    
- Inefficient pagination
    

---

### 2. Database index efficiency

Because IDs increase over time:

- Inserts are mostly append-only
    
- B-tree indexes stay compact
    
- Much better write performance
    

This matters at scale.

---

### 3. Shorter than UUIDs

- Snowflake ID: **64 bits**
    
- UUID: **128 bits**
    

When Base62-encoded:

- Snowflake → ~11 characters
    
- UUID → ~22 characters
    

Much better for:

- Short URLs
    
- Copy/paste
    
- UX
    

---

### 4. Built-in tracing and observability

From a Snowflake ID, you can infer:

- Approximate creation time
    
- Which node generated it
    
- Ordering relative to other events
    

This is **huge** for debugging distributed systems.

---

## Snowflake IDs in a URL shortener

### Flow

1. Client calls `POST /shortUrl`
    
2. Application generates Snowflake ID
    
3. ID stored as primary key
    
4. ID Base62-encoded
    
5. Encoded value becomes shortCode
    

```
Snowflake ID (64-bit)
   ↓
Base62
   ↓
shortCode
```

---

## Example

### Stored in DB

```text
id: 9223372036854775807
original_url: https://example.com
```

### Exposed URL

```
https://s.io/LygHa16AHY
```

Short, sortable, unique.

---

## Problems with Snowflake IDs (be honest)

### 1. Operational complexity

You must manage:

- Worker IDs
    
- Clock synchronization
    
- Deployment coordination
    

UUIDs don’t need this.

---

### 2. Clock skew risk

If system clocks move backward:

- ID collisions can happen
    
- Systems must guard against this
    

Production systems add safeguards, but complexity exists.

---

### 3. Leaks creation time

Snowflake IDs expose:

- Approximate creation timestamp
    

This is usually acceptable, but not always.

---

## UUID vs Snowflake — quick comparison

|Property|UUID v4|Snowflake|
|---|---|---|
|Global uniqueness|✅|✅|
|Shard-safe|✅|✅|
|Time ordering|❌|✅|
|Index friendly|❌|✅|
|URL length|Long|Short|
|Ops complexity|Low|Medium|
|Traceability|❌|✅|

---

## When to use Snowflake IDs

Use Snowflake when:

- You expect high scale
    
- You shard databases
    
- You care about write performance
    
- You want sortable, compact IDs
    
- You need better observability
    

This is why:

- Twitter
    
- Discord
    
- Instagram
    
- Many large systems
    

Use Snowflake-style IDs.

---

## Final mental model

- **UUID** → correctness first, simplicity first
    
- **Snowflake** → scale, performance, observability
    
Snowflake IDs are what you use **after** you outgrow UUIDs.