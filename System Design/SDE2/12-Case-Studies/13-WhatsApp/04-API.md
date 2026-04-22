
> [!info] Two types of API in a chat system
> Not everything needs real-time. Sending and receiving messages needs WebSockets — the server must push without waiting for a request. Loading chat history and the inbox are request-response — the client asks once, the server responds. Use the right tool for each job.

---

## The rule

```
Needs server to push unprompted?  → WebSocket event
Request-response is fine?         → REST API
```

Chat history and inbox don't change while you're looking at them in a way that requires a push. You open a conversation, load the history, done. REST is perfectly adequate. Message delivery is different — Bob can't poll for Alice's message, it has to arrive the moment she sends it. That needs WebSocket.

---

## WebSocket Events

### Client → Server: Send a message

When the user hits send, the client emits this event over the open WebSocket connection:

```
event: "message.send"
payload: {
  conversation_id: "conv_abc123",   // which conversation this belongs to
  sender_id:       "user_001",      // who is sending
  message_id:      "msg_xyz789",    // client-generated ID for deduplication
  content:         "hey",           // the message text
  timestamp:       1713087600000    // client timestamp (used for ordering)
}
```

> [!important] Why conversation_id and not receiver_id?
> `conversation_id` is the right abstraction. A conversation is the container — the server looks it up and knows who the participants are. Using `receiver_id` means the server has to reconstruct "which conversation are these two people in?" on every message. `conversation_id` gives you that answer immediately. It also future-proofs for group chat — a group conversation has N participants, there is no single `receiver_id`.

> [!important] Why client-generated message_id?
> The client generates the message ID before sending. This enables idempotency — if the network drops and the client retries, the server sees the same `message_id` and deduplicates rather than storing the message twice. Without this, a retry creates a duplicate message.

---

### Server → Client: Deliver a message

When a message arrives for a user, the server pushes this event to the recipient's WebSocket connection:

```
event: "message.receive"
payload: {
  conversation_id: "conv_abc123",   // which conversation to display in
  sender_id:       "user_001",      // who sent it
  message_id:      "msg_xyz789",    // same ID as the send event
  content:         "hey",
  timestamp:       1713087600000
}
```

> [!important] Why sender_id in the push event?
> The payload is self-contained — the client doesn't need to infer anything from context. `sender_id` tells the client whose avatar to show and which side of the chat to render the bubble on. It also future-proofs for group chat where multiple senders exist in the same conversation.

---

## REST APIs

### Fetch chat history

Called when a user opens a conversation. Loads messages in reverse chronological order (newest first) with cursor-based pagination.

```
GET /api/v1/chat/:conversation_id?cursor=<message_id>&limit=20

Response:
{
  conversation_id: "conv_abc123",
  messages: [
    {
      message_id: "msg_xyz789",
      sender_id:  "user_001",
      content:    "hey",
      timestamp:  1713087600000
    },
    ...
  ],
  next_cursor: "msg_abc456"
}
```

> [!important] Cursor-based, not offset-based pagination
> The cursor is a `message_id`, not a page number. With offset pagination (`page=2`), if new messages arrive while the user is scrolling, the offset shifts — messages get skipped or duplicated. A cursor pointing to a specific message always returns exactly the messages before that point, regardless of new arrivals. `next_cursor` in the response is what the client passes on the next request to load older messages.

---

### Fetch inbox

Called on app open. Returns all conversations for the user, sorted by most recent message first — this is the main chat list screen.

```
GET /api/v1/chats/:user_id

Response:
{
  chats: [
    {
      conversation_id: "conv_abc123",
      participant:     "user_002",      // the other person in the conversation
      last_message:    "hey",           // preview text shown in inbox
      timestamp:       1713087600000    // used for sort order
    },
    ...
  ]
}
```

> [!important] participant not sender_id/receiver_id
> The client already knows it's the logged-in user. What it needs to know is who the *other* person is — their name, avatar, and last message preview. A single `participant` field gives the client exactly what it needs without redundant data.

Sorted by `timestamp` descending — most recent conversation at the top, satisfying FR #3.

---

## Summary

| Operation | Protocol | Endpoint / Event |
|---|---|---|
| Send message | WebSocket | event: `message.send` |
| Receive message | WebSocket | event: `message.receive` |
| Load chat history | REST GET | `/api/v1/chat/:conversation_id` |
| Load inbox | REST GET | `/api/v1/chats/:user_id` |
