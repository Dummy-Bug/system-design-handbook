In order to understand Kafka we have to get familiar with following concepts.

### Producer

System responsible for putting the payloads/events/data/ messages inside the Message Stream/Queues.

### Consumer

System responsible for reading the payloads/events/data/ messages put by producer inisde the Message Stream/Queues.

### Partition

To better understand this let's take an example of Uber . There's usecase of updating the location of drivers in the Uber app.So assume Driver app is sending the Location details to the App Server of Uber now it does not make sense to directly store this location data inside DB because the scale of Uber is really high probably 7-10M drivers.Now in Peak office hours all the drivers would be moving so their live location would be changing very frequently.So every single driver's request would bombard the Uber's App Server.and even if Uber scale the App Server but do we still want to put these bombarded request inside the DB ? and one more issue here is that we just do not want only the latest location of Driver rather we want complete trace of driver's location to track because sometimes user raise a dispute claiming driver has taken a separate route and for this Uber need to know the route that Driver tooke .So it's not just about storing the Lat and Long of current location rather Lat and Long of whole driver's trip.

Hence placing a Message Queue between Uber's App Server and DB makes perfect sense such that now consumer can pick entries from Queue and place them inside the DB so that our DB is not bombarded with humungous requests.but this still does not solve Uber's problem as normal Message Queues do not keep the data forever.It may happen that consumer read the data from Queue but just before making entry inside the DB the machine dies and because Queue was normal queue it would have deleted the payload from the Queue. That's where Kafka comes into the picture again.kafka does not delete the payload from the Queue/Stream even after consumer has read the payload.but now Queue can become the bottleneck as now Queue would be bombarded with the too many requests if we have a single Queue. So we horizontally scale it and Kafka by default supports it.So we need multiple Queues to store the data.say we have N such Queues now the load would be evenly distributed among them . These set of N queues are called as **Partition**.So partition is out of the box solution provided by Kafka in order to make sure that we are able to distribute the data in horizontal scaleable way. Now we have collection of these N partitions let's say partitions are on the basis of Hash function.So natural questions can be what could be the Partitioning Key for these partitions and that will be the logical answer based on the system that we are designing.Let's say OLA which only one Region India so state division is good starting point.City division is even more granular and better.For simplicity we have called partitions as multiple queues but these are not queues rather these partitions are Immutable sequence of append only events. so whatever event or message is going to come up it appends that to a partition.Message in Kafka is nothing but a Key:Value pair along with it we have timestamp and few headers.The important thing here is **Immutability** like once producer has published something to partition it can never be altered and this gives the Durability aspect to kafka.If we want to delete the events from the Kafka ? yes but we have to define a retention policy like for how much time we want to keep the data inside the Kafka 5 days , 7 days , 90 days and so on and after the TTL is over the data would be removed. We can also define the retention on the basis of size like keeping the upper limit for the size.obviously manually we can always forcefully delete the things.So **partition is not a queue it is an append only file**. so it means if there are two consumers C1 and C2 and if they read from the same topic data is not removed because it's not a queue from where you can deque the data.Kafka maintain something like an offset and this offset defines something like what was the last entry point you have actually read and based on that offset they move ahead. let's say C1 has read uptil data D2 then next time when it reads it will read from either from D3 or from the begining D1(we have to define this property inside the consumers). so consumer can read everytime from begining to the end or from the point wherever they left last.so it is like an iteration based mechanism and every partition maintains these offsets which is like sequential identifier for the payload.best part is consumers keep on commiting that what was the last offset that we have read so that they can come up and read from the remaining set of data.

* Inside the partition ordering of the message is always guaranteed but across partitions ordering is not guaranteed. like if we have three partitions then messages inside individual partition would be in order but no guarantee of ordering across all three partitions.


### Topic

For systems like Uber which is multi resgion driver location is not the only thing that we would like to store inside the Kafka.We may also want to store the Ride requests that are coming to get store inside the Kafka because based on the Ride request we have to calculate the Pricing.If from a particular region we are getting too many ride rquests or too many requests are coming for a particular destination.so for all of these cases we can have group of partitions to store other type of data.This is where the concept of [**Topics**](https://miro.medium.com/v2/resize:fit:720/format:webp/0*6FVLBloofcJp_RsF.png) comes into picture. We can say for one type of data say Driver location we can have one set of N partitions called One Kafka Topic let's name it driver_location and for other type of data say ride requests we can have other set of partitions let's name it ride_request_topic.So Topic is storing all the data for the one type of event and inside that Topic there can be multiple partitions and based on the partitioning logic one of the partition would take the event but for different different type of events we have different different topics.

so in our Leetcode problem we had two separate Queues named Submission Queue containig user's submission payloads and Evluation Queue containing submission's evaluated result but inside Kafka user's submission related data would be one Topic and Evaluation related topic as other topic.so now Producer has to tell to which topic it wants to add the data to say submission topic and once it enters into the topic then logic of partition comes into the picture like to which partition submission data would get store.so in world of Kafka we do not need multiple queues with the functionality of multiple consumer reading from the same topic.


### Kafka Cluster and Broker

Set of servers is called as **Kafka Cluster** and one individual server is called as **Kafka Broker**. So set of Kafka Brokers together makes up a Kafka Cluster.
* One Kafka Cluster can have multiple Topics with each topic having multiple partitions.
* If we add more Brokers to the cluster then it means we are adding more servers to the cluster.
* Having multiple brokers allows horizontal scalability, and when topics are configured with a replication factor greater than one, partitions are replicated across multiple brokers to ensure high availability and fault tolerance means we can setup the partitions of same kafka Topic such that they are residing in different Kafka Brokers.

How Kafka decides which partition to put the message into?like how the message should be distributed across the multiple partitions.

The data would be in (Key:Value) form .Hence here are the following ways
* Default Hashing using Murmur algorithm.No gurantee of uniform distribution.
* If no Key is defined then Round Robin fashion partitions are selected.

### Replication

To ensure reliability and durability Kafka supports **Replication**.In replication Kafka has couple of leaders and followers nodes. Each partition has a designated Leader Replica which is going to be there on the Broker and this Leader or the Master is going to be responsible for any Read or Write request that's going to come to the server or broker and in case if this leader goes down then **KRaft** (earlier ZooKeeper was used) is responsible to figure out which one of the followers has the latest data synced with previous leader and then that follower is promoted as the new leader.so these followers are never going to handle any kind of consumer requests they are just there to passively replicate the data from the leader so kind of working as a backup.

### Kafka Controller

Kafka controller is responsible for the replication process. Controller monitors the health of all the servers and check if any replica is down or particular broker is down and check if there's need to assign a new leader.

---
What if when producer is trying to add the data there's failure? In that case most of the producers supports automatic retries. so producer can define the number of retries , the time when to retry etc.

but same thing is not supported for the consumer.If a consumer read the payload but it was not able to process the payload in any failure case then retry support is not provided for consumer. so we have to add our own custom logic.

* Kafka supports retry for producers but not for consumers out of the box

say we have our custom retry logic implemented and imagine a case even after many custom retries consumer is not able to read the data,what can you do in this case with Kafka ?In that case there's somethig known as [**Dead Letter Queue(DLQ)**](https://aws.amazon.com/what-is/dead-letter-queue/).It's a place where we can store all of our failed messages so that we can investigate them later.

---
Let's say inside a Topic we have 4 partitions now at any point we can never have number of different consumers more than the number of partitions.so at max 4 different consumers are allowed and each would read one corresponding partition.**so maximum 1 consumer per partition**.consumer of same type is one consumer group.like code submission consumer can have 4 parallel consumer process running that can read from these 4 partitions.There's not upper limit to the number of consumer groups.so there can be N number of consumer groups but inside the consumer group we can have only maximum number of consumer equals to the partitions available.

okay so what if we have 4 partitions but lesser number of consumer processes of same consumer type ? say 3 consumers of type code submissions.so what will happen to this 4th partition ?The data inside this partition would stay there till we rebalance the data or repartition like from 4 we come back to 3 partitions or an existing consumer start reading from this 4th partition.

so in interviews following are important

* What all Topics should be there
* What should be your partitioning strategies.
* Do you even need multiple partitions.
* Do you need any DLQ.
* What replication strategy is we looking at.
* Do you need multiple Kafka brokers. 

---

since now say in Leetcode we have used language as the partitioning key .one problem here would be Java , CPP and Python would get humongous amount of submissions but other languages like swift , ruby etc won't.so assume Leetcode supports 20 languages so we will be having 20 partitions and out of these 20 partitions 3 partitions are going to be called as **Hot Partitions**.because these partitions would be having maximum amount if load bombarded to them.now how can we resolve this issue ?
* One solution is one partition can cater to more than one languages.so Java is catered in the Java partition as well as in Ruby partition as well.
* Other solution is just do not allocate any Key , let the partitionng happen in the round robin manner.
* Have a compund key such that along with language add some more property that can help us to re-distribute .for example along with language add the user location as well.
* We can also indicate to our producers that our partitions are overwhelmed with too many requests so that producers can slow down.This technique is also called **Back-Pressure**.