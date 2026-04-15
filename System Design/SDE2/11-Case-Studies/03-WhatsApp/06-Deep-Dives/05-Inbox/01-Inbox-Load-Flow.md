
> [!info] The inbox — what Alice sees when she opens WhatsApp
> A list of conversations, each showing: contact name, avatar, last message preview, timestamp, unread count. All of it must load fast on app open.

---

## What Alice needs

When Alice opens WhatsApp, the first screen she sees is her conversation list. Every row has:

```
[Avatar] Bob                    9:42am
         "hey what's up?"       [3]
```

Four pieces of data per row:
- Contact name + avatar
- Last message preview
- Last message timestamp
- Unread count badge

Alice might have 50 conversations. All 50 rows need to render before she sees anything useful.

---

## The loading flow

```
Alice opens WhatsApp
→ Client requests inbox for user_id = alice
→ Server fetches list of conversation_ids for alice
→ For each conversation: fetch name, avatar, last_message, last_ts, unread_count
→ Server returns sorted list (most recent first)
→ Client renders top K conversations
→ Alice scrolls → paginated load for older conversations
```

The client renders what it receives and re-orders by timestamp so the most recent conversation is always at the top.

Pagination is important here — Alice doesn't need all 200 of her conversations at once. She needs the top 20. If she scrolls, load the next 20. This keeps the initial load fast and avoids fetching data that will never be viewed.

---

## The key design question

You have Alice's `user_id`. You need 5 fields per conversation for 50 conversations.

How you fetch that data determines whether your database survives at scale.
