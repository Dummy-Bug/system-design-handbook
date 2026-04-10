Cassandra was directly inspired by two systems — Bigtable (for the data model) and Amazon Dynamo (for the replication model). So they share a lot of DNA: column families, row keys, sparse cells, LSM trees. The differences are architectural, and they matter for interviews because they determine which system fits which problem.

---

## Architecture — masterless vs master + tablet servers

The most fundamental difference. **Cassandra has no master node at all. Every node is equal, every node can be a coordinator, and every node knows the full ring topology via gossip**.

Bigtable has a master node that holds the tablet assignment map — which tablet server owns which row range. Clients must ask the master before they can route a request to the right tablet server.

```
Cassandra:
Client → Any Node → "I know the full ring via gossip, key X is on Node C" → Node C
(pure local computation, no external lookup)

Bigtable:
Client → Master → "Tablet Server 2 owns that row range" → Tablet Server 2 → GFS
(external metadata lookup required)
```

**Why this matters:** Cassandra's masterless design means no single point of failure. Any node can die and the cluster keeps serving requests. Bigtable's master is a SPOF — if it goes down, clients can't find data until it recovers.

> [!info] Gossip — how Cassandra stays masterless
> Every second, each Cassandra node exchanges cluster state with a few random neighbours — who's alive, who owns which ring range. Within seconds, every node converges on the same complete picture of the cluster. No central server needed. This is what makes the coordinator pattern work without a master.

---

## Storage — local disk vs GFS

In Cassandra, each node writes SSTables to its own local disk. The node owns its data physically. If the node dies, that data is only available through replicas on other nodes.

In Bigtable, tablet servers write nothing to local disk. All data — SSTables, write-ahead logs — lives on GFS, a separate distributed storage layer that handles its own internal replication. Tablet servers are stateless compute — they process requests but own no data.

```
Cassandra node dies:
→ local disk dies with it
→ data survives only via replication (RF=3 means 2 other nodes have copies)
→ replacing the node requires streaming data back — can take hours

Bigtable tablet server dies:
→ no data lost — it was all on GFS
→ master reassigns the tablet to another server in seconds
→ that server opens the GFS files immediately — no data copying
```

**Why this matters:** Bigtable's disaggregated storage makes failure recovery near-instant and operationally simple at scale. Cassandra's local disk model gives lower latency (data is always local, no network hop to a storage layer) but makes node recovery expensive.

> [!info] Disaggregated storage
> Separating compute from storage means any compute node can serve any data — the storage layer outlives individual machines. This pattern is now standard in cloud databases: Amazon Aurora, Google Spanner, Azure Cosmos DB all use it.

---

## Consistency — tunable vs strong by default

Cassandra gives you a dial. Every read and write can be configured independently — ONE for maximum throughput, QUORUM for balanced consistency, ALL for strong consistency. You choose the trade-off per operation, and the R+W>N formula determines whether you get strong or eventual consistency.

Bigtable is strongly consistent within a single row by default. **There is no tuning required** — a read always returns the latest committed write for that row. This is possible because only one tablet server owns a given row at any time, so there is no risk of two servers having conflicting versions.

```
Cassandra:  tunable — ONE / QUORUM / ALL per operation
Bigtable:   strong consistency built in — always reads the latest write per row
```

**Why this matters:** Cassandra's tunability makes it flexible — you can optimise for throughput when consistency can be relaxed, and tighten up when it can't. Bigtable's strong consistency is simpler to reason about but less flexible.

---

## The full comparison

| Property | Cassandra | Bigtable |
|---|---|---|
| Architecture | Masterless, peer-to-peer | Master + tablet servers |
| Routing | Gossip — every node knows the ring | Master holds tablet map |
| Storage | Local disk per node | GFS (disaggregated) |
| Node failure | Data at risk, slow recovery | No data loss, instant recovery |
| Consistency | Tunable (ONE / QUORUM / ALL) | Strong per row by default |
| SPOF | None | Master node |
| Open source | Yes | No (Cloud Bigtable is managed) |
| Self-hosted | Yes | No (Google Cloud only) |

---

## When to pick which

```
Cassandra:
✅  You need to self-host or run on-premise
✅  You need tunable consistency per operation
✅  You want no single point of failure by design
✅  Your team is comfortable managing replication and compaction

Bigtable:
✅  You're already in Google Cloud
✅  You want strong consistency without configuration
✅  You want instant node recovery with no data migration
✅  You'd rather pay Google to operate it than manage it yourself
```

> [!tip] Interview framing
> "Both are wide-column stores with the same data model — column families, sorted row keys, sparse cells. The architectural difference is that Cassandra is masterless and stores data locally, while Bigtable separates compute from storage via GFS and uses a central master for tablet routing. For Google Cloud workloads needing strong consistency and zero-ops, Bigtable. For self-hosted, tunable, no-SPOF deployments, Cassandra."
