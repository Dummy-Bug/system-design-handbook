
> [!info] What is a Notification System?
> A notification system is the infrastructure that sends messages to users across multiple channels — push notifications, SMS, and email — when something happens inside an application. It sits between your application's backend and the outside world, taking an internal event ("user got a new message") and translating it into a delivery across whichever channel the user prefers.

The problem it solves is simple: your app needs to reach users even when they aren't actively using it. When someone likes your Instagram photo, Instagram's backend fires an event. That event needs to find you — on your phone screen, in your inbox, or via a text — without the app being open. The notification system is what makes that possible.

What makes it an interesting design problem is the combination of scale and reliability. A breaking news alert might need to reach 50 million users in under a minute. Each of those users might prefer a different channel. Push notifications can fail silently (phone offline, app uninstalled). SMS costs money and has rate limits. Email can bounce. The system has to handle all of this — fan out to millions, respect user preferences, retry failures, and never double-deliver.

> [!tip] Real-world context
> Every major product runs one of these. WhatsApp buzzing when a message arrives — push notification. Uber emailing your receipt — email channel. Bank flagging a suspicious transaction — SMS because it doesn't require internet. YouTube notifying subscribers of a new video — fan-out to potentially millions of users from a single event. The design patterns here (Kafka fan-out, multi-channel delivery, DLQ, idempotency) show up as building blocks in almost every other large-scale system.

---

**Push vs SMS — the two most important channels**

**SMS** travels via the telecom network and lands on any phone without internet or an app installed. It's the most reliable channel for critical alerts (OTPs, bank fraud warnings) but costs money per message and has carrier-enforced rate limits.

**Push notification** travels via Apple (APNs) or Google (FCM) servers, which maintain a persistent connection to every phone that has the app installed. It's free, fast, and works even when the app is closed — but it requires internet, and delivery is best-effort (phone offline = message dropped unless queued).

```
SMS  → telecom network → any phone, no internet needed, costs money

Push → Apple/Google servers → app installed + internet required, free, best-effort
```
