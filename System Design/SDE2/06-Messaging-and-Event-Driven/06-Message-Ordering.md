# Message Ordering

> [!info] Queues do not guarantee message ordering by default — especially when multiple workers are consuming in parallel. Ordering must be designed explicitly, using a combination of client-side sequence numbers and server-side timestamps.

---

## The problem

You have a chat app. User Alice sends three messages in a conversation:

```
1. "hey"
2. "how are you"
3. "you there?"
```

These need to arrive at Bob's screen in exactly that order. If Bob sees "you there?" before "hey" — the experience is broken.

Now your queue has multiple workers consuming messages in parallel:

```
Worker A gets "you there?"   → processes fast → done
Worker B gets "how are you"  → processes slow → done
Worker C gets "hey"          → processes slow → done

Result at Bob's screen: "you there?", "how are you", "hey"  ← completely wrong
```

Multiple workers processing in parallel destroys ordering. The queue hands out messages as fast as it can — it doesn't care which worker finishes first.

---

## Why client timestamps alone don't work

First instinct: stamp each message with the client's clock, sort by timestamp at the consumer.

The problem: the network doesn't guarantee delivery order. "hey" might leave Alice's phone first but arrive at the server after "how are you" due to network jitter. And client clocks are unreliable — two users' phones can be slightly out of sync, making cross-user timestamp comparison meaningless.

---

## Why server timestamps alone don't work either

Second instinct: let the server stamp messages as they arrive.

The problem: the server receives messages in whatever order the network delivers them. If "how are you" arrives before "hey" at the server, the server assigns it a lower sequence number — wrong order preserved forever.

---

## The right solution — client sequence numbers + server timestamps

You need both working together.

**Step 1 — Client assigns sequence numbers per sender per conversation**

Each sender maintains a counter for each conversation they're participating in. Every message they send gets the next number in that counter.

```
Alice sending in conv_id: 123:
"hey"         → sender: Alice, conv_id: 123, client_seq: 1
"how are you" → sender: Alice, conv_id: 123, client_seq: 2
"you there?"  → sender: Alice, conv_id: 123, client_seq: 3
```

The `(conv_id, sender, client_seq)` triple uniquely identifies a message's intended position. Even if the network delivers them out of order, the server can reorder them correctly.

**Step 2 — Server reorders by client_seq before storing**

```
Server receives in order: client_seq 2, then 3, then 1
Server sorts by client_seq → 1, 2, 3
Server stores in correct order, assigns server-side IDs
```

**Step 3 — Interleaving messages from multiple senders**

The sequence number is per sender — Alice has her own counter, Bob has his own. To display the full conversation correctly, the server uses its own timestamp to interleave both senders' messages.

```
Alice sends in conv_id: 123:
"hey"           → sender: Alice, client_seq: 1, server_ts: 10:00:00.050
"how are you"   → sender: Alice, client_seq: 2, server_ts: 10:00:00.150
"you there?"    → sender: Alice, client_seq: 3, server_ts: 10:00:00.400

Bob replies in conv_id: 123:
"yeah I'm here" → sender: Bob,   client_seq: 1, server_ts: 10:00:00.250
"what's up?"    → sender: Bob,   client_seq: 2, server_ts: 10:00:00.350

Final conversation sorted by server_ts:
1. Alice: "hey"           (10:00:00.050)
2. Alice: "how are you"   (10:00:00.150)
3. Bob:   "yeah I'm here" (10:00:00.250)
4. Bob:   "what's up?"    (10:00:00.350)
5. Alice: "you there?"    (10:00:00.400)
```

The client_seq guarantees each sender's messages are in the right relative order. The server timestamp interleaves the two senders correctly.

---

## Can a queue guarantee ordering natively?

Most simple queues — no. When you have multiple workers consuming in parallel, ordering is destroyed. The solution is to design ordering at the application level as described above.

Some advanced systems like Kafka handle this differently. Kafka guarantees ordering within a **partition** — all messages with the same partition key (e.g. conv_id) go to the same partition and are consumed in order by one consumer. This means one worker handles all messages for a given conversation, preserving order natively. But that's a Kafka-specific mechanism covered in the Kafka deep dive.

---

## Summary of the ordering strategy

| Layer | Responsibility |
|---|---|
| Client | Assigns `client_seq` per sender per conversation |
| Network | Delivers in any order — unreliable |
| Server | Reorders by `client_seq` before storing; uses `server_ts` to interleave senders |
| Consumer | Reads messages already in correct order from storage |

> [!tip] **Interview framing:** "For message ordering in a chat system, I'd have each client assign a sequence number per conversation. The server reorders on arrival using the client sequence number before storing. For interleaving messages from different senders in the same conversation, I'd use the server-assigned timestamp as the canonical order — client clocks are unreliable."

> [!danger] Never rely on client-side timestamps for ordering across different senders. Two devices' clocks can drift. Always use server-side timestamps as the canonical interleaving mechanism.
