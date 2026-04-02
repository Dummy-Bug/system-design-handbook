* Should we optimize key-value store for Availability , Consistency or Partiotion tolerance.

### Calculations
we have total of 10B entries if we have 1 entry with key as String and each char as one Byte then 10Byte for key and for now assume Values are also string so 40Byte for values so total is 50Bytes per entry so
* for 10B entries we need 50 * 10 * 10^9 => 0.5 * 10^12 , so the moment we reach power of 12s we reach the TeraByte scales.

So when we have this much of scale assuming in worst case 1TB, then can we even avoid partitioning ? **NO** because this is an In-memory storage would we be able to store 1TB of data in memory ?**NO** . We can have *eviction policies* like **LRU** , **LFU** and **FIFO** etc etc and all . Even if we evict the data for our assumption we can take we will only keep 10% of 0.5TB = 50 GB then the moment we start evicting the data we will start losing on **Consistency** because because of eviction now we will not ne having everything that user added.Once a User write there might be a case when he reads it the data won't be there. and even after eviction we can store 50GB of data only in one machine.so partition is inevitable.

so we have to optimize for Partition Tolerance and Availability because we won't be able to handle the consistency very well.
but we can still try to optimize for **Tunable consistency**.
