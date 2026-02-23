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



