# Encryption

## Two Different Problems, Two Different Solutions

> [!info] Encryption in transit protects data while it's moving. Encryption at rest protects data while it's sitting on disk.

---

## Encryption In Transit — TLS/HTTPS

**The problem:** Data travelling over the internet passes through routers, ISPs, and data centers. Without encryption, anyone in between can read it.

```
Without TLS:  POST /login  password=secret123   ← anyone intercepting can read this
With TLS:     POST /login  x7Kp#mN2$qL9...      ← meaningless without the key
```

**How TLS works (one-liner for interviews):**
> "TLS does a handshake where client and server agree on a shared encryption key without transmitting it over the network, then all data is encrypted with that key."

```
HTTPS = HTTP + TLS
     = your API, encrypted in transit
```

> [!important] HTTPS is non-negotiable. Bearer tokens sent over plain HTTP can be intercepted trivially. Always enforce HTTPS — redirect HTTP to HTTPS, reject plain HTTP at the API gateway.

---

## Encryption At Rest — AES-256

**The problem:** A hacker breaks into your database server and copies the entire users table. The data never travelled anywhere — it was just sitting on disk. Without encryption, they have everything.

```
Without encryption at rest:  { "ssn": "123-45-6789" }   ← readable
With encryption at rest:     { "ssn": "x7Kp#mN2..." }   ← useless without key
```

**AES-256** — the standard symmetric encryption algorithm used for data at rest. 256-bit key, practically unbreakable with current computing.

```
DB compromised → attacker gets encrypted bytes → useless without decryption key
Keys stored separately (AWS KMS, HashiCorp Vault) → attacker can't get both
```

> [!tip] For interviews: "I'd encrypt sensitive fields at rest using AES-256, with keys managed by a dedicated key management service like AWS KMS — separate from the data itself."

---

## Summary

```
Encryption in transit  → TLS/HTTPS
                         protects data MOVING over the network
                         prevents man-in-the-middle attacks

Encryption at rest     → AES-256
                         protects data SITTING on disk
                         prevents damage from DB breach or physical theft
```

> [!important] Both are required. A system with only one is still vulnerable.
> TLS without at-rest encryption → breach the DB, get plaintext data.
> At-rest encryption without TLS → intercept the network, get plaintext data.
