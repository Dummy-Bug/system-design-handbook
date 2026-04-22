
> [!info] Why APNs/FCM cannot be the source of truth for double tick
> Push notification delivery receipts exist but cannot be trusted for per-message delivered status.

---

## The tempting shortcut

When Alice sends Bob a message and Bob is offline, the server sends a push notification via APNs or FCM. APNs and FCM do offer delivery callbacks — they can tell you whether the notification was delivered to the device.

The tempting shortcut: use APNs delivery callback as the signal for double tick. "APNs confirmed delivery → update last_delivered_seq → show double tick."

This breaks in multiple ways.

---

## Problem 1 — notification delivery ≠ message delivery

APNs confirms that the notification banner arrived on Bob's phone. It does not confirm that WhatsApp received the message payload.

The notification only carries a preview: "Alice: hey." It does not contain the actual message data. Bob's device hasn't received the message yet — it's received a nudge telling it that a message exists.

The actual message is delivered over WebSocket when Bob opens the app. Until that happens, the message is not on Bob's device — it's still only on the server.

Showing double tick based on APNs delivery would be misleading. Double tick means the message is on Bob's device. The notification being delivered doesn't mean that.

---

## Problem 2 — APNs delivery callbacks are unreliable and delayed

APNs and FCM do not guarantee real-time delivery callbacks. In practice:

```
APNs callback latency: seconds to minutes
FCM callback latency: variable, sometimes missing entirely
Callback failure rate: non-zero, especially on poor connectivity
```

Building tick state on top of an unreliable, delayed signal would cause double ticks to appear and disappear, or appear at wrong times. The user experience would be broken.

---

## Problem 3 — Chinese phones have no FCM

Chinese Android phones (Xiaomi, Huawei, OPPO) ship without Google Play Services. FCM doesn't work. Each manufacturer has their own push infrastructure with their own delivery semantics. Building tick logic on top of platform-specific notification callbacks means maintaining separate logic per manufacturer.

---

## The right signal — WebSocket delivery ack

The only reliable signal for "message arrived on Bob's device" is Bob's WhatsApp app explicitly acking over WebSocket:

```
WS server pushes message to Bob's client
Bob's client receives it → renders it → sends cumulative ack: "delivered seq=44"
Server: this is ground truth. The message is on the device.
```

This is synchronous, in-band, and application-level. There is no ambiguity. WhatsApp sent the message, Bob's app received it, Bob's app confirmed it.

---

## When Bob is offline — no double tick yet

If Bob is offline, there is no WebSocket. There is no delivery ack. The message stays at single tick.

```
Alice sends → server stores → single tick ✓
Bob is offline → no WebSocket → no ack → stays single tick
Bob turns phone on → notification arrives → still single tick (notification ≠ delivery)
Bob opens WhatsApp → WebSocket established → messages pushed → Bob acks → double tick ✓✓
```

The double tick only fires after the WebSocket ack. Not before.

> [!danger] Common trap
> "APNs confirmed notification delivery, so we can show double tick" — this is wrong. Notification delivery and message delivery are different things. Double tick = message on device via WebSocket, not notification on lock screen via APNs.
