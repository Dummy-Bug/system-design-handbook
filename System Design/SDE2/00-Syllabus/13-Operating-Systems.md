## Phase 13 — Operating Systems Fundamentals (SDE-2)

> **Goal:** Understand the abstraction layers the OS provides and how they impact application behavior, resource contention, and basic performance.

### 13.1 — Processes and Threads
*The unit of execution.*

- **Process vs. Thread:** Memory isolation (Process) vs. shared address space (Thread). Overhead of creation and destruction.
- **Multithreading Models:** User threads vs. Kernel threads. Why "too many threads" slows down a system (Context Switching).
- **Concurrency vs. Parallelism:** Running things "at the same time" vs. "making progress on multiple tasks."
- **Zombie & Orphan Processes:** What happens when a parent dies or fails to wait for a child.

### 13.2 — Memory Management Basics
*Where does the data live?*

- **The Stack vs. The Heap:** Allocation speed, scope, and common pitfalls (StackOverflow vs. Memory Leaks).
- **Virtual Memory:** How the OS gives every process the "illusion" of having its own private, contiguous memory.
- **Paging & Segmentation:** Basic mechanics of how memory is mapped to physical RAM.
- **Thrashing:** What happens when the system spends more time swapping memory to disk than executing code.

### 13.3 — File Systems & I/O
*Interacting with the disk.*

- **File Descriptors:** Everything is a file in Linux. Limits on open files (`ulimit`) and why they cause "Too many open files" errors in production.
- **Buffered vs. Unbuffered I/O:** Why we use `BufferedReader` in Java or `bufio` in Go. The cost of frequent syscalls.
- **Hard Links vs. Symbolic Links:** Differences in how the OS tracks file data on disk.
- **Basic Disk Scheduling:** How the OS decides the order of read/write operations (FIFO, SSTF).

### 13.4 — Inter-Process Communication (IPC)
*How processes talk to each other.*

- **Pipes & Named Pipes (FIFOs):** Simple one-way communication.
- **Shared Memory:** The fastest way to share data, but requires strict synchronization.
- **Message Queues:** Asynchronous communication between local processes.
- **Unix Domain Sockets:** Faster than TCP/IP for communication on the same machine (used by Docker, Databases).

### 13.5 — Basic Concurrency & Synchronization
*Preventing the race.*

- **Race Conditions:** Why `counter++` is not safe in a multithreaded environment.
- **Mutexes & Semaphores:** Locking mechanisms to protect critical sections.
- **Deadlocks:** The four conditions (Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait) and how to avoid them (Lock Ordering).
- **Critical Sections:** Identifying the minimum code that needs protection to maintain performance.
