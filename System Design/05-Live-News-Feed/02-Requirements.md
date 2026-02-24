### Functional Requirements

* News Feed Generation (how to generate feed)
* News Feed Content (posts,stories etc)
* News Feed Publishing/Displaying (like order of posts etc)

### Non Functional Requirements

* **Low Latency** -> News Feed Generation should happen in real time like the latency seen by the end user should be minimal like 1 or 2 seconds.like if we open the Netflix we can see that it does not provide us the feed instantly rather it shows us empty boxes (**Skeleton Loading**)that are filled later by the content. That's how they make sure that people are hooked to the system and make 2seconds feel as if content was available in an instant.
* **Scalability** -> We need highly scalable system that meets the demand of ever increasing number of users.
	* **Availability and Fault Tolerance** -> Availability is prioritized for a News Feed because the feed is a discovery or consumption surface, not a correctness-critical system. Missing or slightly stale content is acceptable; the system being down is not.
	
	**News Feed Is Not a Source of Truth**
	
	A feed is a derived view, not primary data.
	
	- Likes, comments, posts are stored elsewhere (source-of-truth systems)

	- Feed is a materialized / computed projection of that data
	
	If the feed is:

	- Slightly stale
	- Missing a post temporarily
	- Ordered a bit differently
	
	👉 Nothing breaks permanently
	But if the feed is unavailable:
	- App feels broken
	- Users churn immediately
	
	---
	
	**User Perception: Downtime Hurts More Than Staleness**
	
	From a user’s perspective:
	
	- ❌ App doesn’t load feed → “App is down”

	- ✅ Feed loads but misses a post → barely noticed
	
	Example:
	- You post something
	- Your follower sees it after 30 seconds instead of instantly
	
	That’s acceptable.
	But:
	
	- Feed fails to load for 10 seconds → user closes app
	Availability directly impacts engagement and retention.
	
