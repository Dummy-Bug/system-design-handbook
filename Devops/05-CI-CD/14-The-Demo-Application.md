The server is ready — Jenkins has its tools, the application has a directory to live in, and Jenkins is allowed to write there. What it still has nothing to do with is an application. This note is that application: small on purpose, because the point is to watch it go through a pipeline, not to study the code.

## Why the code barely matters here

A pipeline does not care what the application does. It cares that the code builds, that the tests pass, that a package is produced and that the package runs on the server. So the application is written in advance and kept deliberately simple, and the interesting part is everything that happens to it afterwards.

It is a small calculator service in **Spring Boot**, built with **Maven**, the same shape as the calculator from earlier in this folder but now served over HTTP.

## What it does

It exposes two endpoints — two addresses you can send a request to:

| Endpoint | What it returns |
|---|---|
| `/health` | That the service is up: its status, the service's name, and the version of the application currently running |
| `/api/add?a=10&b=5` | The sum of the two numbers passed as `a` and `b`, after checking that both actually are numbers |

**The health endpoint is for machines, not users.** Nobody visits it to do anything; it exists so that something else — a monitoring system, a load balancer, a pipeline — can ask whether the service is alive and get a quick, definite answer. It reports only that: whether the service is running, not whether every feature in it is correct.

Behind the endpoints is a small class holding the actual arithmetic, with three operations:

| Operation | What it does |
|---|---|
| `add` | Adds two numbers |
| `subtract` | Subtracts one from the other |
| `calculateDiscount` | Takes a price and a discount percentage and returns the discounted price |

Only `add` is wired to an endpoint so far. The others exist to be tested, and adding `/api/subtract` or a discount endpoint later would follow exactly the same pattern.

## The tests

There are two groups of tests, and the split between them is the point.

**Tests of the arithmetic itself** — calling the operations directly, with no web server involved:

| Test | Input | Expected |
|---|---|---|
| Addition | 2 and 3 | 5 |
| Subtraction | 10 minus 4 | 6 |
| Discount | 10% off a price of 1000 | 900 |
| An invalid discount is rejected | 120% off 1000 | An error — a discount must be less than 100% |

**Tests of the endpoints** — sending real requests to the running application and checking the responses:

| Test | What is checked |
|---|---|
| Health check | The response code is `200`, meaning success, and the body reports the status as up |
| Addition endpoint calculates correctly | The response code is `200` and the result is `42` |
| Addition endpoint rejects bad input | Passing text such as `hello` instead of a number is refused rather than crashing or returning nonsense |

> [!note] The two groups catch different mistakes.
> The first group proves the business logic is right — that 10% off 1000 really is 900. The second proves that logic is reachable and behaves properly over the web — that the endpoint reads its parameters, calls the right method, returns the right status code and refuses input it should refuse. An application can pass every test in the first group and still be broken in a way only the second group sees.

The invalid-discount test deserves a word, because it is the one developers forget to write. Checking that correct input gives correct output is natural. Checking that **nonsensical input is refused** — a discount of more than 100%, which would produce a negative price — is where a large share of real defects live, and a test for it costs one line.

## Linting

The project also carries a **linter configuration**: rules that are checked against the source without running it, for problems such as a variable that is declared and never used, or a method that is written and never called. In a Maven project this is done with PMD, run through Maven, whose default rules include exactly those two checks.

Neither is an error the compiler cares about. Both are a sign that something was left half-finished, and a pipeline that runs the linter refuses to carry such code any further.

## Its port

Spring Boot listens on `8080` by default — the same port Jenkins is already using on this server. So this application is set to `8081`, with one line in its `application.properties`:

```properties
# src/main/resources/application.properties
server.port=8081
```

This is the rule from the installation note applied: the application moves, the tool does not.

## Run it locally before anything else

Before any of this goes near a pipeline, the application is run and checked on the developer's own machine. That is the ordinary order of work for any developer:

```mermaid
flowchart LR
    W["Write the application"] --> L["Run it and test it locally"]
    L --> P["Only then hand it<br/>to a pipeline"]
    style W fill:#2d333b,color:#fff
    style L fill:#1f4f7a,color:#fff
    style P fill:#1f6f3f,color:#fff
```

The tests run through the project's Maven wrapper, and all of them pass:

```bash
# in the project directory, on the developer's machine
./mvnw test
```

Then the application is started and exercised by hand. A request to `http://localhost:8081/api/add?a=10&b=5` returns **15**. Changing `b` to 50 returns **60**. The health endpoint reports the service as up.

> [!important] A pipeline is not a substitute for running it yourself first.
> The pipeline runs the same tests you could have run, on a machine you have to wait for, and reports back minutes later. Finding a failure there that a thirty-second local run would have shown is a slow way to learn something you could have known immediately. The pipeline is the guarantee that nothing broken gets through; running it locally first is what keeps you from spending the pipeline's time finding your mistakes for you.
