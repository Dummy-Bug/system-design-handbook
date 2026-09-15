#config #docker #deployment #python

**An image is built once and run many times, so every setting has to sit on one side of a line: baked into the artifact, or handed to it at start.** Putting a value on the wrong side is what makes configuration changes cost a deploy, and what puts secrets somewhere they cannot be taken back from.

# Baked In Or Passed In

> [!info] An image is a zip of a whole filesystem — the operating system files, the interpreter, the dependencies and your code — built once and stored in a registry. A container is one running copy of it. Nothing is added to an image after it is built, which is why what you put inside it is a decision rather than a detail.

## The file gets baked into the image

A project's `.env` file sits next to the code, so it travels with the code. That is convenient while developing and is the root of most of what goes wrong in production — for reasons that have nothing to do with the file format.

Two words first, because the rest depends on them.

**An image is a zip of a whole filesystem** — not just your code, but the Linux files, the interpreter, the dependencies, your source, everything the program will see. It is built once, given a name, and pushed to a **registry**, a server that stores images the way a git host stores repositories. **A container is one running copy of an image**, and starting five containers starts five copies of that same filesystem. Nothing is added to the image after it is built.

An image is built from a list of steps, each one producing a **layer**, which is a saved snapshot of what that step changed. The file below is an illustration of the shape a real project has, not a file in this lab — the runnable one comes later in this note:

```dockerfile
FROM python:3.13-slim

WORKDIR /app
ARG ENV=stg

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

COPY . .
RUN mv .env.python.${ENV} .env

CMD ["python", "-m", "service"]
```

`ARG ENV=stg` declares a value chosen when the image is **built**, defaulting to `stg`, and `docker build --build-arg ENV=prod` changes it. `${ENV}` is substituted during the build, so `RUN mv .env.python.${ENV} .env` becomes `mv .env.python.stg .env` in one build and `mv .env.python.prod .env` in another.

> [!note] `ARG ENV` and the `ENV` keyword are two different things
> A Dockerfile's `ENV` keyword sets environment variables **inside** the image, for the program at run time — `ENV AWS_REGION=ap-south-1`. `ARG` declares a build-time value that is gone once the build finishes, and the program can never read it. This one is merely *named* `ENV`, which is why the two look related. It could have been called `TARGET` and nothing would change.
>
> Build arguments are also recorded in the image's build history, so `ARG` is not a way to pass a secret either. This one carries the word `prod`, which is harmless.

So the last two lines mean: copy everything in this directory into the image, then rename the file belonging to the environment being built.

**`COPY . .` copies every environment's file.** A project holding `.env.python.dev`, `.env.python.stg` and `.env.python.prod` puts all three into the image, and the rename picks one. The other two are still in there, unused and perfectly readable — so the staging image carries production's secrets.

**Layers behave exactly like git commits**, which [[04-Secrets-Not-Config]] uses to make the same point about a committed `.env` file. Each one is immutable and identified by a hash of its content, and a later layer can only add files or hide them — it cannot reach back and change an earlier one. So `RUN rm .env.python.prod` would remove the file from the final filesystem and leave it in the layer that copied it, readable by anyone who pulls the image. It is the same mechanism as git history, in a second store.

And the audience for that store is larger than it looks:

| Who can read the file | Why they can |
|---|---|
| every developer on the team | they pull the image to run it locally |
| every CI job | it builds on the image, tests it, retags it |
| every machine in the cluster | it pulls the image to start containers |
| any token with registry read access | a pipeline credential, a bot, an old service account |
| every machine that pulled it once | the layers stay in its local cache until pruned |
| every old tag in the registry | previous builds still contain what they contained |

Reading it needs no exploit and no cleverness:

```bash
docker pull <registry>/service:stg
docker run --rm <registry>/service:stg cat .env.python.prod
```

And there is a way that never starts a container at all. `docker history` lists the layers with the step that produced each one, which points straight at the small one holding your files:

```
$ docker history config-demo --format '{{.Size}}\t{{.CreatedBy}}'
0B       CMD ["python" "app.py"]
20.5kB   COPY baked.env app.py show_config.py ./
20.6MB   RUN /bin/sh -c pip install --no-cache-dir py…
8.19kB   WORKDIR /app
```

`docker save` then writes the whole image out as a tar archive, and that 20.5kB layer unpacks to the files themselves:

```
$ docker save config-demo -o config-demo.tar
$ tar -xOf config-demo.tar blobs/sha256/3259e8a31ac9... | tar -tf -
app/
app/app.py
app/baked.env
app/show_config.py

$ tar -xOf config-demo.tar blobs/sha256/3259e8a31ac9... | tar -xOf - app/baked.env
TTL_SECONDS=500
LOG_LEVEL=ERROR
MODEL=gemini-3.6-flash
```

The file was never hidden — it was somewhere nobody looks, and reading it took two commands and no running container.

## Rotating a baked-in secret costs a deploy

Suppose the token leaked and has to be replaced. The value lives in a file that is in the repository and in the image, so:

```
edit .env.python.prod      the value changes
commit and push            it is a code change, so it goes through git
open a pull request        with a production secret in the diff
review and merge           somebody approves a diff containing that secret
CI builds the image        a full build of every layer after the change
push to the registry       a few hundred megabytes
deploy                     rollout, health checks, old containers drained
```

Seven steps and a build, to change one string. In most teams that is somewhere between twenty minutes and the next release window — and this is happening during an incident, because a leak is why you are rotating.

**The review step is its own problem.** The diff contains the new secret in plain text, so every reviewer sees it and it lands in the pull request, which the host keeps. Rotating the secret publishes its replacement to a slightly different audience.

| | Secret baked into the image | Secret supplied at start |
|---|---|---|
| Steps to rotate | edit, commit, review, build, push, deploy | change the value, restart |
| Who sees the new value | every reviewer, and the pull request history | whoever is allowed to set it |
| Time | a release cycle | seconds |
| Rebuild | every time | never |

> [!warning] An expensive rotation is a rotation that does not happen
> This is the part that decides how secure the system actually is. If rotating costs a deploy and a review, the quarterly rotation slips, the one owed when somebody leaves the team gets postponed, and the response to a suspected leak turns into a discussion about whether it is worth the disruption.
>
> Which matters because of where the old copies are: every old image and every old commit still holds the old value, and **the only thing that ever makes those copies harmless is rotating** — the argument [[04-Secrets-Not-Config]] ends on. Baking the value into the artifact makes that one remedy the expensive option.

## What the run passes beats what the image carries

The two previous sections are the argument against putting a value in the image. This one is the pattern that replaces it, and it needs no new mechanism at all — it is [[01-Declared-Not-Fetched]]'s ranking, used on purpose.

A value passed to the container at start time arrives as a **real environment variable**, which is rank 2. A file inside the image is rank 3. So the run wins, and the file answers everything the run did not mention.

`src/config_lab/note06/baked.env`, standing for the file that ships inside the image:

```
TTL_SECONDS=100
LOG_LEVEL=WARNING
MODEL=gemini-2.0-flash
```

`src/config_lab/note06/a_the_file_and_the_run.py`:

```python
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="src/config_lab/note06/baked.env")

    ttl_seconds: int = 900
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    model: str = "none"


settings = Settings()

print("ttl_seconds =", settings.ttl_seconds)
print("log_level   =", settings.log_level)
print("model       =", settings.model)
```

```
$ uv run python src/config_lab/note06/a_the_file_and_the_run.py
ttl_seconds = 100
log_level   = WARNING
model       = gemini-2.0-flash

$ TTL_SECONDS=60 uv run python src/config_lab/note06/a_the_file_and_the_run.py
ttl_seconds = 60
log_level   = WARNING
model       = gemini-2.0-flash
```

The shell variable here stands for whatever the deployment passes — `docker run -e TTL_SECONDS=60`, an environment entry in a task definition, a config map in a cluster. All of them arrive the same way, as real environment variables, which is why this runs exactly as the container would.

**One value moved and the others did not.** `ttl_seconds` came from the run, `log_level` and `model` came from the file, and nothing had to list which settings the deployment intended to override. The file does not know it is being overridden; the deployment does not know what else the file holds.

| | Lives in the image | Supplied at start |
|---|---|---|
| What it carries | what is the same on every run | what differs per deployment |
| Changing it | rebuild the image | change the variable, restart |
| Who writes it | whoever writes the code | whoever runs the service |
| Rank when both exist | 3, the file | **2, and it wins** |

**That split is the whole pattern.** The image becomes a set of sensible defaults that make the service runnable anywhere, and the deployment supplies the handful of values that actually differ — the environment name, the table, the endpoints, the secrets. Neither half has to know about the other, and the ranking does the joining.

> [!important] This is why the baked file stops being dangerous, but only for values
> Once every environment-specific value is passed at start, what remains in the file is defaults that are true everywhere, and shipping those inside the image is fine — that is what defaults are for.
>
> It does not rescue secrets. A secret in the image is readable from the image whether or not the deployment overrides it, as [[04-Secrets-Not-Config]] shows. Overriding at run time changes which value is used; it does not remove the one that is sitting in a layer.

### The same thing, in a real container

The run above used a shell variable to stand for what a deployment passes. Here it is with an actual image, so nothing is standing in for anything.

`src/config_lab/note06/image_demo/baked.env`, the file that will ship inside the image:

```
TTL_SECONDS=500
LOG_LEVEL=ERROR
MODEL=gemini-3.6-flash
```

`src/config_lab/note06/image_demo/app.py`:

```python
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="baked.env")

    ttl_seconds: int = 900
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    model: str = "none"


settings = Settings()

print("ttl_seconds =", settings.ttl_seconds)
print("log_level   =", settings.log_level)
print("model       =", settings.model)
```

`src/config_lab/note06/image_demo/Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app
RUN pip install --no-cache-dir pydantic-settings

COPY baked.env app.py show_config.py ./

CMD ["python", "app.py"]
```

```
$ docker build -t config-demo src/config_lab/note06/image_demo

$ docker run --rm config-demo
ttl_seconds = 500
log_level   = ERROR
model       = gemini-3.6-flash

$ docker run --rm -e TTL_SECONDS=60 config-demo
ttl_seconds = 60
log_level   = ERROR
model       = gemini-3.6-flash
```

**Same image both times.** Nothing was rebuilt between those two runs — the build ran once, and the second run differs only by `-e TTL_SECONDS=60`, which is how a deployment passes a value. The container received a real environment variable, rank 2 beat the file at rank 3, and the two settings nobody mentioned still came from the file.

That is the promotion the earlier sections said was impossible when the value is baked in: **one artifact, built and tested once, behaving differently in each place because of what the run supplies.**

And the file really is inside the image, which is what the first section of this note rests on:

```
$ docker run --rm config-demo cat baked.env
TTL_SECONDS=500
LOG_LEVEL=ERROR
MODEL=gemini-3.6-flash
```

That output came out of the image rather than the project directory: giving `docker run` a command replaces the default one, so this started a container from the built image and read the file that was copied in at build time. Anyone who can pull `config-demo` can run that command — which is why a secret in that file is a secret published to everyone with registry access.

> [!note] The image is 240MB for two small Python files
> `app.py` is eighteen lines and `show_config.py` thirty-four. Almost all of the 240MB is the base image: the Debian files, the Python interpreter and the installed library. Worth seeing once, because it is why a rebuild is not free, and why rotating a value that lives inside the artifact costs a push of that size instead of a variable change.

## The repository stops knowing what production runs

The previous section moved everything that varies out of the image. This one is the bill for that, and it arrives immediately.

Two files standing for a task definition, a config map, or a page in a deploy tool. They live outside the project on purpose — any path will do, because the whole point is that this is not in the repository:

```
staging.env                     prod.env
TTL_SECONDS=120                 TTL_SECONDS=30
LOG_LEVEL=INFO                  LOG_LEVEL=ERROR
                                MODEL=gemini-3.6-pro
```

`--env-file` passes every line of a file as environment variables, which is how a deploy tool hands over a whole set at once rather than one `-e` at a time:

```
$ docker run --rm --env-file staging.env config-demo
ttl_seconds = 120
log_level   = INFO
model       = gemini-3.6-flash

$ docker run --rm --env-file prod.env config-demo
ttl_seconds = 30
log_level   = ERROR
model       = gemini-3.6-pro
```

One image, two deployments, no rebuild — which is the pattern working. Now go looking in the project for what production is actually running:

```
$ grep -rn "TTL_SECONDS" src/config_lab/note06/
baked.env:1:TTL_SECONDS=100
image_demo/baked.env:1:TTL_SECONDS=500
```

**Two answers, and neither is true of either deployment.** Staging runs 120, production runs 30, and the repository reports the defaults, which is all it has ever known. `model` is worse: production runs `gemini-3.6-pro`, a value that appears nowhere in the project at all.

So: **reading the code no longer tells you what the service is doing.** Nothing is hidden — the half that varies was deliberately moved to where it can vary, and the repository is the half that cannot.

| Question | With everything baked in | With the run supplying it |
|---|---|---|
| what does production run | read the committed file | read a task definition somebody else owns |
| who can answer it | anyone with the repository | anyone with access to the deploy tool |
| where is a change reviewed | a pull request | whatever that tool records, if it records anything |
| who can change it unreviewed | nobody | whoever holds that access |

That is the trade rungs 3 and 4 asked you to accept, and it is still worth accepting — the alternative was rebuilding an image to change a timeout. But it leaves a real gap, and it is the gap behind most incidents that begin with somebody saying the code looks right.

## The service has to be able to say what it resolved

The answer to that gap is not documentation, which drifts, and not access to the deploy tool, which you may not have at three in the morning. It is a command the running service answers itself.

`src/config_lab/note06/image_demo/show_config.py`:

```python
import os
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="baked.env")

    ttl_seconds: int = 900
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    model: str = "none"
    api_key: SecretStr = SecretStr("unset")


baked_keys = set()
for line in Path("baked.env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        baked_keys.add(line.split("=", 1)[0].strip().upper())

settings = Settings()

print(f"{'setting':<14} {'value':<22} came from")
for name in Settings.model_fields:
    value = getattr(settings, name)
    if name.upper() in os.environ:
        source = "passed at start"
    elif name.upper() in baked_keys:
        source = "baked.env, inside the image"
    else:
        source = "default in the class"
    print(f"{name:<14} {value!s:<22} {source}")
```

```
$ docker run --rm config-demo python show_config.py
setting        value                  came from
ttl_seconds    500                    baked.env, inside the image
log_level      ERROR                  baked.env, inside the image
model          gemini-3.6-flash       baked.env, inside the image
api_key        **********             default in the class

$ docker run --rm --env-file prod.env config-demo python show_config.py
setting        value                  came from
ttl_seconds    30                     passed at start
log_level      ERROR                  passed at start
model          gemini-3.6-pro         passed at start
api_key        **********             passed at start
```

`Path("baked.env")` works there for the same reason `env_file` does: `WORKDIR /app` makes `/app` the working directory inside the container, and a relative path resolves from wherever the program runs — the rule from [[01-Declared-Not-Fetched]], on the other side of the image boundary.

Three things are on that screen, and they are the three a person debugging actually needs.

**What the value resolved to**, after every source has been consulted — not what a file says, not what a task definition says, but what the object in memory holds.

**Where it came from.** The second column is the diagnosis. A setting that should have been supplied by the deployment and says `default in the class` is the fault, located, without opening the deploy tool. The first run shows exactly that shape: nothing was passed, so three values fell back to the image and one to the class.

**No secret.** `api_key` prints `**********` in both runs, whether it arrived from the environment or the default, because the field is a `SecretStr` — [[04-Secrets-Not-Config]] doing the work, with nothing added here. That is what makes this command safe to run in production and safe to paste into a ticket.

> [!important] Print the resolved values, never the sources
> The temptation is to dump the environment or the file. Both leak, and neither answers the question: the environment includes every unrelated variable the platform set, and the file is the half you already had.
>
> The resolved object is the only view that accounts for precedence, and it is the only one where a secret is a masked field rather than a raw string.

## Check it before the service says it is listening

Everything above assumed the configuration is read at startup. It is worth showing what the alternative costs, because reading a value only where it is needed looks tidier and is the more common shape.

The same missing variable, two programs. Both are in one image, so nothing differs but when the value is read.

`src/config_lab/note06/startup_demo/checked_at_startup.py`:

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: SecretStr


settings = Settings()

print("listening on 8080")
print(
    "serving a request, using the key of",
    len(settings.api_key.get_secret_value()),
    "characters",
)
```

`src/config_lab/note06/startup_demo/checked_at_first_use.py`:

```python
import os

print("listening on 8080")
print("health check: ok")

print("serving a request")
api_key = os.environ["API_KEY"]
print("using the key of", len(api_key), "characters")
```

`src/config_lab/note06/startup_demo/Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app
RUN pip install --no-cache-dir pydantic-settings

COPY checked_at_startup.py checked_at_first_use.py ./

CMD ["python", "checked_at_startup.py"]
```

With `API_KEY` not supplied:

```
$ docker run --rm startup-demo python checked_at_startup.py
Traceback (most recent call last):
  File "/app/checked_at_startup.py", line 16, in <module>
    settings = Settings()
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
api_key
  Field required [type=missing, input_value={}, input_type=dict]

$ docker run --rm startup-demo python checked_at_first_use.py
listening on 8080
health check: ok
serving a request
Traceback (most recent call last):
  File "/app/checked_at_first_use.py", line 15, in <module>
    api_key = os.environ["API_KEY"]
KeyError: 'API_KEY'
```

**Both exit 1** — that is the shell's `$?` after each run, not something Docker printed. The difference is everything that happened before it.

The first printed **nothing at all** — no `listening on 8080`, because the settings are built on the line above it. The process never claimed to be up, so a platform watching it sees a container that failed to start, stops the rollout, and keeps the previous version serving.

The second announced itself, passed its health check, and accepted a request. To the platform that is a healthy container, so the rollout completes, the old version is retired, and traffic moves over. The failure arrives on the first request that touches the setting — from outside, this is not a bad deploy, it is an outage.

| | Read at startup | Read at first use |
|---|---|---|
| Printed before failing | nothing | `listening`, `health check: ok`, `serving a request` |
| What the platform concluded | the container will not start | the container is healthy |
| What the rollout did | stopped, previous version kept serving | completed, old version retired |
| Who saw the error | whoever deployed | whoever made the request |
| What it looks like afterwards | a failed deploy | an incident |

> [!warning] A crash-restart loop is an expensive way to find a missing variable
> The second shape usually does not fail once. The platform restarts the container, it starts cleanly again, serves until the next request touches that setting, and dies again — so the logs fill with a repeating failure whose cause is several steps from where it surfaces, and the service is up and down rather than plainly down.
>
> The first shape cannot do that. There is no state in which it is running and broken.

**The cost of the good version is one line's placement.** Building the settings at import, rather than reaching for `os.environ` where the value is needed, is what converts every missing or malformed variable in this folder into a container that refuses to start — which is where [[03-Refuse-To-Start]] began, arriving here as a deployment property rather than a code one.
