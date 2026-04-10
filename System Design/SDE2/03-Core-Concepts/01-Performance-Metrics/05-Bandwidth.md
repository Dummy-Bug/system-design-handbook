# Bandwidth

> [!question] Why does a 1 Gbps plan download files faster than a 10 Mbps plan if data always travels at the speed of light?
> Because bandwidth is not about how fast data travels — it's about how much data travels per second.

---

## The Big Misconception

When your ISP says *"you have 100 Mbps internet"* — that number is your bandwidth. ISPs market it as "speed" because it's easier for regular people to understand.

But technically it is not speed.

The actual signal — whether through fibre, copper wire, or WiFi — travels at or near **the speed of light** regardless of whether you're paying for 10 Mbps or 1 Gbps. The data doesn't travel faster on an expensive plan.

> [!info] So what are you actually paying for?
> A **wider pipe**. More data fits through per second. Not faster data.

---

## The Highway Analogy

Imagine a highway where all cars drive at exactly 100 km/h — that's fixed, nobody goes faster.

- **10 Mbps plan** → a 2 lane highway. Only 2 cars can travel side by side.
- **1 Gbps plan** → a 100 lane highway. 100 cars travel side by side simultaneously.

The cars don't go faster. More cars just fit through at the same time.

This is exactly how bandwidth works. The data travels at the same speed — you just get more of it flowing through per second.

---

## So why does your YouTube video buffer?

Not because the data is travelling slowly across the world.

It's because **too much data is trying to come through your pipe at once** and it can't all fit. The pipe is full. New data has to wait.

Widen the pipe (upgrade your plan) → more data fits → video stops buffering.

---

## The units

| Unit | What it means |
|---|---|
| **Mbps** (Megabits per second) | Home internet, mobile connections |
| **Gbps** (Gigabits per second) | Datacenter connections, server-to-server |

> [!warning] Bits vs Bytes
> Bandwidth is measured in **bits**. File sizes are measured in **bytes**. 1 byte = 8 bits.
> A 100 Mbps connection downloads a 100 MB file in: `100MB × 8 = 800Mb / 100Mbps = 8 seconds` — not 1 second.

---

## Real world numbers

| Connection | Bandwidth |
|---|---|
| Home broadband (average) | 100–500 Mbps |
| Mobile 4G | 20–50 Mbps |
| Mobile 5G | 100–1000 Mbps |
| Server to server (same datacenter) | 10–100 Gbps |
| Undersea cables (continent to continent) | Multiple Tbps |

---

## Where bandwidth matters in system design

Bandwidth becomes the bottleneck any time your system moves **large volumes of data**:

- **Video streaming** — serving HD/4K video to millions of users simultaneously chews through bandwidth fast
- **File storage (Dropbox)** — users uploading and downloading large files
- **Database replication** — copying data between servers across regions
- **Backups** — transferring terabytes of data to cold storage

