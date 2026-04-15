
> [!info] Where to store the read receipts flag — user level, not conversation level
> One boolean per user. Not duplicated across every conversation they're in.

---

## The naive place — message_status table

The `message_status` table already exists. It has a row per user per conversation. The tempting move is to add a flag there:

```
message_status table
───────────────────────────────────────────────────────────────────────
user_id    conversation_id    last_delivered_seq    last_read_seq    read_receipts_enabled
bob        conv_abc123        44                    44               false
bob        conv_def456        17                    17               false
bob        conv_ghi789        8                     8                false
```

Bob is in 200 conversations. He has 200 rows in `message_status`. All 200 have `read_receipts_enabled = false`.

Now Bob goes to Settings and toggles read receipts back ON.

How many rows do you update?

**200 writes. For one setting toggle.**

And if Bob is in 2000 conversations? 2000 writes. The cost of a single settings toggle scales with the number of conversations — completely unnecessary.

---

## The right place — user profile table

Read receipts is a **user-level** preference. Bob set it once. It applies everywhere. It belongs in one place:

```
users table
───────────────────────────────────────────────
user_id    phone    name    read_receipts_on
bob        +1...    Bob     false
alice      +1...    Alice   true
```

One row. One write when Bob toggles the setting. Done.

When the system needs to check Bob's preference — one lookup by `user_id`. No join across conversation rows.

---

## But now every status event needs a settings lookup

If the flag lives in the users table, then every time Bob's client might send a read event, the system needs to know Bob's preference.

With the flag in the users table, the server would have to:

```
Bob opens chat
→ Bob's client considers sending read event
→ check users table: is read_receipts_on for bob?
→ if false, suppress
```

That's an extra DB lookup on every single chat open. At WhatsApp's scale — hundreds of millions of chat opens per day — that's a lot of unnecessary reads.

---

## The solution — client-side cache

Bob's WhatsApp client fetches his settings once at login and caches them in memory:

```
App launch → fetch user settings → cache locally:
  { read_receipts_on: false, last_seen_on: true, ... }
```

Now the check is free — it's a local memory read, not a network call:

```
Bob opens chat
→ check local cache: read_receipts_on = false
→ do not send read event
→ zero network calls, zero server load
```

The cache is invalidated only when Bob explicitly changes a setting. Settings changes are rare — maybe once a year per user. The cache is effectively always warm.

---

## Summary

```
Where the flag lives:  users table (one row per user)
How it's accessed:     client-side cache loaded at login
When cache refreshes:  only on explicit settings change
Cost of toggle:        one DB write to users table
Cost of check:         zero (local memory read)
```

> [!tip] Interview framing
> "Read receipts is a user-level preference — one boolean in the users table. The client fetches settings at login and caches them locally. The check before sending a read event is a local memory read — zero server calls. The flag only touches the DB when the user explicitly changes their setting."
