# Consistency Models — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of the consistency spectrum, eventual consistency, and when each model applies. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is Consistency in a Distributed System?

> [!question] What does "consistency" mean in a distributed system? Why is it harder than in a single-server system?

> [!success]- Answer
>
> **In a single-server system:**
> Consistency is simple — one place stores the data. Read it, you always get the latest value. Write it, the next read sees the write.
>
> **In a distributed system:**
> Data is replicated across multiple nodes for availability and performance. The problem: after a write to node A, how long until node B has the same value?
>
> ```
> User writes: "username = Alice" → goes to Node A
> Node A replicates to Node B (takes ~50ms)
>
> 10ms later, user reads from Node B:
>   Consistent: "Alice" ✓
>   Inconsistent: old value (stale) ✗
> ```
>
> **Consistency in distributed systems means:**
> How current does a read need to be? Does every read see the latest write? Or is slight staleness acceptable?
>
> ```
> Strong consistency → every read sees the latest write, from any node
> Eventual consistency → replicas converge eventually — reads may be stale temporarily
> ```
>
> The challenge: strong consistency requires coordination between nodes on every operation — which adds latency. Eventual consistency is faster but readers may see stale data.
>
> > [!tip] Interview framing
> > *"Consistency in a distributed system is about whether reads see the latest writes across all nodes. It's harder because data is replicated — after a write to one node, others may be momentarily behind. Strong consistency is correct but slower. Eventual consistency is fast but may serve stale data."*

---

## Q2 — The Consistency Spectrum

> [!question] Name the consistency models from weakest to strongest. Give a one-line description of each.

> [!success]- Answer
>
> **From weakest to strongest:**
>
> ```
> Eventual          → replicas converge eventually, no guarantee on when
>                     "you'll see the write... sometime"
>
> Read-Your-Writes  → you always see your own writes
>                     other users may still see stale data
>
> Monotonic Reads   → time never goes backwards for a user
>                     you won't see an older value after seeing a newer one
>
> Causal            → causally related operations seen in correct order by everyone
>                     "reply appears after the message it replies to"
>
> Strong            → every read sees the latest write (quorum-based)
>                     all nodes agree before any read succeeds
>
> Linearizable      → strong + real wall-clock time ordering
>                     matches actual real time, not just internal ordering
> ```
>
> **Each level includes all guarantees of weaker levels to its right.**
>
> **Quick real-world mapping:**
> ```
> Eventual          → Instagram like count
> Read-Your-Writes  → Your own Instagram profile
> Monotonic Reads   → Twitter timeline
> Causal            → WhatsApp chat messages
> Strong            → Bank balance
> Linearizable      → Google Spanner (global financial)
> ```
>
> > [!tip] Interview framing
> > *"Spectrum from weakest to strongest: Eventual → Read-Your-Writes → Monotonic Reads → Causal → Strong → Linearizable. The key question for any system is: what does it cost to show stale data? Feed counts → nothing. Bank balance → financial loss."*

---

## Q3 — Eventual Consistency

> [!question] What is eventual consistency? When is it acceptable and when is it dangerous?

> [!success]- Answer
>
> **What it is:**
> All replicas will eventually converge to the same value — but there's no guarantee on how quickly, or whether a read will see the latest write right now.
>
> ```
> User A likes a post:   write goes to replica 1
> User B reads the post: served from replica 2
>
> Replica 2 hasn't synced yet
> User B sees: 1,240 likes (instead of 1,241)
>
> After a few seconds: all replicas sync → User B now sees 1,241
> ```
>
> **When eventual consistency is acceptable:**
> ```
> ✓ Social feed like counts    → off by a few is unnoticeable
> ✓ View counters              → 1.24M vs 1.241M — users don't care
> ✓ Shopping cart              → better to stay available with slight staleness
> ✓ Product recommendations    → slight delay in personalisation is fine
> ✓ User activity feeds        → a few seconds delay acceptable
> ```
>
> **When eventual consistency is dangerous:**
> ```
> ✗ Bank balance               → user sees $1000, spends $900, balance is actually $200
>                                decision made on stale data = financial loss
> ✗ Inventory counts           → user adds last item, it's already sold
>                                oversell → cancelled order → broken trust
> ✗ Hotel/seat booking         → both users see "1 available" → double booking
> ✗ Distributed locks          → two services both think they hold the lock
> ```
>
> > [!important] The cost of stale data determines whether eventual consistency is safe. If stale data causes financial loss, double booking, or incorrect actions — you need stronger consistency.
>
> > [!tip] Interview framing
> > *"Eventual consistency is fine when staleness is harmless — like counts, feeds, analytics. It's dangerous when stale data drives user decisions — balance checks, inventory, bookings. The question to ask: what does a user do with this data, and what happens if it's slightly wrong?"*

---

## Q4 — Read-Your-Writes

> [!question] What is the read-your-writes consistency guarantee? What breaks when it's violated?

> [!success]- Answer
>
> **Read-your-writes:**
> After you write something, your subsequent reads will always see that write — even if other users may still see the old value.
>
> ```
> You update your username to "AliceNovak"
> You immediately visit your profile page
>
> With read-your-writes:   "AliceNovak" ✓
> Without read-your-writes: "Alice" ← served from stale replica
>                           Looks like the change failed
> ```
>
> **What breaks when violated:**
>
> **Users think their actions didn't work:**
> ```
> User posts a photo → immediately views profile → photo not there
> → "Did it save?" → posts again → now has duplicate posts
>
> User changes password → logs out → logs back in with new password → rejected
> → "My password change didn't work" → contacts support
> ```
>
> **Especially bad for write-then-read patterns:**
> ```
> Submit form → redirect to confirmation page that reads what you just wrote
> If replica hasn't synced → confirmation shows empty/old data
> ```
>
> **How to enforce it:**
> ```
> Option 1: always read from primary after write (performance cost)
> Option 2: sticky sessions — route user to same replica consistently
> Option 3: version tokens — carry write version in cookie, reject if replica is behind
> ```
>
> > [!tip] Interview framing
> > *"Read-your-writes ensures you see your own changes immediately. Violated when writes go to primary and reads route to a stale replica. Users think their action failed and repeat it. Fix: route user reads to the same node they just wrote to, or carry a version token in their session."*

---

## Q5 — Causal Consistency

> [!question] What is causal consistency? Give a chat application example where violating it causes a visible problem.

> [!success]- Answer
>
> **Causal consistency:**
> Operations that are causally related must be seen in the correct order by all nodes. A reply must appear after the message it replies to. A comment must appear after the post it's commenting on.
>
> ```
> Alice posts: "Anyone want pizza for lunch?"
> Bob replies: "Yes! Let's do it."
>
> Causal relationship: Bob's reply DEPENDS ON Alice's post
> Alice's post must be seen before Bob's reply — always, by everyone
> ```
>
> **What happens without causal consistency:**
> ```
> Replica 1 syncs Bob's reply before Alice's post
> User C (reading from replica 1) sees:
>
>   "Yes! Let's do it."    ← Bob's reply
>   "Anyone want pizza?"   ← Alice's post (appears after reply)
>
> The reply appears before the message it's replying to
> → Conversation is incoherent → user is confused
> ```
>
> **More examples of causal relationships:**
> ```
> Comment appears before the post it comments on
> Message edited appears before the original message
> "User followed" notification appears before any content from that user
> ```
>
> **Why not strong consistency for chat?**
> ```
> WhatsApp has 2 billion users
> Strong consistency requires quorum — wait for majority of nodes to confirm
> On a poor network connection → user's messages are delayed or blocked
> Better: causal consistency — messages still deliver, just in correct causal order
> ```
>
> > [!tip] Interview framing
> > *"Causal consistency ensures operations with cause-effect relationships are seen in the right order. Chat needs this: a reply must appear after its parent message. Strong consistency would work but is overkill — it blocks during poor network conditions. Causal lets messages flow freely while preserving order."*
