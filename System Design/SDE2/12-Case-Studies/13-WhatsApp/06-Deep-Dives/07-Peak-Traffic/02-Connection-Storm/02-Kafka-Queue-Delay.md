
> [!info] Queuing registry writes via Kafka
> Instead of writing to the connection registry synchronously on connect, the connection server publishes an event to Kafka. Registry workers drain the queue at a controlled rate.

---

## The solution

When Alice connects to connection server 7, instead of immediately writing to Redis:

```
Old flow (synchronous):
Alice connects → HSET registry user:alice conn_server_7 → done

New flow (async):
Alice connects → publish {user: alice, server: conn_server_7} to Kafka → done
```

Alice's connection is live immediately. The Kafka event is picked up by a registry worker, which writes to Redis at a rate the cluster can handle.

```
Kafka topic: connection-registry-updates
Consumers:   registry worker pool (N workers)
Each worker: reads events, writes to Redis at controlled rate
```

The write rate to Redis is now determined by the consumer throughput, not the connection rate. You control the drain rate by scaling the consumer pool.

---

## Controlling the drain rate

```
Target Redis write rate:   100K ops/second per primary
10 primaries:              1M writes/second total capacity
Consumer pool:             sized to produce ~800K writes/second (leaving headroom)
```

The Kafka queue absorbs the spike. At midnight, 500M events pile into Kafka. The consumer pool drains them steadily over the next few minutes. Redis is never overwhelmed.

---

## Queue depth monitoring

The Kafka consumer lag (queue depth) tells you how far behind the registry is. Under normal conditions this is near zero. During a connection storm it spikes, then drains within a few minutes as the consumers catch up.

> [!tip] Interview framing
> "Registry writes go through Kafka. On connect, the connection server publishes an event. A consumer pool drains it at a rate Redis can handle. The connection is live immediately — the registry update follows asynchronously within seconds."
