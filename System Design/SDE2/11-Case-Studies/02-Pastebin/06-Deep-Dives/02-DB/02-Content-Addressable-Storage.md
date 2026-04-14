
> [!info] Content-addressable storage means the content itself determines its address — not a random ID you assign to it.
> Same content = same address. Always. Everywhere.

---

## The Problem with Random IDs

In URL Shortener, every URL gets a unique random short code. Simple. But Pastebin has a different problem — users paste text, and text can repeat.

Imagine 500 developers all paste the same stack trace after a popular library releases a breaking change. With random IDs, you store that identical 10KB text 500 times. That's 5MB of pure duplication — same bytes, different rows, wasted storage.

At scale this adds up fast. Popular content (common error messages, boilerplate configs, tutorial code) gets pasted over and over. Storing each copy separately is wasteful.

---

## The Insight — Use the Content as Its Own Key

Instead of generating a random ID, you **hash the content** and use that hash as the key.

```
SHA-256("hello world") → "b94d27b9934d3e08a52e52d7da7dabfac484efe04294e576..."

Two users paste "hello world":
  User A → hash → "b94d27..." → store once
  User B → hash → "b94d27..." → already exists → don't store again
```

Same content = same hash = same row in the `content` table. The content is stored exactly once regardless of how many users paste it.

This is called **content-addressable storage**. The address (key) is derived from the content itself, not assigned arbitrarily. Git uses this exact model — every commit, tree, and blob is stored by its SHA hash. If two repos have the same file, Git stores it once.

---

## What This Gives You

```
Without content-addressing:
  500 users paste same 10KB text → 500 rows → 5MB stored

With content-addressing:
  500 users paste same 10KB text → 1 row → 10KB stored
  Savings: 99.998%
```

For a system where popular content (error logs, config templates, code snippets) gets pasted repeatedly, this is a significant storage win.

---

## How It Works in Pastebin

```
User submits paste text
  ↓
App server computes SHA-256(text) → content_hash
  ↓
Check content table: WHERE content_hash = ?
  ↓
EXISTS   → content already stored → skip S3 upload
NOT EXISTS → upload text to S3 → insert row into content table
  ↓
Either way: INSERT into pastes table with this content_hash
```

The `content` table is keyed by `content_hash`. The `pastes` table holds a foreign key to `content_hash`. Multiple paste rows can point to the same content row — that's the deduplication.

---

## The Hash Function — SHA-256

SHA-256 produces a 256-bit (64 hex char) hash. Collision probability is astronomically low — two different inputs producing the same hash has never been observed in practice. For a Pastebin at 3.65B pastes over 10 years, you will not see a collision.

```
SHA-256 output: 64 hex chars = 32 bytes
Stored as:      VARCHAR(64) — the content_hash column
```

MD5 would be smaller (32 chars) but has known collision vulnerabilities. SHA-256 is the safe default.

---

> [!tip] Interview framing
> "Content-addressable storage: hash the paste text with SHA-256, use the hash as the content table PK. Same content from any user produces the same hash — stored once, not multiple times. Same model Git uses for blobs. Deduplication happens automatically with no extra logic — just check if the hash exists before uploading to S3."
