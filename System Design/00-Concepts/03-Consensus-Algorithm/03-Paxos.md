Similer to Raft , Paxos also has set of actors.

**Proposers** - It is the advocate who initiates the process for  doing something about the client request.Let's say a client request comes and it hits a node say database node.So now this database node would advocate that Hey we have received a new request , let's do something for this request.
* Proposers tries to to convice Acceptors to agree on a value.
so we do not have leader in this setup just a proposer trying to convince other nodes.

**Acceptors** - These are the voters.They receive the proposals from proposers and vote to accept them based on defined rules.
- Voters also ensure that if a decision is made it does not get violated.

**Quoram** - To make a progress we need a majority of acceptors to alive and communicating.

* if we have 2F+1 acceptors then we can tolerate upto F failures. e.g if we have 11 nodes if 5 of them fails we still have 6 to give us the majority .

**Proposal Number** - Unique ID number.
- These numbers must be totally ordered ,so whenever a proposer is going to send a proposal to acceptors, they are going to send a unique number , now this unique number is going to be incrementing Integers with timestamps.
- Very useful for acceptors to distinguish between old and new proposal

## Phase 1: Prepare/Permission

Whosoever node becomes the proposer by accepting the client request,they pick a proposal number N (higher than what it has already seen)
* It prepare a request PREPARE(N) and message to the quoram of acceptors.
* Each acceptor looks at the incoming value N , if N > existing proposals then the acceptor reolies with a request PROMISE(N).Now if the acceptor had previous accepted value then that value and it's proposal number would be added to this PROMISE(N).So acceptor is kinda replying with your number N is the highest , if someone else sends me a request which is lesser than N then I am going to totally ignore them as you are the biggest player here but prior to you I already promised V(any previous value lesser than N) with their value but ofcourse I am going to follow you.


## Phase 2: Voting

* The proposer needs to propose a new value now.
* If none of the acceptors were working with any old value ,then our proposer can propose a new value, else it has to use the highest value given by acceptor.
* It sends the request ACCEPT(N,V)
* If acceptors do not have a higher proposal number now they can accpet.


Let's take an example by taking three DB nodes and horizontally scaled App server and one of them sends a request say SET x = 100, now say DB-1 accepted the request so it would become a proposer.Now DB-1 is going to propose a value N=1, because till now it has not seen any proposal value.Now DB-1 will send PREPARE(1) to both DB-2 and DB-3.Now DB-2  would accept and reply with PROMISE(1) as it has not seen any value before. let's assume DB-3 is crashed .So we have two(DB-1 itself and DB-2) voters voting for value N = 1. now in phase 2,DB-1 is going to sent ACCEPT(1,x=100).So DB-1 wil write x=100 in it's own log.now DB-2 chekc is N=1 still the highest or not if yes then it would also write x=100 in it's log and sents back the accepted request `Accepted`. This is the happy path.
In the following sequence diagram instead of Leader it would be Proposer.

![[03-paxos.jpeg]]

Here is the sequence diagram for simultaneous writes.
![[04-Simultaneous-writes.jpeg]]


Once DB-2 succeeded with value x = 999, it would broadcast a message to all nodes that everyone has to committ x=999.now DB-1 would look at it's local log and it would see that N=101 is > N = 100 so it has to write this value x = 999.

Now assume there was one more node DB-4 which missed all of this action because it was down and now it has come back.So it would do something called as **log replay** , it is going to communicate with other nodes and refill the set of logs which were missing.if DB-4 was a new node then it would directly get the snapshot file with all the existing logs.


It might have happened that when DB-1's write of X=100 got rejected , DB-1 may receive another write request and this time chose value N = 102 and due to this DB-2's value won't get commit and then DB-2 get's the new request and so on which can leads to never ending cycle kinda thing so in order to avoid it we have **Randomized Backoff** which states that a failed node cannot retry before a certain amount of timeout.
