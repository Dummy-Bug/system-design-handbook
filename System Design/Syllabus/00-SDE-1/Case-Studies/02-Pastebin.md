# Pastebin

## Problem Statement
- What we're building (store and share text/code snippets)
- Core user flows (create paste, view paste)
- Out of scope for SDE-1 (syntax highlighting engine, versioning, teams)

## Functional Requirements
- Create a paste with text content
- Retrieve paste by short ID
- Optional expiry

## Non-Functional Requirements
- Pastes can be large (up to a few MB)
- Read-heavy workload
- Short IDs must not collide

## Capacity Estimation
- DAU, paste size distribution
- Storage growth over time
- Read vs write QPS

## High-Level Design
- Client → API server → DB + object storage
- Where to store small vs large pastes
- Short ID generation

## Deep Dives
- Why large text content should go in object storage not DB
- Short ID generation — same approach as URL shortener
- Caching popular pastes
- Expiry — how to clean up expired pastes (TTL vs background job)
