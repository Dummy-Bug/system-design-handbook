## The private file problem

Object storage gives you a key that maps to a URL pointing at a file. For a public YouTube video — fine. Anyone can have that URL, the video is meant to be public.

But what about a private file? A medical report. A paid course video. A confidential document. If you give out a permanent S3 URL, anyone who gets hold of it — by forwarding, by sniffing, by accident — can access the file forever. There's no authentication on S3's side.

The naive fix is to route every file download through your own server:

```
User requests file
→ Request hits your server
→ Server checks: is this user authenticated?
→ Yes → server fetches file from S3 → streams it to user
```

This works for access control. But you've just brought back the exact problem that killed the database approach — every byte of every file now flows through your server. At scale, your servers become the bottleneck. Bandwidth costs spike. You need to scale your fleet just to proxy files.

---

## The solution: Pre-signed URLs

The insight is: **authentication and file delivery are two separate concerns**. Your server is good at authentication. S3 is good at file delivery. Don't mix them.

A pre-signed URL is a temporary, signed URL that S3 generates on request. It has an expiry time baked in — say 15 minutes. During those 15 minutes, anyone with the URL can access the file directly from S3. After that, the URL is dead.

```
User requests file
→ Request hits your server
→ Server checks: is this user authenticated and authorised?
→ Yes → server asks S3 to generate a pre-signed URL (expires in 15 min)
→ S3 returns the signed URL
→ Server gives that URL to the user
→ User fetches file directly from S3 — server never touches the bytes
```

Your server only handles the lightweight authentication check. The heavy file transfer happens directly between S3 and the user. At 1,000 concurrent video viewers, your server is handling 1,000 tiny auth checks — not 500GB/s of video bytes.

---

## What happens if the download takes longer than the expiry?

This is a natural question. If a user is downloading a 2GB file and the URL expires halfway through — does the download fail?

No. The expiry only prevents **new** requests from starting with that URL. Once a download is already in progress, it completes. Think of it like a concert ticket — once you're inside the venue, they don't kick you out when the ticket expires. The ticket was only needed to get in.

---

## Pre-signed URLs for uploads too

Pre-signed URLs work in both directions. You can generate a pre-signed URL that allows a user to **upload** directly to S3 — again, without the bytes flowing through your server.

```
User wants to upload a video
→ Client asks your server: "I want to upload"
→ Server checks auth, generates a pre-signed upload URL
→ Client uploads directly to S3 using that URL
→ S3 stores the file, notifies your server (via S3 event / webhook)
→ Server saves the key in the database
```

This is the standard pattern for any upload flow at scale.

> [!important] Pre-signed URL security properties
> - The URL contains a cryptographic signature — it cannot be forged or extended
> - Expiry is enforced by S3 — no clock skew tricks can bypass it
> - You control the expiry duration — shorter = more secure, longer = better UX for slow downloads
> - You can also pre-sign with specific conditions (e.g., max file size for uploads)

> [!tip] Interview framing
> "For private file access I'd use pre-signed URLs — the server handles authentication and generates a short-lived signed URL, the user fetches directly from S3. This keeps file delivery off my application servers entirely while still enforcing access control."
