
Assuming we have 10 posts inside *POST_DB* that are published 5 different users. now say we want to rank only 4 posts out of these 10.

our user Tom follows all of these users. so in order to generate feed for Tom we need all these posts and rank 4 out of them so we need some ranking mechanism

### Ranking Service

* For each post we would have some attributes or features such as likes , comments , shares , created_at , updated_at
* Based on the previous history(fetched from Monitoring service) of Tom that would convey what kind of content Tom likes to consume the relevance for each post is calculated (using ML algorithms).
* So ML algorithms would assign a relevance score for each post sort the posts and return it .
* Eventually all these 4 posts would be shown on Tom's timeline in the decreasing order of relevance score.
