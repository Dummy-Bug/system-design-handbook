Every job has a line saying `runs-on`. That line names the machine the job's steps will actually execute on, and it is the single most consequential setting in a workflow file — the earlier notes built an entire virtual machine by hand to answer the same question for Jenkins.

> A machine that runs a job is called a **runner**. There are two kinds, and a workflow can use both.

## Runners GitHub provides

The first kind costs nothing to set up because it does not exist until the job starts:

```yaml
    runs-on: ubuntu-latest
```

**GitHub creates a fresh virtual machine**, runs the job's steps on it, and destroys it afterwards. Three families are available, and the choice is simply which operating system the work needs:

| `runs-on` | The job runs on |
|---|---|
| `ubuntu-latest` | Linux |
| `windows-latest` | Windows |
| `macos-latest` | macOS |

**None of these is your computer, and none of them is your server.** That is the difference from the Jenkins arrangement in the earlier notes, where the pipeline ran on a Linux virtual machine that had to be created, given Java, kept updated and kept running. Here the machine is GitHub's, it is new for every run, and it is gone when the run ends.

```mermaid
flowchart LR
    E["A push or pull request"] --> G["GitHub creates a fresh machine"]
    G --> R["The job's steps run on it"]
    R --> D["The machine is destroyed"]
    style E fill:#7a5a1f,color:#fff
    style G fill:#1f4f7a,color:#fff
    style R fill:#1f6f3f,color:#fff
    style D fill:#3a3a3a,color:#fff
```

**Being destroyed every time is a feature rather than a limitation.** A build that passes on a machine created seconds ago cannot be passing because of something somebody installed on the build server last March and forgot about. Every run starts from the same clean state, which is why the workflow has to install its own Java rather than assume it — the point that the next note watches go wrong.

> [!tip] This is what removes the maintenance.
> With Jenkins, somebody owns the build server forever: its disk fills up, its plugins need updating, its JDK drifts out of date, and it has to be reachable and running for anything to build at all. A hosted runner has no such owner because it has no continuous existence. For the build-and-test half of a pipeline, this removes the entire category of work.

## Why you would ever want your own

Hosted runners handle building, testing and packaging. They cannot handle the last step, and the reason is worth stating plainly.

**A deployment has to reach the machine the application runs on.** That machine is yours — the Linux server from the earlier notes, or a cloud instance, or anything else permanent. A hosted runner is a stranger on the internet that vanishes in a few minutes, and getting it to install software onto your private server means opening your server to it and handing it credentials.

A **self-hosted runner** turns the problem around. Instead of reaching your server from outside, **the runner software is installed on your server**, and it connects outward to GitHub and waits to be given work. Nothing needs to be opened to the internet, because the connection is made from the inside out.

| | GitHub-hosted | Self-hosted |
|---|---|---|
| Who owns the machine | GitHub | You |
| Lifetime | Created and destroyed per job | Runs continuously |
| Software on it | Fresh every time | Whatever you installed, accumulating over time |
| Can deploy to your private server | Not without exposing it | Yes, because it is already inside |
| Maintenance | None | Yours |

Both kinds can be used in the same repository, and the sensible arrangement uses each for what it is good at: tests on a hosted runner, deployment on a self-hosted one.

**Installing a runner of your own is real work**, and there is no reason to do it yet. The next note builds both workflows in the order that makes the trade visible: the testing half first, end to end, on machines GitHub provides and at the cost of one file in the repository — and only then the deployment half, at the point where a hosted runner genuinely cannot go any further. Setting up your own machine is much easier to judge once you have seen precisely what it buys and what it does not.
