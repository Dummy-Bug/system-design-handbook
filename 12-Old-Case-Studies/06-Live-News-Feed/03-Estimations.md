
### Traffic Estimations

Assume we have 1B users registered with our app and 50% of them are active daily.

* DAU 500M
on an average we can assume each user has around 300 following and 200 pages

we can assume on an average person open an App 10 times a day.so we have 500M * 10 => 5B requests per day.
* 5B/86400 ~ 60k requests per second.



### Storage Estimations

Assume on an average in-memory we have to keep 500 posts of each user and out of these 500 we show the user N(say 50 or 100) posts. it means each user's feed we have to keep 
in-memory everytime they open the app which is ready to be published.

Assuming each post of 1KB(storing the metadata like reference of posts or stories stored in s3 bucket) , so for every user we need 500KB of storage , so 500M * 500KB ~ 500TB memory which needs to be there at all times, that would mean we need 5000 server machines with each machine capable of having 100GB(average storage on a machine) in-memory storage.

