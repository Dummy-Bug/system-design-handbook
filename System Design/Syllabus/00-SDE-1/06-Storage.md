# Storage

## Types of Storage
- Block storage — raw disk, used by OS and databases (EBS, local SSD)
- File storage — traditional file system with folders (NFS, EFS)
- Object/Blob storage — flat namespace, key → object (S3, GCS)
- Which to pick — databases use block, apps share files use file storage, media/binary files use object storage

## Object Storage
- What S3-type storage is and how it works (bucket + key → object)
- Why files don't belong in a relational database (size, cost, wrong tool)
- When to store metadata in DB and binary in object storage
- Pre-signed URLs — give clients temporary upload/download access without exposing credentials
- Storage classes — hot (Standard), warm (Infrequent Access), cold (Glacier). Cost vs access speed tradeoff.
- Content-addressable storage — hash of content is the key, same content never stored twice (deduplication)

## File Uploads
- Client uploads to app server vs client uploads directly to S3 — why direct is better at scale (no bottleneck on your server)
- Multipart uploads — split large files into chunks, upload in parallel, server reassembles
- Resumable uploads — on failure, restart from last successful chunk, not from zero
- Chunking — standard chunk size is 4–8 MB

## Storage Tiers
- Hot tier — SSD, Redis, in-memory. Fastest, most expensive. For frequently accessed data.
- Warm tier — object store (S3 Standard, S3-IA). Slower, cheaper. For data accessed occasionally.
- Cold tier — Glacier, tape. Very slow retrieval. For backups and archival.
- Moving data between tiers — lifecycle policies (S3 can auto-move to Glacier after N days)
- Why tiering matters — serving everything from hot storage is expensive and unnecessary
