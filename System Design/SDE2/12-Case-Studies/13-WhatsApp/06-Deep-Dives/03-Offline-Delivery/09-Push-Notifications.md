
> [!info] Push notifications are the only way to reach a phone when the app is closed
> WhatsApp cannot maintain a background connection to Bob's phone. Apple and Google are the only entities allowed to do that.

---

## The problem with background connections

When WhatsApp is closed, it cannot maintain a WebSocket connection to its servers. The OS aggressively kills background network connections to save battery. A WebSocket that WhatsApp opened while running will be torn down within seconds of the app moving to the background.

This means WhatsApp has no way to push a message to Bob's phone when the app is closed — unless it uses someone else's always-on connection.

---

## APNs and FCM — the OS-level pipes

Apple and Google each maintain a **persistent background connection** from every phone to their own infrastructure. This connection is maintained by the OS itself — not by any app — and it stays alive even when all apps are closed.

```
iOS phones   → always-on connection to APNs (Apple Push Notification Service)
Android phones → always-on connection to FCM (Firebase Cloud Messaging)
```

Any app that wants to reach a phone when it is closed must go through these pipes. There is no alternative on standard iOS and Android.

---

## How WhatsApp uses APNs/FCM

WhatsApp registers Bob's device with APNs/FCM when he installs the app. APNs/FCM gives back a **device token** — a unique identifier for Bob's phone.

WhatsApp's notification service stores this token:

```
user_id: bob → device_token: "abc123xyz..."  (iOS)
             → platform: iOS
```

When Bob is offline and Alice sends a message, the notification service calls the APNs API:

```
POST to APNs:
  device_token: "abc123xyz..."
  payload: {
    title: "Alice",
    body:  "hey",
    conversation_id: "conv_abc123"
  }
```

APNs delivers this to Bob's phone over its always-on connection. The OS shows the banner.

---

## Every app uses this — no exceptions

This is not specific to WhatsApp. Every app that sends notifications uses APNs or FCM:

```
WhatsApp    → APNs / FCM
Instagram   → APNs / FCM
Gmail       → APNs / FCM
Uber        → APNs / FCM
Slack       → APNs / FCM
Any app     → APNs / FCM
```

No app can bypass this. Apple and Google have locked the notification pipeline at the OS level. Apps that try to maintain their own background connection get their connections killed and their battery usage flagged.

---

## The Chinese phone exception

Chinese Android phones (Xiaomi, Huawei, OPPO, Vivo) often ship without Google Play Services — which means FCM is unavailable. Chinese apps cannot use FCM for notifications.

Each major Chinese manufacturer built their own push notification infrastructure:

```
Xiaomi  → Mi Push
Huawei  → HMS Push (Huawei Mobile Services)
OPPO    → OPPO Push
Vivo    → VPush
```

Apps targeting China integrate with all of these separately. WhatsApp does not operate in China, so this is not a concern for this design — but it illustrates how fundamental APNs/FCM are: even in markets where they don't work, manufacturers had to build identical replacements.

> [!tip] Interview framing
> "When Bob is offline, the server can't push directly to his phone — the app isn't running and the OS kills background connections. We integrate with APNs for iOS and FCM for Android. These are the OS-level notification pipes that Apple and Google maintain. Every app uses them — there's no other way."
