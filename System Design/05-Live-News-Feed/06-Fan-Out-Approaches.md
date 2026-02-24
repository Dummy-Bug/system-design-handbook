
When a user (e.g., a celebrity like LeBron James) creates a post, the system must ensure the post reaches their audience at scale.

There are two core strategies:

- Fan-Out-on-Read (Pull)
- Fan-Out-on-Write (Push)

Most real systems use a **Hybrid** of both.

---

## Fan-Out-on-Read (Pull Model)

### Description
- Posts are stored only in the author’s timeline.
- No follower feeds are updated at write time.
- When a user opens the app, the system:
  - Fetches posts from followed users/pages
  - Merges and ranks them dynamically.

This avoids pushing a single post to millions of followers.

---

### Advantages
- Storage efficient (no per-user feed duplication)
- Avoids massive write amplification
- Easier to experiment with ranking logic

---

### Disadvantages
- Higher read latency
- Expensive feed generation at read time
- Requires strong caching and compute infra

---

### Best Suited For
- Celebrities / high-fanout users
- Pages with millions of followers
- Inactive or occasional users

---

## Fan-Out-on-Write (Push Model)

### Description
- As soon as a post is created:
  - The system updates the feed cache of each follower.
- Feed is already materialized when the user opens the app.

---

### Advantages
- Very fast read latency
- Excellent UX for frequent users
- Simple feed read path

---

### Disadvantages
- Severe write amplification
- Not scalable for celebrities
- Wasted work for inactive users

---

### Best Suited For
- Normal users with limited followers
- Highly active users
- Close friend connections

---

## Hybrid Fanout Strategy (Used in Practice)

Real-world systems combine both approaches:

- Fan-Out-on-Write for:
  - Normal users
  - Close friends
  - High-engagement relationships

- Fan-Out-on-Read for:
  - Celebrities
  - High-fanout pages
  - Cold / inactive users

This balances:
- Read latency
- Storage cost
- Write scalability

---

> Fan-out-on-write optimizes read latency but does not scale for high-fanout users, while fan-out-on-read avoids write amplification but increases read cost. A hybrid approach is used to balance scalability and user experience.