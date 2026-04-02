
**Kafka** - Because we want multiple consumers as consumer-A is going to optimize for a more faster processing but on the toll of accuracy and consumer-B is going to optimize for accuracy for larger time frames but on the toll of efficiency.and also this Kafka Stream would be acting as a shock observer for us as well.

Let's first go with the slower system

> If we have the data of topk trending tweets last 1 hour for each of 24 hours then it would become really easy to calculate the topk trending tweets of the day as we can merge all of the topk tweets of each hour and return the result.

![[Excalidraw/Drawing 2026-03-25 11.59.45.excalidraw]]
> Similary if we want to calculate the topk for last hour we can do it easily if we already have the data topk trending tweets of last 60 minutes that is topk trending tweets for 1st minute, 2nd minute and so on till 60th minute then we can megre all of them to get the topk trending tweets of one hour.

In C2 or consumer-B we can accumulate last 1 minute of data and dump it into the file processing system say HDFS.This data can be accumulated into something like **Parquet files**.

**Parquet Files** - These are columnar storage file format designed for efficient data storage and retrieval particularly well-suited for big data analytics.

Normal row-based file (CSV/JSON):
```
// Each row stores all fields of one tweet together
tweet_id, user_id, like_count, timestamp, text
1001,     u1,      500,        1711:00,   "hello world"
1002,     u2,      300,        1711:01,   "good morning"
1003,     u3,      450,        1711:02,   "breaking news"
1004,     u4,      200,        1711:03,   "good night"
```

To get like counts of all tweets you have to read every single row entirely even though you only need one column.

Parquet (columnar):
```
// Each column is stored together physically on disk

tweet_id column:    [1001, 1002, 1003, 1004]
user_id column:     [u1,   u2,   u3,   u4  ]
like_count column:  [500,  300,  450,  200  ]
timestamp column:   [1711:00, 1711:01, 1711:02, 1711:03]
text column:        ["hello world", "good morning", ...]
```

To get like counts of all tweets you only read the like_count column — skip everything else entirely.

cool so dump every event that we got for a minute inside these Parquet files and then apply map-reduce processing for connecting all parquet files and clubbing the data for one minute and use the following architecture to get the topK as we disscussed  using Map-Reduce ![[Excalidraw/Drawing 2026-03-25 08.44.43.excalidraw]]
The moment we have found the topK for the corresponding last minute then we try to store that inside more files, and we can have multiple files prepared for each minute and then later in the same system we can try to merge all the files of last minutes to get files of let's say last 5 minutes and then we can have topk of last 60 minutes and so on.

We keep on computing the ranges and we keep on dumping them e.g say we got the data from 6:12 to 6:17 and now we have the data for 6:18 as well so we generate a new last 5 minute range and put that into Top K service .

But all this is going to take time that's why we have a buffer of atleast 5 minutes.but if we want to answer for lesser than 5 minutes something like last 1 minute of trending tweets then we need a faster computation because writing to the files , doing computation from files can be harder and expensive.

## CountMin Sketch 

A probablistic data structure for estimating frequency of elements in data stream, offering space efficiency at the cost of potential overcounting due to hash collision.

- If our data is ever growing CountMin sketch space never grow it always consumes constant amount of space.

The problem with hashmaps were if number of unique keys increase then size of hashmap will also increase but that's not the case here.It takes kinda linear space and in more constant fashion .

CountMin has 2D structure with corresponding Width and Depth.
d=3 means depth of CountMin sketch -> 3 rows and then we define certain amount of columns say w=5 means width of  CountMin sketch 5-> 5 columns.

![[Excalidraw/Drawing 2026-03-25 13.06.43.excalidraw]]
- We take d number of hash functions
- Each hash function generates the data in the range [0,w-1]

let's say we pass "apple"
	h1("apple") - 0
	h2("apple") - 2
	h3("apple") - 2

so what CountMin sketch says is that if h1("apple") = 0 then you go in the first row and you go in the 0th column and increment 

Now let's add "banana" 
	h1("banana") - 4
	h2("banana") - 4
	h3("banana") - 4

![[Excalidraw/Drawing 2026-03-25 13.16.12.excalidraw]]

Now say "apple" is to be added again 
	h1("apple") - 0
	h2("apple") - 2
	h3("apple") - 2
Hash function gives the same value for same input

![[Excalidraw/Drawing 2026-03-25 13.18.29.excalidraw]]

Now comes "Orange"
	h1("orange") - 1
	h2("orange") - 2
	h3("orange") - 2

Now "banana" again and then "apple"
so CounMin sketch would look something like this after all these insertions

![[Excalidraw/Drawing 2026-03-25 13.21.25.excalidraw]]

let's calculate 
Freq("Banana") = Min(
				val->h1("Banana") , 
				val-> h2("Banana"),
				val->h3("Banana"))
				)

Min(2,2,2) - > 2 so frq("banana") = 2(True)

Freq("orange") -> min(1,4,4) = 1(True)

Freq("apple") -> min(3,4,4) = 3(True)

sometimes we can get frequency slightly higher but when ? if all the hash values of "orange" and all the hash values of "apple" were same then freq("apple") -> 4 and and freq("orange) -> 4
as both are contributing to the frequency of each other.

[How can we achieve to close to 99% accuracy in CountMin sketch ?](https://vivekbansal.substack.com/p/count-min-sketch)

- With the depth -> 10 and width -> 2000, the probability of not having an error is 99.99% and the error rate is just 0.1%.

Redis has a version of [CountMin sketch](https://redis.io/docs/latest/develop/data-types/probabilistic/count-min-sketch/) implemented internally.
[Heavy Keeper by Redis](https://redis.io/docs/latest/develop/data-types/probabilistic/top-k/)


![[Excalidraw/Drawing 2026-03-25 13.34.20.excalidraw]]

so for every minute we can have a service that prepares a topK using Redis and since it stores very less amount of data so we can have multiple occurences of Redis-Topk for different-different hours and minutes like for the first minute we have the CountMin sktech , for the second minute we have the CountMin sktech, for third and so on. Now let's say if our 5 minute data is not ready yet we can still serve the 5 minute data from merging these multiple topk min sketches because every min sketch can give us the topK.This approach is faster because everythinh is going in-memory like we do not have to write to any files and so.

There are other solution possible as well e.g we can continously dump the data into Time Series DB if we do not want the file based solution and then try to think of ideas from there.