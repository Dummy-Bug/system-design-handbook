[[03 Simple Approaches.pdf]]

Instead of generating and storing a separate `shortCode`, we can **derive the short URL by hashing the original URL**.

---

## How hashing would work

### Flow

1. Client sends:
    

`{   "originalUrl": "https://example.com" }`

2. Backend computes a hash of `originalUrl`
    

Example hashes:

- SHA-256
    
    `https://example.com → e3b0c44298fc1c149afbf4c8996fb924...`
    

3. Take a subset of the hash (for brevity), e.g. first 7–8 characters:
    

`e3b0c44`

4. Use that as the short URL:
    

`https://s.io/e3b0c44`

No separate shortCode generation logic; the short URL is **deterministic**.

---

## Why this looks attractive

- No auto-increment IDs exposed
    
- No random generator needed
    
- Same URL always produces the same short URL
    
- Simple mental model
    

---

# Problems

## 1. Hash collisions (fundamental issue)

Hashes are **not guaranteed to be unique** when truncated.

Example:

`hash(urlA)[0..7] == hash(urlB)[0..7]`

This causes:

- One short URL pointing to two different destinations
    
- Data corruption or forced overwrites
    

Avoiding collisions means:

- Longer hash → ugly URLs
    
- Collision checks → complexity returns
    

---

## 2. Length vs usability trade-off

- Short hash → collisions
    
- Long hash → defeats “short” in short URL
    

Example:

`SHA-256 full length = 64 hex chars`

`https://s.io/e3b0c44298fc1c149afbf4c8996fb924...`

This is worse than using a BIGINT.

---

## 3. No control over uniqueness scope

Hashing:

- Binds identity to the original URL
    
- Prevents multiple short URLs for the same target
    

You lose the ability to:

- Create multiple campaigns for the same URL
    
- Track per-user or per-tenant links
    
- Set different expirations
    

---

## 4. Hard to rotate or change behavior

If you ever:

- Change hash algorithm
    
- Change truncation length
    
- Add salting
    

You break existing URLs or need complex versioning.