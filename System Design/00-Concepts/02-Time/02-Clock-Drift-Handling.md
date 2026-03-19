## How to Solve Clock Drift ?

Instead of using our own clocks everytime what if we use more accurate clock and somehow calculate the time using that.So we should keep resync our clock with more accurate clocks every now and then.

## Network Time Protocol

Network Time Protocol (NTP) is designed as a layered system to deliver highly accurate time to end users without exposing critical infrastructure directly to the internet.

At the top of the hierarchy are [**Stratum 0 devices**](https://www.geeksforgeeks.org/computer-networks/network-time-protocol-ntp/). These are ultra-precise time sources such as atomic clocks and GPS receivers. They maintain extremely accurate time but are not connected to the public network.

These Stratum 0 devices feed time into [**Stratum 1 servers**](https://www.9tut.com/network-time-protocol-ntp-tutorial). Stratum 1 servers are directly connected to the high-precision hardware and act as the first level of network-accessible time sources. They are still tightly controlled and not widely exposed to general public traffic.

Below them are **Stratum 2 servers**. These servers synchronize their time from one or more Stratum 1 servers and are typically the ones exposed to broader networks, including the public internet. Most client systems—such as laptops, servers, and mobile devices—retrieve time from these Stratum 2 servers.

Large operating system vendors like Apple and Microsoft maintain their own distributed NTP infrastructure. This hierarchical design ensures:

- **Accuracy**: Time originates from highly precise sources.
- **Scalability**: Load is distributed across multiple layers of servers.
- **Security and reliability**: Critical timekeeping devices are isolated from direct internet access.

In short, NTP works by propagating accurate time from highly trusted, isolated sources down through multiple layers until it reaches end-user devices in a scalable and secure way.


say at t=1 our machine initiate a request to the NTP server and at t=2 server receives the request. at t=3 it sent back the response and at t=4 machines received the response.

![[Excalidraw/Drawing 2026-03-18 19.44.41.excalidraw]]
so we have network delays as well as some computation delays so by the time the actual time contained inside the response we have already spent some more time , so at t=4 we did not get the actual real time immediatley might be slightly older time a few miliseconds etc.

t1 -> Client sends -> 10:20:00(client thinks it's 10:20)
t2 -> Server receives -> server's actual time 10:10 + 2second travel(10:10:02).This is the time at the server.
t3 -> server response -> 1second to process (10:10:03)
t4 -> client receive -> 10:20:05


calculate propagation time delay -> (t4-t1)-(t3-t2)
-> (5)-(1) = 4 seconds , so packets took 4 seconds to travel.

**How client can resolve it's time after receiving the repsonse?**

at t1 client's time was 10:20:00 response received at t4 10:20:05 and out of which 4 second is the travel time , 1 seconds is the processing time and returned response time is 10:10:02. so (propagation time)/2 is the time for traveling the signal from client to server on sided 4/2 -> 2 second. so returned time(10:10:03) + time taken for signal to travel from server to client 2seconds -> 10:10:03 + 2seconds -> 10:10:05.
so 10:10:05 is the estimated time at the server when client received the response at 10:20:00 according to it's own time.

> There's one more problem here our client had time 10:20:00 when it sent the request but now it has calculated the new time to be 10:10:05 but it just cannot just reset time to 10:10:05 because server's time was behind and client's clock was faster .Because say at 10:10:06 we had some cron jobs and now if we reset the time to 10:10:05 after 1 seconds these jobs would run again.if server's time was ahead say 10:20:05 then again issues would happen since if there were some jobs those were to run 10:20:03 all those jobs would get skip if we reset the client's time directlyt to 10:20:05 from 10:20:00.


## Clock Skew

How far out is our clock is from the actual time.
theta -> (t2-t1 + t3-t4)/2
-> (10:10:02 - 10:20:00 + 10:10:03 - 10:20:05)/2
-> ( (-9m58sec) + (-10m2sec) ) /2
-> -20m/2 -> -10minutes.

so client's machines is 10 minutes behind the server's time.

***For demonstration purposes we have taken these large numbers in minutes , ideally actual numbers are in milliseconds***

> If theta < 125ms -> speed it up or slow it down by 500ppm.

> If  125ms <= theta < 1000s -> reset the clock because this time difference is way way high which we cannot cover it by slowing down or speeding up the clock by few ppm otherwise clock skew would remain for too much time. we might need manual intervention if there was something that was expected to happen but that time period was skipped etc .

> If theta >= 1000s -> situation of Panic , manual intevention is required on how to change the clock etc because time difference is too high.

theta is nothing but time or clock difference or clock drift.
