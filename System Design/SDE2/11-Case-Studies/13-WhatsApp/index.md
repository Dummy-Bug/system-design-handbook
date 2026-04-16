# WhatsApp

Design a real-time messaging system at 500M DAU — persistent WebSocket connections, guaranteed message delivery, offline queuing, message ordering, read receipts, and inbox at scale.

---

<div class="grid cards" markdown>

-   **Requirements & Base Architecture**

    ---

    - [Functional Requirements](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/01-FR.md)
    - [Estimation](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/02-Estimation.md)
    - [Non-Functional Requirements](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/03-NFR.md)
    - [API Design](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/04-API.md)
    - [Real-Time Comms](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/04-Real-Time-Comms/01-The-Problem.md)
    - [Base Architecture](01-Overview.md)

-   **Deep Dives**

    ---

    - [Database](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/06-Deep-Dives/01-DB/01-DB-Choice.md)
    - [Message Ordering](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/06-Deep-Dives/02-Message-Ordering/01-The-Problem.md)
    - [Offline Delivery](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/06-Deep-Dives/03-Offline-Delivery/01-The-Problem.md)
    - [Message Status](01-The-Three-Ticks.md)
    - [Inbox](01-Inbox-Load-Flow.md)
    - [Caching](01-Message-History-Cache.md)
    - [Peak Traffic](01-Redis-Sharding.md)
    - [Fault Isolation](01-Client-Reconnect.md)

-   **Final Design & Observability**

    ---

    - [Final Architecture](01-Final-Architecture.md)
    - [SLIs & SLOs](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/08-Observability/01-SLI-SLO-Connection.md)
    - [Measuring Latency](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/08-Observability/02-Measuring-Latency.md)
    - [Measuring Availability](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/08-Observability/03-Measuring-Availability.md)
    - [Alerting](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/08-Observability/04-Alerting.md)
    - [Error Budget](System%20Design/SDE2/11-Case-Studies/13-WhatsApp/08-Observability/05-Error-Budget.md)

</div>
