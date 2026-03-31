## Functional

- User should be able to watch/stream a movie on their devices (mobile, laptop, tablet, etc.)
- Support admins to upload the videos that would be watched by the users.


## Non Functional

### 1. High Availability over Strong Consistency

**Availability is our top priority** — every streaming request from a viewer must receive a valid response.

> [!note] Why eventual consistency is acceptable here
> Unlike a banking system, movie streaming does **not** require instant consistency. Consider how YouTube or Netflix handle uploads:
> - A video is uploaded → it enters a **processing pipeline** (transcoding, subtitle generation, copyright checks, timestamping)
> - During this phase, the video is **not yet visible** to viewers
> - Netflix and Prime Video know movie release dates **months in advance**, so they begin ingestion and processing well before the launch date
>
> **Example:** A movie launching on April 1st may start its upload and processing pipeline on March 20th — giving the system 10+ days of headroom.

We can tolerate **eventual consistency** in content availability, but every active viewer's request must always get a valid response.

---

### 2. Support for Large File Uploads (10–20 GB+)

Raw movie files are **massive** — a high-quality film can easily be 10–20 GB before transcoding. The system must be able to handle uploads of this scale reliably, including recovering from interrupted uploads without starting over.

---

### 3. Seamless Streaming Regardless of Bandwidth

> [!important] Playback must never stop due to a slow or unstable connection
> If a viewer has low internet bandwidth, the system should degrade video quality gracefully rather than buffer indefinitely or stop playback.

---

### 4. Scalability & Fault Tolerance

The system must handle **millions of concurrent viewers** without degradation. Any internal component failure must not disrupt the streaming experience for active users.

---

### 5. Read-Heavy Workload

> [!tip] The read:write ratio is extremely skewed
> A single movie uploaded once may be **streamed millions of times**. The system must be optimised for reads, not writes.

The write path (upload + processing) can tolerate higher latency. The read path (streaming) must be low-latency and highly performant.


# Estimations

- Assuming we have approx 1M videos upload daily.
- 1B videos are going to be watched daily.
> [!tip] QPS
> Average watch QPS -> 10^4
> Peak load assume 10x -> 10^5



