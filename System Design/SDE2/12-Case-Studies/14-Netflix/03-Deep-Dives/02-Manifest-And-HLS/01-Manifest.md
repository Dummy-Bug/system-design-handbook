## What the Client Needs Before Playing a Single Frame

When you click play on Inception, the Netflix app cannot just start fetching video. It first needs to know two things — what resolutions are available for this movie, and what the URL is for every chunk at every resolution.

The app cannot guess this. Someone has to tell it.

The naive instinct is to send all of this when the user is browsing — attach it to the movie list response. But the numbers make that impossible:

```
Inception → 4 resolutions × 2250 chunks = 9000 chunk URLs
Homepage shows ~50 movies across genre rows

9000 × 50 = 450,000 URLs sent on every homepage load
```

That is gigabytes of metadata for a page that should load in under 200ms. So this information does not travel with the browse response.

Instead, it arrives only when the user actually clicks play — as one small text file called the **manifest file**.

> [!info] What is a manifest file
> A small text file that arrives the moment you click play. It lists every available resolution and the S3 URL for every chunk at every resolution. It is the client's complete roadmap for the entire movie — before a single frame of video has been fetched.

The first response when you click play is not video. It is this text file. Only after the client has it can it start fetching chunks.

---

## What Is Inside the Manifest File

The manifest file is a plain text file with a `.m3u8` extension — the format is called **HLS** (more on that shortly). At a high level it contains one row per resolution, and each row has two things — the bandwidth required to stream that quality, and the URLs for every chunk at that resolution.

```
manifest.m3u8
─────────────────────────────────────────────────────
480p  → bandwidth required: 1 Mbps  | chunk URLs
720p  → bandwidth required: 3 Mbps  | chunk URLs
1080p → bandwidth required: 5 Mbps  | chunk URLs
4K    → bandwidth required: 25 Mbps | chunk URLs
─────────────────────────────────────────────────────
```

The client reads this file and now knows exactly what is available and what each quality costs in terms of bandwidth.

---

## How the Client Picks Resolution

The client cannot pick a quality before it knows its own network speed. And it cannot know its network speed before downloading something. So it always starts the same way — it fetches the very first chunk at the lowest quality, 480p, regardless of the device or connection.

That first chunk is tiny:

```
480p bitrate  = 1 Mbps
chunk duration = 4 seconds

chunk size = 1 Mbps × 4s = 4 Mb = 0.5 MB
```

Half a megabyte. It downloads in milliseconds even on a slow connection. The client measures how long it took and calculates the available speed:

```
chunk size     = 0.5 MB
download time  = 0.1 seconds

speed = 0.5 / 0.1 = 5 MB/s = 40 Mbps
```

Now it looks at the manifest rows. 4K needs 25 Mbps, the client has 40 Mbps — it picks 4K for chunk 2 onwards. If the client had measured only 2 Mbps, it would have picked 480p and stayed there until the speed improved.

> [!info] Why start at 480p
> The client has no speed measurement yet — it cannot safely assume anything. Starting at the lowest quality guarantees the first chunk always downloads successfully. The speed measurement from that chunk then drives every subsequent quality decision.

---

## Adaptive Bitrate Switching — Mid-Stream Quality Changes

The client does not measure speed just once at the start. It measures speed after every single chunk download. This is what makes streaming adaptive.

Say the client is streaming Inception at 4K. The user is on WiFi at 40 Mbps. At chunk 47, they step into an elevator — signal drops to 2 Mbps.

```
chunk 47 download time was slow → measured speed = 2 Mbps
manifest row for 720p requires  = 3 Mbps  → too high
manifest row for 480p requires  = 1 Mbps  → fits

client fetches chunk 48 from the 480p row
```

The video never stops. Quality drops slightly for a few seconds. When the elevator ride ends and signal recovers, the client measures speed again after the next chunk, sees 40 Mbps, and switches back up to 4K.

This process — measuring speed after every chunk and picking the best fitting resolution for the next chunk — is called **Adaptive Bitrate Streaming (ABR)**.

> [!important] ABR is entirely client-side
> The server does not decide quality. It just stores all the chunks and serves whatever the client asks for. The client reads the manifest, measures its own speed, and picks the right chunk URL. Netflix's servers have no idea what resolution any given user is watching at any moment.
