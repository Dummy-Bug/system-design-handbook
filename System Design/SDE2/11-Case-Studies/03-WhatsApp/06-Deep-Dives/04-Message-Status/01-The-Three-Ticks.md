
> [!info] The three tick states in WhatsApp 1:1 messaging
> Single tick = stored on server. Double tick = arrived on Bob's device. Blue tick = Bob opened the chat.

---

## What the ticks actually mean

WhatsApp shows Alice one of three states for every message she sends:

```
✓   single grey tick   → message stored on server
✓✓  double grey tick   → message delivered to Bob's device
✓✓  double blue tick   → Bob opened the chat and saw the message
```

These are three fundamentally different events. Each requires a different signal from a different part of the system.

---

## Single tick — server ack

Alice hits send. Her client sends the message over WebSocket to the WS server. The WS server writes the message to DynamoDB and assigns it a sequence number.

The moment the DynamoDB write succeeds, the server acks back to Alice's client over WebSocket:

```
Alice's client → WS server: "hey" (conv_abc123)
WS server → DynamoDB: write seq=42, content="hey"
WS server → Alice's client: ack (seq=42 stored)
Alice's client: show single tick ✓
```

Single tick means: "we have your message, it won't be lost." Nothing about Bob yet.

---

## Double tick — device delivery ack

The WS server attempts to deliver the message to Bob. If Bob is online, the message is pushed over WebSocket to Bob's device. Bob's client receives it and sends a delivery ack back:

```
WS server → Bob's client: message seq=42
Bob's client receives it → ack back: "delivered seq=42"
WS server updates last_delivered_seq for Bob in conv_abc123
WS server → Alice's client: double tick ✓✓ for seq=42
```

Double tick means: "the message is on Bob's device." Bob hasn't necessarily seen it — his phone might be in his pocket, the app might not be open.

---

## Blue tick — read receipt

Blue tick fires when Bob actually opens the chat. Not when the notification arrives. Not when he reads the preview from the lock screen. Only when the chat is open and the messages are visible on screen.

```
Bob opens conv_abc123
Bob's client → WS server: "read up to seq=44 in conv_abc123"
WS server updates last_read_seq for Bob in conv_abc123
WS server → Alice's client: blue tick ✓✓ for seq=42, 43, 44
```

> [!important] Notification banner ≠ blue tick
> Bob reading the message preview from his lock screen does NOT trigger a blue tick. The OS delivers the notification — WhatsApp's app is not running, no read event is fired. Blue tick only comes from the app being open and the chat being visible.

---

## Why three separate signals

These three events happen at three different layers:

```
Single tick  → server layer    (DynamoDB write)
Double tick  → device layer    (Bob's client ack over WebSocket)
Blue tick    → app layer       (Bob's chat open event)
```

They can be separated by minutes, hours, or days. Bob's phone might receive the message at 9am (double tick) but he might not open WhatsApp until 9pm (blue tick). The design must track these independently.
