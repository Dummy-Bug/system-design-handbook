# Leaderboard

## Problem Statement
- What we're building (real-time ranking of users by score)
- Core user flows (update score, get top-N, get user rank)
- Out of scope for SDE-1 (multi-game, seasonal resets at scale, percentile breakdown)

## Functional Requirements
- Update a user's score
- Fetch top N users with their scores
- Fetch rank of a specific user

## Non-Functional Requirements
- Reads are frequent (many users checking rankings)
- Score updates can be frequent
- Rank must be reasonably fresh (not necessarily real-time to the millisecond)

## Capacity Estimation
- Number of users, updates per second
- Size of leaderboard data in memory

## High-Level Design
- Client → API server → Redis sorted set + DB
- When to write to DB vs only Redis

## Deep Dives
- Redis sorted set — why it's a perfect fit (ZADD, ZRANK, ZRANGE)
- Persistence — Redis is in-memory, what happens on restart
- DB as source of truth, Redis as read layer
- Handling score ties
