# Instagram API Design

This section defines the API contract for Instagram — every endpoint a client calls, what it sends, and what it gets back. Some endpoints are deep-dived in other case studies (marked with a pointer) to avoid duplication.

> [!info] Identity comes from the auth token
> Every authenticated endpoint extracts the acting user from a bearer token in the `Authorization` header. **Never** accept `user_id`, `author_id`, or `follower_id` in the request body — that is a security hole. A client could impersonate another user by sending their ID.

---

## Owned by This Case Study

### Home Feed

The primary read endpoint. Returns posts from people the user follows, ordered by recency.

```
GET /api/v1/feed?cursor={next_cursor}&limit={n}
response: {
  posts: List<Post>,
  next_cursor: {timestamp or post_id}
}
```

**Why cursor and not offset?** At 500M DAU, `OFFSET 1000000` scans a million rows before returning. Cursor pagination uses an indexed column (timestamp or post_id) and does `WHERE created_at < cursor` — constant time regardless of how deep you scroll.

> [!tip] Deep dive
> How the feed is assembled — fan-out on write vs fan-out on read, hybrid for celebrities — is the **core deep dive of this case study**. Covered in `Deep-Dives/`.

---

### Explore Feed

Personalised content from accounts the user does **not** follow.

```
GET /api/v1/explore?cursor={next_cursor}&limit={n}
response: {
  posts: List<Post>,
  next_cursor: opaque_token
}
```

The cursor here is **opaque** — unlike the home feed (chronological cursor = timestamp), the Explore feed is ML-ranked and the cursor encodes ranking position and session state.

---

### Likes

```
PUT    /api/v1/posts/{post_id}/like
DELETE /api/v1/posts/{post_id}/like
response: { 200 OK, like_count }
```

PUT (idempotent) not POST. Liking twice = still liked. User identity from auth token, never from the body.

> [!tip] Deep dive pointer
> Counter sharding, approximate like counts at scale, and avoiding write hotspots on viral posts — covered in the **Reddit** case study.

---

### Comments

```
POST /api/v1/posts/{post_id}/comments
body:     { content, idempotency_key }
response: { 201 Created, comment: { id, content, created_at } }

GET /api/v1/posts/{post_id}/comments?cursor={next_cursor}&limit={n}
response: { comments: List<Comment>, next_cursor }

DELETE /api/v1/comments/{comment_id}
response: { 200 OK }
```

Comment creation is POST (creates a new resource) and requires an **idempotency key** — a network retry must not create duplicate comments.

> [!tip] Deep dive pointer
> Nested comments, adjacency list vs closure table, and comment ranking — covered in the **Reddit** case study.

---

### Profile

```
GET /api/v1/users/{user_id}/profile
response: {
  user: { id, username, bio, profile_pic, follower_count, following_count },
  posts: List<Post>,
  next_cursor: token
}
```

---

## Covered in Other Case Studies

### Upload a Post → YouTube

Uploading a 50MB video through the application server wastes bandwidth. The client gets a **presigned URL** and uploads directly to S3.

```
POST /api/v1/posts/upload-url
body:     { file_type: "image" | "video", file_size }
response: { post_id, presigned_url, expires_in }

// client uploads directly to presigned_url

POST /api/v1/posts/confirm
body:     { post_id, caption }
response: { 200 OK, post: { ... } }
```

> [!tip] Deep dive pointer
> The full upload pipeline — chunking, resumable upload, transcoding, multiple resolutions — is covered in the **YouTube** case study.

---

### Follow → LinkedIn

```
PUT    /api/v1/users/{user_id}/follow
DELETE /api/v1/users/{user_id}/follow
response: { 200 OK, is_following: bool }
```

> [!tip] Deep dive pointer
> Social graph internals — follower list sharding, graph traversal, "People You May Know" — is covered in the **LinkedIn** case study.

---

### Direct Messages → WhatsApp

```
POST /api/v1/dms/{user_id}/messages
body:     { content, idempotency_key }
response: { 201 Created, message: { ... } }

GET /api/v1/dms/{user_id}/messages?cursor={next_cursor}&limit={n}
```

> [!tip] Deep dive pointer
> WebSocket connections, message ordering, offline delivery, read receipts — all covered in the **WhatsApp** case study.

---

### Stories → Snapchat

```
POST /api/v1/stories/upload-url
body:     { file_type, file_size }
response: { story_id, presigned_url }

POST /api/v1/stories/confirm
body:     { story_id }
response: { 200 OK, expires_at: {timestamp + 24h} }

GET /api/v1/stories/feed
response: {
  users: List<{ user_id, profile_pic, has_unseen, stories: List<Story> }>
}
```

> [!tip] Deep dive pointer
> Ephemeral media, TTL deletion, view-once mechanics, and story expiry pipeline — covered in the **Snapchat** case study.

---

### Notifications → Notification System

```
GET /api/v1/notifications?cursor={next_cursor}&limit={n}
response: { notifications: List<Notification>, unread_count }
```

> [!tip] Deep dive pointer
> Kafka fan-out, DLQ, retry, per-channel workers — covered in the **Notification System** case study.

---

## Summary

**Covered in this case study:**

| Endpoint | Method | What It Does |
|---|---|---|
| `/feed` | GET | Home feed — posts from followings |
| `/explore` | GET | Explore feed — personalised discovery |
| `/users/{id}/profile` | GET | View a user's profile and posts |

**Covered in other case studies:**

| Endpoint | Method | Go Here For Deep Dive |
|---|---|---|
| `/posts/upload-url` → `/posts/confirm` | POST | YouTube — upload pipeline |
| `/stories/*` | POST/GET | Snapchat — ephemeral media, TTL deletion |
| `/posts/{id}/like` | PUT/DELETE | Reddit — counter sharding, approximate counts |
| `/posts/{id}/comments` | POST/GET/DELETE | Reddit — nested comments, adjacency list |
| `/users/{id}/follow` | PUT/DELETE | LinkedIn — social graph |
| `/dms/*` | POST/GET | WhatsApp — real-time messaging |
| `/notifications` | GET | Notification System — Kafka fan-out |
