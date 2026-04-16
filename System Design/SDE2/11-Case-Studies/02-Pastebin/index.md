# Pastebin

Design a system like pastebin.com — users paste text, get a short link, content is retrieved by anyone with the link. 10M DAU, expiring pastes, large content blobs.

---

<div class="grid cards" markdown>

-   **Requirements & Base Architecture**

    ---

    - [Functional Requirements](System%20Design/SDE2/11-Case-Studies/02-Pastebin/01-FR.md)
    - [Estimation](System%20Design/SDE2/11-Case-Studies/02-Pastebin/02-Estimation.md)
    - [Non-Functional Requirements](System%20Design/SDE2/11-Case-Studies/02-Pastebin/03-NFR.md)
    - [API Design](System%20Design/SDE2/11-Case-Studies/02-Pastebin/04-API.md)
    - [Base Architecture](05-Base-Architecture.md)

-   **Deep Dives**

    ---

    - [Short Code Generation](06-Deep-Dives/01-Short-Code-Generation/01-Requirements.md)
    - [Database](06-Deep-Dives/02-DB/01-DB-Choice.md)
    - [Caching](06-Deep-Dives/03-Caching/01-Why-Cache.md)
    - [Peak Traffic](06-Deep-Dives/04-Peak-Traffic/01-Hot-Key-Problem.md)
    - [Fault Isolation](06-Deep-Dives/05-Fault-Isolation/01-Why-Fault-Isolation.md)
    - [Async S3 Upload](06-Deep-Dives/06-Async-S3-Upload/01-Why-Async-Upload.md)
    - [Expiry & Cleanup](06-Deep-Dives/07-Expiry-Cleanup-Job/01-Why-Cleanup-Job.md)

-   **Final Design & Observability**

    ---

    - [Updated Architecture](06-Deep-Dives/08-Updated-Architecture/01-Updated-Architecture.md)
    - [SLIs & SLOs](07-Observability/01-SLI-SLO-Connection.md)
    - [Measuring Latency](07-Observability/02-Measuring-Latency.md)
    - [Measuring Availability](07-Observability/03-Measuring-Availability.md)
    - [Alerting](07-Observability/04-Alerting.md)
    - [Error Budget](07-Observability/05-Error-Budget.md)

</div>
