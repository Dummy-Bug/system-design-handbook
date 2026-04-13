But we cannot use the same architecture when we have 1B tweets per day. we cannot have 10^10 frequency map in-memory.

**Why 1B tweets breaks in-memory:**

```
1B tweets × 50 Bytes per entry = 50GB
```

50GB just for the frequency map. And remember you need **multiple maps** for your sliding window buckets:

```
30 buckets × 50GB each = 1.5TB just for sliding window maps
```

No single machine holds 1.5TB of RAM cost-effectively.

---

Let's focus only on bigger data instead of time ranges 

![[Excalidraw/Drawing 2026-03-25 08.44.43.excalidraw]]

same architecture just multiple machines containing their own separate Hashmap+Heap solving for 10M tweets and each returning top k results.

> so now problem has reduced to we have M sorted lists then find topK from those list.so Merger would take all these sorted lists and then provide the final topK results . This forms the fundamental basis of Map-Reduce.

[**MapReduce**](https://www.databricks.com/blog/what-is-mapreduce) - It is a programming model and a distributed computing paradigm used for processing large datasets across a cluster of computers, invloving a **map** phase for data transformation and a **reduce** phase for data aggregation.

- This kind of processing is really good when we want to have accurate data but if we want faster results on the toll of an accuracy we might want to think about something else.
- But even this approach does not solve the Time Range issue.



 