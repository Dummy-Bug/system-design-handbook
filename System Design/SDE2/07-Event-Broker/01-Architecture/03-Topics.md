
> [!info] A topic is a named category for events. Producers write to a topic. Consumers subscribe to a topic. Every event in Kafka belongs to exactly one topic.

---

## What a topic is

In a large system you have many different kinds of events happening at the same time — ad clicks, user signups, payment completions, inventory updates. You can't throw all of them into one undifferentiated stream. Consumers need to say "I only care about ad clicks" without having to sift through payment events and inventory updates.

A topic is just a named channel. You create a topic called `ad_clicks`, another called `payment_events`, another called `user_signups`. Producers write events into the right topic. Consumers subscribe to whichever topics they care about.

```
Producer: ad server     → writes to → topic: ad_clicks
Producer: checkout svc  → writes to → topic: payment_events
Producer: auth svc      → writes to → topic: user_signups

Consumer: billing svc       → reads from → topic: ad_clicks
Consumer: fraud svc         → reads from → topic: ad_clicks
Consumer: analytics svc     → reads from → topic: ad_clicks, payment_events
Consumer: email svc         → reads from → topic: user_signups
```

Topics let producers and consumers operate completely independently. The ad server doesn't know which services are reading its events. Billing doesn't know how many other consumers are on the same topic. They just agree on the topic name, and Kafka handles the rest.

---

## A topic is not one file on one machine

At small scale you could imagine a topic as a single log file — events appended in order, consumers reading from it. That works until the volume grows.

At 100,000 ad clicks per second, one machine can't keep up. One disk fills up. One network card saturates. So Kafka splits each topic into **partitions** — independent sub-logs, each living on a different machine — so the write load and storage are spread across the cluster.

That's covered in the next file. For now: a topic is the logical name. Partitions are how Kafka makes that topic scale.

> [!important] Topic names are the contract between producers and consumers. If a producer writes to `ad_clicks` and a consumer subscribes to `ad-clicks` (dash instead of underscore), they never connect. Agree on naming conventions early.
