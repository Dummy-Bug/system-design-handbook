Tests tell you the code was right before it shipped. Observability is how you find out what it actually does afterwards, under real traffic — and the first pass at it leaned on a managed service that did the collecting for you. This folder is about running that machinery yourself, starting with the standard that makes it possible to swap any piece of it out later.

# One agent per vendor

Before there was a standard, every observability product came with its own way in. New Relic had an agent, Datadog had a different one, Splunk had another, and each carried its own configuration format, its own set of libraries and its own idea of what the data should look like.

That is tolerable while you only use one. It stops being tolerable the moment you want to change.

```mermaid
flowchart LR
    APP["Your application"]
    APP -->|New Relic agent + config| NR["New Relic"]
    APP -->|Datadog agent + config| DD["Datadog"]
    APP -->|Splunk agent + config| SP["Splunk"]
```

Moving from one to another is not a matter of changing a hostname. The agent is ripped out and a different one installed, the configuration is rewritten, and anywhere the application talks to the observability layer directly, that code changes too. The cost of switching is paid in engineering time, which means in practice the choice made on day one tends to stick long after it stopped being the right one.

# What OpenTelemetry is

OpenTelemetry is an open-source observability framework, and it is abbreviated as **OTel**. What it contributes is **vendor neutrality**: a single common way to produce and move observability data, which every compliant tool on the receiving end understands.

```mermaid
flowchart LR
    APP["Your application"] -->|one standard way out| OTEL["OpenTelemetry"]
    OTEL --> NR["New Relic"]
    OTEL --> DD["Datadog"]
    OTEL --> PR["Prometheus"]
    OTEL --> ES["Elasticsearch"]
```

The application is instrumented once. Where the data ends up becomes a configuration decision rather than a rewrite, and switching backends stops being a project.

# The three pillars

OTel defines three kinds of data, and everything it does is in service of carrying these three.

| Pillar | What it is | Examples |
|---|---|---|
| **Logs** | Statements recording discrete events as they happen | A request arrived, a lookup failed, a value was cached |
| **Metrics** | Numerical values collected over a period of time | CPU usage, requests per second, memory consumption, latency, error rate |
| **Traces** | The journey of one single request through the system | This request entered at the gateway, called two services, spent 40 ms in the database |

Logs and metrics are already familiar. A **trace** is the one worth pausing on: it follows a single request from the moment it arrives to the moment it is answered, across every service it touches on the way. In a single application that is mildly useful. In a system split across several services it is often the only way to answer where the time went, because no individual service can see the whole path.

```mermaid
flowchart LR
    REQ["One request"] --> GW
    subgraph TRACE["One trace — every step, stitched together"]
        direction LR
        GW["Gateway"] --> SVC["Order service"] --> DB[("Database")]
    end
```

# The three layers, and which one OTel owns

Splitting the problem into layers makes it clear what the standard is actually for.

```mermaid
flowchart TB
    S["Semantic layer
    what data to collect
    your application, your server"]
    P["Protocol layer — this is OpenTelemetry
    how it is shaped and moved"]
    ST["Storage layer
    where it lands"]
    S -->|emits| P -->|writes to| ST
    style P fill:#1b4332,color:#ffffff,stroke:#40916c,stroke-width:2px
```

**The semantic layer** is where data originates — your application deciding what is worth recording.

**The protocol layer** is the transport: what shape the data takes and how it travels.

**The storage layer** is where it is kept, and it is usually more than one place. Metrics go to a time-series database such as Prometheus; logs go somewhere searchable such as Elasticsearch or OpenSearch.

**OTel concerns itself with the middle layer only.** This boundary is worth stating plainly, because it explains what the standard will and will not do for you.

> [!info] **Guarantees:** that telemetry leaving your application has a defined shape and a defined way of travelling, so any compliant backend can receive it. **Does not guarantee:** what you choose to record, where you send it, how long it is kept, or what you do with it once it arrives. Those decisions stay yours.

# The same idea, elsewhere

The shape of the problem is not unique to observability, and it may be easier to recognise in a setting where the same fix was applied.

**A language model with agentic capabilities** — meaning it can use tools and carry out tasks rather than only answering — has to talk to software outside its own ecosystem. Google Suite, meaning Gmail and Calendar. Slack, a messaging tool. Discord. AWS. Some weather service. Every one of those exposes its own set of APIs, designed with no thought at all for the model that wants to call it.

**The reason they are not designed for it is incentives, not oversight.** Google has no reason to care how somebody else's model connects to Google Suite. Slack has no reason to care either. A vendor invests in that integration when the model is their own — which is why **Gemini has a strong integration with Google Suite out of the box and a much weaker one with Slack.** Not because Slack is harder, but because Slack is a different company with a different set of APIs, and nobody on either side was paid to bridge them.

Now multiply that. There are millions of such tools. You cannot configure a model to speak to Slack one way, Discord another way, Google Suite a third way, AWS a fourth, a weather app a fifth, and keep doing that forever.

The **Model Context Protocol** solves that by inverting the burden. Rather than the caller learning every tool, each tool exposes itself through one common protocol, and the caller only has to speak that.

```mermaid
flowchart LR
    subgraph WITHOUT["Without a common protocol"]
        L1["Caller"] --> A1["Tool A API"]
        L1 --> B1["Tool B API"]
        L1 --> C1["Tool C API"]
    end
    subgraph WITH["With one"]
        L2["Caller"] --> PROTO["Protocol"]
        PROTO --> A2["Tool A"]
        PROTO --> B2["Tool B"]
        PROTO --> C2["Tool C"]
    end
```

OTel is that same move for telemetry. Data may be produced in Java, Python or C#. It may be destined for a time-series database, a log store, or a paid service run by someone else — and those destinations are maintained by entirely separate organisations. New Relic is one company, Datadog is another, and a great many of the open-source tools have nothing to do with either.

Make it concrete. **You have a Python application writing metrics into Prometheus, and you decide to move to New Relic.** Without a common standard, that migration means finding every place the application talks to Prometheus and rewriting it against a different vendor's client. With one, the application keeps emitting exactly what it emitted before and the destination changes in configuration.

What makes that possible is a middleman. It says to the application: do not worry where this is going, just hand it to me according to my receivers. And it says to the storage: do not worry where this came from, it will be prepared according to my exporters. In between, it does whatever processing the two ends need.

# The collector

That middleman has a name. The **OpenTelemetry Collector** is a vendor-agnostic proxy that sits between the application and the storage, and it has three parts.

```mermaid
flowchart LR
    APP["Application"] --> R["Receiver
    how data is taken in"]
    R --> P["Processor
    filter, batch, enrich"]
    P --> E["Exporter
    how data is written out"]
    E --> PROM["Prometheus"]
    E --> ES["Elasticsearch"]
```

**The receiver** knows how to accept data from the client. **The processor** does whatever work happens in between — aggregating, filtering, reshaping. **The exporter** knows how to write into a particular storage backend.

Named concretely, receivers and exporters are things like OTLP, Jaeger, Prometheus and OpenSearch — and the same protocol can sit on both sides, since a collector is free to accept OTLP and forward OTLP onward.

![[Backend Engineering/19-Self-Hosted-Observability/Images/otel-collector-pipeline.png]]

**The collector is optional**. Data can be sent straight to a backend that is capable of receiving it, and the collector earns its place when you want aggregation or filtering to happen outside the application.

In practice you rarely assemble these parts by hand. Tools built on top of OTel — the stacks in the notes that follow — already have them wired up.

# OTLP, the wire protocol

The protocol itself is **OTLP**, the OpenTelemetry Protocol. It is what makes the standard concrete: it specifies both how the data is carried and how it is encoded.

| Concern         | What OTLP specifies                                                                  |
| --------------- | ------------------------------------------------------------------------------------ |
| What it carries | The three pillars: traces, metrics, logs                                             |
| Transport       | gRPC by default, which runs on HTTP/2 and allows multiplexed, persistent connections |
| Encoding        | Protocol Buffers, or JSON                                                            |

The reason for the choice is throughput. **Shipping telemetry means a constant stream of network calls, so a persistent connection that carries many messages at once beats opening a new one each time.**

This is internal machinery. Once a stack is integrated you see dashboards and search results rather than protocol buffers, and the only reason to know it is there is to understand what is being agreed on when a tool advertises itself as OTel-compliant.

> [!info] The pieces have distinct roles that are easy to blur together. The **API** is what instrumented code calls to emit data. The **SDK** implements that API and configures how data is collected and exported. The **collector** is the optional proxy in between. The **protocol** is OTLP, the agreement about the wire.
