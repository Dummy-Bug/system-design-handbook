![[Excalidraw/Drawing 2026-03-26 12.25.06.excalidraw]]
- separate service for viewing or Query the auction as viweing requests would be lot more than creation of an auction.

But we still have not handled the Fault Tolerance aspect of the system as what if bid request reaches the Bid Mutation service but our service crashes then the bid would be lost and user will have to bid again which is bad user experience as well as not following the Failt Tolerance property so we have to introduce a system that for sure persists the data.

![[Excalidraw/Drawing 2026-03-26 12.40.58.excalidraw]]

after the introduction of Kafka now even if our whole system is down still from Kafka we can retrieve the bid and start processing it.


What DB to chose for storing auction's data ? simple relational DB like Mysql or Pgsql or mongodb(provide master slave so all the reads would go to slaves and the writes to master and since writes are less anyway so it make sense to use relational db)is good as there are not many writes on an auction writes would only come if we also store the highest bid on the auction table itself.

Auction Table
```Http

id
item_id
start
end(nullable)
highest_bid_price(to reduce joins includingh here)
highest_bid_id
winner_id
```

for one auction there would be lot of bidding coming up, there would be many useless bids as well e.g price way lower than already highest bid etc etc but we still have to write it so it looks like write heavy system so Cassandra can be good with partition key `auction_id`so all the bids of an auction stores inside that datastore. if one of the auction is very hot auction then we can have hot partition.
```Json
// Hot auction fix: Partition key = (auction_id, time_bucket) e.g. (1001, "2024-01-01-14")  auction_id + hour bucket → spreads one hot auction across multiple partitions
```
Bidding Table
```Http

id
auction_id
user_id
bid_amount
timestamp(it would help if two users made the bid at same time)
```


> Timeseries DB can also be considered as they are also good for write heavy system and time is also valuable here but we will stick to Cassandra as of now.







