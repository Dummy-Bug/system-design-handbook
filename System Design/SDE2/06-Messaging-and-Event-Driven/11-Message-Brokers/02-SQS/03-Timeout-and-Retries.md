# Visibility Timeout and Retries

> [!info] The visibility timeout is a lease. When a worker picks up a message, SQS hides it from everyone else for the timeout duration. If the worker ACKs in time, the message is deleted. If not — crash, slow processing, or anything else — the message reappears and gets retried automatically.

---

## Setting the right timeout value

Too short: the worker is still processing but the timeout expires. SQS thinks the worker crashed and hands the message to a second worker. Now two workers are processing the same job simultaneously.

Too long: a worker crashes immediately after picking up the message. The message stays invisible for the full timeout before becoming available again. If your timeout is 10 minutes and the worker crashes at second 1, the job sits stuck for 9 minutes 59 seconds before another worker can pick it up.

**The right approach — set timeout based on p99 processing time:**

```
Measure: how long does this job take in the worst case (p99)?
Video transcoding p99: 4 minutes
→ Set visibility timeout to 8 minutes (2x p99)

Email sending p99: 3 seconds
→ Set visibility timeout to 10 seconds (comfortable buffer)
```

Different job types need different timeouts — another reason for one queue per job type.

---

## Extending timeout for long-running jobs

Some jobs are genuinely unpredictable in duration. A video might be 30 seconds or 3 hours. Setting a 6-hour timeout to be safe means crashed workers block jobs for 6 hours.

The fix: start with a reasonable timeout and **extend it while the job is still running** using `ChangeMessageVisibility`.

```java
// Worker periodically extends its lease while processing
ChangeMessageVisibilityRequest extendRequest = ChangeMessageVisibilityRequest.builder()
    .queueUrl(queueUrl)
    .receiptHandle(message.receiptHandle())
    .visibilityTimeout(300)  // extend by another 5 minutes
    .build();

sqsClient.changeMessageVisibility(extendRequest);
```

The worker calls this every few minutes while processing. If the worker crashes, it stops extending, the timeout expires naturally, and the message reappears. Best of both worlds — no stuck jobs, no false timeouts.

---

## How SQS tracks retry count

Every time a message is redelivered, SQS increments an internal counter: `ApproximateReceiveCount`. Your consumer can read this to know how many times the job has been attempted.

```java
String receiveCount = message.attributes()
    .get(MessageSystemAttributeName.APPROXIMATE_RECEIVE_COUNT);

int attempts = Integer.parseInt(receiveCount);

if (attempts > 3) {
    log.warn("Job failed {} times, investigate: {}", attempts, message.body());
}
```

This is also how DLQ redrive works — SQS moves the message to the DLQ automatically once `ApproximateReceiveCount` exceeds your configured `maxReceiveCount`. That's covered in the next file.

---

> [!danger] Retries are not a bug — they are the normal failure recovery path in SQS. A worker crash, a network blip, a slow DB call — all of these result in a retry. Design your consumers to be idempotent so retries are harmless. The idempotency pattern is covered in the next file.
