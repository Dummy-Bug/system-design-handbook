## When to reach for object storage

Any time the problem involves: videos, images, audio, documents, backups, ML model artifacts, static website assets, database snapshots. If it's a large unstructured file — it goes in object storage, not a relational DB.

---

## Core model

```
Object storage = flat namespace + key-value for bytes
→ PUT file → get back a key
→ GET key → get back the bytes
→ No queries, no schema, completely opaque
```

---

## The two-layer pattern

```
Your DB  → stores the key (pointer)
S3       → stores the actual bytes

User uploads → bytes go to S3 → key goes to Postgres
User fetches → key from Postgres → bytes from S3 directly
```

---

> [!question] How do you serve private files from S3 without routing all traffic through your server?

> [!success]-
> Pre-signed URLs. Your server handles the auth check, then asks S3 to generate a temporary URL (e.g., expires in 15 minutes). User fetches directly from S3. Server never touches the bytes. The expiry prevents permanent sharing — but an in-progress download completes fine even after the URL expires (like a concert ticket — once you're inside, you're inside).

---

> [!question] A user is uploading a 10GB video and their connection drops at 5GB. What happens?

> [!success]-
> With multipart upload — nothing is lost. The file was split into parts (e.g., 100MB each) before uploading. S3 tracks which parts completed. On reconnect, only the failed parts are re-uploaded. Parts also upload in parallel — dramatically cutting total upload time.
> 
> **Key detail:** S3 tracks by part ID (a checklist), not position. Even with parallel uploads, if parts 1-10 fail and 11-50 succeed, only parts 1-10 need retrying.

---

> [!question] How does Dropbox avoid storing duplicate files?

> [!success]-
> Content-addressable storage — the SHA-256 hash of the file's content becomes its S3 key. Before uploading, the client computes the hash and checks if that key already exists. If it does, skip the upload entirely.
>
> For large files — chunk-level dedup: split into fixed-size blocks (e.g., 4MB), hash each block, only upload blocks not already in storage. Edits re-upload only changed blocks. Unchanged blocks are reused.
>
> **Limitation:** fixed-size chunking can't find shared content across different files — only across the same file or modified versions of it.
>
> **Mutable writes:** use copy-on-write. Edits create a new object with a new hash. Shared objects are never mutated.

---

## Storage Classes

```
S3 Standard          → hot data, instant access, expensive
S3 Infrequent Access → warm data, instant access, cheaper + retrieval fee
S3 Glacier           → cold data, minutes-hours retrieval, very cheap
```

Use lifecycle policies to auto-tier based on age/access frequency.

---

## Quick decision map

```
Large unstructured files (video, image, PDF)     → S3 / object storage
Private file access                              → Pre-signed URLs
Large file uploads (> a few hundred MB)          → Multipart upload
Avoid storing duplicate files                    → Content-addressable + chunk dedup
Cost-efficient long-term storage                 → Storage classes + lifecycle policies
```

---

## Systems that use object storage

| System | What goes in object storage |
|---|---|
| YouTube | Video files, thumbnails |
| Dropbox / Google Drive | All user files |
| Instagram | Images, videos |
| Gmail | Email attachments |
| Netflix | Video content |
| Any web app | Static assets (JS, CSS, images) |
