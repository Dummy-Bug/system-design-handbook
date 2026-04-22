## The problem with uploading large files as one chunk

Say a user is uploading a 10GB video to YouTube. They're halfway through — 5GB uploaded — and their internet drops for 2 seconds.

If the file is being sent as one continuous stream, that connection break kills the entire upload. 5GB wasted. Start from scratch. Terrible user experience — and a real problem when you consider that mobile connections drop constantly.

---

## The fix: split the file into parts

Instead of sending the file as one giant chunk, you split it into smaller parts — say 100MB each — and upload each part as a separate, independent request.

```
10GB video → 100 parts of 100MB each

Part 1  uploaded ✓
Part 2  uploaded ✓
...
Part 51 uploaded ✓
Connection drops ✗
...connection restored...
Part 52 resumed ✓
Part 53 uploaded ✓
...
```

S3 tracks which parts have been successfully received. When the connection drops and resumes, you only re-upload the parts that failed. The 51 parts already in S3 stay there.

This is called **multipart upload**.

---

## S3 tracks parts by ID, not position

An important detail: S3 doesn't track parts by "how far through the file did we get." It tracks parts by their **part number** — essentially a checklist.

```
Part 1  ✓
Part 2  ✓
Part 3  ✗  (failed)
Part 4  ✓
Part 5  ✓
```

This matters because of parallelism (see below). Parts can arrive out of order. S3 doesn't care — it just checks off each part ID as it arrives. When you tell S3 "complete the upload", it assembles all the parts in order by part number.

So if parts 1-10 fail but 11-50 succeed (due to parallel uploads), S3 knows exactly which parts are missing. You only re-upload parts 1-10. Not everything before part 51.

---

## The parallelism benefit

If you have 100 parts — why upload them one by one? You have 100 independent requests that don't depend on each other. Upload them all simultaneously.

```
Sequential:   Part1 → Part2 → Part3 → ... → Part100  (10 minutes)
Parallel:     All 100 parts uploading at the same time  (1-2 minutes)
```

On a fast connection, parallel multipart upload can cut upload time by 5-10x. This is why large file uploads in well-built apps feel much faster than you'd expect.

---

## The complete multipart upload flow

```
1. Client initiates multipart upload → S3 returns an upload ID
2. Client splits file into N parts
3. Client uploads all parts in parallel, each tagged with part number + upload ID
4. S3 stores each part separately, tracks which are complete
5. Client sends "complete upload" request with the list of part ETags
6. S3 assembles the parts in order, the file is now a single object
```

If the upload is abandoned (client crashes, user cancels), S3 keeps the partial parts until you explicitly abort the multipart upload or a lifecycle policy cleans them up. Left uncleaned, partial multipart uploads can silently accumulate storage costs — something worth mentioning in a design interview when discussing operational hygiene.

> [!important] Multipart upload gives you two things
> - **Resumability** — connection drops? Only re-upload the failed parts, not the whole file
> - **Speed** — upload all parts in parallel, dramatically cutting total upload time

> [!tip] Interview framing
> "For large file uploads I'd use multipart upload — split the file into chunks, upload in parallel for speed, and if the connection drops, only retry the failed chunks. This is standard for any file > a few hundred MB."
