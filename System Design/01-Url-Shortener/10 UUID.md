[[05 Distributed Ids.pdf]] #uuid

UUID = **Universally Unique Identifier**

- Size: **128 bits**
    
- Designed to be unique across:
    
    - Machines
        
    - Processes
        
    - Time
        
    - Datacenters
        

Example (UUID v4):

`550e8400-e29b-41d4-a716-446655440000`

---

## Why UUIDs solve sharding collisions

### Key property: Global uniqueness

UUIDs are generated at the **application layer**, not the database.

So even if you have:

`Shard A Shard B Shard C`

Each service instance generates UUIDs independently.

There is **no shared counter**, hence:

- No overlap
    
- No coordination
    
- No collision risk (practically zero)
    

---

## Using UUIDs in a URL shortener

### Flow

1. Client calls `POST /shortUrl`
    
2. Application generates a UUID
    
3. UUID is stored as primary key
    
4. UUID is encoded (Base62 / Base64URL)
    
5. Encoded value becomes the shortCode
    

`UUID (128-bit)    ↓ Base62 encode    ↓ shortCode`

---

## Example

### Stored in DB

`id (UUID): 550e8400-e29b-41d4-a716-446655440000 original_url: https://example.com`

### Exposed as short URL

`https://s.io/4fT9XcQm2aJkP`

---

## Advantages of UUIDs

### 1. No collisions across shards

- Safe for horizontal scaling
    
- Safe for multi-region writes
    
- No central ID generator
    

---

### 2. No information leakage

Unlike auto-increment IDs, UUIDs do **not** reveal:

- Total number of URLs
    
- Creation order
    
- Growth rate
    

This is critical for public-facing systems.

---

### 3. Decouples identity from storage

UUIDs are:

- Not tied to database type
    
- Not tied to sharding strategy
    

You can:

- Reshard
    
- Migrate databases
    
- Change storage engines
    

Without breaking URLs.

---

## Problems with UUIDs (important)

UUIDs are **correct**, but not **ideal**.

---

### 1. Very long identifiers

UUIDs are 128-bit.

Raw form:

`550e8400-e29b-41d4-a716-446655440000`

Even Base62-encoded, they are still:

- Longer than Snowflake IDs
    
- Longer than sequential Base62 IDs
    

This hurts:

- URL aesthetics
    
- Copy-paste usability
    

---

### 2. Poor database index locality

UUIDs are **random** (especially v4).

Implications:

- Inserts hit random index pages
    
- B-tree fragmentation
    
- Slower writes at scale
    

This becomes noticeable at high QPS.

---

### 3. No inherent ordering

UUIDs do not encode time (unless using newer versions).

You cannot:

- Sort by creation time
    
- Infer age from the ID
    
- Use ID ordering for pagination efficiently
    

All of this requires extra columns.

---

### 4. Weak observability and tracing

From a UUID alone, you **cannot infer**:

- When it was created
    
- Which node generated it
    
- Which region it came from
    

For distributed debugging, this is a limitation.

---

## Summary

UUIDs solve the **correctness problem**:

- No collisions
    
- No shard conflicts
    
- No data leakage
    

But they introduce **operational drawbacks**:

- Long URLs
    
- Index inefficiency
    
- Poor traceability
    
- No time ordering