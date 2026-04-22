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
    - [Base Architecture](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/05-Base-Architecture.md)

-   **Deep Dives**

    ---

    - [Short Code Generation](01-Raw-IDs.md)
    - [Database](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/06-Deep-Dives/02-DB/01-DB-Choice.md)
    - [Caching](01-Why-Caching.md)
    - [Peak Traffic](01-The-Spike-Problem.md)
    - [Pre-Generated Keys](01-Collision-At-Scale.md)
    - [Cold Storage](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/06-Deep-Dives/07-Cold-Storage/01-The-Problem.md)
    - [Fault Isolation](01-Fault-Isolation.md)

-   **Final Design & Observability**

    ---

    - [Final Architecture](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/09-Final-Design/01-Final-Design.md)
    - [SLIs & SLOs](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/08-Observability/01-SLI-SLO-Connection.md)
    - [Measuring Latency](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/08-Observability/02-Measuring-Latency.md)
    - [Measuring Availability](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/08-Observability/03-Measuring-Availability.md)
    - [Alerting](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/08-Observability/04-Alerting.md)
    - [Error Budget](System%20Design/SDE2/12-Case-Studies/02-URL-Shortener/08-Observability/05-Error-Budget.md)

</div>
