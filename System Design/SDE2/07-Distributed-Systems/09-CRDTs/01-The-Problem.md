
> [!info] The core idea
> Vector clocks can detect concurrent writes but cannot resolve them. Last write wins loses data silently. CRDTs solve this by designing data structures that can always merge concurrent writes automatically — without coordination, without losing anyone's work.

---

## The setup

Two users are editing the same Google Doc at the same time on different servers. Both make changes. The changes need to be merged.

If the edits are causally related — one happened after the other — vector clocks tell us the order and we apply them sequentially. No conflict, no problem.

But what if both users type at the exact same time with no communication between them? Vector clocks detect this as **concurrent**. Now you have two conflicting edits to the same document. How do you merge them?

---

## Why last write wins is not acceptable

The naive approach is last write wins — whoever's write has the higher timestamp survives, the other gets discarded.

Say User 1 types "Hello" and User 2 types "World" at the same position at the same time. Last write wins keeps "World" and silently throws away "Hello." User 1 never even knows their work was lost.

In a spreadsheet that might be acceptable in some cases. But in Google Docs — imagine writing an entire paragraph and it just disappears because someone else typed at the same time. That's a broken product.

> [!danger] Last write wins = silent data loss
> The user whose write got discarded has no idea it happened. Their screen still shows their text. The server quietly threw it away. This is not a merge — it's data corruption.

---

## "But Google Docs shows me the other person's cursor"

Yes — that's a UI feature, not a consistency guarantee. Google Docs shows a cursor with the other person's name as a visual hint. But it doesn't actually prevent two people from typing at the same position at the same time.

Think about it — you and your friend are both typing fast. The UI shows their cursor but network lag means you don't see their cursor move in real time. By the time you see them typing at the same spot, you've already typed there.

The cursor indicator reduces the chance of conflicts — it doesn't eliminate them. The underlying data structure still needs to handle the case where two edits land at the same position simultaneously.

---

## What we actually need

The real requirement is: merge **both** edits without losing either one, and do it **without any coordination** between the servers. No locking, no waiting, no asking the other server what it has.

This is exactly what CRDTs solve.
