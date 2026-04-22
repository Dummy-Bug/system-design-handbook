
> [!info] The goal of API design
> API design is about defining the contract between the client and the server. For a URL shortener, there are exactly two flows — create a short URL and redirect to the original. Each flow gets one endpoint.

---

## Endpoint 1 — Shorten a URL

```http
POST /api/v1/urls

Request Body:
{
  "long_url": "https://some-very-longurl.com/with/a/lot/of/path"
}

Response 200 OK:
{
  "error": null,
  "data": {
    "short_url": "bit.ly/x7k2p"
  },
  "metadata": {
    "created_on": "2026-04-13T10:00:00Z"
  }
}
```

**Why POST?** Because you are creating a new resource — a new short URL mapping. POST is the correct verb for resource creation.

**Why `/api/v1/`?** API versioning. If you ever need to change the contract — different response shape, new fields, breaking changes — you release `/api/v2/` and old clients keep working on `/api/v1/`. Always version your APIs from day one.

**No auth header** — anonymous access is in scope. Anyone can shorten a URL without logging in.

---

## Endpoint 2 — Redirect

This is where most people get it wrong the first time.

The instinct is to design something like `GET /redirect?shortURL=x7k2p`. But think about who the client is for this flow.

When a user clicks `bit.ly/x7k2p`, there is no app making a separate API call on their behalf. **The browser itself is the client.** It makes a GET request directly to `bit.ly/x7k2p`. That request hits your server. Your server looks up `x7k2p` and responds.

The short URL **is** the API endpoint. So the redirect endpoint is simply:

```
GET /{shortCode}

Example: GET bit.ly/x7k2p

Response 301 Moved Permanently:
  Location: https://the-actual-long-url.com
```

No `/redirect` prefix. No query params. Just the short code as the path — because that is literally what the browser hits when someone clicks the link.

---

## Why 301 and not 302

A redirect response has two options:

| Code | Name | Browser behaviour |
|---|---|---|
| 301 | Moved Permanently | Browser caches the redirect — never hits your server again |
| 302 | Found (Temporary) | Browser does not cache — every click hits your server |

**301 means:** after the first click, the browser remembers the destination and goes there directly. Your server never sees the request again.

**Trade-off:**
- 301 → less load on your servers, faster for the user after first click ✓
- 301 → requests never reach your server → you cannot track analytics ✗
- 302 → every click hits your server → you can track analytics ✓
- 302 → more load on your servers ✗

Since analytics is out of scope for this system, **301 is the right call.** Less load, faster user experience.

> [!important] The expiry-based approach is wrong
> It might seem clever to use 301 for long-lived URLs and 302 for short-lived ones. But the real deciding factor is whether you need analytics — not expiry time. If you need to track clicks, use 302 regardless of expiry.

---

## Why the redirect response has no body

A redirect response (3xx) tells the browser "go somewhere else." The body is irrelevant — the browser immediately reads the `Location` header and follows it, ignoring everything else.

```
HTTP 301
Location: https://the-actual-long-url.com
← no body needed, browser never reads it
```

This is not because it is a GET request — GET responses absolutely can have bodies (e.g. `GET /users/123` returns a JSON body). It is specifically because **3xx responses are instructions to redirect**, and the browser acts on the `Location` header alone.

---

> [!tip] Interview framing
> Two endpoints: `POST /api/v1/urls` to create a short URL, `GET /{shortCode}` to redirect. The redirect endpoint is just the short code as the path — because the browser hitting the link IS the API call. Return 301 if analytics are not needed (browser caches, less load), 302 if you need to track every click (every request hits your server). The redirect response has no body — it is a 3xx, the browser reads the Location header and follows it immediately.
