
> [!info] Reference counting solves the shared ownership problem — who is responsible for deleting something that multiple people are using?
> The answer: nobody deletes it until everyone is done with it.

---

## The Delete Problem

Content-addressable storage means multiple users can share the same content row. User A and User B both paste "hello world" — one row in `content`, two rows in `pastes`, both pointing at the same `content_hash`.

Now User A deletes their paste. What happens to the content?

**Naive answer: delete the content row.**

This is wrong. User B's paste still points to that content_hash. Their link is now broken — they try to read their paste and get nothing. User A's delete broke User B's paste without User B doing anything.

---

## The Fix — Reference Counting

The `content` table has a `ref_count` column. It tracks how many `pastes` rows are currently pointing at this content.

```
User A creates paste → content row inserted with ref_count = 1
User B creates same paste → content already exists → ref_count = 2

User A deletes → ref_count = 2 → 1  (content stays, User B's link works ✓)
User B deletes → ref_count = 1 → 0  (nobody pointing at it → physically delete ✓)
```

Content is only physically deleted when `ref_count` reaches zero. Until then, it stays. This is the same pattern used in filesystems (inode link count), Python's garbage collector, and S3 object lifecycle management.

---

## The Double-Delete Problem

Reference counting introduces a new problem. What if User A deletes twice?

```
Initial state:      ref_count = 2
User A deletes:     ref_count = 2 → 1  ✓
User A deletes again: ref_count = 1 → 0 → content deleted ✗
```

User B's link just broke because User A called delete twice — maybe due to a retry after a network timeout, maybe a bug in the client. This is the same idempotent delete problem from the API design, now showing up at the data layer.

---

## The Fix — Pastes Row as Ownership Record

The solution is to treat the `pastes` table row as the **ownership record**. A user owns content as long as their row in `pastes` exists. When they delete, you DELETE their `pastes` row and decrement `ref_count`. If they try to delete again, the `pastes` row is already gone — there's nothing to delete, so `ref_count` is not touched.

```
First delete:
  pastes row EXISTS for (userA, shortCode) 
  → DELETE pastes row
  → decrement ref_count: 2 → 1  ✓

Second delete (retry):
  pastes row DOES NOT EXIST for (userA, shortCode)
  → nothing to do
  → ref_count unchanged: stays at 1  ✓
```

User B's link is safe. The double-delete is absorbed harmlessly.

This works because the `pastes` row deletion is idempotent — deleting a row that doesn't exist is a no-op. The ref_count decrement is gated behind the row deletion: no row, no decrement.

---

## Atomicity — Wrapping in a Transaction

The DELETE from `pastes` and the decrement of `ref_count` in `content` must happen atomically. If the decrement succeeds but the row deletion fails (or vice versa), you end up with an inconsistent ref_count.

```sql
BEGIN;
  DELETE FROM pastes WHERE short_code = ? AND user_id = ?;
  -- only if a row was actually deleted (affected_rows = 1):
  UPDATE content SET ref_count = ref_count - 1 WHERE content_hash = ?;
  -- if ref_count reaches 0, schedule physical deletion
COMMIT;
```

PostgreSQL's ACID guarantees make this safe. Both operations succeed or neither does.

---

## When ref_count Reaches Zero

When `ref_count` hits zero, the content has no owners. Two things need to happen:

1. DELETE the row from the `content` table
2. Delete the blob from S3

The S3 deletion can be async — it doesn't need to happen in the same transaction. A background job can pick up orphaned S3 objects and clean them up. The content row deletion, however, should happen in the same transaction as the final ref_count decrement to keep the DB consistent.

---

> [!tip] Interview framing
> "ref_count on the content table tracks how many pastes point at it. Create increments, delete decrements. Physical deletion only when ref_count hits zero. Double-delete problem solved by using the pastes row as the ownership record — no row, no decrement. The DELETE from pastes and the ref_count decrement are wrapped in a single transaction for atomicity."
