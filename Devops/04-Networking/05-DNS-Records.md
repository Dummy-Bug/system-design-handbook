The previous note ended on a claim it did not cash: the authoritative name server holds more per domain than a single address. That extra content is the subject here, and it is where DNS stops being a lookup table you read about and becomes a thing you configure.

## What the authoritative server actually stores

Against one domain, the authoritative server holds a set of entries called **DNS records**. Each record is a different kind of fact about the domain, and each has a type that says which kind.

There are many types. As a DevOps engineer you need six:

| Type    | Holds                                                   |
| ------- | ------------------------------------------------------- |
| `A`     | The domain's IPv4 address                               |
| `AAAA`  | The domain's IPv6 address                               |
| `CNAME` | An alias — this name is really that other name          |
| `TXT`   | Arbitrary text, used mostly to prove you own the domain |
| `MX`    | Which mail server handles email for the domain          |
| `NS`    | Which name servers are authoritative for the domain     |

Every record, whatever its type, is written with the same three fields:

| Field | Means |
|---|---|
| **Type** | Which of the above this record is |
| **Name** | Which name within the domain this record is about |
| **Value** | The answer |

> [!tip] `@` in the name field means the domain itself.
> When a record applies to the bare domain rather than a name underneath it, you write `@` rather than spelling out `bookcart.in` again. The provider already knows which domain you are configuring, so repeating it in every row would be noise. `@` is the shorthand for the top of the domain, often called the apex or root.

## A and AAAA — name to address

The `A` record is the one doing the fundamental job. It maps a domain to an **IPv4** address.

| Type | Name | Value           |
| ---- | ---- | --------------- |
| `A`  | `@`  | `143.45.156.67` |

That single row is what makes `bookcart.in` resolvable. Read it back as a sentence: for the domain itself, the IPv4 address is `143.45.156.67`.

The `AAAA` record — spoken as **quad-A**, because it is four A's — holds exactly the same kind of fact for an **IPv6** address:

| Type | Name | Value |
|---|---|---|
| `AAAA` | `@` | `2001:db8::1` |

Two record types rather than one, for the reason set out earlier: both address versions are live, and they are different lengths in a different notation, so they cannot share a field. A domain reachable over both has both records. A domain that has never adopted IPv6 has only the `A`.

## Subdomains

The `name` field is what makes a domain more than one thing.

`bookcart.in` is the domain. `api.bookcart.in` is a **subdomain** — anything placed in front of the domain, separated by a dot. So is `admin.bookcart.in`, and `manager.bookcart.in`, and `blog.bookcart.in`.

Each one gets its own record, with its own value:

| Type | Name | Value |
|---|---|---|
| `A` | `@` | `143.45.156.67` |
| `A` | `api` | `143.45.156.34` |
| `A` | `admin` | `143.45.156.54` |

Three names, three different addresses, one domain. The lookup for `api.bookcart.in` finds the second row and returns `143.45.156.34`, **which may be a different machine entirely from the one the apex points at.**

> [!important] You do not buy subdomains. You buy one domain and create as many as you like.
> This trips people up constantly. There is one purchase and one annual fee, for `bookcart.in`. Everything in front of the dot is yours to invent, register in your own records, and point wherever you want, at no additional cost and with no additional transaction.

### Why you would want several

The typical reason is that one product is several applications, with different audiences.

A shop has a customer-facing site and an admin panel, and they are not the same application. Instagram is the easiest example to picture: there is the app every user runs, and there is a separate administrative interface that a small number of staff sign into, with rights no ordinary account has. Those are different codebases, often on different machines, and giving each its own subdomain keeps them cleanly apart:

| Subdomain | What is deployed there |
|---|---|
| `bookcart.in` | The customer-facing application |
| `api.bookcart.in` | The backend the applications call |
| `admin.bookcart.in` | The administrative interface |
| `manager.bookcart.in` | A middle tier with more rights than a user and fewer than an admin |

```mermaid
flowchart TD
    D["bookcart.in<br/>one domain, one purchase"] --> S1["bookcart.in<br/>→ 143.45.156.67"]
    D --> S2["api.bookcart.in<br/>→ 143.45.156.34"]
    D --> S3["admin.bookcart.in<br/>→ 143.45.156.54"]
    S1 --> M1["Customer application<br/>server 1"]
    S2 --> M2["Backend<br/>server 2"]
    S3 --> M3["Admin application<br/>server 3"]
    style D fill:#7a5a1f,color:#fff
    style S1 fill:#1f4f7a,color:#fff
    style S2 fill:#1f4f7a,color:#fff
    style S3 fill:#1f4f7a,color:#fff
    style M1 fill:#1f6f3f,color:#fff
    style M2 fill:#1f6f3f,color:#fff
    style M3 fill:#1f6f3f,color:#fff
```

Two facts sit behind that diagram, and they are worth stating separately because together they cover every arrangement you will meet. **One server can host multiple applications** — established earlier, and the reason ports exist. And **one application can be deployed across multiple servers**. Neither constrains the other, so subdomains on different machines, or several subdomains on one machine, are both perfectly ordinary.

> [!question] Ports do not complicate this.
> A question that comes up is how port mapping works across subdomains. It mostly does not need to: if the subdomains resolve to different addresses, they are different machines and each has its own ports to itself. Where two do share a machine, the reverse proxy in front of them is what tells them apart, exactly as before.

## CNAME — one name standing for another

Start with a correction that catches almost everybody:

> [!warning] `www.bookcart.in` is not the same thing as `bookcart.in`.
> They look interchangeable because browsers treat them that way, quietly adding or hiding the `www` as they please. In DNS they are simply two different names. `www` sits in front of the domain, separated by a dot, which by the definition above makes it a subdomain — no different in kind from `api` or `admin`. If nothing has been configured for it, it does not resolve, and a visitor who types it gets nothing.

The `CNAME` record fixes this. It creates an **alias**: a record saying this name is really that other name, go and look there instead.

| Type | Name | Value |
|---|---|---|
| `CNAME` | `www` | `bookcart.in` |

Now a lookup for `www.bookcart.in` is told to resolve `bookcart.in` instead, which has an `A` record, which yields the address:

```mermaid
flowchart LR
    W["www.bookcart.in"] -->|"CNAME says:<br/>really means"| APEX["bookcart.in"]
    APEX -->|"A record"| IP["143.45.156.67"]
    IP --> SRV["The server answers"]
    style W fill:#7a5a1f,color:#fff
    style APEX fill:#1f4f7a,color:#fff
    style IP fill:#1f4f7a,color:#fff
    style SRV fill:#1f6f3f,color:#fff
```

### The more useful case — pointing at a service you do not run

Aliasing `www` to the apex is the obvious use. The one that earns `CNAME` its place is pointing a name you own at a service somebody else runs.

Suppose the blog is not something you host. It is a space on a third-party platform — GitHub Pages, say — sitting on their servers, served from whatever machines they happen to be using this month. You want a visitor to reach it at `blog.bookcart.in` rather than at the platform's own address, `bookcart.github.io`.

You already have a record type that points a name at a machine, so the obvious move is to use it. Nothing stops you from looking up the platform's current address, finding something like `143.45.156.90`, and writing it down as your own record:

| Type | Name | Value |
|---|---|---|
| `A` | `blog` | `143.45.156.90` |

That works. Today.

> [!failure] What you have just done is copy down a fact about somebody else's infrastructure.
> That address belongs to the platform, not to you. You have no say in it, no claim on it, and no way to be told when it changes — and it will change, because platforms migrate, add capacity and move between providers as a matter of routine. The day they retire that machine, they update their own records, every other customer follows along automatically, and you do not. Your blog goes dark, nothing in your own records looks wrong, and the first you hear about it is a visitor telling you the site is down.

What you can do instead is store their **name** rather than their **address**:

| Type | Name | Value |
|---|---|---|
| `CNAME` | `blog` | `bookcart.github.io` |

Now the lookup takes two steps instead of one, and the point of the whole arrangement is which party holds which fact:

```mermaid
flowchart TD
    Q["Resolver asks<br/>where is blog.bookcart.in?"] --> CN
    subgraph YOURS["Your records"]
        CN["CNAME: blog is really bookcart.github.io<br/>which platform hosts the blog — a fact you know"]
    end
    CN -->|"so resolve that name instead"| AR
    subgraph THEIRS["The platform's records"]
        AR["A: bookcart.github.io<br/>which machine is serving it today — a fact they know"]
    end
    AR --> IP["143.45.156.90<br/>handed to the browser"]
    style Q fill:#2d333b,color:#fff
    style CN fill:#7a5a1f,color:#fff
    style AR fill:#1f4f7a,color:#fff
    style IP fill:#1f6f3f,color:#fff
```

Each side stores only what it is actually in a position to know. You know which platform your blog lives on, and that changes when you decide it changes. They know which machine is answering this week, and that changes on their schedule without involving you. When the platform moves, the bottom record changes, the top one was never about an address in the first place, and nothing on your side is touched.

| | Writing their address as an `A` record | Writing their name as a `CNAME` |
|---|---|---|
| What you store | A copy of the platform's IP address | The platform's hostname |
| Who that fact really belongs to | Them, while you hold a stale duplicate | Them, and you point at the original |
| When they move servers | Your record is now wrong, and wrong silently | Nothing on your side changes |
| What you have to monitor | Their infrastructure, forever | Nothing |

That indirection is the whole value of the record type, and it is the same trick as the name-to-address mapping itself, applied one level up: you stopped hard-coding a value you do not control and started referring to it by name.

> [!important] Nobody is redirected anywhere. This is not an HTTP redirect.
> A `CNAME` is resolved inside DNS, before any connection is opened. No response comes back with a `301`, nothing bounces the browser to a different site, and the address bar keeps saying `blog.bookcart.in` for the entire visit. The resolver simply performs a second lookup and hands the browser one final address, and the visitor sees none of it. This is also what separates it from a reverse proxy, which sits in the traffic path and carries every packet — a `CNAME` is consulted once during resolution and then plays no further part.

## TXT — proving the domain is yours

A `TXT` record holds arbitrary text, with no format imposed on what goes in it. **Its dominant use is verification**, and the reason that works is worth building up rather than asserting, because on the face of it a line of text is a strange thing to accept as proof of anything.

### The problem it solves

You go to a service that will act on your domain's behalf — a workspace and mail suite, an analytics product, an identity provider — and you tell it that `bookcart.in` is yours.

The service now has to decide whether to believe you, and it has nothing to go on. You typed a name into a form. If that is enough, then it is enough for anybody: a stranger can type `bookcart.in` into the same form and, depending on the service, end up receiving mail sent to your domain, signing people in as your identity provider, or reading your traffic figures. **A domain that can be claimed by anybody who types it is not owned in any meaningful sense.**

So the service needs a test that only the real owner can pass, and it needs one that does not depend on trusting anything you say.

### Why a DNS record is that test

Ask who is physically capable of making a record appear for `bookcart.in`, and the answer is a chain with exactly one entrance:

```mermaid
flowchart TD
    OWN["The registrar account that bought bookcart.in"] -->|"is the only thing that can set"| DEL["Which name servers are authoritative for the domain"]
    DEL -->|"which are the only servers that can publish"| REC["Any record at all under bookcart.in"]
    REC -->|"therefore"| PROOF["A string found in bookcart.in's records<br/>could only have been put there by the owner"]
    style OWN fill:#1f4f7a,color:#fff
    style DEL fill:#1f4f7a,color:#fff
    style REC fill:#1f4f7a,color:#fff
    style PROOF fill:#1f6f3f,color:#fff
```

That chain is the entire argument. **The ability to make an arbitrary string appear in a domain's DNS answers is itself the proof of ownership**, because that ability sits downstream of owning the domain and there is no other way to reach it. Nobody has to take your word for anything — the record could not exist unless you were who you said you were.

### Why this record type and not another

Every other record type has a fixed shape, and none of them has anywhere to put a verification string:

| Record | What its value is allowed to be |
|---|---|
| `A` | An IPv4 address, and nothing else |
| `AAAA` | An IPv6 address, and nothing else |
| `CNAME` | Another domain name |
| `MX` | A mail host and a priority number |
| `TXT` | Any text at all |

`TXT` is the only one with a free-form value, which is why it became the general-purpose slot for machine-readable facts about a domain. **Verification tokens live there because there was nowhere else to put them, not because `TXT` means verification.**

### What actually happens

The service hands you a string, you publish it, and the service goes and looks:

| Type | Name | Value |
|---|---|---|
| `TXT` | `@` | `google-site-verification=xyz123abc` |

```mermaid
sequenceDiagram
    participant Y as You
    participant S as The service
    participant D as Your domain's records
    Y->>S: bookcart.in is mine
    S->>Y: then publish this exact string
    Y->>D: TXT @ google-site-verification=xyz123abc
    S->>D: what TXT records does bookcart.in have?
    D->>S: google-site-verification=xyz123abc
    Note over S: that is the string it issued, so the claim holds
```

> [!important] The string has to be random, and unique to your request.
> A fixed value would prove nothing. If every customer published the same text, you could pass verification for a domain you had never touched simply by pointing at the text somebody else had already published on it. Because the string is generated for you at the moment you make the claim, and is not guessable, finding it under `bookcart.in` proves that the person who made the claim is the person who can write records there. Those two being the same person is the whole thing being tested.

You can usually delete the record once verification passes. Services often ask you to leave it, because most re-check periodically rather than once — and if the string has gone when they look again, the service concludes the domain is no longer yours and may drop the integration. It costs nothing to leave in place, so leave it.

> [!question] Why not just ask you to upload a file to the website instead?
> Some services offer that as an alternative, and it proves something weaker. It requires the site to already be running, so it cannot be done before anything is deployed; it proves control of the web server rather than of the domain, which are not always the same party; and it is useless for mail, which has no website to upload anything to. A DNS record covers every one of those cases, which is why it is the method that works everywhere.

Nothing about `TXT` is specific to any one vendor. Google Workspace verification works this way, Microsoft's does too, and so does Google Analytics — each hands you a different string for the same record type, and each then checks that it appears.

> [!tip] Verification is not the only thing living in `TXT` records.
> The records that say which mail servers are permitted to send messages claiming to be from your domain — `SPF`, `DKIM` and `DMARC` — are all `TXT` records as well, and they are there for exactly the same reason: the value they need to hold is free-form text, and this is the only type that allows it. If you ever look at the raw records of an established domain, most of the clutter you find will be these.

## MX — where the mail goes

Owning a domain also gives you the ability to have email addresses at it. Instead of a generic mailbox somewhere, the shop can have `orders@bookcart.in` and `support@bookcart.in`.

That requires somebody to actually run the mail infrastructure, and the `MX` record — for **mail exchange** — is where you name them:

| Type | Name | Value |
|---|---|---|
| `MX` | `@` | `10 mail.someprovider.com` |

When a mail server anywhere in the world has a message for an address at your domain, it looks up your `MX` record to find out where to deliver it. Running mail infrastructure is a specialised job and generally not one you take on; the record simply points at whoever does.

## NS — which server is authoritative

The last record type is the one that makes the others findable, and it is the only one that does not live where the others do.

The `NS` record — for **name server** — answers the question: which DNS servers are authoritative for this domain? Its value is the names of those servers:

| Type | Name | Value |
|---|---|---|
| `NS` | `@` | `ns1.dnsprovider.com` |
| `NS` | `@` | `ns2.dnsprovider.com` |

Two are typical, so that one being unreachable does not take the domain down.

If your records are hosted on a cloud provider's DNS service, these are that provider's name server names. If you use a CDN and DNS provider such as Cloudflare, they are Cloudflare's. The names change; the role does not.

## Where each record has to be written

This is the part people get wrong, and the confusion is the registrar-versus-authoritative split from the previous note showing up as a practical question.

```mermaid
flowchart TD
    subgraph REG["The registrar — where the name was bought"]
        NS["NS records<br/>naming the authoritative servers"]
    end
    subgraph HOST["The DNS host — where records are served from"]
        REST["A · AAAA · CNAME · TXT · MX<br/>the actual content"]
    end
    LOOKUP["A lookup arrives"] --> REG
    REG -->|"redirects the lookup to"| HOST
    HOST --> ANSWER["Returns the answer"]
    style LOOKUP fill:#2d333b,color:#fff
    style NS fill:#7a5a1f,color:#fff
    style REST fill:#1f4f7a,color:#fff
    style ANSWER fill:#1f6f3f,color:#fff
```

> **`NS` records go at the registrar.** That is where a lookup arrives first, because the **registrar** is what the **TLD knows about**. Its job is to say: the content for this domain is not here, it is over there.

**Everything else goes at the DNS host** — the provider actually serving your records, which is usually wherever the application is **deployed**. `A`, `AAAA`, `CNAME`, `TXT` and `MX` all live there.

So the common setup, end to end: buy the name from a registrar, deploy the application on a cloud provider, host the DNS records with that provider, and then go back to the registrar once to set the `NS` records pointing at it. After that single step, every future record change happens at the provider and the registrar is never touched again.

> [!question] Which address does a visitor to the bare domain actually get?
> Whatever the apex `A` record points at — which in the layout above is the customer-facing application, since that is what receives the first call. The backend is reached separately, at `api.bookcart.in`, because a record was written for it. If you want a machine to be reachable by name, it needs a record; there is no automatic exposure.

> [!note] The customer-facing tier goes by two names, which is worth knowing before somebody uses the other one.
> It is commonly called the frontend. In backend-side conversation the same tier is often called the middleware, on the grounds that it sits between the user and the real backend rather than being an endpoint in itself. Both words describe the thing the apex record points at, and nothing changes depending on which one is used.

## Reading records back

You do not have to take a provider's dashboard at its word. Every record type above is publicly queryable, and `nslookup` is on your machine already:

```bash
# run from any terminal — reading the DNS records of a domain
nslookup -type=A     example.com     # the IPv4 address
nslookup -type=AAAA  example.com     # the IPv6 address
nslookup -type=NS    example.com     # which servers are authoritative
nslookup -type=MX    example.com     # where mail for the domain goes
nslookup -type=TXT   example.com     # verification strings and similar
nslookup -type=CNAME example.com     # any alias on this name
```

Running the `NS` query against a large site returns its name servers directly, which is the quickest way to see the registrar-to-host redirection actually working rather than taking it on trust. Running the `CNAME` query against a bare domain usually returns nothing, and that is correct rather than a failure — an apex normally has an `A` record rather than an alias.
