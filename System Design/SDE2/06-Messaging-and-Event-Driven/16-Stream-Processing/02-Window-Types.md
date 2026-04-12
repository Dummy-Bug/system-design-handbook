
> [!info] To aggregate events into meaningful counts or sums, you need to bucket them into time windows. There are three window types: 
> - Tumbling (fixed, non-overlapping — orders per minute) 
> - Sliding (overlapping — transactions in the last 5 minutes)
> - Session (dynamic size based on user inactivity — pages in one visit). 


## 1. Tumbling Window

**Fixed size, non-overlapping buckets.**

```
|-- 12:00-12:01 --|-- 12:01-12:02 --|-- 12:02-12:03 --|
```

- Every event belongs to **exactly one** window
- Windows don't overlap
- When one closes, the next immediately opens

**Use cases:**
- Orders/Requests per minute 
- Revenue per hour
- Error count per 5 minutes

```java
stream
  .window(TumblingWindow(1.minute))
  .count()
```

---

## 2. Sliding Window

**Fixed size, overlapping — slides forward continuously.**

```
Window at 12:01:00 → covers [12:00:00 – 12:01:00]
Window at 12:01:01 → covers [12:00:01 – 12:01:01]
Window at 12:01:02 → covers [12:00:02 – 12:01:02]
```

- An event can belong to **multiple windows**
- More compute-intensive than tumbling
- Gives you a constantly updated "last N minutes" view

**Use cases:**
- Fraud detection: "5 transactions in last 10 seconds"
- Spend alerts: "more than $1000 in last 5 minutes"
- Moving averages

```java
stream
  .groupByKey(userId)
  .window(SlidingWindow(size = 5.minutes, slide = 1.second))
  .sum(amount)
```

---

## 3. Session Window

**Dynamic size — defined by inactivity gaps, not clock time.**

```
12:00:01 click
12:00:05 click
12:00:09 click
         ... 20 minutes of silence ...
12:20:15 click   ← new session starts here
12:20:18 click
```

- Window stays open as long as events keep arriving
- Closes automatically after a **configurable inactivity gap** (e.g., 10 minutes)
- Window size varies per user based on their behavior

**Use cases:**
- User session duration
- Pages per session
- "Did this session end in a purchase?"

```java
stream
  .groupByKey(userId)
  .window(SessionWindow(inactivityGap = 10.minutes))
  .count()
```

---

## Comparison

| | Tumbling | Sliding | Session |
|---|---|---|---|
| Size | Fixed | Fixed | Dynamic |
| Overlap | No | Yes | No |
| Event belongs to | 1 window | Multiple windows | 1 window |
| Triggered by | Time | Time | Inactivity gap |
| Compute cost | Low | High | Medium |
| Use case | Periodic aggregates | "Last N minutes" | User activity grouping |

---

## Key Insight

Choose based on what question you're answering:

- **"How many X per minute?"** → Tumbling
- **"How many X in the last 5 minutes?"** → Sliding  
- **"What did a user do in one visit?"** → Session
