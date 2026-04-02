
## Functional

- We need to list top k trending tweets happening in the time range of last 5 minutes, last 1 hr,last 1d ,last 7d and so on.
- It will be good if we can have some idea for sliding window(from 2.15pm to 3.15pm) range instead of granual range (from 2pm to 3pm) .

## Non Functional

- Scalable 
- Fault Tolerant
- Availability >>> Consisteny , we can tolerate some errors.
- Maybe we do not want have highly consistent answers for immediate short time ranges but if we can have better consistency for bigger time ranges then it would be preferable

> If people likes a tweet then we can say it's trending


## Estimation

DAU - 10B
10% of them interacting heavily with the platform - 1B

- Assuming half a billion users are tweeting 10 tweets a day `0.5 * 10 -> 5B tweets per day` (Interviewer can increase or decrease this number accordingly).

Number of Tweets matter as this would become the dataset from which we would find the top k.




