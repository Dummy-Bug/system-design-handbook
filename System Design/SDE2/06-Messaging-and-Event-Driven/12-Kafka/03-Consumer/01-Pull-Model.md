
> [!info] Kafka uses a **Pull-based** model where the Consumer (the reader) decides when and how much data to read. This protects the Consumer from being overwhelmed by spikes in data.

---

## The "Buffet" vs. "Overwhelming Waiter"

Most messaging systems push data to you as fast as it arrives. 
- **Push:** A waiter brings you plates of food as fast as the kitchen cooks them. If you are slow, your table overflows and you crash.
- **Pull (Kafka):** Data sits at the Buffet (the Broker). *You* (the Consumer) walk up and grab as much as you can handle.

If your **Billing Service** is processing 10,000 clicks/sec and a spike of 100,000 clicks/sec happens, your service won't crash. It will just keep pulling its 10,000/sec, and the rest will safely wait on the Broker's disk.

---

## Batch-Pulling: The "Supermarket Cart"

Pulling 1 click at a time is inefficient because of network overhead. Instead, the Consumer pulls in **Batches**.

Your **Billing Service** (the Consumer) makes one request:
*"Give me as much data as you can, up to 1 MB, or wait up to 100ms."*

The Broker responds with a single large packet containing hundreds or thousands of clicks. Your service then processes all of them in its own RAM.

---

## The Bookmark (Offset) and the "Commit"

When you pull a batch of 1,000 clicks (from Offset 10,001 to 11,000), you need to keep track of your progress.

### The Flow:
1. **Pull:** Pull 1,000 clicks (Offsets 10,001–11,000).
2. **Process:** Your Billing Service calculates the charges for all 1,000 clicks in its own memory.
3. **Commit:** Once the **entire batch** is finished, your service sends a "Commit" message back to the Broker: *"I have finished Offset 11,000. Save this bookmark."*

### The "Crash" Problem: At-Least-Once Delivery
If your service crashes **mid-batch** (after billing 500 clicks, but before the "Commit"):
- You have already charged 500 people in your database.
- But you **haven't committed** the offset yet.
- When you restart, you will pull the **same 1,000 clicks again**.

> [!danger] **Double Charging Risk:** In a naive system, you would charge those first 500 people a second time. This is why "At-Least-Once" delivery (Kafka's default) requires **Idempotent Consumers**—your Billing Service must check "Have I already charged for Click #10,001?" before doing it again.

> [!tip] **Interview framing:** "I'd use a pull-based model to prevent our downstream services from being overwhelmed during traffic spikes. Because Kafka provides 'At-Least-Once' delivery by default, I would ensure my billing logic is idempotent to handle the duplicate messages that can occur if a consumer crashes before committing its offset."
