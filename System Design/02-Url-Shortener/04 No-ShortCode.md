[[03 Simple Approaches.pdf]]

### 1. Simplest approach — no shortCode

Instead of keeping a separate `shortCode`, we can directly use the
database-auto-incremented `id` which as the short URL identifier.

This minimizes storage and logic complexity.

```json
{
  "success": true,
  "message": "Created",
  "data": {
    "id": 123,
    "originalUrl": "https://example.com"
  }
}
```

# Problems
## 1. Predictability (security + abuse risk)

Auto-increment IDs are **sequential**.

`/123 /124 /125`

**Implications:**

- Easy scraping and enumeration using **GET /{id}**
    
- Anyone can crawl all URLs by incrementing numbers and 
    
- No protection against data harvesting

## 2. Information leakage

The ID reveals:

- How many URLs your system has created
    
- Creation order
    
- Growth patterns

In internal tools this is fine but In public systems, this is usually unacceptable.

## 3. Coupling URL to database implementation

You are exposing:

- Internal primary key
    
- Storage strategy (auto-increment)
    
**Consequences:**

- Harder DB migrations
    
- Harder sharding
    
- Harder switch to UUID / Snowflake later

Once users bookmark `/123`, you’re locked in.

## 4. ID size and poor URL ergonomics (**important**)

In real systems, primary keys are often stored as `BIGINT`.

A signed `BIGINT` is a **64-bit integer**, with a maximum value of:

`9,223,372,036,854,775,807`

That is **19 digits long**.

If such an ID is exposed as a short URL:

`https://s.io/9223372036854775807`

**Problems:**

- Not “short” anymore
    
- Hard to read, share, or manually type
    
- Error-prone in emails, chat, QR codes
    
- Poor user experience compared to 6–8 character short codes
    
This completely defeats the purpose of a URL shortener.

## Why BIGINT primary keys have 19 digits

Databases commonly use `BIGINT` because it is:

- 64 bits wide
    
- Efficient for CPUs and indexing
    
- Large enough for massive scale
    

A signed 64-bit integer has this range:

`−2⁶³ to 2⁶³ − 1`

The maximum positive value:

`2⁶³ − 1 = 9,223,372,036,854,775,807`

That number happens to be **19 digits long**.

This is why:

- BIGINTs are excellent **internal identifiers**
    
- BIGINTs are terrible **external identifiers**

