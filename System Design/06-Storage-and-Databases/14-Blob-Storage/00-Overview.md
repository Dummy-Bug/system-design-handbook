# Blob / Object Storage — Overview

> [!info] Object storage is a system designed for one thing only — storing massive, unstructured files cheaply and reliably. No queries, no rows, no schema. Just: put file in, get key back. Use key to get file. Dumb but powerful.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Object-Storage-Model.md | What object storage is, why DBs can't do this, the two-layer pattern |
| 02-Presigned-URLs.md | Temporary access for private files without routing through your server |
| 03-Multipart-Upload.md | Resumable + parallel uploads for large files |
| 04-Content-Addressable-Storage.md | Hash = key, deduplication at the file level |
| 05-Chunk-Level-Deduplication.md | Block dedup, fixed-size chunking, copy-on-write |
| 06-Storage-Classes.md | Hot/warm/cold tiers — cost optimisation for access patterns |
| 07-Interview-Cheatsheet.md | Quick reference for revision |

---

## The one-line model

```
Relational DB   → structured rows, queryable, optimised for transactions
Document store  → JSON documents, queryable by fields
Object storage  → raw bytes, opaque, fetch by key only — built for massive files
```

---

## Where it fits in system design

Any time the interviewer mentions files, images, videos, backups, or static assets — object storage is the answer for the actual bytes. Your relational DB stores the **pointer** (the key). S3 stores the **file**.

```
User uploads video
→ Video bytes go to S3
→ S3 returns a key
→ Key gets stored in Postgres alongside the user record

User watches video
→ Look up key in Postgres
→ Fetch video directly from S3
```

> [!tip] When to mention in interviews
> Dropbox, YouTube, Instagram, Gmail attachments, static website assets, ML model artifacts, database backups — anywhere files live, object storage is involved.
