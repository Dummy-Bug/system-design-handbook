# Fault Tolerance — Overview

> A fault tolerant system doesn't pretend failures won't happen. It's designed knowing they will.

> [!abstract] Every system fails — servers crash, networks drop, services go slow. Fault tolerance is the art of keeping the system useful despite those failures. This folder covers how failures happen, how to contain them, and the patterns that prevent one broken component from taking down everything else.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Fault-Tolerance.md | What it is, the three failure modes — crash, slow, byzantine |
| 02-Graceful-Degradation.md | Return something useful rather than total failure |
| 03-Bulkhead.md | Isolate failures so one component can't take down others |
| 04-Timeout-Retry-Backoff.md | Don't wait forever, retry smartly, back off exponentially |
| 05-Circuit-Breaker.md | Stop trying when you know something is broken |
| 06-Interview-Cheatsheet.md | What to say in an interview, full checklist |
