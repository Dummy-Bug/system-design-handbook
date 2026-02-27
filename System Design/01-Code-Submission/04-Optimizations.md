![[02_Optimized_Architecture.png]]

* Here in this flow what if Submission DB is having a lot of load then whole process would get slow as this step is still synchronous .
* Since Submission Service and Submission DB are interacting on a network hence there can be network latency ,network lag

so all in all we are adding the entry inside the Submission Queue after receiving the acknowledgment from Submission DB. So even if the evaluator service or workers are absolutley free they still have to wait for the response from Submission DB indirectly as Submission Service is waiting for the Submission DB.

What if instead of waiting for the acknowledgement Submission Service add the payload inside Queue parallel to making entry inside the DB. 

But what if entry was added inside the Submission DB but due to some reasons it was not added inside the Submission Queue and vice versa? consider a scenario where while adding entry inside the Queue Submission Service rebooted or something.

so it is very possible that entry is added either inside Submission DB or inside Submission Queue but not both. so while designing such a system we have to make sure that services have to add as less entries as possible.

so synchronous flow was slow but parallel flow has it's own set of issues.

* One solution could be introduce a blackbox X just ahead of Submission Service such that X handles everything and all Submission Service have to do is add entry inside X just once.

* One of the solution could be since anyway Evaluator Service is consuming the data from the Submission Queue anyway how about a new service X such that it's responsibility is to consume data from the Submission Queue but instead of evaluation this service's job is only to create an entry inside the DB.In this case Submission Service would directly make the entry inside the Submission Queue that too only once.
	**Problems**
	* Most of the Queuing servers are not going to allow multiple consumers. and the reason being most of the Queue servers like AWS s3 remove the payload once it is consumed.We can have separate Queues one for evaluator service and other for new service X but by doing so now Submission Service have to make two submissions which was the problem that we were trying to solve in first place because entry inside one of the Queues failed and inside another succeeded.

so we kinda need a mechanism such that Submission Service should add the entry once and other services should be able to consume it more than once.that's where the concept of **Message Streams** comes into play.It is same as message queues with one big difference as Message Streams allows multiple consumers to read the same payload. So Message Streams promise **Atleast One Entry**.few popular examples of such Streams are **Apache Kafka** and **AWS Kinesis**.


so now Submission Service will create an entry inside the Kafka instead of Message Queues and now Evaluator Service and new service both are consumer of Message Stream.and now Submission Service no longer have to wait for the DB entry to get created Hence it can immediatley return the response to web-client.Remember we are adamant on making entry inside DB because user may want to view his older submissions and all.


--- 

### Kafka

In order to understand Kafka we have to get familiar with following nuances and terminologies or concepts.

#### Producer

System responsible for putting the payloads/events/data/message inside the Message Stream/Queues.

#### Consumer

System responsible for reading the payloads/events/data/message put by producer inisde the Message Stream/Queues.

#### Partition

To better understand this let's take an example of Uber . There's usecase of updating the location of drivers in the Uber app.So assume Driver app is sending the Location details to the App Server of Uber now does it does not make sense to directly store this location data inside DB because the scale of Uber is really high probably 7-10M drivers.Now in Peak office hours all the drivers would be moving so their live location would be changing very frequently.So every single driver's request would bombard the Uber's App Server.and even if Uber scale the App Server but do we still want to put these bombarded request inside teh DB ? and one more issue here is that we just do not want only the latest location of Driver rather we want complete trace of driver's location to track because sometimes user raise a dispute claiming driver has taken a separate route and for this Uber need to know the route that Driver tooke .So it's not just about storing the Lat and Long of current location rather Lat and Long of whole driver's trip.

Hence placing a Message Queue between Uber's App Server and DB makes perfect sense such that now consumer can pick entries from Queue and place them inside the DB so that our DB is not bombarded with humungous requests.but this still does not solve Uber's problem as normal Message Queues do not keep the data forever.It may happen that consumer read the data from Queue but just before making entry inside the DB the machine dies and because Queue was normal queue it would have deleted the payload from the Queue. That's where Kafka comes into the picture again.kafka does not delete the payload from the Queue/Stream even after consumer has read the payload.but now Queue can become the bottleneck as now Queue would be bombarded with the too many requests if we have a single Queue. So we horizontally scale it and Kafka by default supports it.So we need multiple Queues to store the data.say we have N such Queues now and now the load would be evenly distributed among them . These set of N queues are called as **Partition**.So partition is out of the box solution provided by Kafka in order to make sure that we are able to distribute the data in horizontal scaleable way. Now we have collection of these N partitions let's say partitions are on the basis of Hash function.So natural questions acn be what could be the Partitioning Key for these partitions and that will be the logical answer based on the system that we are designing.Let's say OLA which only one Region India so state division is good starting point.City division is even more granular and better.For simplicity we have called partitions as multiple queues but these are not queues rather these partitions are Immutable sequence of append only events. so whatever event or message is going to come up it appends that to a partition.Message in Kafka is nothing but a Key:Value pair aliong with it we have timestamp and few headers.The important thing here is **Immutability** like once producer has published something to partition it can never be altered and this gives the Durability aspect to kafka.If we want to delete the events from the Kafka ? yes but we have to define a retention policy like for how much time we want to keep the data inside the Kafka 5 days , 7 days , 90 days and so on and after the TTL is over the data would be removed. We can also define the retention on the basis of size like keeping the upper limit for the size.obviously manually we can always forcefully delete the things.So **partition is not a queue it is an append only file**. so it means if there are two consumers C1 and C2 and if they read from the same topic data is not removed because it's not a queue from where you can deque the data. so Kafka maintain something like an offset. so this offset defines like what was the last entry point you have actually read and based on that offset they move ahead. let's say C1 has read uptil data D2 then next time when it reads it will read from either from D3 or from the begining D1(we have to define this property inside the consumers). so consumer can read everytime from begining to the end or from the point wherever they left last.so it is like an iteration based mechanism and every partition maintains these offsets which is like sequential identifier for the payload.best part is consumers keep on commiting that what was the last offset that we have read so that they can come up and read from the remaining set of data.


#### Topic

For systems like Uber which is multi resgion driver location is not the only thing that we would like to store inside the Kafka.We may also want to store the Ride requests that are coming to get store inside the Kafka because based on the Ride request we have to calculate the Pricing.If from a particular region we are getting too many ride rquests or too many requests are coming for a particular destination.so for all of these cases we can have group of partitions to store other type of data.This is where the concept of [**Topics**](https://miro.medium.com/v2/resize:fit:720/format:webp/0*6FVLBloofcJp_RsF.png) comes into picture. We can say for one type of data say Driver location we can have one set of N partitions called One Kafka Topic let's name it driver_location and for other type of data say ride requests we can have other set of partitions let's name it ride_request_topic.So Topic is storing all the data for the one type of event and inside that Topic there can be multiple partitions and based on the partitioning logic one of the partition would take the event but for different different type of events we have different different topics.

so in our Leetcode problem we had two separate Queues named Submission Queue containig user's submission payloads and Evluation Queue contyaining submission's evaluated result but inside Kafka user's submission related data would be one Topic and Evaluation related topic as other topic.so now Producer has to tell to which topic it wants to add the data to say submission topic and once it enters into the topic then logic of partition comes into the picture like to which partition submission data would get store.so in world of Kafka we do not need multiple queues with the functionality of multiple consumer reading from the same topic.



 