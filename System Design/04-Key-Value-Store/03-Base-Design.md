if we are going to support different-different types of Values we also need a corresponding serializers and deserializers logic from client's side as well. or we can provide them the list of pre-made types or logics and clients have to atleast for one of them. All this would be handled inside App Server 

```

Client --> Gateway --> App Server
```


with that we will keep the HashMap in-memory and inside that hashmap we will have key-val pair but this design is not scalable as of yet. as we have only single app server machine that would lead to Single Point of Failure.so we need to horizontaly scale it meaning we need multiple replicas of app server. so whenever any Read or Write comes all of the replicas going to sync the data eventually.in in these replicas we can follow (**R + W > X**) and we will minimize our R as much as possible as we are going to optimize for Reads.


but there's still a problem with this Architecture.all these horizontally scaled servers are replicas of each other (from now on we will call one set of replicas as one cluster)as we are storing in-memory hashmap and since we have to store 1TB of data we can never store it in one machine at all even if we go very expensive machine of ECE2 instance. so we have to partition the data across the cluster.so we need to change our architecture.

now we will have have multiple clusters and there would be a Load Balancer after Gateway and before the App Server clusters.


```

Client → Gateway → LB → App Server Replica 1
	                  App Server Replica 2
		            App Server Replica 3
```

![[01-Architecture.png]]

now this Load balancer would receive the key and assuming this load balancer have some kind of hashing logic with which it will redirect our data to multiple app server.so whatever cluster has the data would send it back to client.


### Problems

* At some point of time we want to make our key value store durable as well.what if complete cluster goes down? we are anyway not ensuring the consistency so we can decide to not even ensure eventuall consistency as well.so we have decided to not provide consistency at all. so if cluser 2 goes down then client's data can't be Read at all.

* what if interviewer says that no we should atleast have to have eventual consistency.so we have to maintain some kind of persistence at each app server level say we chose **Write Ahead Logs** WAL. It's an append only file.so whenever we get a new key-val pair we append it to the file and we can write this asynchronously.so we are not wasting anytime while Writing.So if 2nd cluster goes down then we can use WAL file and re-distribute the data of 2nd cluster to 1st and 3rd cluster.but issue is 1st and 3rd clusters are already working at peak load now adding more data will overwhelm the whole system and whole system would go down due to cascading failure.

so we need to devise better Load Balancing strategies.that's where **Consistent Hashing** comes into the picture as it solves the problem of Data Redistribution.
