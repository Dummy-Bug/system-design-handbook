### Ride Volume Estimations

* assuming uber process around 20M rides per day 
* with 20M active Riders and
* 3M active Drivers per day.

### Storage Estimations

* Assuming for storing rider's information we require 1000 bytes.
* Total riders on the app say 400M
* Hence we require 400M * 1000Bytes => 400GB.
* Similarly if we have 5M driver we need around 5GB 

### Trip MetaData

* Assuming for storing trip's information we need 100Bytes
* 20M rides * 100Bytes => 2GB
* **Peak Traffic** we can assume to be 30% of total rides per day.

so we kinda require 2GB data per day so full year we require ~1TB of storage.

### Bandwidth Estimation

**Description** Maximum amount of data that can be tranmitted over a network connection in a given amount of time.It is also known as data transfer rate.

* If 20M rides are happening per day so in one second 20M/86400 ~ 232 rides per second.
* Now we know that each trip takes 100Bytes so it will take 232 * 100bytes ~23KB => 185kbps bandwidth should be priovided by system in order to function well.
* one of the service would keep on sending the driver's location every 4 seconds , imagine new location which is coming in takes 16Bytes . so assume total active drivers 3M*(4Bytes(driver's data)+16Bytes) => 57MB => (64 * 8)/4sec => 128mbps.






