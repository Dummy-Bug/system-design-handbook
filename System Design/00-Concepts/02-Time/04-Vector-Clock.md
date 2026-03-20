## Problems in Lamport Clock

In Lamport clock we just keep one counter value and then we keep on sharing this counter value among the nodes

Lamport clock does not capture the entirety of causal relationship. Like Lamport clock is really useful for total ordering of event.but we will never be able to figure out everything regarding the causality of the relationships.e.g if there's an event A that happens before B, A-->B then Lamport Timestamp of A would be lesser than that of B C(A) < C(B). so if count of any even event x is less than count of any even y C(X) < C(Y) then are we sure that X-->Y ?

![[02-Lamport-Clock-Cons.jpeg]]
> Imagine we have two nodes and at n1 some event A happens so n1's local counter c1 goes from 0 to 1.let's say another event named X happens in n2 and c2 goes from 0 to 1.now one more event B happens in n2 so c2 goes from 1 to 2.
> 
  So now we have Time(A)=1,Time(B)=2 But A did not cause B.
  as B was an independent event.

It has issues with concurrency.Lamport clocks only give us a **consistent ordering**, not a **true causal relationship**.

They guarantee:

> If event A _caused_ event B, then timestamp(A) < timestamp(B)

But the reverse is **not true**:

> timestamp(A) < timestamp(B) **does NOT mean** A caused B

Say We have:
- User1 writes value at logical time **5**
- User2 writes value at logical time **6**

Lamport clock says:

> 5 < 6 → User2’s write is “later”

So the system overwrites User1 with User2.

The problem is:

> Lamport clocks **force a total order** on events that are actually **concurrent (independent)**.

In our case:
- User1 and User2 wrote independently
- There is **no communication**, no dependency
- So these events are **concurrent**, not causal

But Lamport clocks can’t detect that.

They just assign numbers and say:

> “6 is bigger than 5 → must be later → overwrite”

These two writes are **concurrent updates to the same data**, so this is a **conflict**, not a “last write wins” situation.


Here check the following sequence diagram.
See here B has not communicated with anyone and some local event X happens in B so it's counter would go from 0 to 1.Now since node C is an observer so it would execute snapshot of whole system say it captures the state of the gaming system using capture operation which is a local event so it's counter would increse from 52->53.

![[03-Lamport-Concurreny-issues.jpeg]]

Now the problem occurs during comparison.Now Lamport clock thinks X caused Y because Cx < Cy but they were unrelated events.

---

## Vector Clocks

These clocks can distinguish between events that are causally related and that are concurrent.


> Instead of maintaing single logical value or counter we maintain a vector of values(size=number of nodes involved).
> 
> Every node will maintain vector of integers for N nodes so we have vector of size N.
> 
> Vi[j] where Vi means we are looking at the vector of ith node and jth index of this Vi vector represent what knowledge Node i has about the logical time of Node j.
> V1[2]-> means what Node 1 knows about logical time of Node 2


> Intially all events are 0
> 
> Local Event -> Nodei increments ith position of it's own vector by 1 means Vi[i] = Vi[i] + 1
> 
> Sending a Message -> Nodei increments ith position of it's own vector and send the entire vector Vi to the new message.
> 
> Receiving a Mesage -> If a Nodej receives a message then it will update every other element k(k belongs to [0,N- 1]) in it's vector by taking the maximum of the incoming message vector. Vj[k] = Max(Vj[k],Vi[k]) and then it increments it's own position by 1. Vj[j] = Vj[j] + 1.


see the sequence diagram below here when Bob replies to Alice then it is the effect of the cause(as Alice sent "Hello").we have reply to a message feature in whatsapp and other chat applications so reply has a causal effect that reply only goes to the message which was existing.people just cannot receive the reply without receiving the existing message.If we compare the two vectors clocks of Alice A [1,0,0] and Bob B [1,2,0] for every index we will do the comparison `1<=1 , 0 < 2 and 0<=0`and we can conclude that vector A < B Hence vector X is cause of Y.

Whereas if you see a concurrent event which is Charlie's message "anyone here" so compare A [1,0,0] and C [0,0,1]
`1>0 , 0<=0 and 0<1`. Here oth index is neith < nor <= so not all indices values are smaller or smaller than equal to .Hence A is not cause of the vector C Hence we can say these were concurrent events because even C is not cause of A because not all values of vector C are smaller than vector A.