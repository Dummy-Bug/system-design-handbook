
> [!danger] The async upload creates a window where the DB row exists, the user has a valid shortCode, but the content is nowhere. If the upload fails, the paste is permanently broken.

---

## What broken looks like

The user submits a paste. They get back:

```
201 Created
{ "shortCode": "aB3xYz" }
```

They copy the link. They share it. Meanwhile, the background S3 upload fails — S3 returns a 500, or the worker process crashes, or the network drops.

Now the DB row looks like this:

```
short_code:  aB3xYz
s3_url:      NULL
status:      IN_PROGRESS
content:     (not stored anywhere)
```

Someone clicks the link:

```
GET /paste/aB3xYz
  → cache miss (nothing cached yet)
  → DB lookup → row found, s3_url = NULL
  → nothing to fetch
  → ???
```

The read path has no content to return. The paste exists in the DB but is unreadable. The original writer has no idea — they got a 201 and assumed everything worked.

---

## Why this is a durability problem

Durability means: once you tell a user their data is saved, it stays saved. Returning 201 Created is an implicit promise — "your paste exists, here's the shortCode."

If the async upload silently fails and the paste becomes unreadable, that promise is broken. The user's data is effectively lost — they can't retrieve it, and they don't know why.

This is the failure mode the state machine is designed to handle.

---

## The dedup case makes it worse

Recall the dedup check: if two users submit identical content, only one S3 object is stored and both rows point to the same s3_url (via ref_count).

If the first upload fails, neither user's paste has content. Both got 201s. Both pastes are broken. The failed upload affects multiple rows simultaneously.

This is why silent failures are unacceptable — a single S3 upload failure can corrupt multiple pastes.
