### Functional Requirements

* Users can register and authenticate.
* Users can view list of questions.
* Users can submit a code solution in the available set of language and get the code evaluated on custom or internal test cases.


### Non Functional Requirements

**Fault Tolerance:** The system must continue functioning correctly even if individual components (such as application servers or database nodes or evaulatore servers etc) fail. User submissions should not be lost due to partial system failures, and the system should automatically recover through retries, replication, or failover mechanisms.

* System should be **Available** like if someone is normally solving the problems and the system is down for few minutes then it's not a problem but if there's a contest going on then we cannot afford the unavailability as contests are time based problem solving session.At the time of contests if a user is not able to submit a problem then he will loose his rating. because even if you have solved all the problems but time taken by you is not as less as other users then you would still end up in the last of all the users who have solved the same number of problems.
* For contests consistency is important but we have some leaverage on this . as soon as contest is over Leetcode does not provide rating at that exact moment. because lot of time these platforms do plag check in order to detect a cheater. now plag check can only be done once the Leetcode has all the submissions by all the users.so Immediate consistency is not required so no worries of showing exact leaderboard just after the contest is over.Leaderboard creation should be correct but it is not needed as soon as contest is over.So **Eventual consistency** is good for this scenario.
* System should be **Highly scalable** during contests.