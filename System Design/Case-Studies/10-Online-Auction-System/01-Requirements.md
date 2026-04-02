## Functional

- People should be able to trigger an auction for an item.
- People should be able to view the auctions:see the metadata about the auction,and current highest bid.
- People should be able to bid a price for the item.
- People can participate simultaneously in different auctions.
- Auction can end with a given end time or 24 hours after no interaction.

## Estimation

 - The system should be able to cater 50M auctions concurrently.
 - one auction runs for 10 days 
 - Every auction has 200 bids.
 - so total bids in 1 year = 365 * 1B ~ 400B bids in and in 10 years 4000B bids.


```
so total bids for 10 days-> 50M * 200 -> 10B bids -> 10 * 10^9
so total bids per day -> 10^9
so total bids per seconds -> 10^9/10^5 -> 10kbids/sec - QPS
```

## Non Functional 

 - **Fault Tolerance** - Data durability is very important. say some user have put a highest bid then we cannot drop their bid .
 - **Consisteny** - High availability is important but we will priortize strong consistency because it should not happen that user A has won the auction but use B is still bidding as he does not know that it's over.Everybody should see the same state of the auction.
 - Change in highest bid should be visible to people in realtime 
 - Proper observability and monitoring 

