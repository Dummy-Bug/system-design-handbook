## The deduplication problem

Imagine Dropbox. A million users all upload the exact same file — say, a popular PDF textbook. Should S3 store a million separate copies of that file?

Of course not. The storage cost alone would be absurd, and every single copy is byte-for-byte identical. You only need one copy.

But how does S3 know two files are identical without comparing every single byte of both files? Comparing a 500MB file byte-by-byte against every existing file in storage would be impossibly slow.

---

## The solution: hash the file

You run the file through a **hash function** — something like SHA-256. A hash function takes any input (a file of any size) and produces a fixed-length fingerprint — say, a 64-character string.

The key property: **same input always produces the same hash**. And for practical purposes, different inputs produce different hashes.

```
SHA-256("hello world") → b94d27b9934d3e08a52e52d7da7dabfac484efe04294e576b1...
SHA-256("hello world") → b94d27b9934d3e08a52e52d7da7dabfac484efe04294e576b1...  (identical)
SHA-256("hello World") → 64ec88ca00b268e5ba1a35678a1b5316d212f4f366b2477232...  (completely different)
```

Even a single character difference produces a completely different hash. This is what makes hashing useful for detecting duplicates.

---

## Content-addressable storage

In a **content-addressable storage** system, the hash of the file's content *is* the key. Instead of generating a random key or using a filename, you compute the hash and use that as the S3 key.

```
File: the popular textbook PDF
SHA-256 hash: "a3f9c2..."

S3 key: "a3f9c2..."
```

Now when user #2 tries to upload the same textbook:

```
Client computes SHA-256 of the file → "a3f9c2..."
Client asks S3: "do you already have an object with key a3f9c2...?"
S3: "yes"
Client: skips the upload entirely
```

No upload needed. S3 already has the file. Both users' accounts now point to the same key — one copy stored, zero bytes wasted.

---

## Where deduplication happens

The deduplication check happens **before** the upload. The client computes the hash locally, asks S3 if it already exists, and only uploads if it doesn't. This means the user doesn't waste bandwidth uploading a file that's already there.

> [!danger] Hashing a 10GB file on the client is slow
> Computing SHA-256 of a 10GB file means reading every byte of that file — that takes time and burns CPU on the user's device. This is why file-level deduplication alone isn't enough for very large files. The solution is chunk-level deduplication — covered in the next file.

---

## The mutable write problem

There's a subtlety here. If two users share the same file (pointing to the same S3 key), what happens when one of them edits it?

If you mutate the object in place, user A's edit overwrites user B's file. That's a disaster.

The fix is **copy-on-write**: when a user modifies a file, you don't touch the original object. Instead, you create a new object with the modified content — which gets its own new hash and its own new key. User A's account now points to the new key. User B's account still points to the old key, completely untouched.

```
Before:
  User A → key: "a3f9c2..."  (the original textbook)
  User B → key: "a3f9c2..."  (same object)

User A edits the file:
  New file → new SHA-256 → new key: "7b2e91..."
  
After:
  User A → key: "7b2e91..."  (their modified version)
  User B → key: "a3f9c2..."  (original, untouched)
```

Shared objects are **never mutated**. Edits always produce new objects. This is safe, simple, and the standard approach.

> [!tip] Interview framing
> "I'd use content-addressable storage — the SHA-256 hash of the file becomes its key. Before uploading, the client checks if that hash already exists in storage. If it does, we skip the upload entirely — deduplication at zero cost. Edits use copy-on-write, so shared objects are never mutated."
