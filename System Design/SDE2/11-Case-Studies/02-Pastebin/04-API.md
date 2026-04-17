## Create a Paste

```
POST /api/v1/pastes

Header:
  Authorization: Bearer <JWT>

Body:
  {
    content:      string,           // the paste text
    expiryDays:   enum(1 | 7 | 30), // expiry window, default 30 if omitted
    customAlias?: string            // optional, max 8 chars — user-chosen short code
  }

Response 200 OK:
  {
    data:  { shortCode: string },
    error: null
  }
```

**Why JWT in the header?**
Writes require authentication — JWT carries the user identity without a DB lookup on every request. The short code in the response is what the user shares. If `customAlias` is provided and available, it becomes the short code. If absent, the system generates one.

**Why `expiryDays` as an enum?**
Free-form duration inputs require validation, sanitisation, and edge-case handling. Fixed options (1, 7, 30) mean the server never receives an invalid value — the client enforces the constraint. Simpler validation, simpler cleanup jobs (you know exactly which buckets to scan at expiry time).

**Why `customAlias` is optional and capped at 8 chars?**
Most users want a system-generated code — don't force a decision they don't care about. The cap keeps short codes short and consistent with auto-generated code length. Naming it `customAlias` rather than `custom` makes the intent explicit in the API contract.

---

## Read a Paste

```
GET /api/v1/pastes/:shortCode

No auth required — anyone with the link can read

Response 200 OK:
  {
    data: {
      content:   string,
      expiresAt: timestamp   // "expires April 21 2026 at 14:00 UTC"
    },
    error: null
  }

Response 404:
  {
    data:  null,
    error: "not found or expired"
  }
```

**Why no `userName` in the response?**
Exposing the creator's identity was not a functional requirement. Adding unrequested fields bloats the response and creates a privacy surface — if a user created a paste anonymously they'd expect their identity not to be leaked. Only return what was agreed in FRs.

**Why return `expiresAt`?**
The viewer needs to know how long the content will be available — especially useful for time-sensitive pastes like incident logs or temporary configs. Showing "expires in 3 days" is genuinely useful UX. The client can render a countdown or a date.

**Why 404 for both not-found and expired?**
Merging both cases into 404 avoids leaking information about whether a short code ever existed. If expired pastes returned a different error code, an attacker could enumerate which codes existed and when they were created.

---

## Delete a Paste

```
DELETE /api/v1/pastes/:shortCode

Header:
  Authorization: Bearer <JWT>

Response 204 No Content  (success — paste deleted)
Response 204 No Content  (success — paste didn't exist, still return 204)
Response 403 Forbidden:
  {
    error: "not your paste"
  }
```

**Why 204 even when the paste doesn't exist?**
This is an **idempotent delete**. If the user clicks delete, the server deletes the paste, but the response never makes it back due to a network failure — the client retries. If the second call returns 404, the client thinks something went wrong, but everything is actually fine. Returning 204 on both calls means retries are always safe. Same result whether called once or ten times.

**Why 403 when a different user tries to delete?**
The JWT carries the caller's `userId`. Before deleting, the server checks `JWT.userId == paste.creatorId`. If they don't match, return 403 Forbidden — the caller is authenticated but not authorised to touch this resource. This is a hard security requirement: users must not be able to delete each other's pastes.

**Note on soft vs hard delete:**
The delete operation sets a `deleted_at` timestamp on the row rather than physically removing it. This keeps audit trails intact, makes the operation fast (no cascading deletes), and allows for potential recovery windows. The paste becomes inaccessible immediately but the row persists briefly before a background job cleans it up.

---

## Full API Summary

```
POST   /api/v1/pastes              Create paste (auth required)
GET    /api/v1/pastes/:shortCode   Read paste   (no auth)
DELETE /api/v1/pastes/:shortCode   Delete paste (auth required, must be creator)
```

---

> [!tip] Interview framing
> "Three endpoints: POST to create (auth required, returns shortCode), GET to read (no auth, returns content + expiresAt), DELETE to remove (auth required, 403 if not creator, idempotent — 204 even if paste doesn't exist). Custom alias is an optional field on the POST body, capped at 8 chars. Expiry is an enum not free-form — simpler validation and cleanup."
