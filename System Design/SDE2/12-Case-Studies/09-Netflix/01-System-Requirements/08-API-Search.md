# API Design — Search

## The Endpoint

When a user types into the Netflix search bar, the client fires a GET request with the search term as a query parameter.

```
GET /api/v1/search?q=leo&limit=10

Headers:
  Authorization: Bearer <JWT>

Response 200 OK:
{
  "results": [
    {
      "movie_id": "m_45",
      "title": "Leo",
      "thumbnail_url": "https://cdn.netflix.com/thumbnails/leo.jpg",
      "match_field": "title",
      "duration_seconds": 5400,
      "genre": "Animation"
    },
    {
      "movie_id": "m_89",
      "title": "Inception",
      "thumbnail_url": "https://cdn.netflix.com/thumbnails/inception.jpg",
      "match_field": "cast",
      "duration_seconds": 8880,
      "genre": "Thriller"
    }
  ],
  "next_cursor": "eyJvZmZzZXQiOjEwfQ=="
}
```

**`match_field`** tells the client what matched — title, cast, genre, or description. Netflix uses this to show a subtle hint below the result: "Leonardo DiCaprio" appears under Inception so the user understands why it came up even though "leo" isn't in the title.

---

## Why GET and Not POST

Search is a read operation — it changes no state on the server. GET is the correct verb. GET requests are also cacheable at the CDN and API Gateway layer — if 10,000 users all search "squid game" within the same minute, the response can be cached and served without hitting the Search Service every time. POST requests are never cached by default.

> [!danger] Never put the search term in the request body with POST
> POST implies creating a resource. A search creates nothing. Using POST for search also breaks caching — every search query hits your backend even when the answer was just computed for someone else a second ago.

---

## Pagination — Cursor Again

Search results are paginated the same way as the home feed — cursor-based, not offset-based.

The reason is identical: Netflix's catalogue is constantly changing. A new title matching "leo" could be added between page 1 and page 2. Offset pagination would shift all results and produce duplicates or gaps. The cursor holds a stable position in the result set regardless of concurrent catalogue changes.

```
GET /api/v1/search?q=leo&limit=10
→ { results: [...10 items], next_cursor: "eyJvZmZzZXQiOjEwfQ==" }

GET /api/v1/search?q=leo&limit=10&cursor=eyJvZmZzZXQiOjEwfQ==
→ { results: [...next 10 items], next_cursor: "eyJvZmZzZXQiOjIwfQ==" }
```

When `next_cursor` is null, there are no more results.

---

## JWT in the Header

The search term goes in the query string. The JWT goes in the `Authorization` header — never in the URL.

Query strings are logged by every proxy, CDN, load balancer, and API gateway between the client and server. A JWT in the URL is a credential sitting in every access log in plain text. The search term in the URL is fine — "?q=leo" is not sensitive. The user's identity token is.

---

## Full API Surface — Updated

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/home` | GET | Home feed — paginated genre rows |
| `/api/v1/search` | GET | Search by title, cast, genre — paginated results |
| `/api/v1/stream` | GET | Start or resume playback |
| `/api/v1/stream/progress` | POST | Save playback position every ~10 seconds |
| `/api/v1/download` | POST | Get a time-limited download URL |
