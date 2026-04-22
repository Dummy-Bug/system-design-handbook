# Simple Social Feed

## Problem Statement
- What we're building (users post, followers see posts in a feed)
- Core user flows (create post, follow user, view feed)
- Out of scope for SDE-1 (fanout at celebrity scale, ranking/recommendations, media)

## Functional Requirements
- Create a post
- Follow / unfollow a user
- View chronological feed (posts from people you follow)

## Non-Functional Requirements
- Reads (feed view) are far more frequent than writes (new post)
- Feed should be reasonably fresh
- No need to handle millions of followers per user at this level

## Capacity Estimation
- DAU, posts per user per day
- Average follows per user
- Feed fetch QPS

## High-Level Design
- Client → API server → DB
- Tables needed (users, posts, follows)
- How to generate a feed (query posts from followed users, order by time)

## Deep Dives
- Feed generation — pull model (query at read time) vs push model (fanout on write)
- Why pull model is fine at SDE-1 scale
- Pagination on the feed (cursor-based)
- Caching the feed for active users
- What breaks when a user has 1M followers (and why that's SDE-2)
