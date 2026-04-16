# URL Shortener

Design a system like bit.ly — takes a long URL, returns a short code, redirects at scale. 100M DAU, 1B redirects/day.

---

<div class="grid cards" markdown>

-   **Requirements & Base Architecture**

    ---

    - [Functional Requirements](System%20Design/SDE2/11-Case-Studies/01-URL-Shortener/01-FR.md)
    - [Estimation](System%20Design/SDE2/11-Case-Studies/01-URL-Shortener/02-Estimation.md)
    - [Non-Functional Requirements](System%20Design/SDE2/11-Case-Studies/01-URL-Shortener/03-NFR.md)
    - [API Design](System%20Design/SDE2/11-Case-Studies/01-URL-Shortener/04-API.md)
    - [Base Architecture](05-Base-Architecture.md)

-   **Deep Dives**

    ---

    - [Short Code Generation](06-Deep-Dives/01-Short-Code-Generation/01-Raw-IDs.md)
    - [Database](06-Deep-Dives/02-DB/01-DB-Choice.md)
    - [Caching](06-Deep-Dives/03-Caching/01-Why-Caching.md)
    - [Peak Traffic](06-Deep-Dives/04-Peak-Traffic/01-The-Spike-Problem.md)
    - [Pre-Generated Keys](06-Deep-Dives/06-Pre-Generated-Keys/01-Collision-At-Scale.md)
    - [Cold Storage](06-Deep-Dives/07-Cold-Storage/01-The-Problem.md)
    - [Fault Isolation](06-Deep-Dives/08-Fault-Isolation/01-Fault-Isolation.md)

-   **Final Design & Observability**

    ---

    - [Final Architecture](08-Final-Design/01-Final-Design.md)
    - [SLIs & SLOs](09-Observability/01-SLI-SLO-Connection.md)
    - [Measuring Latency](09-Observability/02-Measuring-Latency.md)
    - [Measuring Availability](09-Observability/03-Measuring-Availability.md)
    - [Alerting](09-Observability/04-Alerting.md)
    - [Error Budget](09-Observability/05-Error-Budget.md)

</div>
