### Current assumption

- Primary key = auto-incrementing `BIGINT`
    
- shortCode = Base62(id)
    

This works **only** as long as:

- Single database
    
- Single ID sequence
    

---

## What breaks when we shard

When you shard, you typically have:

`DB-1 → ids: 1, 2, 3, 4, ... DB-2 → ids: 1, 2, 3, 4, ... DB-3 → ids: 1, 2, 3, 4, ...`

Now encode IDs using Base62:

`DB-1 id 42 → g DB-2 id 42 → g DB-3 id 42 → g`

### Result

- Same `shortCode`
    
- Different `originalUrl`
    
- **Hard collision**
    
- System becomes incorrect by design
    

This is not a bug. This is a **fundamental limitation** of auto-increment IDs in distributed systems.

---

## Why “just add shardId” is not enough

You might think:

`shortCode = base62(shardId + id)`

Problems:

- You’ve reinvented a distributed ID generator
    
- URL format is now coupled to sharding topology
    
- Re-sharding breaks URLs
    
- Migration becomes painful
    

This is why serious systems **stop using DB auto-increment as identity**.