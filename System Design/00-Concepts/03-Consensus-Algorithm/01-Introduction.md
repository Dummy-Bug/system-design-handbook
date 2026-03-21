Let's say we have a horizontally scaled microservice now assume there's a cron job which everyday at 10am tries to send email to users now if we have 5 servers then a user will recieve the same email 5 times.So we have to make sure that not all of the servers should be allowed to send the email 
* Hence we have to make one of those server a leader and only that leader node or server will process the cron.
* If any case elected leader goes down we have to have the mechanism such that new leader can be elected to carry out the tasks.
* Now if later the old leader comes back and start acting as a leader again then action done by this would be rejected as new leader was already elected in the absence of previous leader.So it would be notified that it is no longer a leader.

To do these leader elections consensus algorihms plays an important role.Here some of the algorithms
![[Excalidraw/Drawing 2026-03-21 16.28.32.excalidraw]]

## Distributed DB Schema change

* Assume we have multiple shards of distributed DB.We have some data in all of these Shards now let's say we want to do Schema change in distributed DB. Assume initially we had 5 columns in a table so each of these shards would have these 5 columns inside them.now we want to add one more column so how can we make sure that when we add a column to a table then that table is sharded across all the servers and that schema change is populated everywhere.It's not just about adding a column only it can also be adding an index , now that index should be propagated to all the shards. and what about the case wherein one of the shard got the index and one of the shard did not get the index.Let's say our Schema was A then we made a schema change B then we keep on making schema changes now we have to make sure that not only all of these shards get the schema change but they should get the schema change in same order like A , B , C ...like let's say while change B was being propagated to shard 3 dues to any network break or any issue it could not apply the changes and then someone apply the change C then we have to make sure that shard 5 receives the change B and then the change C.So change B should not get lost in the process and this apply to all the shards.because change B could be add the column and change C could be remove the previous added column so in shard 3 this would give erorr as change B was never applied.So system cannot apply the further changes untill it has confirmed that all the previous changes have been applied to all the shards. So consensus algotihm help in resolving such scenarios as well.

## Membship List in cluster of nodes

* Let's say we have 5 servers up and running in leaderless architecture.Now assume node5 is down,now say node 1 tried reaching out to node5 but it could not but still we cannot makr node5 as dead because it might be the case that node1 was the one which was at fault and node5 could be temporarily down or there was network issue of some kind. So in this particular cluster of 5 nodes we can maintain membership list which would be present inside all of these nodes which would convey that which all nodes are reachable from the current node.Now if some node wants to declare that some other node is dead then there should be consensus that majority of the nodes like atleast 3 out if 4 should also could not reach node5 only then node5 is considered dead.

## Dsitributed Locks

* Assume both server s1 and s2 tries to take lock to some DB at the exact same time then who gets the lock ?In this case as well consensus algorithms can be really helpful because we can have majority vote that we are alloweing request from s2 take the priority so s2 would take the lock and s1 would be denied.

## What is Consensus Algorithm ?

> It is a protocol used by distributed process to agree on a single data value or a specific state of the system even if some nodes fail or the network is unreliable.In other terms we can consider it as a voting system that allows a cluster of systems to act as a single coherent brain.

for an algorithm to be considered as Consensus algorithn there are few requirements
- **Agreement** - All non faulty nodes must decide on same value
- **Validity** - Decided value must be proposed by one of the nodes and not be created randomly.
- **Termination** - Algorithm should not go forever and all the non faulty node should reach at decision at the end.

