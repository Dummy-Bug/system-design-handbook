
> [!info] Custom aliases give users control over their short code — but every user-provided input is an attack surface.
> Validate early, check reserved words fast, check availability last.

---

## What Custom Aliases Are

Instead of a system-generated code like `a3kZ9m`, the user can request a memorable alias: `pastebin.com/my-config`, `pastebin.com/deploy-notes`, `pastebin.com/team-standup`.

Custom aliases must be:
- URL-safe
- Unique (not already taken)
- Not conflicting with system routes

---

## Validation Flow

When a user provides a `customAlias` in the POST body, the app server runs three checks in order before accepting it:

```
1. Format validation (app server, no DB/Redis needed)
   - Base62 characters only (a-z, A-Z, 0-9)
   - Length: 1–8 characters
   - No spaces, hyphens, slashes, emoji, special chars
   → Fail: 400 Bad Request immediately

2. Reserved word check (Redis SET lookup — O(1))
   - Words like: admin, api, health, login, logout, static, assets, docs
   - These conflict with your own API routes and system paths
   → Fail: 400 "alias not available"

3. Availability check (Postgres lookup on short_code PK)
   - Does a paste already exist with this short_code?
   → Fail: 409 Conflict "alias already taken"
   → Pass: use it as short_code, skip Redis INCR counter
```

Checks are ordered cheapest-first. Format validation costs nothing — pure string check on the app server. Reserved word check hits Redis — sub-millisecond, no DB round-trip. Availability check hits Postgres — only runs if the alias passed the first two checks.

---

## Reserved Words in Redis

The reserved words list lives in a Redis SET. On startup, app servers load the list from DB into Redis. Checks are O(1):

```
SISMEMBER reserved_words "admin"  → 1 (reserved, reject)
SISMEMBER reserved_words "my-cfg" → 0 (not reserved, continue)
```

The list is small (hundreds of words at most) and rarely changes. Backed by Postgres for persistence — if Redis restarts, the app server reloads the list from DB on startup.

---

## Overlap Risk — Custom Alias vs Generated Codes

The Redis counter generates codes like `000001`, `000002`, `a3kZ9m`. A user could request a custom alias that happens to be a future counter value — for example, requesting `000042` as a custom alias.

Two scenarios:

**Scenario A — Custom alias requested before counter reaches that value:**
User gets `000042` as their alias. Later, counter increments to 42 and tries to use `000042`. The Postgres INSERT fails (unique constraint on short_code). App server retries with the next counter value. One retry, no data corruption.

**Scenario B — Counter already issued `000042`:**
The availability check (step 3) catches this — `000042` already exists in pastes. User gets 409 Conflict. They must choose a different alias.

The unique constraint on `short_code` is the safety net. It catches any overlap regardless of source. The system never silently overwrites an existing code.

---

## Why Custom Aliases Don't Use the Redis Counter

When a custom alias is accepted, the app server uses it directly as the `short_code` — it does NOT call Redis INCR. The counter is only for system-generated codes. Custom aliases bypass the counter entirely and go straight to the Postgres INSERT.

This means the counter doesn't "know" about custom aliases. That's fine — the counter's job is generating unique codes for the system-generated path. The Postgres unique constraint handles the rest.

---

> [!tip] Interview framing
> "Custom alias validation in three steps: format check (Base62, 1-8 chars) on app server, reserved word check against Redis SET, availability check against Postgres PK. Cheapest checks first. Reserved words block system paths like /admin and /api. Overlap between custom aliases and generated codes handled by Postgres unique constraint — INSERT fails, counter retries with next value. Custom aliases bypass the Redis counter entirely."
