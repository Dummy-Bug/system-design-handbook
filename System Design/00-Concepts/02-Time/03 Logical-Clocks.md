As we say we should not trust client for sending timestamp but there are some corner cases where we are bound to take time from clients.
**Offline Apps** : There are applications where we can update things locally without internet and when we get internet access it gets sync to the server.e.g notetaking app like Evernote, we took a note and now we have to sync to the server, now let's say sync happened after 3 hours so what timestamp of note creation are we going to consider ? when it got synced or when it got created.say not was created at 5 pm and synced happened at 8 pm.This is a classic situation where we cannot take server or sync time.

**Financial Transactions** : We should always use server time , like trading a stock now stock's price is dependent on when actually stock was traded so client can and will alter to the time when stock was lowest priced.

**Security and Auth** : Server time only.

**Rate Limiting** : Server time.

**Creating DB Records** : DB server time.


Imagine we have two Application servers acting as client to one DB server both send request to DB server.Now even in this scenario there can be cases where we have to take time of application servers(clients) instead of DB time.

let's say inside DB or Message queue server etc we were storing some ordering events e.g Figma like application wherein multiple people are collaborating on the same design and they are sending changes to the design.now let's say request of user u1 lands on server s1 and request user u2 lands on server s2.

![[Excalidraw/Drawing 2026-03-20 11.33.22.excalidraw]]
now assume u2 made request change first at 10:00:00.Ausming s1 lagging behind in time with respect to s2 because of clock drift by 3 seconds.Assume u1's request change at 10:00:02 . Assume request take 1 second to travel, so request should hit s1 at 10:00:03 UTC but s1 is slow or behind by 3 seconds so actual time noted by s2 would be 10:00:00 .Assuming s2 does not have any clock drift so request of u2 would hit s2 at 10:00:01 because of 1 second of propagation delay. So s1 would record the time 10:00:00 and s2 would record 10:00:01 and even though u2 had made the rquest earlier than u1 it would be treated as secondary inside DB and it's not because of clock drift only it can be due to multiple other reasons as well.

In applications like Security and Finacials exact time matters but situations like this one and google doc and chatting applications etc instead of exact time the ordering of events matters more and this brings in the concept of Causality and happens before.

## Causality and Happens Before

let's say we have three servers s1 ,s2 and s3 and all these servers are sharing messages with each other.

assuming s1 is in USA s2 in UK and s3 in India meaning s2 is probably close to s1 and s3 but s1 and s3 are far apart.
now say s1 broadcasted a message named m1 to s2 and s3 at t=0 ,s2 received at t=1 and broadcasted message m2 to s1 and s3

![[Excalidraw/Drawing 2026-03-20 12.41.13.excalidraw]]
now it can happen that at t=3 s2 received m2 first and m1 later at t=4 because of the geographical distance.So fundamental problem here is that s3 sees m2 before m1 but it m1 happened before m2.So here cause and effect has broken technically because m1 was the cause and m2 was the effect but in s3 effect appeared before cause.Databses specifically are prone to such kind of problems because if we had last write win policy then in this case last write would come out to be m1 which would be wrong.


## Logical Clock/Time

We do not care about physical clock we only care about the ordering.How can in what order events occurred.and we have two mechanism two solve this probem
* `Lamport Clock`
* `Vector Clock`

## Linearlizability in Distributed DB

It is a standard with which we provide a recency gurantee.Once a write is completed all the subsequent reads from any client returned that recent value or more recent value, so client will never get a past value.This is called Linearlizability. so if event A has happened before event B then client will always see changes of A followed by changes of B and hence DBs maintains the causal consistency.Let's say we have multiple copies of data(say instagran post) across multiple DB instaces , now if any comment happens then everywhere client should be able to see the post or post followed by comment. It will never happen that only comment is visible.


## Lamport Clock

It keeps a single counter with itself and whenever any event happens then it tries to increment the counter or merge the counter.

> If we have three nodes then every node will have it's own local counter initialized to 0.

> If any event happens to the local node we increment the counter of that node.
> 
> On a request to send a message we increment the counter and attach the counter with message.
> 
> If we receive a message in a node then we update the counter by taking the maximum of current node counter and incoming counter and adding one to it.
> 

so counter is monotonically increasing always as we are never decreasing it.

![[01-lamport-clock.jpeg]]
