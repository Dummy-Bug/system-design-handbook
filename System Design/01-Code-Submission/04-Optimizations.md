![[02_Optimized_Architecture.png]]

* Here in this flow what if Submission DB is having a lot of load then whole process would get slow as this step is still synchronous .
* Since Submission Service and Submission DB are interacting on a network hence there can be network latency ,network lag

so all in all we are adding the entry inside the Submission Queue after receiving the acknowledgment from Submission DB. So even if the evaluator service or workers are absolutley free they still have to wait for the response from Submission DB indirectly as Submission Service is waiting for the Submission DB.

What if instead of waiting for the acknowledgement Submission Service add the payload inside Queue parallel to making entry inside the DB. 

But what if entry was added inside the Submission DB but due to some reasons it was not added inside the Submission Queue and vice versa? consider a scenario where while adding entry inside the Queue Submission Service rebooted or something.

so it is very possible that entry is added either inside Submission DB or inside Submission Queue but not both. so while designing such a system we have to make sure that services have to add as less entries as possible.

so synchronous flow was slow but parallel flow has it's own set of issues.

* One solution could be introduce a blackbox X just ahead of Submission Service such that X handles everything and all Submission Service have to do is add entry inside X just once.

* Other solution could be Evaluator Service is consuming the data from the Submission Queue anyway how about a new service X such that it's responsibility is to consume data from the Submission Queue but instead of evaluation this service's job is only to create an entry inside the DB.In this case Submission Service would directly make the entry inside the Submission Queue that too only once.
	**Problems**
	* Most of the Queuing servers are not going to allow multiple consumers. and the reason being most of the Queue servers like AWS SQS remove the payload once it is consumed.We can have separate Queues one for evaluator service and other for new service X but by doing so now Submission Service have to make two submissions which was the problem that we were trying to solve in first place because entry inside one of the Queues failed and inside another succeeded.

so we kinda need a mechanism such that Submission Service should add the entry once and other services should be able to consume it more than once.that's where the concept of **Message Streams** comes into play.It is same as message queues with one big difference as Message Streams allows multiple consumers to read the same payload. So Message Streams promise **Atleast One Entry**.few popular examples of such Streams are **Apache Kafka** and **AWS Kinesis**.

Now Submission Service will create an entry inside the Message Stream instead of Message Queues . Evaluator Service and new service both are consumer of Message Stream and Submission Service no longer have to wait for the DB entry to get created Hence it can immediatley return the response to web-client. Remember we are adamant on making entry inside DB because user may want to view his older submissions and all. Hence we need durability.



 