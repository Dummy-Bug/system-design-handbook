
![[02_Architecture.png]]

**1. The Rider Initiates the Request** The Rider's mobile app sends a ride request containing their `user_id` and current `lat`/`long` coordinates.

**2. Load Balancing and Connection**

- **Load Balancer (LB):** The request first hits the LB, which routes the incoming traffic to an available server to prevent any single server from getting overwhelmed.
    
- **WebSocket (WB):** The request is passed to a WebSocket server. WebSockets maintain a persistent, two-way connection between the Rider's app and the backend. This is crucial so the server can push live updates (like the driver's moving car on the map) back to the rider without the app constantly having to ask for it.
    

**3. Processing the Ride Request** The WebSocket forwards the payload to the **Request Vehicle Service**. This is the core orchestrator for the booking process. It now needs to find the best driver for this specific rider.

**4. Finding Nearby Drivers**

- The **Request Vehicle Service** sends the rider's `lat/long` to the **Location Manager Service** and asks, "Who are the available drivers near this location?"
    
- The **Location Manager Service** constantly receives location updates from all active drivers (via the Driver's LB -> WB). It stores these real-time locations in **Redis**.
    
- **Redis** acts as an extremely fast, in-memory geospatial database. The Location Manager queries Redis to find a list of drivers within a certain radius of the rider's coordinates and returns this list to the Request Vehicle Service.
    

**5. Calculating the Best Match**

- Now that the **Request Vehicle Service** has a list of nearby drivers, it needs to figure out who can get there the fastest. It sends the rider's location and the locations of the candidate drivers to the **ETA Service**.
    
- The **ETA Service** calculates the actual driving time (accounting for roads, traffic, etc., often using external mapping APIs) and returns the ETAs.
    

**6. Dispatching the Request to the Driver**

- The **Request Vehicle Service** selects the optimal driver based on the ETA and sends a ride offer.
    
- This offer flows down through the **Location Manager Service** to the specific Driver's **WebSocket** and pops up on the Driver's app.
    

**7. Driver Acceptance and Trip Creation**

- The driver taps "Accept". This confirmation flows back up (Driver -> LB -> WB -> Location Manager -> Request Vehicle Service).
    
- The **Request Vehicle Service** notifies the **Trip Manager Service** that a match has been made.
    
- The **Trip Manager Service** is responsible for the state of the ride. It creates a new "Trip" record (linking the `rider_id` and `driver_id`) and saves this permanent record to the main **Database**.
    

**8. Confirming with the Rider** Finally, the **Trip Manager Service** (or Request Vehicle Service) sends a success message back through the Rider's **WebSocket**. The rider's app updates to show "Driver is on the way," along with the driver's details and the ETA calculated earlier.