## Why a Standard Is Needed

You have a manifest file — a text file listing resolutions and chunk URLs. But a text file can be structured in a thousand different ways. How does the Netflix app on your phone know how to read it? How does it know where the bandwidth value is, where the chunk URLs are, what the resolution field is called?

Someone had to agree on a format. A set of rules that says — this is how a manifest file must be written, and this is how every client must read it. That agreed-upon set of rules is called a **standard**.

It is the same idea as HTTP. HTTP is a protocol — an agreed set of rules for how requests and responses are structured. A streaming standard does the same thing but specifically for video — it defines how manifest files and chunks must be structured so that any client can read any manifest file without guessing.

> [!info] What is a streaming standard
> An agreed set of rules that defines how a manifest file is structured and how video chunks are named and formatted. Any client that follows the standard can play any stream that follows the same standard — regardless of who built the client or who built the server.

> [!important] Protocol vs Standard
> A **protocol** defines how two systems talk to each other — both sides. HTTP defines how a client sends a request AND how a server responds. Both sides must follow the same rules for the conversation to work.
> A **standard** defines a format or set of rules that everyone agrees to follow — it does not have to involve two-way communication. HLS is a standard because it defines the format of the manifest file and chunks. The actual delivery of those chunks happens over plain HTTP.
> In practice the terms are used interchangeably and no interviewer will penalize you for calling HLS a protocol.

---

## Where HLS and DASH Came From

Before 2009, streaming used a protocol called **RTMP** — a single continuous stream at one fixed quality over a persistent connection. No chunks, no adaptive bitrate. If the network slowed down, the video froze. There was no fallback, no quality switch — just a buffering spinner.

On desktop with stable broadband this was tolerable. On mobile it was broken. iPhone launched in 2007 and mobile networks in 2009 were terrible — speeds jumped constantly, connections dropped mid-stream. A fixed-quality continuous stream had no way to survive that.

Apple invented **HLS (HTTP Live Streaming)** in 2009 specifically to solve the mobile problem. Manifest file, time-based chunks, adaptive bitrate — all of it was designed so that an iPhone on an unstable mobile network could keep playing video without freezing.

Android was in the same situation — equally broken on mobile streaming before HLS existed. Google's answer came in 2012 with **DASH (Dynamic Adaptive Streaming over HTTP)** — an open standard backed by a standards body, doing the same thing as HLS but with a different file format.

```
Before 2009  → RTMP, fixed quality, no chunks, constant buffering on mobile

2009         → Apple invents HLS — chunks + adaptive bitrate, built for iPhone

2012         → Google backs DASH — open standard, same concept, different format
```

> [!info] HLS vs DASH in one line
> Same concept — manifest file, time-based chunks, adaptive bitrate. Different file formats. HLS uses `.m3u8` manifest files and `.ts` chunk files. DASH uses `.mpd` manifest files and `.mp4` chunk files.

---

## Which One Does Netflix Use

The answer depends on where the user is watching from.

When a user watches Netflix through the **Netflix app** on iPhone or Android, Netflix's own custom video player is running inside the app. This player is built and maintained by Netflix — it has nothing to do with the OS. Netflix can use HLS, DASH, or any format they want on any device. The OS does not dictate anything.

The constraint only appears in **browsers**. Browsers have their own built-in video players, and those players have format restrictions:

```
Safari (desktop + iOS browser)  → only understands HLS

Chrome, Firefox, Edge            → understands DASH
```

Netflix has no control over Safari's built-in player. If a user watches Netflix on Safari through the browser, Netflix must serve HLS — Safari simply cannot play DASH. Everywhere else Netflix primarily uses DASH.

> [!important] The real reason HLS vs DASH matters for Netflix
> It is purely a browser compatibility constraint. Safari only supports HLS. Netflix serves HLS to Safari and DASH everywhere else. When using the Netflix app — on any device — Netflix's own custom player runs and the choice of standard is entirely Netflix's decision.

> [!info] Netflix in practice
> Netflix stores chunks in both HLS and DASH formats in S3. The app detects the client environment and serves the appropriate format. The manifest file structure differs between the two formats but the underlying chunks and adaptive bitrate logic are identical.
