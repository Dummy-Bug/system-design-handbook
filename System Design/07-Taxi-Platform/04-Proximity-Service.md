Given a rider's location and a search location,we want to find all the drivers with the radius. similar proximity service is required for swiggy and tinder applications.

In Uber rider's location most of the time is stable but driver's location is keep on changing whereas for an app like swiggy the location of restraunts around the user is stable hardly the location of restraunts ever change.

so Uber has very heavy Read-Write operations on DB but swiggy has only Read heavy operations on DB.

so we will be using Databases instead of in-memory to store the data of driver's location 

DRIVER LOCATION
```Http

driver_id (FK)
lattitude
longitude
```

DRIVER
```Http

driver_id (PK)
```

for DRIVER details we can use SQL DB as we already have structured data. and change of driver's details is not that frequent.

DRIVER LOCATION table is a GEOSPATIAL INDEX TABLE which has 
driver_id and indexing on lattitude and longitude for fast location searches.

**GEOSPATIAL DB** These are special type of databases that are used to power the location based search. As we want to find out the nearest drivers as soon as possible so that user experience is seemless.So such type of databases are desgined exactly for these type of scenarios and are very optimize.some of the popular examples of such type of databases are REDIS GEOHASH(by Redis) and POSTGIS(by PostGre SQL)

### Algorithm

Assuming we have a DB that contains driver_id , lat and long entries.now say we have lat (rider_lat)and long(rider_long) of a rider and we have to find all the drivers around inside radius say 5KM.

so one way to execute this query is 
```SQL

select driver_id , lat , long from DRIVER_LOCATION
where (lat between {rider_lat} - raidus AND {rider_lat} + radius)
AND 
(long between {rider_long} - raidus AND {rider_ong} + radius)
```


#### Problems
* This is highly ineffecient approach as the query would go to all the drivers(2M in total) present inside the DB and will check if the driver is fitting in this radius or not.So with the scale of 2M drivers it is extremly slow.
* Even indexing on lat and long won't solve the probem. It will make the process a bit effecient but it won't make that big of difference because issue is that given data is a 2 dimensional . so first all the drivers that lies in the given range of lat would be selected and after that we have to apply the same logic for long as well and then eventually we will take the intersection of both the results as this intersection would contain the drivers who have both lat and ling within 5KM radius. so even if we do indexing still this problem won't vanish.

so is there a way to make this 2D data 1D ?yes GEOSPATIAL DBs convert the 2D data into 1D data stores it into the DB then build indexes on top of it which is very very fast.

#### Approaches

* Hash based approach further divded into Even grid , cartesian tiers and Geo Hash
* Tree based aproach further divided into Quad tree , google s2 and RTree

we will go in depth with Geo Hash approach.in practive none of the above approaches are being used by the big techs as each one of them has their own inbuilt libraries

### Geo-Hash

* So it take whole world map spreads it out on the sheet of a paper and divides it into four quadrants and those four quadrants are divided across the Prime Meridian and Equator. These four quadrants are represented by 2bits we have 00 for left upper half 01 for upper right half 10 for bottom left half and 11 for bottom right half.


* Now from these four quadrants we further divide it into another four quadrants and we do it for each quadrant. and so on for next each sub quadrants
* GeoHash conceptually starts by dividing the world into quadrants but **precision grows by appending one bit at a time** Each additional subdivision adds **one extra bit** to the existing bit sequence, alternately refining longitude and latitude. As we go deeper, the number of bits increases **linearly** (e.g., 1 bit → 2 bits → 3 bits → 4 bits → …), with each added bit reducing the grid size.![[01_GeoHash.jpeg]]
* We keep subdividing the GeoHash grid until the cell size matches our target search radius, at which point the GeoHash precision is sufficient and further subdivision is unnecessary.

## Why Base32 Encoding Is Used in GeoHash

Assume we are at a very specific location, say **Taj Mahal**.

As GeoHash keeps subdividing the world grid:

- Each subdivision adds more bits

- The area represented becomes smaller

- Precision increases

So for a very precise location:

Binary representation example:  
101110011010110010101001101...

This binary string:

- Represents a tiny grid cell
- Can become very long as precision increases

---

## Problem With Raw Binary

If we store raw binary:

- Very long string of `0`s and `1`s
- Hard to read
- Inefficient to store as text
- Not human-friendly
- Not URL-friendly

Example: 101110011010110010101001101011001...
This is not practical.

---

## Solution: Base32 Encoding

GeoHash groups the binary string into **chunks of 5 bits**:

10111 00110 10110 01010 10011 ...

Each 5-bit group is converted into a **Base32 character**.

So instead of: 101110011010110010101001101...
We get something like: u4pruyd

Now:
- Much shorter
- Human-readable
- URL-safe
- Database-friendly
---

## Why Base32 Specifically?

Because:

- 2⁵ = 32
- Each character represents 5 bits
- Good balance between compactness and readability
- Uses digits + lowercase letters (safe in URLs)


#### REDIS GEOHASH

* **GEOADD** It adds a geospatial entry where the lattitude and longitude of each driver are stored as a part of the key.

assume driver_id 123 , lattitude 56.789 and longitude 56.789
so we will have the key (driver : location) and value (123,56.789,-56.789) and 
command 
*GEOADD driver:location 123,56.789,-56.789*
so it only stores the coordinated associated with unique identifier of the driver.
for more [Redis Geo Hash](https://redis.io/docs/latest/develop/data-types/geospatial/)


#### Overall Flow

When a rider requests a ride, the request is sent over a persistent connection (e.g., WebSocket) and handed off to the **Demand Service**, which represents the rider’s intent to book a ride from a given latitude and longitude.

The Demand Service forwards this request to the **Supply Service**, which is responsible for managing driver availability. The Supply Service queries the **Location Manager Service** to fetch all nearby drivers within a certain radius of the rider’s location.

However, proximity alone is not sufficient to decide which driver should be assigned. The Supply Service must compute the **Estimated Time of Arrival (ETA)** for each candidate driver. This is because geographic distance does not always correlate with travel time.

For example, in a city like London divided by the River Thames, a driver who is geographically closer but on the opposite side of the river may have a higher ETA than a driver who is slightly farther away but on the same side. Since riders care about **ETA, not physical distance**, the Supply Service prioritizes drivers based on ETA rather than raw proximity.




