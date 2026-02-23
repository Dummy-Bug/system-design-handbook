We can imagine our clusters to be present around the Ring in clock wise direction and we can have some hash function that would decide which key would go to which cluster check the generated hash value from the hash function and see where it lies on the ring then move in clockwise direction till we reach a point where server is located.but a normal distribtuion of servers around a ring still won't solve the problem cascading failures as other servers would still get overwhelm.

![[02-Hashing-Failure.png]]

so to avoid this problem we can use Virtual Nodes. on the consistent hashing ring instead of having one server present only at the one location in Ring ,we can assume the server is virtually and arbitrarily present in multiple locations of the Ring.now each server will have unique id. now instead of one Hash function we will have multiple Hash function . assume we have 5 Virtual nodes and we have 5 hash function. now for server 1 each hash function would give different value and hence presence of same server on different locations around the Ring.Remember it is not actual server being placed five times.now even if 2nd server goes down we will never bombard our 3rd server with all of the data from 2nd server rather it would be evenly distributed across all the servers. more hash functions we use better the distribution across servers.and this is the same strategies used by Redis , Cassandra, DynamoDB uses etc.
![[03-Hashing-Success.png]]

so whenever we have to do data redistribution using **Consistent Hashing** as with Load Balancing it becomes tricky.

so our latest archtitecture now looks like the following.
![[04-Final-Architecture.png]]
