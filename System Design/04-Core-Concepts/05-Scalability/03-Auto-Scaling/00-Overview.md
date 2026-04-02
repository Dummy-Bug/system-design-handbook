# Auto-Scaling — Overview

> Running peak capacity 24/7 wastes money. Running minimum capacity causes outages. Auto-scaling is the answer.

> [!abstract] Auto-scaling automatically adds servers when load increases and removes them when it drops. This folder covers how the feedback loop works, what metrics trigger scaling, how servers are safely removed without killing in-flight requests, and how to solve the cold start problem so new servers are ready before traffic arrives.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Auto-Scaling.md | What it is, feedback loop, reactive vs predictive, metrics, scale out vs in asymmetry |
| 02-Connection-Draining.md | How LB safely removes servers, in-flight requests, drain timeout tradeoff |
| 03-Cold-Start.md | Pre-baked AMIs, warm pools, predictive scaling as cold start solution |
| 04-Interview-Cheatsheet.md | How to bring auto-scaling into a design interview |
