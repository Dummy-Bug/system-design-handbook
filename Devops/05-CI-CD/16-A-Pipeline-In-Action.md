Everything is now in place separately — Jenkins on a server with its tools configured, a directory it may deploy into, an application that passes its tests, and a `Jenkinsfile` describing the pipeline. None of it is connected yet. This note connects the repository to Jenkins and follows what happens as code is pushed: a first deploy that quietly does not deploy, a feature branch that fails, a fix, a merge, and a live application that changed without anybody logging into the server.

## Getting the code into a repository

Jenkins builds what is in a repository, so the application has to be in one. The sequence is the ordinary one for publishing a local project, covered in detail in [[../03-Git/03-Working-With-A-Remote-Repository|working with a remote repository]]:

1. Initialise Git in the project directory and commit everything — the source, the tests, `pom.xml` and the `Jenkinsfile`.
2. Create an **empty** repository on GitHub, with nothing in it.
3. Connect the local repository to that remote one.
4. Push.

```bash
# in the project directory, on the developer's machine
git init
git add .
git commit -m "Add calculator service"
git remote add origin https://github.com/bookcart/calculator-service.git
git push -u origin master
```

> [!question] How can there be a master branch to push, when the GitHub repository was just created empty?
> Because the branch was created locally, not on GitHub. `git init` made a local repository, and the first commit created its first branch there. The GitHub repository really was empty — it was only connected afterwards, with `git remote add`, and the push is what copied the local branch up to it. The order is local first, then connect, then push, and the empty remote simply receives what the local side already had.

Note the name of that branch. **Unless Git has been configured otherwise, `git init` names the first branch `master`.** Many teams and many tools now expect `main`. Whichever your repository uses, it has to agree with the branch name in the `Jenkinsfile` — and that is about to matter.

## Pointing Jenkins at the repository

The pipeline type used here is a **Multibranch Pipeline**. Rather than a pipeline tied to one branch, it watches a whole repository, **discovers every branch that contains a `Jenkinsfile`**, and runs a separate pipeline for each one. A new branch pushed tomorrow gets its own pipeline automatically, without anybody configuring it.

Creating one:

1. On the dashboard, **New Item**.
2. Give it a name — the repository's name is the natural choice — and choose **Multibranch Pipeline**.
3. Under **Branch Sources**, add the Git source and enter the repository's address, with **Discover branches** enabled so it finds them all.
4. Under **Scan Multibranch Pipeline Triggers**, tick **Periodically if not otherwise run** and choose an interval.
5. Save.

### How Jenkins notices a push

That last setting deserves understanding, because it decides how quickly anything happens.

There are two ways one system can learn that something changed in another, and the distinction turns up well beyond this subject:

| | Pull | Push |
|---|---|---|
| How it works | Jenkins asks the repository at a fixed interval whether anything is new | The repository tells Jenkins the moment something is pushed |
| Delay | Up to one interval | Near-immediate |
| What it needs | Nothing beyond the scan setting | A **webhook** — the repository calling an address on the Jenkins server |
| Set up here | Yes | No |

This setup pulls. Every interval, Jenkins scans the repository, and any branch with new commits gets a new build.

**The interval is a trade.** In production it is set to something like an hour or two, or even a day: scanning more often makes Jenkins keep asking about repositories that have not changed. For a demonstration it is set to **one minute**, which is the smallest the setting allows — deliberately, aggressively short, so that the effect of a push is visible almost immediately. Nobody runs it that low for real.

And a build can always be started by hand: every pipeline has a **Build Now** button, which runs it immediately regardless of the schedule. In production, builds are normally left to start themselves.

## The first run, and the deploy that did not happen

After saving, Jenkins scans the repository and finds one branch, `master`, containing a `Jenkinsfile`. It starts that branch's **build #1**.

Clicking into the build and opening **Console Output** shows everything it did, line by line and in order — fetching the code, then each stage of the `Jenkinsfile` with its commands and their output. This log is where you go first whenever anything fails.

This first run passed checkout, lint, tests and packaging. And then it skipped deploy, and skipped the smoke test.

Nothing had failed. The pipeline did exactly what it was told. The `Jenkinsfile` says to deploy only when the branch is `main`:

```groovy
when {
    branch 'main'
}
```

The branch being built is `master`. The condition was false, so the stage was skipped — correctly, silently, and with the pipeline marked as a success.

```mermaid
flowchart LR
    B["Branch being built:<br/>master"] --> W{"when branch 'main'"}
    W -->|"no match"| SKIP["Deploy skipped<br/>Smoke test skipped<br/>pipeline still green"]
    style B fill:#2d333b,color:#fff
    style W fill:#7a5a1f,color:#fff
    style SKIP fill:#7a1f1f,color:#fff
```

> [!failure] A skipped stage is not a failed stage, and that is what makes this easy to miss.
> The pipeline reports success, because nothing it attempted went wrong. What it did not attempt, it does not complain about. So a condition naming the wrong branch produces a pipeline that is green on every run and has never deployed anything — and the only way to see it is to look at which stages actually ran, not merely at the colour of the result.

The fix is one word. The `Jenkinsfile` is changed to name the branch that actually exists — `branch 'master'` — committed with a message saying so, and pushed. Within a minute, the scan picks up the new commit and starts a build, and this time every stage runs: lint, tests, package, **deploy**, **smoke test**. Pipeline successful.

## Proof that it deployed

The proof is not in Jenkins — it is on the server. A browser pointed at the server's address and the application's port, `http://192.168.64.2:8081/health`, gets an answer: the service is up. And `http://192.168.64.2:8081/api/add?a=10&b=20` returns **30**.

**Nobody copied a file to the server, nobody restarted anything by hand.** A push to a branch was the whole of the developer's involvement, and the application on the server is now running that code — the deploy stage copied the new jar, pointed `current.jar` at it and had `systemd` restart the service.

> [!note] This is continuous deployment, not continuous delivery.
> Recall the distinction from earlier in this folder: under continuous delivery the pipeline takes a change as far as ready-to-deploy and then waits for a person to approve it; under continuous deployment nothing waits. This pipeline has no approval step anywhere — a commit on `master` that passes every stage is deployed, immediately and automatically. Turning it into continuous delivery would mean adding a stage before deploy that pauses for a person to confirm.

## A feature branch that fails

Now the normal day-to-day case: a new feature, developed on its own branch.

A developer creates a branch named `feature/multiply`, adds an `/api/multiply` endpoint, adds a private method doing the multiplication, and writes a test for it. They commit with a message describing the change and push the new branch:

```bash
# on the developer's machine
git checkout -b feature/multiply
# … write the endpoint, the method and the test …
git add .
git commit -m "Add multiplication"
git push -u origin feature/multiply
```

Within a minute Jenkins has discovered a branch it did not know about, created a pipeline for it, and started **`feature/multiply` build #1**.

It fails.

The Stage View shows it plainly: **Lint** is red, and every stage after it — tests, package, deploy, smoke test — is marked as skipped because of an earlier failure. The console output says why. The endpoint was written, and the private multiply method was written, but the endpoint never actually calls the method. It computes nothing with it. The linter's rule against a private method that is written and never used caught it.

```mermaid
flowchart LR
    C["Checkout"] --> L["Lint<br/>FAILED — private method<br/>never used"]
    L -.->|"skipped"| T["Unit tests"]
    L -.->|"skipped"| P["Package"]
    L -.->|"skipped"| D["Deploy"]
    style C fill:#1f6f3f,color:#fff
    style L fill:#7a1f1f,color:#fff
    style T fill:#3a3a3a,color:#fff
    style P fill:#3a3a3a,color:#fff
    style D fill:#3a3a3a,color:#fff
```

> [!important] This is the pipeline working, not the pipeline failing.
> A method that was written and never wired in is exactly the half-finished work that slips through a manual process. Nobody reviewing quickly would necessarily see it; the code compiles, and nothing crashes. Here it was stopped within a minute of being pushed, on a branch nobody else depends on, with the reason written in the log — and it never got near the server.

The fix: make the endpoint call the method. Commit it as a quick fix and push again. The next scan sees a new commit on `feature/multiply`, and **build #2** of that branch starts by itself. This time lint passes, the tests pass, the package is produced — and deploy and smoke test are skipped, because this is not `master`. The branch has been fully checked and has touched nothing.

## Merging, and the deploy that follows

Once the feature is ready, it is merged into `master` — normally through a pull request, where a colleague reviews it first. The merge is a new commit on `master`, so at the next scan `master` gets a new build.

On `master`, every stage runs, deploy included. When it has finished, `http://192.168.64.2:8081/api/multiply?a=10&b=2` returns **20**. The new feature is live.

```mermaid
flowchart TD
    FB["feature/multiply<br/>pushed"] --> F1["Build #1: lint fails<br/>everything after skipped"]
    F1 --> FIX["Fix pushed"]
    FIX --> F2["Build #2: all checks pass<br/>deploy skipped — not master"]
    F2 --> MERGE["Reviewed and<br/>merged into master"]
    MERGE --> M["master build: all checks pass,<br/>deployed, smoke test passes"]
    M --> LIVE["/api/multiply is live"]
    style FB fill:#2d333b,color:#fff
    style F1 fill:#7a1f1f,color:#fff
    style FIX fill:#7a5a1f,color:#fff
    style F2 fill:#1f4f7a,color:#fff
    style MERGE fill:#1f4f7a,color:#fff
    style M fill:#1f6f3f,color:#fff
    style LIVE fill:#1f6f3f,color:#fff
```

While all this runs, the server's **two executors** are the limit. With several branches building at once, a new build waits in the queue until one of the two slots is free — and then the agent picks it up.

> [!question] Can the number of executors be raised?
> Yes. It is a setting on the node, and on a server with more processor and memory to spare it can be increased so more builds run at once. The limit exists to stop so many builds running together that each one is slowed down by the others.

## A failure worth recognising

There is one more failure worth knowing on sight, because it is common and its message does not say what is actually wrong.

A pipeline for a Java 21 application fails in the compile step, every stage after it is skipped, and the log says:

```
error: release version 21 not supported
```

**The code is fine. The JDK is wrong.** The project asks the compiler to produce Java 21 code, and the compiler doing the build comes from a JDK older than 21, which does not know how. The same message appears for any version a JDK is too old to target.

The confusing part is that the Jenkins server itself is running on Java 21. But as the earlier note on preparing the server stressed, the Java Jenkins runs on and the Java a build compiles with are separate things. The build uses the JDK it is given — through the `tools` block, from an installation configured under **Manage Jenkins → Tools** — and if no such installation exists, or the `tools` block names an older one, the build gets whatever older JDK is to hand.

The fix is on the Jenkins side, not in the code: configure a JDK 21 installation under **Tools**, and make sure the `Jenkinsfile`'s `tools` block asks for it by name.

## What changed for the developer

Put the whole note together and look at what the developer did in it. They pushed code to branches, fixed what the pipeline told them was broken, and merged when the work was reviewed. They never connected to the server, never built a package by hand, never copied a file anywhere and never restarted the application.

> [!tip] The whole point, in one line.
> Every check that the first note in this folder showed being skipped because somebody forgot — the linter, the tests, deploying the right build, confirming it runs — now happens on every push, in the same order, without anybody remembering to do it. And the branch that reaches customers is the only one that could have got there after passing all of it.
