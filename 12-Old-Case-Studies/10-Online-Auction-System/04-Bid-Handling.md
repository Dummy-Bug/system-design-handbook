In architecture there would be producer which would produce the payload to Kafka but we have not shown it in the architecture to save the space.

if we route all the bidding traffic to Auction DB then it can take down the DB as it would contain lot of writes.so we have to serve the highest bid price from some read optimize DB and what better than Redis ?

so whenever a bid comes up we will route it to the Redis cluster inside the cluster we will see if the current bid is higher than the last highest bid if yes then update else ignore it and dump it inside bidding DB. In Redis we can use `Lua scripts`(Lua is a language). so Redis will only contain the highest bid price and when someone wants to view the highest bid  or viewing an auction then their request would be redirected to Bid Query Service and that would query the Redis cluster to get the highest bid.We are also going to setup a SSE connection between Bid Query Service and Client for all those people who wants to view the bid because whenever the bid price changes we do not want to Poll.

![[Excalidraw/Drawing 2026-03-26 14.05.41.excalidraw]]


But there's a problem whenever a new user is going to update the bid there request would go to Bid Mutation Service and this service update the Redis cluster and now based on the redis cluster response now we need to update the bid viewing clients but these clients are connected with Bid Query Service via SSE.
so we have to send the data from Bid Mutation Service to Bid Query Service that hey let's update the highest bid for this particular auction now assume there are 10 machines BQS with 100 users connected to each machine of BQS and assume for all the auction data is coming up then how can we send it ? one way is manual API calls from BMS to BQS and once API call of bid reaches BQS it will check I have all these users connected to me via SSE , send each one of them the latest data . Hence better way is to introduce Redis Realtime PubSub and it's a push based mechanism. Now BMS can dump the new data inside pubsub.

The only thing left is inside the Auction Table we still have the highest_bid_price , now it's a call that we have to make as highest_bid_price is also present inside the Redis Cluster , so do we need it inside auction db as well or not and I think yes we should have it because in Redis we might not want to store the highest bid permently we might need to purge the cache as auction is bit old , so we need highest_bid_price inside auction DB but we do not need immediatley . Redis support something called as [Redis Stream](https://redis.io/docs/latest/develop/data-types/streams/).

![[Excalidraw/Drawing 2026-03-26 14.28.51.excalidraw]]


and we can reduce the load by using batching the request using upsert etc .

Now for viewing all auctions API we show the highest bid of one minute ago.
> Since highest_bid_price in Auction DB is updated asynchronously via Redis Stream with batching, it lags behind real-time by ~1 minute. This is acceptable for the list view — users only need real-time accuracy when they open a specific auction, which queries Redis directly.


**Ending an Auction**

**Rule:** If no bid higher than the current highest bid has been received for the last 24 hours → end the auction.

**Why Job Scheduler over Cron Job:**

- Cron jobs run on fixed schedules (every minute, every hour) → cannot schedule for an exact dynamic timestamp
- No built-in retry if job fails
- No visibility into job status
- Single point of failure

Job Scheduler (Temporal) advantages:

- Schedule job for exact dynamic timestamp ✅
- Automatic retry on failure ✅
- Job history and observability ✅
- Distributed → no single point of failure ✅

**Why Temporal over Airflow:**

- Airflow is designed for batch data pipelines → overkill here
- Temporal is designed for exactly this use case → long running workflows with dynamic timers and retry guarantees

---

**Why reschedule operations are sparse (not expensive):**

```
Total bids coming in     → high volume
Valid bids (higher than  
current highest)         → much lower

Example:
current highest = 500
1000 bids arrive
→ Lua script filters: only ~50 bids beat 500
→ only 50 Redis updates
→ only 50 Redis Stream events
→ only 50 Temporal reschedules ✅
```

Lua script acts as a **filter** — only the small fraction of bids that beat the current highest ever touch Redis Stream or Temporal.

---

**Flow:**

```
Bid arrives
    ↓
Lua script (atomic): is new bid > current highest?
    ↓
NO  → ignore, just write to Bidding DB
    ↓
YES → update Redis Cluster
    → write event to Redis Stream (for Auction DB sync)
    → reschedule Temporal job to now + 24hrs
```

---

**Auction Ending Flow (Temporal orchestrates):**

```
Temporal fires after 24hrs of no higher bid
    ↓
Step 1: Set auction status = "closing" 
        → no new bids accepted for this auction_id
    ↓
Step 2: Force flush Redis Stream → Auction DB
        → don't wait for batch, drain immediately
    ↓
Step 3: Verify Auction DB has latest highest_bid_price
    ↓
Step 4: Mark auction status = "closed"
        Write winner_id + winning_bid_id to Auction DB
    ↓
Step 5: Purge auction data from Redis
```

**Why Step 1 is critical:** Must stop accepting new bids BEFORE flushing, otherwise new bids arriving during flush create another race condition.

So all the Functional Requirements have been served.

In the end we can have Log Ingestion(AWS cloudwatch etc etc) service where we can dump the logs from all of our services and we can use different-different monitoring and alarms.


- so total bids in 1 year = 365 * 1B ~ 400B bids in and in 10 years 4000B bids.

* 1 Bid takes approx 50 Byte if we look at what we are storing inside the table then this is good assumption 
  `so 4000B * 50 Bytes -> 200 *10^12 Bytes ~ 10^14 -> 100TB`

We can store this much amount in DBs very easily these days but problem is if we do not shard it properly then all the writes would go into one Cassandra shard and that would not be that much optimize.so even a basic partition strategy like on auction_id will help here very much


few questions can come like , what if instead of BMS and BQS as two separate microservices we have only one service then do we still need PubSub ? Yes but why ? let's say a new bid update request comes to Monolith Bid service-A but the other users are connected to other instances of Bid service-B etc now how would service-A going to tell it to Bid service-B that it has some updated bid value ? so we have to use PubSub here as well.




