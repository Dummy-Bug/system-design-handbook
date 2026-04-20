# System Overview — Netflix

Netflix is a video streaming platform — but unlike YouTube, users never upload anything. Netflix either licenses content from studios like Warner Bros, Disney, and Sony, or produces its own originals like Stranger Things and Squid Game. In both cases, the production company delivers raw video files directly to Netflix. Netflix then processes, stores, and streams that content to its subscribers.

This makes Netflix a **closed ingest system**. The upload pipeline is entirely internal — no user-facing upload API exists. The interesting engineering problem is not on the write side at all. It is entirely on the read side: how do you take one copy of a video and stream it smoothly to 260 million subscribers across Mumbai, Lagos, and São Paulo simultaneously, without buffering, at any hour of the day.

What makes this hard is the gap between **one raw video file** stored centrally and **millions of concurrent streams** happening globally — each on a different device, different screen size, and different network speed. A raw studio file is often a single high-quality format. Netflix has to convert it into 50+ combinations of resolution and codec before a single user can press play.

> [!info] Real-world context
> Netflix serves 260 million subscribers. At peak, it accounts for ~15% of global internet traffic. A single popular show release — like a new season of Squid Game — can spike to millions of concurrent streams within minutes of dropping.
