An application that keeps its data in a list loses everything when it restarts. Replacing that list with a real database is the point of this material, and the first step is the connection itself — which turns out to be something already familiar wearing different clothes.

# Your server becomes a client

A web application asks your Spring Boot server for a list of products. Your server does not hold them; the database does. So a second exchange has to happen.

```mermaid
flowchart LR
    W["Web app"] -- "1. give me the products" --> S["Spring Boot app"]
    S -- "2. give me the products" --> D[("Database server")]
    D -. "3. rows" .-> S
    S -. "4. products" .-> W
```

In exchange 1 your application is the **server**. In exchange 2 it is the **client** — it makes a request, the database processes it and responds. Client and server as roles rather than identities, applied again.

Which means connecting to a database needs exactly what connecting to anything needs: a **socket address**, made of the protocol, the address, and the port.

# Plus credentials

Databases hold the valuable things, so they are almost always protected.

| What you need | Why |
|---|---|
| **Protocol** | Which set of rules to speak |
| **IP or host** | Which machine |
| **Port** | Which process on it |
| **Username** | Who is connecting |
| **Password** | Proof of it |

> [!info] **The username is near-universal even without a password.** A database server can assign different roles to different users, each with different privileges — one able to read only, another able to alter tables. The username is how it knows which set applies. A password may be absent on a local development instance; on anything shared it is not.

Some databases want more. **A managed cloud database may need a project identifier and an instance identifier alongside the rest, because those are how the provider locates it.** The shape varies; the idea does not.

> [!info] **On-premise and cloud work the same way.** A database you host yourself and one rented from a provider are both a database server reachable at an address. The configuration differs in its values, not its nature.

# Every database has its own protocol

There is no single database protocol. Each publishes its own, optimised for what it does:

| Database | Protocol |
|---|---|
| MySQL, MariaDB | MySQL client/server protocol |
| PostgreSQL | PostgreSQL protocol |
| Oracle | Its own |
| MongoDB | MongoDB wire protocol |
| Redis | Its own |
| Cassandra | CQL binary protocol |

Which is why connection strings differ in their prefix and agree on everything else:

```text
1  mysql://username:password@localhost:3306/mydb
2  postgresql://username:password@localhost:5432/mydb
3  mongodb://username:password@localhost:27017/mydb
```

Protocol, credentials, host, port, database name. Leave the port out and the default for that protocol is assumed — 3306 for MySQL, 27017 for MongoDB.

> [!info] **One database server can hold many databases.** The name at the end of the string selects which one, which is why it is part of the connection rather than something you choose later.

# A GUI client is a client too

A database GUI is worth a moment, because it makes the point concrete. Setting up a connection in one asks for a hostname, a port, a username and a password.

It does **not** ask for the protocol — because a MySQL-specific tool already knows it speaks MySQL. Everything else still has to be supplied, exactly as your application supplies it. **The tool is a client process connecting to a database server,** no different in kind from your code.

> [!info] You do not need to learn how these protocols work internally. What is worth your attention is how to use a database well — modelling the data, querying it efficiently, scaling it. The protocol is machinery underneath, and something else will speak it for you.

Which raises the question of what that something else is.
