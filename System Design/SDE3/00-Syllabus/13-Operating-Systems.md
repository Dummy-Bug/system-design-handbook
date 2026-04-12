## Phase 13 — Operating Systems for Senior Engineers (SDE-3+)

> **Prerequisite:** [[System Design/SDE2/00-Syllabus/13-Operating-Systems|SDE-2 Operating Systems Fundamentals]] and mastery of SDE-2 Core Concepts (Concurrency & Locking).
> **SDE-3 Focus:** Moving beyond "it runs on Linux" to understanding how the kernel-space/user-space boundary, I/O path, and memory subsystem dictate the performance and reliability of high-scale systems.

### 13.1 — The Execution Model & Scheduling
*In SDE-2, you use threads. In SDE-3, you optimize the scheduler.*

- **Context Switching Costs:** Understanding the hidden tax of high concurrency. User-to-kernel transitions, register saving, and TLB flushes.
- **CPU Affinity & Pinning:** Why high-performance systems (like Redis or ScyllaDB) pin threads to specific cores to avoid "L1/L2 cache pollution" and migration overhead.
- **User-space Scheduling (M:N):** How Go (Goroutines) and Java (Project Loom) bypass OS limitations by scheduling thousands of "green threads" on a few OS threads.
- **Interrupts & Tail Latency:** How hardware interrupts (NIC, Disk) can steal CPU cycles from your app, causing P99 spikes. Understanding "Interrupt Throttling."

### 13.2 — Advanced Memory Management
*In SDE-2, you care about Heap vs Stack. In SDE-3, you care about the MMU.*

- **Virtual Memory & Page Faults:** Why a "cold" application is slow. Understanding Major vs. Minor page faults and how `mlockall()` prevents swapping.
- **The Page Cache (The Hidden Buffer):** How the OS uses "free" RAM to cache disk I/O. Why high-scale DBs (Postgres) rely on it, while others (ScyllaDB/ClickHouse) bypass it for predictability.
- **Huge Pages (Transparent Huge Pages):** Reducing TLB misses for large-memory apps (JVM, Databases). When to enable them vs. when they cause fragmentation "latency spikes."
- **NUMA (Non-Uniform Memory Access):** On multi-socket servers, memory access isn't equal. Why "remote" memory access is 2-3x slower and how to make your app "NUMA-aware."

### 13.3 — High-Performance I/O & Storage Path
*In SDE-2, you write to a file. In SDE-3, you optimize the I/O ring.*

- **Synchronous vs. Asynchronous I/O:** The limitations of `read()`/`write()` (blocking) vs. `select()`/`epoll()` (readiness) vs. true AIO (completion).
- **io_uring (The Modern Linux Game Changer):** How to achieve millions of IOPS by eliminating syscall overhead through shared rings between user-space and kernel-space.
- **Zero-Copy Architecture:** Using `sendfile()`, `mmap()`, and `splice()` to move data from disk to NIC without copying it into user-space RAM. The secret to Kafka's throughput.
- **Direct I/O (O_DIRECT):** When and why a database should tell the OS "Don't help me with caching; I know my data better than you do."

### 13.4 — The Networking Stack & Bypassing the Kernel
*In SDE-2, you use Sockets. In SDE-3, you tune the stack or bypass it.*

- **The Journey of a Packet:** From NIC hardware buffer → Interrupt → SoftIRQ → IP Stack → Socket Buffer → User Space. Where packets get dropped under load.
- **TCP Stack Tuning:** Tuning `tcp_rmem`/`wmem`, `somaxconn` (backlog), and `tcp_tw_reuse` for high-connection environments (Load Balancers).
- **Kernel Bypass (DPDK / RDMA):** For sub-microsecond latency, bypassing the Linux kernel entirely and reading directly from the NIC in user-space.
- **eBPF (Extended Berkeley Packet Filter):** Running "sandbox" code inside the kernel for high-performance load balancing (Cilium), observability, and DDoS mitigation (XDP).

### 13.5 — Virtualization & Container Internals
*In SDE-2, you use Docker. In SDE-3, you understand the isolation.*

- **Linux Namespaces & Cgroups:** The "magic" behind containers. How the OS restricts what a process can see (Namespaces) and what it can consume (Cgroups).
- **Container "Noisy Neighbors":** How a process in one container can starve another through CPU cache contention or I/O bandwidth, despite Cgroup limits.
- **Micro-VMs (Firecracker / gVisor):** The architecture behind AWS Lambda. Combining the speed of containers with the security isolation of a full VM.

### 13.6 — Kernel-Level Observability
*In SDE-2, you look at CPU/RAM. In SDE-3, you look at the Flame Graph.*

- **Profiling with `perf`:** Identifying which kernel function or app function is hogging the CPU.
- **Flame Graphs:** Visualizing the stack trace of an entire system to find the "hot path" across user and kernel space.
- **Tracing Tools (`strace`, `lsof`, `tcpdump`):** Beyond basics — using them to find hidden syscall bottlenecks or "zombie" sockets.
