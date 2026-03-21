## Write Conflicts

Let's say two users are trying to book the same seat.
**Solutions**
* Do not process the request concurrently , let's say we have put messaging queue or streming system such that whenever someone tries to book a seat we process those requests one by one.
* We can use Locks etc 

In these above solution we never reach at the stage of write conflicts.Let's say in the first place we are not able to stop the write conflict from happening.Let's take the example of Twitter Let's say we are storing follower and following mapping and we are using Redis for this. Now for a particular user say influencer get lot of follow requests and unfollow requests.The more number followers a user has the more inconsistency in the number of followers we can see.like someone might have 2.1M followers and next day she might have 2.05M followers and on next day she might have 2.15M followers.Like their follower count keeps on fluctuating at very high note.So lot's of Reads and Writes would be there and not just follow and unfollow people are just watching their profile many many times.So such type of users like celebrities and influencers requires system like Redis for fast Read and Writes operations.for now let's say we only care about follower count so only count is something that we store inside and the list of followers.We are not keeping only single master and read replicas as we will have many Writes.because we are storing List so we cannot just push and pop the followers , first we have to search the follower if he has unfollowed etc etc.so we can use Set instead of List and we will only store Ids of the user.`Set<Integer> followers`. In system like twitter we do not need strong consistency.now if Elon Musk has around 1B followers then we do not immedatley needs to show his exact follower but eventually everyone would see the actual number of folllowers.

Let's say we have 3 master nodes instead of one and they are individually have the replicas as well.Now if a follow request is coming from one of the application server then that request can be redirected to any of these 3 servers.Now we do not want to keep Elon Musk's data only in one Node so we have distribute it across these master nodes so that we can fan out Writes. 

> for this we can use Quorums: 2Node Write and 2Node Read,if we use this then everytime people will get accurate number of followers.But as disscussed above we do not need to support strong consistency here so we can optimize more on the performance because for 2Node writes we still have to write to 2Nodes.

Let's start with simpler problem that is we want to store follower count of Elon Musk say his ID is 199 with total follower count of 1000 , assume every master node is synced so every node has this information stored inside them.Now assume someone has followed him and this request goes to Node1 so it would contain 199:1001 then another follow request gets routed to Node2 so it would also contain 199:1001 and same for Node3 so it would also contain 199:1001 assuming Node1 and Node2 and Node3 did not sync data with each other.So actually 3 more people followed Elon Musk but because none of the Nodes has been synced each have new values unknown to other nodes.So how to resolve such a prolem ?because it should be 1003 followers but each Node has 1001 so this is conflicting data because we do not know which Node has the accurate data.So these nodes are out of sync we somehow need to sync them.

> In case of two user trying to change same profile picture of Company's main page we can opt for **Last Write Win** strategy which states that whichever write happens later(according to the timestamp) would override the existing one.This is what followed by Cassandra.But Timestamp is something that we cannot completely rely on as we disscussed in the past but there's one more catch say 2nd user won but what about the first user ?He just tried to update the profile picture and now he would see completely different profile picture that he did not even uploaded.but benefit of this approach is it is very fast


but there will be solution where Last Write Win solution won't be optimal for example in our scenario if we follow the same strategy then total followers would be 1001 only which would wrong.

## CRDT

Conflict free Replicated Data Types are the data structures or data types which have algorithmic capabilities to resolve conflicts if occurr.Redis , Evernote etc systems use CRDT.

**How CRDT avoids conflicts ?**

Say we want to implement counter with CRDT then we have option of 
- G-Counter(Grow only counter):-  Let's say we want to store count in different-different nodes then every node is going to have ID and they are going to track their own increments in map or dictionary and later we perform merge operation and then all the nodes would come in sync.INSERT THE G-COUNTER Sequence diagram here
- PN-Counter :- This can be incremented as well as decremented.When synchronized the value converges towards the sum of all increments minus sum of all the decrements. INSERT THE PN-COUNTER Sequence diagram here

Now we can use PN-Counter concept in our problem as well.
let's C receives two requests instead of just one so when merge is gonna happen each of the master will have {a:1,b:1,c:2} after sync is complete.

* Or-Sets :- If one region ADD an element and other REMOVE it simultaneously,the ADD takes precedence.We tag every ADD operation to the unique ID or Tag, like element with an ID considered as Active or Present in the cart.Now if User A tries to remove an item say apple then it will start scanning all the ids of apple and move it to something called tombstone(kinda used for soft delete that tells that the given key was deleted at given Timestamp) INSERT OR-SET diagram here


[Check Redis Doc for CRDTs](https://redis.io/blog/diving-into-crdts/)

check Repo for the implementations by netopyr/wurmloch-crdt
