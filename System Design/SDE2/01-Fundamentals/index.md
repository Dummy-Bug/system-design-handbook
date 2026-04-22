---
title: Core Concepts
hide:
  - navigation
  - toc
---

<div class="cs-level-hero cs-lv-concepts">
  <div class="cs-level-bg-num">02</div>
  <div class="cs-level-inner">
    <p class="cs-level-eyebrow">Concepts</p>
    <h1 class="cs-level-title">Core Concepts</h1>
    <p class="cs-level-sub">The vocabulary of distributed systems. Every architecture decision traces back to one of these.</p>
  </div>
</div>

<div class="cs-cards">

  <a class="cs-card" href="01-Performance-Metrics/00-Overview/">
    <div class="cs-card-title">Performance Metrics</div>
    <div class="cs-card-desc">Latency, throughput, bandwidth, and percentiles — the four measurements that appear in every design discussion.</div>
    <div class="cs-topics">
      <span>Latency</span><span>Throughput</span><span>Bandwidth</span><span>P99</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="02-Service-Levels/00-Overview/">
    <div class="cs-card-title">Service Levels</div>
    <div class="cs-card-desc">SLIs, SLOs, SLAs, and error budgets. How you define and commit to system behavior — and what happens when you breach it.</div>
    <div class="cs-topics">
      <span>SLI</span><span>SLO</span><span>SLA</span><span>Error Budget</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="03-Availability/00-Overview/">
    <div class="cs-card-title">Availability</div>
    <div class="cs-card-desc">SPOF, redundancy, nines, active-active vs active-passive. What "highly available" actually requires you to build.</div>
    <div class="cs-topics">
      <span>SPOF</span><span>Redundancy</span><span>Nines</span><span>Active-Active</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="04-Reliability/00-Overview/">
    <div class="cs-card-title">Reliability</div>
    <div class="cs-card-desc">MTBF, MTTR, RTO, RPO. The difference between a system that rarely fails and one that recovers fast when it does.</div>
    <div class="cs-topics">
      <span>MTBF</span><span>MTTR</span><span>RTO</span><span>RPO</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="05-Scalability/00-Overview/">
    <div class="cs-card-title">Scalability</div>
    <div class="cs-card-desc">Horizontal vs vertical scaling, load balancing at L4 and L7, auto-scaling, and connection draining. How systems grow without breaking.</div>
    <div class="cs-topics">
      <span>Load Balancing</span><span>L4 / L7</span><span>Auto-Scaling</span><span>Cold Start</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="06-Fault-Tolerance/00-Overview/">
    <div class="cs-card-title">Fault Tolerance</div>
    <div class="cs-card-desc">Graceful degradation, bulkheads, circuit breakers, retries with backoff. How systems survive partial failure without cascading.</div>
    <div class="cs-topics">
      <span>Circuit Breaker</span><span>Bulkhead</span><span>Retry</span><span>Backoff</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="07-Durability/00-Overview/">
    <div class="cs-card-title">Durability</div>
    <div class="cs-card-desc">WAL, replication, and backups. The mechanisms that ensure data survives node failure, crash, or disaster.</div>
    <div class="cs-topics">
      <span>WAL</span><span>Replication</span><span>Backups</span><span>Crash Recovery</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="08-Concurrency-Locking/00-Overview/">
    <div class="cs-card-title">Concurrency & Locking</div>
    <div class="cs-card-desc">Race conditions, pessimistic and optimistic locking, MVCC, and distributed locks. How systems handle parallel writes without corruption.</div>
    <div class="cs-topics">
      <span>Optimistic Locking</span><span>MVCC</span><span>Distributed Lock</span><span>Idempotency</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="09-Consistency-Models/00-Overview/">
    <div class="cs-card-title">Consistency Models</div>
    <div class="cs-card-desc">Strong, eventual, causal, and monotonic. What "up to date" means in a distributed system and when each model is the right call.</div>
    <div class="cs-topics">
      <span>Strong Consistency</span><span>Eventual</span><span>Causal</span><span>Monotonic</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="10-Network-Partitions/00-Overview/">
    <div class="cs-card-title">Network Partitions</div>
    <div class="cs-card-desc">What happens when nodes can't talk. Split brain, quorum decisions, and why partition handling defines your entire consistency strategy.</div>
    <div class="cs-topics">
      <span>Split Brain</span><span>Quorum</span><span>Fencing</span><span>Partition Recovery</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="11-CAP-Theorem/00-Overview/">
    <div class="cs-card-title">CAP Theorem</div>
    <div class="cs-card-desc">Consistency vs availability when a partition happens. CP vs AP — and why every distributed system is forced to choose during a split.</div>
    <div class="cs-topics">
      <span>CAP</span><span>CP Systems</span><span>AP Systems</span><span>Partition Tolerance</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="12-PACELC/00-Overview/">
    <div class="cs-card-title">PACELC</div>
    <div class="cs-card-desc">Extends CAP to cover normal operation. Even without a partition, you still trade latency against consistency — PACELC names that tradeoff.</div>
    <div class="cs-topics">
      <span>PACELC</span><span>Latency vs Consistency</span><span>PA/EL</span><span>PC/EC</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="13-Security/00-Overview/">
    <div class="cs-card-title">Security</div>
    <div class="cs-card-desc">Auth, JWT, encryption at rest and in transit. The security primitives that belong in every system design, not just the ones marked "sensitive."</div>
    <div class="cs-topics">
      <span>JWT</span><span>OAuth</span><span>Encryption</span><span>TLS</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="14-State-Machines/00-Overview/">
    <div class="cs-card-title">State Machines</div>
    <div class="cs-card-desc">Modeling order flows, workflows, and status transitions as explicit states. The pattern that makes async systems auditable and debuggable.</div>
    <div class="cs-topics">
      <span>State Transitions</span><span>DB Implementation</span><span>Audit Trail</span><span>Timeout Events</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

  <a class="cs-card" href="15-NFRs/00-Overview/">
    <div class="cs-card-title">NFRs</div>
    <div class="cs-card-desc">Non-functional requirements: the hidden constraints that shape every architecture decision before you draw a single box.</div>
    <div class="cs-topics">
      <span>Scalability NFRs</span><span>Availability NFRs</span><span>Conflicting NFRs</span><span>Design Decisions</span>
    </div>
    <div class="cs-card-cta">Open topic <span>→</span></div>
  </a>

</div>
