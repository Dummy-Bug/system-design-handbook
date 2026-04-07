# Performance Metrics — Overview

> Every architecture decision is a response to one of these metrics being bad. Know them before designing anything.

> [!abstract] Before you can design a system, you need a vocabulary for what "good" looks like. This folder builds that vocabulary — latency, throughput, bandwidth, and percentiles are the four measurements that appear in every design discussion. Without them you can't define requirements, justify decisions, or identify bottlenecks.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Introduction.md | What performance metrics are and why they matter |
| 02-Latency.md | Round trip time, sources of delay, RAM vs disk numbers |
| 03-Throughput.md | RPS/QPS, threads, what happens under load |
| 04-Latency-vs-Throughput.md | Why optimizing one can hurt the other |
| 05-Bandwidth.md | Data flow per second, the speed of light misconception |
| 06-Bandwidth-vs-Latency-vs-Throughput.md | Three different bottlenecks, three different solutions |
| 07-Percentiles.md | P50/P95/P99/P999, why averages lie |
| 08-Interview-Cheatsheet.md | How to apply all of this in a design interview |
| Interview-Questions/ | SDE-1, SDE-2, SDE-3 questions with full answers |
