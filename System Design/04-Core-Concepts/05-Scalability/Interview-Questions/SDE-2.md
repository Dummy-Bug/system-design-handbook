# Scalability — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around scaling strategies, sharding, database bottlenecks, and auto-scaling design. Expected at SDE-2 level.

---

## Q1 — Database Bottleneck at Scale

> [!question] Your API handles 10,000 requests/second. App servers are fine but DB latency is 800ms and climbing. Walk me through your scaling strategy for the database.

> [!success]- Answer
>
> **Diagnosis first — what kind of problem?**
> ```
> Check slow query log:
>   Missing index → add index → immediate fix
>   Full table scan on 100M rows → optimize query first
>
> Check connection pool:
>   All connections occupied → PgBouncer connection pooler
>   Reduces 10k app server connections to 100 DB connections
>
> Check read/write ratio:
>   90% reads, 10% writes → read replicas will help significantly
>   50% writes → sharding discussion needed
> ```
>
> **Layer 1 — Cache (biggest impact, implement first):**
> ```
> Redis in front of DB
> Popular queries hit cache → 80-90% of reads served from memory in ~1ms
> DB load drops dramatically
>
> Trade-off: stale data during TTL window
>            acceptable for most read data
> ```
>
> **Layer 2 — Read replicas:**
> ```
> Add 2-3 read replicas
> Route all SELECT queries to replicas
> Primary handles writes only
>
> Trade-off: replica lag (typically <100ms) → slightly stale reads
>            acceptable for most business use cases
> ```
>
> **Layer 3 — Sharding (only if writes are the bottleneck):**
> ```
> When single primary can't keep up with write volume:
>
> Shard by user_id:
>   Users 0-999999 → DB Shard 1
>   Users 1M-2M   → DB Shard 2
>
> Trade-off:
>   Cross-shard queries are expensive → avoid or denormalize
>   Resharding later is painful → choose shard key carefully
>   Transaction guarantees weakened across shards
> ```
>
> **Sequence matters:**
> ```
> Cache → connection pooling → read replicas → sharding (last resort)
>
> Each earlier step may eliminate the need for later ones
> Sharding first is over-engineering
> ```
>
> > [!tip] Interview framing
> > *"Start with diagnosis: slow queries, connection exhaustion, or throughput? Cache first — eliminates 80% of DB reads. Then read replicas for remaining reads. Only shard if write throughput is the problem — sharding adds significant operational complexity and should be the last resort."*

---

## Q2 — Sharding Key Selection

> [!question] You're sharding a 500M user social platform. Your colleague suggests sharding by creation date (year). You push back. Why, and what do you propose instead?

> [!success]- Answer
>
> **Why date-based sharding is a bad choice:**
>
> **Problem 1 — Hot shard (uneven load):**
> ```
> Shard 2026: all active users joined recently → gets all the traffic
> Shard 2020: inactive users → barely any traffic
>
> One shard handles 80% of load → becomes a bottleneck
> Horizontal scaling didn't actually spread the load
> ```
>
> **Problem 2 — Uneven data distribution:**
> ```
> Platform growing → all new users go to current year's shard
> Old shards have tombstoned/inactive users
> New shard fills up rapidly → needs resharding again soon
> ```
>
> **Why user_id is better:**
> ```
> Shard by user_id modulo N:
>   user_id % 4 = 0 → Shard 1
>   user_id % 4 = 1 → Shard 2
>   user_id % 4 = 2 → Shard 3
>   user_id % 4 = 3 → Shard 4
>
> Load is distributed evenly (assuming random user_id distribution)
> Active and inactive users spread across all shards
> ```
>
> **The new problem with user_id sharding:**
> ```
> "Get all posts by users in the same city"
>   → those users are on different shards
>   → must query ALL shards and merge results
>   → scatter-gather pattern → expensive at scale
>
> Solution: denormalize or duplicate data to avoid cross-shard queries
>            store city in user_id shard, accept data duplication
> ```
>
> **The golden rule:**
> ```
> Shard key = field you query by most often
>             should distribute evenly
>             should minimize cross-shard queries
> ```
>
> > [!tip] Interview framing
> > *"Date sharding creates hot shards — new users all hit the current shard. user_id modulo N distributes evenly. The trade-off: queries that need multiple users require scatter-gather across all shards. Choose the shard key based on your most common access pattern and minimize cross-shard operations."*

---

## Q3 — Auto-Scaling Design

> [!question] You're designing auto-scaling for a web service that gets daily traffic spikes at 9am when users start their day. How do you configure it?

> [!success]- Answer
>
> **The problem with reactive auto-scaling for known peaks:**
> ```
> 8:59am: normal traffic → 10 instances running
> 9:00am: traffic spikes 5x → CPU jumps to 90%
>
> Reactive auto-scaling:
>   CPU > 70% for 60 seconds → trigger scale-out
>   New instances take 90 seconds to boot and warm up
>   9:00am - 9:02am: traffic spike, under-provisioned → degraded latency
>   Users experience slow responses during the exact peak
> ```
>
> **Solution — predictive pre-scaling:**
> ```
> Scheduled scaling: at 8:45am, set minimum instances to peak capacity
>   → 15 minutes before spike → instances are warm and ready
>   → 9:00am: traffic arrives → already at capacity ✓
>   → No cold start on the critical path
> ```
>
> **Full configuration:**
> ```
> Pre-baked AMIs / container images (not installing packages at boot):
>   Boot time: 60-90 seconds (not 5 minutes)
>
> Warm pools (pre-initialized instances):
>   Keep 5 stopped-but-initialized instances ready
>   Can start in <30 seconds vs fresh boot
>
> Scale-out trigger: CPU > 70% for 60 seconds
>   → Quick response for unexpected spikes
>
> Scale-in trigger: CPU < 30% for 15 minutes
>   → Conservative — don't scale in during brief dips
>   → Connection draining: wait 30s for in-flight requests to complete
> ```
>
> **Stateless servers are required:**
> ```
> Auto-scaling only works cleanly with stateless servers
> Sessions in Redis → any instance can handle any user
> Scaling out/in doesn't affect users
> ```
>
> > [!tip] Interview framing
> > *"Reactive auto-scaling has cold-start lag — you're always behind the spike. For known daily peaks, pre-scale 15 minutes early. Configure scale-out at 70% CPU, scale-in conservatively at 30% for 15 minutes with connection draining. Pre-baked AMIs reduce boot time. Auto-scaling only works on stateless servers — sessions must be in Redis."*

---

## Q4 — Stateless vs Stateful Scaling Challenge

> [!question] Your gaming leaderboard service needs to be horizontally scaled. The leaderboard is currently maintained in memory on a single server. What's the problem and how do you redesign it?

> [!success]- Answer
>
> **The current problem:**
> ```
> Single server holds entire leaderboard in memory
>   → Single point of failure (server dies → leaderboard gone)
>   → Cannot scale horizontally (other servers don't have the data)
>   → As users grow, single server becomes CPU/memory bottleneck
> ```
>
> **Naive horizontal scaling fails:**
> ```
> Server A: holds Alice at rank 1
> Server B: holds Bob at rank 2
>
> User reads leaderboard:
>   Request routes to Server A → sees only Alice's rank
>   Request routes to Server B → sees only Bob's rank
>
>   No server has the full picture
> ```
>
> **The fix — externalize leaderboard state to Redis Sorted Set:**
> ```
> Redis Sorted Set: ZADD leaderboard 9500 "alice"
>                             ZADD leaderboard 9200 "bob"
>
> Any server: ZRANGE leaderboard 0 9 REV WITHSCORES → top 10
>
> App servers become stateless → horizontally scalable ✓
> Redis holds all leaderboard state
> ZADD is O(log N) → fast even at millions of entries
> ```
>
> **Redis HA for the leaderboard:**
> ```
> Redis Sentinel → automatic failover if Redis primary fails
> Redis Cluster  → shard if leaderboard is massive (unlikely for most games)
> ```
>
> **The key principle:**
> ```
> Anything in server memory = not horizontally scalable
> Move all shared state to Redis or the DB
> App servers become "computers that run code" — disposable, interchangeable
> ```
>
> > [!tip] Interview framing
> > *"In-memory state on a single server is a SPOF and a scaling blocker. Move leaderboard state to Redis Sorted Set — O(log N) operations, globally accessible, any server can read/write it. App servers become stateless and can scale independently. Redis Sentinel for HA."*

---

## Q5 — Read-Heavy vs Write-Heavy Design

> [!question] Two systems: a news feed (95% reads) and an analytics event collector (99% writes). How do your scaling strategies differ?

> [!success]- Answer
>
> **News feed — read-heavy (95% reads):**
>
> ```
> Bottleneck: DB can't handle millions of read queries/second
>
> Strategy: aggressive read optimization
>
> Layer 1: CDN for static content (articles, images)
>          → served at edge, never hits origin
>
> Layer 2: Redis cache in front of DB
>          → feed is pre-computed and cached per user
>          → cache TTL: 60 seconds for feed freshness
>          → 90%+ of reads served from cache
>
> Layer 3: Read replicas
>          → remaining DB reads spread across 5 replicas
>          → primary handles writes only
>
> Result: 1 primary DB handles all writes
>         thousands of reads per second from cache + replicas
> ```
>
> **Analytics event collector — write-heavy (99% writes):**
>
> ```
> Bottleneck: DB can't sustain millions of writes/second
>
> Strategy: absorb spikes, batch writes
>
> Layer 1: Kafka / SQS message queue in front of DB
>          → events written to Kafka in milliseconds
>          → DB consumes at its own pace (no spike absorption issue)
>          → provides durability guarantee (events persisted in Kafka)
>
> Layer 2: Batch writes
>          → consumer batches 1000 events, writes in one DB transaction
>          → reduces DB write amplification by 1000x
>
> Layer 3: Sharding by event type or time
>          → different event types to different shards
>          → avoids hot spots
> ```
>
> **The fundamental difference:**
> ```
> Read-heavy:  add caches and replicas (scale reads)
> Write-heavy: add queues and batching (absorb writes)
>
> Caching is useless for write-heavy systems — you can't cache writes
> Queues are unnecessary overhead for read-heavy systems
> ```
>
> > [!tip] Interview framing
> > *"Read-heavy: cache aggressively (Redis, CDN) and add read replicas — 90% of reads never touch the DB. Write-heavy: queue first (Kafka), batch DB writes, shard if needed. The strategies are completely different — applying cache-first to a write-heavy system solves the wrong problem."*
