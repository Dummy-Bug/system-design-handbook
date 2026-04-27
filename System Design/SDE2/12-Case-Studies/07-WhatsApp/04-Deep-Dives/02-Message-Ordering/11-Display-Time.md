
> [!info] Display time and ordering time are completely separate concerns
> seq_no handles ordering. Timestamp handles display. They use different data, serve different purposes, and have different accuracy requirements.

---

## The question that surfaces late

Once you've decided that `seq_no` handles ordering and client timestamp is stored as a display attribute, a natural question comes up: who fills the timestamp field? The client? The server? And what does the recipient actually see?

---

## Client fills the timestamp — always

The timestamp represents **when the sender sent the message, from their perspective.** Alice hit send at what her phone said was 4:20 PM. That is the experience Alice had. That is the time that should appear under her message.

If the server overrides it to 4:30 PM (server time), Alice sees her own message stamped 10 minutes in the future. That is confusing and wrong from a UX perspective.

```
Alice's phone: 4:20 PM
Alice hits send → timestamp=4:20 stored in DynamoDB
Bob receives message → reads timestamp=4:20 from DB → displays "4:20 PM"
```

The server never touches the timestamp field. It is written once by the sender's client and stored as-is.

---

## What the recipient sees

Bob receives Alice's message. His client reads the `timestamp` attribute from the message payload — Alice's stored timestamp. Bob's own clock is irrelevant for displaying incoming messages.

```
Alice's stored timestamp: 4:20 PM
Bob's current clock:      4:10 PM  (Bob's phone is behind)

Bob's UI shows:  "4:20 PM"   ← Alice's stored time, not Bob's clock
```

This is the correct behavior. The timestamp on a message represents when it was sent, not when it was received. Every major messaging app — WhatsApp, iMessage, Telegram — works this way.

---

## The cosmetic bug that cannot be fixed

Here is the unavoidable edge case. Alice's clock is correct at 4:20. Bob's clock is 1 second behind at 4:19:59. Bob replies to Alice's message.

```
Alice sends "hey"     → timestamp stored: 4:20:00   seq=1
Bob replies "hi"      → timestamp stored: 4:19:59   seq=2
```

Alice's client renders the conversation sorted by seq:

```
seq=1  Alice: "hey"    4:20:00
seq=2  Bob:   "hi"     4:19:59   ← reply appears 1 second before the original message
```

Bob's reply shows a timestamp 1 second earlier than Alice's original message. A reply before the question, visually.

**This is a known cosmetic limitation of client-side timestamps.** It cannot be fixed without forcing all clients to use server-assigned timestamps for display — which creates the other problem of a message showing a time that doesn't match what the sender's phone said.

---

## Why it doesn't matter

1. **The ordering is correct.** seq=1 is before seq=2. The messages render in the right order. The only thing that looks off is the timestamp label — not the position of the messages.

2. **1 second of clock skew is imperceptible in a real conversation.** Nobody is going to notice "4:19:59" vs "4:20:00" when messages are flying back and forth. They read the content, not the timestamp.

3. **WhatsApp has this exact bug in production.** If your phone clock is behind, your sent messages will show a time that appears before the previous message's timestamp. It is a cosmetic artifact of using client timestamps for display. It ships anyway because the fix — server timestamps for display — creates a worse user experience (your messages show a time you didn't see on your phone).

---

## The full separation of concerns

```
seq_no      → ordering (who came first in the conversation?)
              assigned by server via Redis INCR
              stored as DynamoDB sort key
              accurate to the logical sequence, not wall-clock time

timestamp   → display (what time label shows under the message?)
              filled by sender's client
              stored as DynamoDB attribute
              accurate to sender's local experience, not globally precise
```

These two fields answer two different questions. Conflating them — using timestamp for ordering, or using seq for display — gets you a broken system. Keep them separate.

> [!tip] Interview framing
> "Timestamp is a display attribute only — the sender's client fills it with their local clock, we store it as-is. seq_no handles ordering. There's a known cosmetic issue where a reply can show a timestamp 1 second before the original message if the replier's clock is slightly behind. That's acceptable — the ordering is correct, the display is just slightly off. WhatsApp ships with this same limitation."
