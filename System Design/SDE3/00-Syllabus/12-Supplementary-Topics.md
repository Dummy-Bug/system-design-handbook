## Supplementary Topics (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Supplementary Topics (Observability basics, OLTP/OLAP, Lambda/Kappa, Feature Flags, Reconciliation, Graceful Degradation).
> **SDE-3 Focus:** Moving from "supplementary tools" to "orchestrating the long-term lifecycle, compliance, and economic health of a platform."

### 12.1 — Advanced Multi-Tenancy & Resource Isolation (Extension of SDE-2 7.1 & 12)
*In SDE-2, you know tenants. In SDE-3, you build the "Isolation Engine."*

- **Hard Multi-Tenancy (Cellular Isolation):** Partitioning the compute, network, and storage per-tenant for "Zero-Trust" isolation (e.g., dedicated database instances per high-value client).
- **Fair-Share Resource Management (Quotas):** Implementing "Token-Bucket-as-a-Service" at the platform level to prevent a "Noisy Neighbor" from consuming the entire fleet's resources.
- **Tenant Migration & Rebalancing:** Orchestrating the "Move" of a tenant from one cell to another without a single dropped packet.

### 12.2 — Compliance & Data Governance (SDE-3 Exclusive)
*Moving beyond "Correctness" to "Legality & Trust."*

- **Global Data Sovereignty (GDPR/CCPA/LGPD):** Designing a system where EU data *physically* stays in the EU while allowing global search and analytics. Managing the "Right to be Forgotten" across 1PB of logs/backups.
- **Audit Trails as a Primitive:** Designing an immutable, append-only "Audit Log" (often using Kafka Compacted Topics) for every sensitive action—built as a core primitive, not an afterthought.
- **Encryption at Scale (KMS/HSM Orchestration):** Managing "Envelope Encryption" for millions of per-tenant keys. Handling "Key Rotation" with zero downtime.

### 12.3 — Control Plane vs. Data Plane Orchestration (SDE-3 Exclusive)
*Designing for "Static Stability."*

- **Data Plane Simplicity:** Ensuring that the "Hot Path" (request serving) stays simple and doesn't depend on the "Slow/Complex" Control Plane (e.g., config DB) to function.
- **Configuration Propagation at Scale:** Managing the 10-second "Propagation Delay" of a new feature flag or routing rule across 50,000 servers without causing a "Split-Brain" config state.
- **Self-Healing Control Planes:** Designing the control plane to detect and repair itself when it becomes inconsistent with the data plane's actual state.

### 12.4 — Observability Economics (Extension of SDE-2 12.1)
*In SDE-2, you ship logs. In SDE-3, you manage the "O11y Bill."*

- **Sampling Theory (Probabilistic Tracing):** Moving from "100% Trace Collection" (which is too expensive) to "Adaptive Sampling" that only collects traces for errors or slow requests.
- **Metrics Cardinality Management:** Preventing a "Metric Explosion" where one developer adds a `user_id` tag to a metric and doubles the monthly Prometheus bill.
- **Synthetic Monitoring & Global RUM:** Beyond "Server Metrics"—using "Real User Monitoring" (RUM) data from browsers to detect global internet-level routing failures that don't show up in your backend logs.
