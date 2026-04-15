
> [!info] What happens when a message is routed to a dead server
> Between server 7 dying and the cleaner removing stale registry entries, there is a window where messages get routed to a dead server. The fallback is the offline delivery system — the same mechanism used for genuinely offline users.

---

## The inconsistency window

Server 7 dies at 00:00:00. The cleaner runs at 00:00:45 (after monitoring detects the failure). In those 45 seconds:

- Alice is reconnected to server 3
- Her registry entry still says `user:alice → server7`
- Bob sends Alice a message at 00:00:20

The app server reads the registry, sees server 7, and tries to deliver:

```
App server → HTTP POST to server7 → connection refused (server is dead)
```

What does the app server do now?

---

## The fallback — treat as offline

A failed delivery to a dead server is indistinguishable from a user being offline. The app server can't reach Alice right now, for whatever reason.

The existing offline delivery system handles exactly this:

```
App server → routes to server7 → connection refused
→ treat Alice as offline
→ write message to pending_deliveries table
→ return delivery ack to Bob (message queued)

45 seconds later:
→ cleaner removes stale server7 entries
→ Alice's reconnect to server3 has already written new registry entry
→ delivery worker reads pending_deliveries
→ looks up registry: user:alice → server3   (fresh entry)
→ routes to server3 → Alice receives message
```

Alice receives the message within a minute of server 7 dying. Bob's message was never lost.

---

## The registry update race

There's a subtle timing detail here. Alice reconnects to server 3 almost immediately after server 7 dies. Her new registry entry (`user:alice → server3`) is written via Kafka — arriving within a few seconds.

The cleaner runs at ~45 seconds. By then, Alice's registry already points to server 3 (the new entry overwrote the stale server 7 entry when the Kafka consumer processed it).

So in practice, the window where Alice has a stale registry entry is much shorter than 45 seconds — it's however long the Kafka consumer lag is (seconds, not tens of seconds).

```
Server 7 dies at T=0
Alice reconnects to server 3 at T=2
Kafka consumer writes user:alice → server3 at T=5
Cleaner runs at T=45 (but registry is already clean for Alice by T=5)
```

> [!tip] Interview framing
> "When the app server can't reach a connection server, it falls back to pending_deliveries — same as offline delivery. The message is never lost. The delivery worker retries once the registry is updated, which happens within seconds via the Kafka consumer."
