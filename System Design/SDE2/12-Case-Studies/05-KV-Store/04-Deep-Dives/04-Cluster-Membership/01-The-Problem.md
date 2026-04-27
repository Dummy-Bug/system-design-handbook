## The Problem — How Do 1,200 Nodes Know About Each Other?

A coordinator node receives `put("user:123", "Alice")`. It hashes the key, walks the ring, and finds that Node B, Node C, and Node D own this range. But how does the coordinator **know** that? Something has to maintain a mapping of which nodes exist in the cluster and which key ranges they own.

And it's not just about routing. The coordinator also needs to know which nodes are **alive** right now. If Node D is dead, the coordinator shouldn't waste time sending it a request — it should trigger hinted handoff immediately.

Every node in the cluster needs this information, because any node can be a coordinator (leaderless architecture — no special nodes).

---

## Option 1 — Central Registry

One dedicated server holds the full membership mapping: which nodes exist, which ranges they own, who's alive, who's dead. Every node asks this central server when it needs to route a request.

This is the simpler approach — one source of truth, easy to update when a node joins or leaves. But it has serious problems at our scale:

```
1,200 nodes × hundreds of requests/sec per node = hundreds of thousands of lookups/sec

All hitting one central server.
```

**Single point of failure.** If the registry goes down, no node can route any request. The entire cluster is effectively dead — not because the data is lost, but because nobody knows where anything is.

### Can we scale the registry?

Yes — add read replicas, put a load balancer in front, replicate for fault tolerance. But now we're building a whole distributed system just to manage our distributed system. It's complexity on top of complexity.

More importantly, it **contradicts our architecture**. We chose leaderless specifically to avoid any single special node. Every node is equal, any node can coordinate. Adding a central registry reintroduces a special component that the whole cluster depends on — exactly the kind of dependency we rejected when we chose leaderless over single-leader.

---

## Option 2 — Every Node Holds Its Own Copy

Instead of a central registry, every node maintains its own copy of the full membership list — which nodes exist, which ranges they own, who's alive, who's dead. No central server to query, no single point of failure. Each node can route requests using its own local copy.

The challenge: when something changes (a node joins, a node dies, a node recovers), how does every node find out? With a central registry, you update one place. With local copies on 1,200 nodes, the change has to propagate to all of them.

This is where **gossip protocol** comes in — nodes tell a few neighbors about changes, those neighbors tell their neighbors, and eventually the entire cluster converges on the same view. It's decentralised, fault-tolerant, and aligned with our leaderless design.
