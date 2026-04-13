
> [!info] The core idea
> NTP gets you within 1-10ms of the true time — not good enough for a globally distributed database. Google's answer was to put GPS receivers and atomic clocks directly inside every data center. This gives servers a much more accurate and reliable time source without going out to the internet at all.

---

## Why not put atomic clocks in every server?

The obvious fix to clock drift is to use atomic clocks — they drift less than 1 second in 100 million years. But atomic clocks cost tens of thousands of dollars per unit. A data center running thousands of servers cannot put one in each machine. It's simply not economically feasible.

The compromise: put a **few** atomic clocks and GPS receivers in each data center building. Those few devices serve all the servers in that building over the internal network — much faster and more accurate than going out to the internet like NTP does.

```
NTP:       your server → internet → NTP server (far away)
TrueTime:  your server → intranet → GPS receiver / atomic clock (same building)
```

---

## What is a satellite?

A satellite is just an object orbiting the Earth — like the Moon, but man-made. Humans have launched thousands of artificial satellites that continuously circle the Earth, kept in orbit by gravity.

---

## GPS — not just for location

GPS (Global Positioning System) is a network of about 30 satellites the US military launched into orbit. They are spread out so that from anywhere on Earth, you can always see at least 4 of them in the sky at any time.

Each GPS satellite has an **atomic clock on board**. Every satellite continuously broadcasts a signal containing two things:

```
1. My current position in orbit
2. The exact time I am sending this signal  ← this is the atomic clock part
```

Your phone uses both pieces — it calculates how long each signal took to arrive, and from the travel times of 3-4 satellites it figures out your location. But that location calculation only works because the satellites have perfectly accurate clocks. Without precise timestamps, travel time calculation breaks down entirely.

---

## How Google uses GPS for time — not location

Google's data centers put a **GPS receiver on the roof**. Not to track location — purely to receive the time signal that GPS satellites broadcast. The receiver ignores the position data and only reads the timestamp.

```
GPS satellite (atomic clock onboard) → broadcasts precise time signal
Data center GPS receiver on roof → picks up signal → feeds accurate time to all servers via intranet
```

All servers inside the data center poll this receiver over the internal network. No internet dependency. No NTP latency. Much tighter accuracy.

---

## GPS as primary, atomic clock as backup — and why

You might expect atomic clocks to be the primary since they drift less than 1 second in 100 million years. But atomic clocks have no external reference — they just count from whenever they were started. Over time, even atomic clocks drift slightly with no way to self-correct.

GPS on the other hand is continuously receiving signals from satellites — it is always getting corrected in real time.

```
Atomic clock:  extremely precise per tick but drifts slowly with no external correction
GPS receiver:  slightly less precise per tick but continuously corrected by satellites
```

So in practice:
- **GPS is the primary** — always connected, always being corrected
- **Atomic clock is the backup** — when GPS signal drops (bad weather, outage), the atomic clock holds accurate time for a short period until GPS comes back

If GPS was down for days, the atomic clock would eventually drift too. But GPS outages are short, and the atomic clock is accurate enough to cover that window.

---

## But GPS satellites drift too — who corrects them?

GPS satellites' atomic clocks drift as well. The US military continuously monitors all satellite clocks from ground stations on Earth and sends correction signals up to the satellites regularly.

```
GPS satellite atomic clock drifts slightly
Ground station detects drift → sends correction signal to satellite
Satellite clock corrected → broadcasts accurate time again
```

From your data center's perspective, the GPS signal is always accurate because the military is handling the correction of the satellites themselves.

---

## Why don't other big techs do this?

They actually do — or are moving towards it. Amazon has their own time sync service. Meta has built similar infrastructure. But Google built Spanner in 2012 and TrueTime was a core part of its design from day one — the first time anyone publicly documented using GPS + atomic clocks this way for a distributed database. Other companies either still use NTP or have their own variants they haven't talked about publicly as much.
