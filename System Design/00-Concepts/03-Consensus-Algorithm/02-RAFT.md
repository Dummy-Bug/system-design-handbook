Let's take an example of online banking system which has three DB servers, as of now assume DB-A is the master and rest are followers 
* B and C are replica of A.
- Replicated logs will be maintain among them e.g 
	- Deposit 500 to user X.
	- Transfer 100 from user X to user Y.
  now all of these servers would maintain their replication log and these replication logs should be exactly same and has the data in exact same order.

Let's say user has requested to transfer 100rs from account 101 to 102.

Every write request would go to master node A.The moment leader collects the request it won't immediatley commits or persist this write in the final database.

First step it would do is to add this write request to it's local replica log.

`Log Index: 5 | Term:1 | Command: Transfer 100rs from 101 to 102.`

Till now changes are not committed so transfer of money has not been done.

Now after A has made an entry inside it's log it would ask B and C to record entry number 5 inside their log.Now B would check if it has all the entries uptill log index 54 if yes then it will write the entry inside it's log and will return with the acknowledgment back to the leader.Assume DB-C is slow and we do not know if it has received the log entry , recorded it or not, so now is the time leader has to make decision that if it should go and commit the operation or not.If we follow simple quoram based approach two out of three nodes have data written inside their logs so server A would commit it and would put the entry inside the B and respond to the User that transfer is completed alongside it would also tell B and C that entry 5 has been committed so they should also committ inside their local databases.

If the above approach was not taken what could have gone wrong? If we were only relying on leader to have the write and followers would only get async writes then maybe while updating the data to B and C from A it might happen that A crashes , so ultimatley B and C would not have gotten the transaction at all. so we would lose this transaction till A is back to business.

So we only tell the user that his transfer is completed when we have majority of the nodes having the record in their replica so that even if the leader goes down we can have other nodes that can be made leader to and then new leader can commit.

> Let's say if there's a network failure and server A is compleltely cut from B and C.Now B and C would see that server A is unreachable (maybe using heartbeat etc) then within themselves they can elect a new leader.user sends the same query of transferring the money so server A logged it but got disconnected while trying to replicate it to B and C,so the transfer request is going to be rejected.Now if user sends an another transfer request now it would go to new leader say B , now B would log this query now it would ask C to replicate the same entry in it's local log if acknowledge is received then server B would have the majority and it would commit the changes.

![[01-Banking-Example.jpeg]]



## What is Raft consensus algorithm?

Leader is an important component inside Raft algorithm as it handles all the decision making.If a leader dies then we have to elect a new one.

**Leader**
- It handles all client requests.
- Maintain a replicated log , and also sends it to the followers.
- It sends a "hearbeat" to tell it's alive.

**Follower**
- It listens to the leader.
- It also maintains a replicated log itself which it tries to keep in sync with leader.
- If it does not hear a heartbeat it can start a new leader election.

**Candidate** - It is a follower who aspires to become a new leader in the upcoming election and it asks for votes to other followers.

**Term** - For the very first time when a node becomes the leader we call that Term1 and if that leader goes down and somebody else becomes a leader then we call that term as Term2 and so on.

**Log Index** - it refers position of an entry in the log.

**Majority** - floor(total nodes/2) + 1


## Phase 1: The first leader election

Initially we do not have any leader so all the servers would be followers.Since no leader is present there will not be any heartbeat signal so after some time when none of the followers actually receive the heartbeat any one of the server can initiate the election and that point of time the initiating follower (say node3) becomes the candidate.The moment node3 becomes candidate it is going to increment it's current term and it will vote for itself.Then node3 is going to initiate a RPC to every other node to request vote.
* Other nodes would vote for node3 if they have not already voted for some other candidate.because it might be the case that some other candidate had already initiated the election before node3 and asked for votes.
* Candidate's log should be upto date as the follower log from whom they are requesting a vote.because it might be the case that node3 was selected but it went down after some time and new leader was chosen and is working but now node3 has came back and acting as a leader but now it's log Term would not be as updated as other follower's log Term.

### Problems

If no follower hears the heartbe atafter let's say 2 seconds then every follower would try to become the leader so every node would vote for itself no leader will have the majority because all the nodes have vote for itself and now they cannot vote for any other node.

**Randomized Timer** - Every node has a randomized timer (10ms,100ms,30ms etc etc), so each node would wait for different amount of time for the heartbeat and if heartbeat is not received in that time period only then it can start election.

By any chance two of the nodes get the same Randomized Timer then both nodes would vote for themselves now if we had even number of votes say n1 votes for n3 and n2 votes for n4 and both n3 and n4 votes for themselves then again we do not have a majority.so to solve such a situation re-election happens after a randomized election timeout.so every node would be assigned randomized election timeout and one with the least timeout can start re-election and will get the majority eventually.

Let's assume N1 wins the election and it immediatley sends out the heartbeat to all the followers.Now it can happen that one of the follower (say N2 ) has very short randomized timeout so before the heartbeat reaches N2 and it would raise new election and it would start asking for votes from N3 and N4.so N2 would increase the term from T1 to T2 and N3 and N4 would see that T2 has began so they would vote for N2 and we have a new leader.And this scenario can cause a loop.

**Leader stickiness** - Let's say N2 sends the vote request to N3, N3 won't entertain any request if randomized timeout to receive the heartbeat is still pending on N3 because N2's time was only 2ms but N3's time is  3sec so it still has the time to receive the heartbeat from N1.If N3's timeout is also over then it can agree that N1 is actually dead and can vote for N2.

So election is not initiated if the randomized timeout is less than round trip timeout and timeout maybe reduced due to clock drift also and that's why re-randomized timeouts are also assigned.


## Phase 2: Log Replication

* Leader appends the incoming requests to it's local log,then leader sends `appendEntries` RPC to the followers containing the 
	- new entry
	- current term and 
	- log index.

* Then the followers append the new entry in their replicated log , if they have the last entry with them , they would send back the acknowledgement.

* Then If leader receives the acknowledgement from majority followers, then the leader marks the current entry commited and it returns the result to client.

* Then leader also notifies the followers that entry has been commited and they should also commit.

![[01-Banking-Example.jpeg]]

### Problems

What if A receives the request log it but then before sending the log entry to B and C it goes down?

* Server B and C apart from the log entries also waiting for the heartbeat from the leader A. So they would start their own election and elect the new leader say B is chosen with new Term T2.

Now let's say after new election A comes back and it thinks it is still the leader so it would try to send the heartbeat to B and C. The moment this happens B would send back the rejection to this heartbeat saying B is already at Term T2 meaning leader has changed and you are sending the heartbeat of Term T1.So A would downgrade from leader to follower the moment it becoms the follower but it had already appended the user's request in it's logs and no other node has this entry.So we have to clean it up.A has uncommited entry.B would send the heartbeat to A because B is the new leader now.Now B would see that A's logs are not matching with B's logs as A has one uncommitted entry which is not present in B and C.So server B would force A to override the log to match the logs with B because B has the latest data as it is the new leader.and also if any new commit is present in B then those committs are also to be commtted in A
and that's how actually server A would come back online eventually.

Let's see a different situation where leader A can go down.

![[02-Sequence-Diagram.jpeg]]

what if Node A crashes while passing the commit message to B and C.Now between B and C whoever had the smaller timeout would start the new leader elcection.B is the new leader and now say A has come back now B will convey A that he has term T2 so it has the latest data and A can longer server as the leader.but A has the commited data which is not present inside B and C , what happens to that data ? B just cannot force override it as the data is committted in this case.Actually B would autocommit the uncommitted entries present in it's logs and also ask to do the same for C because in this case uncommited entries were already propagated to B and C only after committing the entry inside A it got crashed so B and C do not contain the committed entries but they still have the uncommited entries of the transaction.So as soon as B becomes the new leader it will auto commit the pending entries because maybe the previous leader was not able to send the corresponding commit requrest.Once it commit the entry it would ask C to do the same.


Let's say server C was not able to send the response back but B was working fine and sent back the response .
![[01-Banking-Example.jpeg]]


now when server C comes back server A assume that C was not able to send back the ACK but must have received the log entries uncommitted and committed all.But it is not the case as server C was crashed so it does not have the latest data.Now in this case A won't send the commit message to C again as A does not know that C does not have the data. Now imagine one more transfer request comes to A so it would append this new entry in it's log and send it t B and C.now here mismatch would happend between A and C log as C does not contain the last log say index 5 and the answer would be NO so if it does not have the index 5 then it cannot just append index 6.So C would reject the request and reply to A that it does not have the old entries in log now Leader would ask the last index that C has then C would reply with say index = 4, so leader would start sending the next entries till the latest entries and then C would apply index 5 because it has index 4 and then leader send index 6 now C will check again if it has index 5 and this time it has index 5 so now it can append index 6 and that's it.


