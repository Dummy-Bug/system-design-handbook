### Functional Requirements
* Design a storage that supports key value store.
* We can for now avoid durability.
* For now In-memory storage is fine.
* **Keys** only STRINGS are allowes
* **Values** any data type can come up.

In the functional requirements more often than not we will get help from the interviewer but for non fucntional requirements interviewer would expect us to think about the cases that we would like to work for.

### Non Functional Requirements
* Scale -> 10B entries as key value
* **READ QPS → 100k – 1M**
	* This is an **internal infrastructure system** (Redis-like), so MAU/DAU do not apply.
	- Load is driven by **upstream services**, not users.
	- A single upstream request may generate **multiple KV reads** (fan-out).
	- Multiple independent flows (sessions, caching, rate limits, configs, etc.) may use the same store.
	- Therefore, QPS is defined as **aggregate system capacity**, not per-flow traffic.
	We design for:
	- **100k–1M sustained read QPS**
	- Ability to handle burst and retry amplification

* ***WRITE QPS → 50k – 100k**
	- Writes are typically lower than reads but more expensive.
	- Writes involve:
	    - Memory allocation
	    - Possible eviction
	    - Rehashing
	    - Synchronization
	- Write throughput usually becomes the **scalability bottleneck** before reads.
- **Latency** -> <5ms for Writes and <2s for Reads



