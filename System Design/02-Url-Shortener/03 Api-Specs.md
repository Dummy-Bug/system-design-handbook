[[02 Design.pdf]]

**1. Create Short URL**

```
POST /api/v1/urls
```

Request Body:

```json
{
  "original_url": "https://www.example.com/some/long/url",
  "custom_alias": "myalias"  // optional
}
```

Response `201 Created`:

```json
{
  "short_url": "https://short.ly/abc1234",
  "original_url": "https://www.example.com/some/long/url",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

**2. Redirect**

```
GET /{short_code}
```

Response `301/302 Redirect` → Location: `https://www.example.com/some/long/url`

---

**3. Delete Short URL** _(optional)_

```
DELETE /api/v1/urls/{short_code}
```

Response `204 No Content`

---

**Use 301** if you want to minimize server load and don't care about analytics.

**Use 302** if you want to track every click (most real systems like Bitly use this).

---

This is a good thing to bring up **proactively** in the interview without being asked — it signals you're thinking beyond just making it work.