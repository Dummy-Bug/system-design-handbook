
> [!info] The read receipt flow — from Bob opening the chat to Alice seeing the blue tick
> One client event, one server write, one push to Alice — if she's online.

---

## What triggers a read receipt

Bob opens WhatsApp. He taps on his conversation with Alice. The chat screen renders the messages.

At this moment, Bob's client fires a read event:

```
Bob's client → WS server: {
  type: "read",
  conversation_id: "conv_abc123",
  seq: 44         ← highest seq currently visible on screen
}
```

This is the signal: "Bob has seen everything up to seq=44 in this conversation."

---

## Server processing

The WS server receives Bob's read event and updates the message_status table:

```
UPDATE message_status
  SET last_read_seq = 44
  WHERE user_id=bob AND conversation_id=conv_abc123
```

One write. Regardless of how many messages Bob just read.

Then it checks if Alice is online:

```
GET ws:alice from Redis registry
→ Alice is online on ws_server_2
→ Push to Alice's client:
   { type: "status_update", conversation_id: conv_abc123, last_read_seq: 44 }
```

Alice's client receives this and updates the display:

```
seq <= 44: show blue tick ✓✓ (blue)
```

---

## What Bob's client sends as the seq number

Bob might have 200 messages in the conversation but the screen only shows the latest 10. Does his client send seq=44 (latest visible) or does he need to scroll to the top first?

WhatsApp's model: the read event fires for the **latest message in the conversation** when the chat is opened, regardless of scroll position. The assumption is — if you opened the chat, you've been notified of all messages in it. Older messages you haven't scrolled to yet are still considered "seen" because you have access to them.

This is a product decision. The blue tick means "Bob opened the chat" — not "Bob scrolled to and read every individual message."

---

## Implicit read — Bob replies

Bob doesn't need to explicitly open the chat and scroll. If Bob sends a message in the conversation, it's implicit that he has read all of Alice's previous messages:

```
Bob sends "on my way" in conv_abc123
→ Server: latest Alice message before Bob's reply = seq=44
→ UPDATE message_status
    SET last_read_seq = 44
    WHERE user_id=bob AND conversation_id=conv_abc123
→ Push blue tick event to Alice
```

WhatsApp applies this automatically. If Bob replied, he read the messages. No need for a separate read event.

---

## What if Alice is offline when Bob reads

The blue tick event can't be delivered immediately. The server stores the update in `message_status` and holds the push event.

When Alice comes back online, the status sync covers this — described in full in the offline status sync file.

> [!tip] Interview framing
> "When Bob opens the chat, his client sends a read event with the highest seq visible. Server does one write to message_status — last_read_seq updated. Server pushes the blue tick event to Alice over WebSocket if she's online. If Bob replied, that's an implicit read — server derives last_read_seq from the reply position."
