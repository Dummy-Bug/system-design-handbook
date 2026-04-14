
> [!info] Wrong data size assumptions break your storage estimates by orders of magnitude
> A photo is 300KB. A video is 50MB. If you mix these up in an estimation, you'll be off by 100× before you've written a single component.

---

## Primitive types

```
Boolean:          1 byte   (stored as 1 byte even though it's 1 bit)
Char (ASCII):     1 byte
Char (UTF-8):     1–4 bytes (English = 1 byte, emoji = 4 bytes)

Integer (INT32):  4 bytes
Long (INT64):     8 bytes

Float:            4 bytes
Double:           8 bytes

UUID:             16 bytes (128 bits)
Timestamp:        8 bytes  (Unix epoch as INT64)
```

---

## Common objects

```
Short URL code (6 chars):       6 bytes
URL (average):                  100 – 200 bytes
URL row (short_code + long_url + metadata): ~500 bytes

Tweet (text only):              ~280 bytes
Instagram caption:              ~300 bytes

Post metadata (id, user, timestamp, likes): ~200 bytes

User profile (basic: name, email, bio, avatar URL): ~1 KB
User profile (full with settings): ~2–5 KB

Session token / JWT:            ~300–500 bytes
Notification payload:           ~200–500 bytes

Chat message (text):            ~200 bytes
Chat message row (with metadata): ~500 bytes

Email (text only):              ~10–75 KB
Email (with attachments):       ~300 KB – 5 MB
```

---

## Media

```
Thumbnail (50×50px):            5 – 20 KB

Profile photo (compressed):     20 – 100 KB
Photo (compressed JPEG, 1080p): 300 KB – 1 MB
Photo (raw, uncompressed):      3 – 12 MB

Audio (1 min, MP3 128kbps):    ~1 MB
Audio (1 min, lossless):        ~30 MB

Video (1 min, 360p):            ~10 MB
Video (1 min, 720p):            ~50 MB
Video (1 min, 1080p):           ~100 MB
Video (1 min, 4K):              ~375 MB
```

**Key insight for video systems:**
When you upload a raw video, it gets transcoded into multiple formats and resolutions. A 1-min 1080p video uploaded (100MB raw) becomes:

```
360p:   10 MB
480p:   20 MB
720p:   50 MB
1080p:  100 MB
4K:     375 MB
+ multiple codecs (H.264, VP9, AV1)
Total:  ~5–15× the original size
```

This is why YouTube's storage estimate must multiply raw upload by ~10 for all transcoded versions.

---

## Storage math rules

**Rule 1 — Replication multiplier:**
```
Raw storage × replication factor = actual storage needed
3 replicas standard → multiply by 3
```

**Rule 2 — Index overhead:**
```
Database indexes add 20–50% on top of raw row data
250 TB raw data → ~300–375 TB with indexes
```

**Rule 3 — Media vs metadata:**
```
Metadata is tiny. Media is everything.
Instagram: user profiles + captions = a few TB
Instagram: photos = petabytes
Always separate your estimate into metadata + media
```

**Rule 4 — Compression:**
```
Text compresses ~3–10× with gzip/snappy
Already-compressed files (JPEG, MP4, MP3) gain almost nothing from further compression
Don't apply text compression ratios to media — it won't help
```

---

## Quick unit conversions

```
1 KB  = 10^3  bytes = 1,000 bytes
1 MB  = 10^6  bytes = 1,000 KB
1 GB  = 10^9  bytes = 1,000 MB
1 TB  = 10^12 bytes = 1,000 GB
1 PB  = 10^15 bytes = 1,000 TB

Powers of 2 (binary):
1 KiB = 2^10 = 1,024 bytes   (~same as 1 KB for estimation purposes)
1 MiB = 2^20 ≈ 1M bytes
1 GiB = 2^30 ≈ 1B bytes
```

For estimation, always use powers of 10 (KB = 1,000). Close enough to powers of 2 for interview math.

---

## Storage estimates for common systems

```
URL shortener (10 years, 50B URLs):
  50B × 500 bytes = 25 TB raw → ~250 TB with indexes + replication

Twitter (10 years, 500M tweets/day):
  500M × 280 bytes = 140 MB/day text
  × 365 × 10 = 511 GB text (negligible)
  Media: 30% tweets have image (300KB avg)
  → 150M × 300KB/day = 45 TB/day media → 164 PB/10 years

WhatsApp (1 year):
  65B messages/day × 200 bytes = 13 TB/day metadata
  5% have media (300KB) → 3.25B × 300KB = 975 TB/day media
  → Storage is dominated by media, not text

YouTube (1 year uploads):
  500K videos/day × 100 MB raw = 50 TB/day
  × 10 (transcoded) = 500 TB/day = ~180 PB/year
```

---

> [!tip] Interview framing
> "A URL row is ~500 bytes, a tweet is ~280 bytes, a photo is 300KB–1MB, a 1-min video is ~50MB at 720p. Always separate metadata from media — metadata is negligible compared to media. Multiply storage by 3 for replication and by 1.3–1.5 for index overhead."
