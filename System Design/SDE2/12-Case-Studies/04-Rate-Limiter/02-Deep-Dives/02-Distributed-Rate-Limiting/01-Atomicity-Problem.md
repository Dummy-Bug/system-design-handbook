
## The Atomicity Problem

The base architecture has a single Redis node and multiple stateless rate limiter servers. Every rate limiter server talks to the same Redis. This is correct — shared state means all servers see the same counters. But there is a hidden problem: the counter check and the counter increment are two separate Redis operations.

---

## The Race Condition

Take Sliding Window Counter. To make an allow/block decision, the rate limiter needs to:

```
1. GET previous window counter
2. GET current window counter
3. Calculate estimate
4. If allowed → INCR current window counter
```

These are separate Redis commands. Redis is single-threaded — it executes one command at a time — but between command 2 and command 4, another rate limiter node can sneak in its own commands.

Here is what happens when two rate limiter nodes receive requests for the same user at the exact same millisecond:

```
State: prev = 8, curr = 2, limit = 5, overlap = 0.25

Node 1: GET prev → 8
Node 2: GET prev → 8         ← both reading simultaneously
Node 1: GET curr → 2
Node 2: GET curr → 2         ← both see curr = 2, Node 1 hasn't written yet

Node 1: estimate = (8 × 0.25) + 2 = 4 → 4 < 5 → allow → INCR curr
Node 2: estimate = (8 × 0.25) + 2 = 4 → 4 < 5 → allow → INCR curr

curr is now 4. But two requests got through when only one slot was available.
```

The problem: Node 2 read `curr = 2` before Node 1's INCR landed. Both calculated the same estimate. Both decided to allow. Both incremented. The limit was violated.

This is the classic **read-modify-write race condition**. Any time you read a value, make a decision based on it, and then write back — another process can read the same stale value between your read and your write.

---

## Why Separate Commands Can't Fix This

You might think: use Redis transactions (MULTI/EXEC).

```
MULTI
  GET prev
  GET curr
  INCR curr
EXEC
```

The problem: inside a MULTI/EXEC block you cannot make decisions. Commands are queued and executed blindly — you cannot say "only INCR if the estimate is below the limit." The GET results are only available after EXEC completes, by which time the INCR has already happened unconditionally.

MULTI/EXEC is useful for batching writes. It cannot solve conditional read-then-write atomicity.

---

## The Fix — Lua Scripts

Redis allows you to run custom logic written in Lua directly on the Redis server. The entire Lua script executes as a single atomic operation — Redis treats it as one custom command.

This works because of Redis's single-threaded execution model. Redis processes one command at a time. When it receives a Lua script, it runs the entire script from first line to last line before processing any other client command. Nothing can sneak in between lines of your script.

```
Normal separate commands:
  Node 1: GET curr      ← executes
  Node 2: GET curr      ← sneaks in between Node 1's GET and INCR
  Node 1: INCR curr     ← uses stale data, race condition

Lua script (EVALSHA):
  Node 1: script starts running
            GET prev
            GET curr
            calculate estimate
            INCR if allowed     ← nothing can interrupt between these lines
          script finishes
  Node 2: script starts running ← waits until Node 1's script is done
            GET prev
            GET curr            ← now sees the updated curr from Node 1
            ...
```

Redis queues all incoming commands. A Lua script is one item in that queue. It runs completely before the next item is dequeued.

---

## The Full Lua Script for Sliding Window Counter

```lua
-- KEYS[1] = previous window key  e.g. "user:abc:/search:29083334"
-- KEYS[2] = current window key   e.g. "user:abc:/search:29083335"
-- ARGV[1] = overlap fraction     e.g. "0.25"
-- ARGV[2] = limit                e.g. "5"
-- ARGV[3] = window TTL in secs   e.g. "60"

local prev_count = tonumber(redis.call('GET', KEYS[1])) or 0
local curr_count = tonumber(redis.call('GET', KEYS[2])) or 0
local overlap    = tonumber(ARGV[1])
local limit      = tonumber(ARGV[2])

local estimate = (prev_count * overlap) + curr_count

if estimate < limit then
    redis.call('INCR', KEYS[2])
    redis.call('EXPIRE', KEYS[2], ARGV[3])
    return 1  -- allow
end

return 0  -- block
```

`or 0` handles the case where the key doesn't exist yet — Redis GET on a missing key returns nil, and `tonumber(nil)` would crash. `or 0` defaults it to zero safely.

---

## How the Rate Limiter Calls It

The Lua script is loaded into Redis once on startup. Redis returns a SHA hash of the script. Every subsequent call uses the SHA — no need to send the full script text on every request at 400K QPS.

```java
// On startup — load once, store the SHA
String sha = redis.scriptLoad(luaScript);

// On every request — compute keys and args, call by SHA
long currentTs   = System.currentTimeMillis() / 1000;
long windowId    = currentTs / 60;
double overlap   = (60 - (currentTs % 60)) / 60.0;

String prevKey   = "user:" + userId + ":/search:" + (windowId - 1);
String currKey   = "user:" + userId + ":/search:" + windowId;

int result = redis.evalsha(sha, 
    List.of(prevKey, currKey),              // KEYS
    List.of(overlap, limit, windowTTL)      // ARGV
);

if (result == 1) allow();
else block();
```

One SHA string. Called 400K times per second. The script runs atomically on Redis each time.

---

## What the Atomicity Guarantee Looks Like Now

```
Node 1: EVALSHA → Redis runs entire script atomically
                    GET prev = 8
                    GET curr = 2
                    estimate = 4 < 5
                    INCR curr → curr = 3
                    return 1 (allow)
                  script done

Node 2: EVALSHA → Redis runs entire script atomically
                    GET prev = 8
                    GET curr = 3   ← sees Node 1's update
                    estimate = 5 >= 5
                    return 0 (block)
                  script done
```

No race condition. Node 2 sees the updated curr because Node 1's script completed before Node 2's script started. The limit is enforced exactly.

---

## Why Not Optimistic Locking?

A reasonable alternative is optimistic locking using Redis WATCH. The idea: watch the key before reading, then in MULTI/EXEC check if the key changed — if it did, abort and retry.

```
WATCH curr
GET prev → 8
GET curr → 2
estimate = 4 < 5
MULTI
  INCR curr
EXEC  ← if curr changed since WATCH, returns nil → retry
```

This works correctly. But at 400K QPS it has a performance problem.

When two nodes both WATCH the same key and race to EXEC:

```
Node 1: WATCH curr
Node 2: WATCH curr
Node 1: GET curr → 2
Node 2: GET curr → 2
Node 1: EXEC ✓  (curr changes to 3)
Node 2: EXEC ✗  (curr changed since WATCH → transaction aborted)
```

Node 2's transaction aborts. It must retry — read again, recalculate, WATCH again, try EXEC again. If a third node also raced, that one aborts too and retries. If traffic is high and many nodes are hitting the same user's key simultaneously, you get a **retry storm** — the more contention, the more retries, the more contention. The system gets slower exactly when it needs to be fastest.

Lua script has no retries. Redis runs the entire script atomically on the first attempt, every time. No WATCH, no abort, no retry loop. At high QPS under contention, Lua script is strictly better than optimistic locking.
