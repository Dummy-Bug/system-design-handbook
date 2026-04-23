
> [!info] How the mutual rule enforces itself — no server changes needed
> Each client checks its own setting before sending read events. The mutual rule falls out naturally.

---

## The elegant part

The mutual rule — "turn off read receipts, lose others' read receipts too" — sounds like it requires complex server logic to enforce. It doesn't.

It enforces itself entirely through one simple rule applied symmetrically on every client:

> **Each client checks its own read receipts setting before sending a read event.**

That's it. No server enforcement. No flag checking on receive. No special handling for mutual scenarios. Just one rule, applied by every client, for their own setting.

---

## Tracing through the scenarios

**Scenario 1 — Bob has read receipts OFF, Alice has read receipts ON**

```
Bob opens Alice's message
→ Bob's client checks: read_receipts_on = false
→ Bob's client: do not send read event
→ Server: no update to last_read_seq
→ Alice's client: never receives blue tick event
→ Alice sees: double grey tick (delivered, not read)

Alice opens Bob's message
→ Alice's client checks: read_receipts_on = true
→ Alice's client: send read event
→ Server: would update last_read_seq for Alice in Bob's conversation
→ Bob's client: receives blue tick event
→ But Bob turned off read receipts — so Bob also can't see this event?
```

Wait — this is where the mutual rule needs one more piece. Bob turned off read receipts. Does he still receive blue tick events from Alice?

---

## The second half of the mutual rule

When Bob turns off read receipts, two things happen:

1. Bob's client stops **sending** read events (Alice can't see his blue ticks)
2. Bob's client stops **rendering** blue tick events it receives (Bob can't see Alice's blue ticks)

```
Alice sends read event for Bob's message
→ Server: updates last_read_seq, pushes blue tick event to Bob
→ Bob's client receives event
→ Bob's client checks: read_receipts_on = false
→ Bob's client: ignore this event, do not render blue tick
→ Bob sees: double grey tick on his sent messages (never blue)
```

The server still processes Alice's read event — because Alice's setting is ON. But Bob's client silently discards the incoming blue tick event.

---

## The full symmetric picture

```
Bob's setting: OFF
Alice's setting: ON

Bob reads Alice's message:
  Bob's client → does not send read event
  Alice: never sees blue tick on her messages to Bob ✓

Alice reads Bob's message:
  Alice's client → sends read event (her setting is ON)
  Server → pushes blue tick event to Bob
  Bob's client → receives event, discards it (his setting is OFF)
  Bob: never sees blue tick on his messages to Alice ✓
```

Both sides of the mutual rule are enforced. Neither requires server changes. The server is completely unaware of the mutual rule — it just processes events and pushes updates. The clients handle the rest.

---

**Scenario 2 — Both have read receipts OFF**

```
Bob reads Alice's message → Bob's client: does not send read event → Alice: no blue tick
Alice reads Bob's message → Alice's client: does not send read event → Bob: no blue tick

Result: neither sees blue ticks. Full mutual privacy.
```

**Scenario 3 — Both have read receipts ON (default)**

```
Bob reads → sends read event → Alice sees blue tick
Alice reads → sends read event → Bob sees blue tick

Result: full visibility both ways. Default behaviour.
```

---

## Why this design is elegant

The mutual rule requires zero special-casing on the server. The server doesn't know about read receipt settings. It just:
- Receives read events (when clients send them)
- Updates last_read_seq
- Pushes blue tick events to the sender

All the privacy logic lives on the clients. Each client manages its own behaviour based on its own setting. The mutual rule is a property that emerges from symmetric client behaviour — not something the server enforces.

```
Server knows nothing about privacy settings
Client sending: check own setting before sending
Client receiving: check own setting before rendering
Mutual rule: emerges automatically from both sides doing the same check
```

> [!tip] Interview framing
> "The mutual rule enforces itself. Each client checks its own read receipts setting in two places: before sending read events, and before rendering incoming blue tick events. The server is unaware — it just processes what it receives. No server-side flag checking, no special mutual rule logic. Symmetric client behaviour produces the mutual rule as a natural consequence."
