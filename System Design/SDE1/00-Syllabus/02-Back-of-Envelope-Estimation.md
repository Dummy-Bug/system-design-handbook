## Phase 2 - Back of Envelope Estimation

> HLD relevance: estimation is what turns a vague design into a reasoned design.
> At SDE-1 level, you should be able to estimate enough to justify caching, queues, replicas, and object storage.

### 2.1 Numbers to memorize

**Latency**
| Operation | Rough latency |
|---|---|
| RAM access | ~100 ns |
| SSD read | ~100-200 us |
| HDD seek | ~10 ms |
| same-datacenter network | ~0.5 ms |
| cross-region network | ~100-150 ms |

**Data sizes**
- short text message: ~200 bytes
- user profile: ~1 KB
- photo: ~300 KB to 1 MB
- short video: tens of MB

**Traffic rules of thumb**
- peak traffic is usually 3x to 5x average
- social systems are often read-heavy
- media dominates storage, not metadata

### 2.2 Estimation framework

**Step 1 - traffic**
- DAU / MAU
- actions per user per day
- average QPS
- peak QPS
- separate reads from writes

**Step 2 - storage**
- size per record
- records per day
- retention period
- replication factor

**Step 3 - bandwidth**
- incoming traffic from writes/uploads
- outgoing traffic from reads/downloads

**Step 4 - cache sizing**
- identify hot data
- estimate working set, not total data size

### 2.3 Practice estimations

**1. URL Shortener**
- write QPS and read QPS
- yearly storage for short links
- when hot-key caching becomes necessary

**2. Notification System**
- notifications per user per day
- per-channel split - push, email, SMS
- queue throughput needed at peak

**3. Chat System**
- message QPS
- storage growth per day
- media vs text storage difference

**4. News Feed**
- post write QPS
- feed read QPS
- fan-out amplification

**5. File Upload / Photo Sharing**
- upload bandwidth
- object storage growth
- CDN egress for downloads

### 2.4 When estimation changes architecture
- QPS > 10K - start thinking about caching and replicas
- QPS > 100K - start thinking about sharding
- storage in TBs - object storage and partitioning matter
- high write rate - queues and batching help
- high read rate - cache and CDN help

### 2.5 What interviewers want here
- reasonable assumptions stated out loud
- simple arithmetic
- architecture justified by numbers
- no pretending the estimates are exact

