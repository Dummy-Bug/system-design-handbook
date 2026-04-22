# Security Basics

## Authentication vs Authorization
- What authentication is (who are you — proving identity)
- What authorization is (what can you do — checking permissions)
- Why they're separate concerns — you can be authenticated but not authorized
- Common confusion and mistakes (mixing both in one layer)

## Authentication Methods
- Session-based auth — server stores session, client holds session ID in cookie
- Token-based auth — stateless, JWT. Server doesn't store anything.
- OAuth 2.0 — delegated access ("Login with Google"). What problem it solves, not the internals.
- API keys — long-lived tokens for service-to-service communication
- When to use which — sessions for traditional web apps, JWT for APIs, OAuth for third-party login

## JWT Basics
- What a JWT contains — header, payload (claims), signature
- How it's verified — server checks signature without DB lookup (stateless)
- What JWT is NOT — it's not encrypted by default (base64 encoded, anyone can decode the payload)
- Access token vs refresh token — access token short-lived (15 min), refresh token long-lived (days/weeks)
- Why short-lived access tokens — if stolen, expires soon. Refresh token rotates it silently.

## Authorization Models
- RBAC (Role-Based Access Control) — assign roles to users, roles have permissions. Simple, common.
- ACL (Access Control List) — per-resource permission list. More granular, more complex.
- When to use RBAC vs ACL — RBAC for most apps, ACL when per-file or per-resource permissions needed (Google Drive, Dropbox)

## Encryption
- Encryption in transit — TLS everywhere, even internal services. What HTTPS provides.
- Encryption at rest — AES-256 for sensitive data on disk (PII, financial data)
- Both are required — TLS doesn't protect data sitting on disk

## HTTPS and TLS
- Why HTTP alone is not safe (plain text, man-in-the-middle)
- What TLS does — encrypts the channel, verifies server identity via certificate
- Certificates — what they prove (server is who it claims to be)
