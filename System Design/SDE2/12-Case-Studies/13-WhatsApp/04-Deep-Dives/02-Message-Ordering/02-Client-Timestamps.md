
> [!info] The obvious solution — use the timestamp the client generated when the user hit send
> Every phone has a clock. Alice's phone knows it's 4:20 PM. Why not just stamp each message with that time and sort by it?

---

## Why client timestamps seem like a good idea

When Alice sends a message, her phone generates a timestamp at the moment she hits send. This timestamp is attached to the message and travels with it to the server and then to Bob.

Bob's client receives the messages with their timestamps intact and sorts by them:

```
m1 → timestamp: 4:20:00.100
m2 → timestamp: 4:20:00.101
m3 → timestamp: 4:20:00.102

After sort: m1, m2, m3 → correct order
```

Simple. No server involvement needed for ordering. Seems to work.

---

## The problem — you cannot trust a client's clock

Client timestamps assume that Alice's phone clock is accurate. But phones are not atomic clocks. They drift. A phone that hasn't synced with NTP recently can be seconds, minutes, or even hours off. A user who manually sets their phone clock to the wrong time will have completely wrong timestamps.

```
Alice's actual time: 4:20 PM
Alice's phone clock: 4:10 PM  (10 minutes behind)

Message stamped with: 4:10 PM
Stored in DB as:      4:10 PM
Displayed to Bob as:  4:10 PM
```

Bob sees a message that claims to have been sent at 4:10, even though the real time was 4:20. Slightly annoying, but manageable in isolation.

The real problem shows up when two different clients are talking to each other — and their clocks disagree.

> [!danger] Never trust a client for anything that requires global accuracy
> Clients lie — not maliciously, just because clocks drift and users can set them manually. Any ordering mechanism that relies on client-generated timestamps is broken by design.
