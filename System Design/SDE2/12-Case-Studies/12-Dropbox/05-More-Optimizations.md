**How to support large files uploads ?**

- Users might be having flaky internet leading to loss of internet in between the uploads.
- API gateway or other services might be having a limit to the request body size.
- Also if a file is more than 50GB it's already a very heavy for most users bandwidth.

**Chunks to the rescue**
- We can divide our big file into small chunks of bytes and then upload them.
- This approach has multiple benefits
	- Helps in implementing Resume Upload feature.
	- Ensures that user is not choking the request with a very huge payload.
	- Helps in implementing parallelism as instead of sync uploading a big file , we can parallel upload multiple small chunks together.
	- We can implement chunking logic on the client side , this will use some procesing on client side.

also to avoid multiple hoping we can get the presigned URL from S3 so that client can directly upload the file to S3 storage using presigned URL.

![[Excalidraw/Drawing 2026-03-29 11.43.47.excalidraw]]

**How can we reduce Latency ?**
- We can run compression on the client side and then send a gzipped compressed chunk.But we need to ensure there is always a lossless compression being done.
- We can do this compression on the server side also but then we won't be able to leverage direct uploads.
- We can replace REST apis with gRPC which uses protocol buffers to send and receive payload which is lighter than JSON on the network as it is serialize to much smaller binary.

**How can we scale Syning of files ?**
- We can use delta of updatedAt to sync only those chunks which have updated.

> Just like how Git does, like it does not keep the exact copy of complete file e.g we wrote a python code and we changed one line , now git won'r store this whole file rather it would only stores the delta or the differences.So similar thing we can do here and we can only try to maintain the diffs or we can try to maintain a separate storage where we are only storing which chunk has been updated.

- We can also use the notification incoming from S3 to know which chunk has been recently changed and then sync only that chunk.This will save a lot of download bandwidth.
- In all of this client will be responsible for stitching the chunks
- Apart from lon/short polling we can use Kafka like an event bus
- Once we receive a successful upload to S3 notification , we will add an event to the kafka event bus and client can maintain a cursor to the queue which will tell them the last synced event.
- Here the events are nothing but the chunks updated, so when a client updates a file chunk , that chunk will be added to as the event to the bus.
- Other clients will use a cursor stored for them in a key-value store like Redis that will tell them the last event they synced instead of quering the data from the DB for metadata.
- So clients will periodically poll but this time read the data from Kafka event bus.We can keep this bus partitioned based on the file_id.
- This improves consistency.For improving consistency further we have a periodic reconcillation process,because the client might still be out of sync due to any failure , so we can do the older sync way of getting changes to implement reconcillation with less frequency. 
![[Excalidraw/Drawing 2026-03-29 19.01.12.excalidraw]]

