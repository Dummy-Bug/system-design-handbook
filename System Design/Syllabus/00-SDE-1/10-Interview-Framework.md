# Interview Framework

> This is how you present everything you've learned. Knowing the theory is not enough.
> A candidate who knows every topic but cannot structure 35 minutes will still not get strong hire.

---

## The Time Structure

| Time | Step | What to do |
|---|---|---|
| 0–5 min | Requirements | Clarify functional + non-functional, define scope |
| 5–8 min | Estimation | QPS, storage — use numbers to justify architecture |
| 8–13 min | API Design | Key endpoints, request/response, idempotency |
| 13–25 min | High-Level Design | Core components, read path, write path |
| 25–35 min | One Deep Dive | Pick the hardest component and go deeper |

> SDE-1 interviews are 30–45 min. You rarely get two deep dives. Pick the most interesting one and go deep on that.

---

## Step 1 — Requirements Clarification

Never start designing without asking these. Interviewers want to see that you don't assume.

**Functional questions (what the system does):**
- What are the core features? Which ones are in scope for today?
- Are there any features I should explicitly leave out?
- Who are the users — consumers, businesses, internal teams?

**Non-functional questions (how the system behaves):**
- How many daily active users are we designing for?
- What's the expected read vs write ratio?
- Do we need strong consistency or is eventual consistency okay?
- What latency is acceptable — real-time (chat) or a few seconds okay (email)?
- Single region or global?
- What availability do we need — 99.9% or 99.99%?

> You don't need to ask all of these. Pick 3–4 that are most relevant to the system. The goal is to show you know what drives architecture decisions.

---

## Step 2 — Estimation

Keep it short — 2–3 minutes. The goal is not precision, it's to justify your design choices.

**Always estimate:**
1. DAU and what each user does per day
2. Read QPS and Write QPS (separately)
3. Storage growth per year

**Always connect the number to a decision:**
- "Read QPS is ~50K/sec — that means we need caching"
- "Storage is 3.6 TB/year — we'll need to shard after year 2"
- "Write QPS is only 1,200/sec — a single primary DB can handle this"

If estimation doesn't change your architecture, you estimated the wrong things.

---

## Step 3 — API Design

Define 2–3 key endpoints. Don't try to define every endpoint — pick the ones that drive the design.

For each endpoint state:
- Method + URL
- Request parameters or body
- Response structure
- Any idempotency consideration (POST that creates something needs an idempotency key)

Example for URL Shortener:
```
POST /urls
Body: { long_url: "..." }
Response: { short_code: "abc123" }

GET /{short_code}
Response: 301 redirect to long_url
```

---

## Step 4 — High-Level Design

Draw the components and the data flow. Always cover:

- [ ] Client
- [ ] Load Balancer / API Gateway
- [ ] Application servers (stateless)
- [ ] Cache layer (Redis — what do you cache and why)
- [ ] Primary database (what type and why)
- [ ] Object storage if media is involved

State the read path and write path separately if they differ.

**The move every interviewer wants to see:**
State your DB choice AND justify it.
- "I'm using PostgreSQL because we need ACID guarantees for financial data"
- "I'm using Redis sorted set for the leaderboard because ZRANK gives O(log n) rank lookup"

---

## Step 5 — One Deep Dive

Pick the single hardest or most interesting component and go deeper. At SDE-1 the bar is:

- Explain what problem the component solves
- Explain how it works (key steps or data structures)
- Explain one thing that can go wrong and how you'd handle it

Good deep dive candidates:
- ID generation / short code generation (URL Shortener, Pastebin)
- Redis sorted set internals (Leaderboard)
- Feed generation — pull vs push (Social Feed)
- Cache stampede and how to prevent it (any system with caching)

---

## NFR → Architecture Decision Cheat Sheet

| NFR | What you do |
|---|---|
| Read-heavy | Add caching (Redis), add read replicas |
| Write-heavy | Async writes, write-optimized DB |
| Low latency | Cache hot data, CDN for static assets |
| High availability | Remove SPOFs, redundancy at every layer |
| Strong consistency | Single primary DB, avoid async replication |
| Eventual consistency OK | Read replicas fine, cache with TTL fine |
| Large media files | Object storage (S3), not DB |

---

## What SDE-1 Strong Hire Looks Like at FAANGM

The interviewer is asking: **"Could this person build this system with some mentorship?"**

Strong hire signals:
- Asks the right clarifying questions before touching the whiteboard
- Estimates something and uses the number to make a decision
- Names a technology AND says why ("Redis sorted set because ZRANK is O(log n)")
- Proactively mentions one tradeoff ("the downside of cache-aside is stale data for up to TTL seconds")
- Identifies one failure mode ("what if the cache node goes down?")
- Communicates clearly — the interviewer can follow your thinking without asking you to explain every sentence

---

## What to Say When You Don't Know

Interviewers test this deliberately. They will push you past what you know.

**The right move:**
State what you know, state what you don't, reason from first principles.

> "I'm not sure of the exact internals of how Cassandra handles this, but I know it's a write-optimized column-family store, so my instinct is it would handle the write throughput better than PostgreSQL here. I'd want to validate the consistency tradeoffs before committing."

This is better than guessing confidently and being wrong. Interviewers know you don't know everything — they're testing how you handle uncertainty.

**Never go silent.** Think out loud even when you're stuck.

---

## 5 Most Common SDE-1 Mistakes

1. **Starting to design before clarifying requirements** — jump straight to the whiteboard, miss a key constraint, design the wrong system

2. **Naming a technology without knowing why** — "use Kafka" → interviewer asks why → silence. If you don't know why, don't say it.

3. **Forgetting the data model** — drawing boxes and arrows but never defining what the DB schema looks like. Schema reveals your thinking.

4. **Not connecting estimation to architecture** — doing math for the sake of math. Every number must lead to a decision.

5. **Going silent under pressure** — the worst thing you can do. Think out loud. A wrong answer you reason through shows more than a correct answer you can't explain.
