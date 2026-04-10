## The problem with file-level deduplication

File-level deduplication (hashing the entire file) works perfectly when two users upload the exact same file. But it has two problems for large files:

**Problem 1 — Hashing a 10GB file is slow.** Computing SHA-256 of a 10GB file means reading every single byte on the client device. That's CPU-intensive and takes noticeable time before the upload can even start.

**Problem 2 — It can't handle partial matches.** If a user has a 100-page document and edits only the last page, the entire file's hash changes. Even though 99 pages are identical to what's already in storage, file-level dedup treats it as a completely new file and re-uploads everything.

---

## The solution: split into chunks, hash each chunk

Instead of hashing the whole file, you split the file into chunks — say 4MB each — and hash each chunk independently.

```
100-page document (400MB)
→ Split into 100 chunks of 4MB each
→ Hash each chunk: [hash1, hash2, hash3, ..., hash100]

For each chunk, ask S3: "do you have a chunk with this hash?"
→ If yes: skip uploading this chunk
→ If no: upload this chunk

Result:
→ Only the new/modified chunks are uploaded
→ All unchanged chunks are reused from storage
```

This is called **block-level deduplication** (Dropbox calls them "blocks"). It's the approach Dropbox uses — it's why uploading a slightly modified version of a large file is much faster than the initial upload.

---

## The edit case

Say you edit the last page of your 100-page document.

```
Before edit:
Chunks 1-99: [hash1...hash99]  (unchanged)
Chunk 100:   [hash100]         (original last page)

After edit:
Chunks 1-99: [hash1...hash99]  (same — still in S3)
Chunk 100:   [hash100_new]     (changed — needs uploading)
```

Only chunk 100 gets uploaded. 99 chunks are reused. For a 400MB document, you've just uploaded 4MB instead of 400MB.

---

## Chunk-level dedup across different users

Here's a question: can chunks be shared across different users' files?

Yes — if two different files happen to contain identical chunks, those chunks are stored once and shared. But in practice this is rare unless the files have large sections of identical content (like two people sharing the same base document template).

The key constraint: chunks are split at **fixed byte offsets** — every 4MB, regardless of what the content is. **This means chunk boundaries are determined by position in the file**, not by meaning.

```
File A: [title][chapter1][chapter2][chapter3]
         ↓ split every 4MB
         Chunk1: bytes 0–4MB   (part of title + part of chapter1)
         Chunk2: bytes 4–8MB   (rest of chapter1 + start of chapter2)
         ...

File B: [different title][chapter1][chapter2][chapter3]
         ↓ split every 4MB
         Chunk1: bytes 0–4MB   (different title shifts everything)
         Chunk2: bytes 4–8MB   (now at different byte offsets)
```

Even if chapter1 is word-for-word identical across both files, the chunks don't align — because the different title shifted all the byte offsets. Different offsets → different chunk boundaries → different hashes → no dedup.

This is the core limitation of **fixed-size chunking**. It deduplicates perfectly for:
- The same file uploaded twice
- Large unchanged sections of a **modified version of the same file** (edits don't shift offsets of later chunks)

But it does **not** deduplicate across genuinely different files that happen to share content.

> [!info] What is a byte offset?
> A file is just a long sequence of bytes — like a row of numbered boxes, starting at 0. Byte offset is the position number. Byte offset 0 is the first byte, byte offset 4,000,000 is the 4-millionth byte. When you split a file into fixed-size chunks, each chunk starts at a specific byte offset. For two chunks to have the same hash, they must contain the exact same bytes — same content at the same positions within that chunk.

---

## Content-defined chunking (beyond SDE-2 scope)

The limitation above — that fixed-size chunking can't find shared content across different files — is solved by **content-defined chunking**. Instead of splitting at fixed byte offsets, you split at boundaries determined by the content itself (using a rolling hash to detect natural split points). This way, inserting a word at the beginning of a document doesn't shift all subsequent chunk boundaries.

This is used in systems like rsync and more advanced backup systems. For SDE-2 interviews, knowing the limitation of fixed-size chunking and that smarter alternatives exist is enough.

---

## Copy-on-write with chunks

When a user modifies a file, copy-on-write applies at the chunk level too:

```
User A's file → [chunk1][chunk2][chunk3]  (all shared)
User B modifies chunk2
→ New chunk2 uploaded as chunk2_new
User B's file → [chunk1][chunk2_new][chunk3]
User A's file → [chunk1][chunk2][chunk3]  ← untouched
```

`chunk1` and `chunk3` are shared between both users. `chunk2` and `chunk2_new` are separate objects. No mutation of shared chunks ever happens.

> [!important] What chunk-level dedup gives you
> - Fast re-uploads — only changed chunks need uploading
> - Storage savings — unchanged chunks stored once, shared across versions
> - Works for the same file across multiple users (if byte-identical)
> - Does NOT find shared content across different files with different byte layouts

> [!tip] Interview framing
> "For large file storage like Dropbox, I'd use chunk-level deduplication — split each file into fixed-size blocks, hash each block, only upload blocks that aren't already in storage. Edits re-upload only the changed blocks. This is how Dropbox handles fast re-syncs of large files."
