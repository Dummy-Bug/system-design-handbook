**The image from the previous note builds, and a container started from it reports that the server is listening.** Open a browser at that port on the host machine and there is nothing there. Two separate things are missing, and they are worth taking one at a time.

# The container is not on your machine's network

```bash
1  docker run -it my-express-server:latest
```

The output says the server started. The browser at `localhost:3000` shows nothing at all.

That is isolation working as designed. The container has its own network, and port 3000 inside it has no relationship to port 3000 on the host. Nothing crosses that boundary until it is asked to.

```mermaid
flowchart LR
    HOST["Host machine — localhost:3000"] -. "no route" .-> CTR["Container — server listening on 3000"]
```

# Ctrl-C does not stop it either

Before fixing the port, there is a smaller problem in the way. Pressing Ctrl-C in the terminal running the container does nothing. The keystroke is not understood as a request to stop the process inside.

```bash
1  docker run -it --init my-express-server:latest
```

**`--init`** runs a small init process inside the container as the first process. Its job is to receive signals and pass them on, so stopping the container from the host stops the process inside it.

With `--init`, Ctrl-C ends the server as expected. Without it, the container has to be stopped from another terminal with `docker kill`.

# Publishing a port

```bash
1  docker run -it --init --publish 3001:3000 my-express-server:latest
```

**`--publish`** builds the route the first diagram was missing. It takes two ports separated by a colon.

```text
--publish 3001:3000
          │    │
          │    └── the port inside the container
          └─────── the port on the host machine
```

**The host port comes first.** Getting this backwards produces a container that starts perfectly and serves nothing, because it maps a host port to a container port where nothing is listening. Publishing `3000:5000` when the server is on 3000 inside means the host's 3000 is wired to the container's 5000, which is empty — the browser shows nothing and no error explains why.

```mermaid
flowchart LR
    B["Browser — localhost:3001"] --> HP["Host port 3001"]
    HP -->|"--publish 3001:3000"| CP["Container port 3000"]
    CP --> S["Express server"]
```

`-p` is the short form and means exactly the same thing:

```bash
1  docker run -it --init -p 3001:3000 my-express-server:latest
```

# Letting the image name the port

A Dockerfile can declare which port its application listens on:

```dockerfile
1  # Dockerfile
2  FROM node
3
4  WORKDIR /developer/nodejs/app_from_github
5
6  COPY . .
7
8  RUN npm ci
9
10 ENV PORT=3000
11
12 EXPOSE 3000
13
14 CMD ["npm", "start"]
```

**`EXPOSE`** documents the port the container serves on. It publishes nothing by itself.

```bash
1  docker run -it --init -P app-from-github:latest
```

**`-P`** in capitals publishes every exposed port — but to a **randomly chosen port on the host**, not to the matching number. The server starts, `localhost:3000` shows nothing, and `docker ps` reveals the port it actually landed on.

> [!important] **Lowercase `-p` and uppercase `-P` are different commands.** `-p 3001:3000` maps a port you chose. `-P` maps every exposed port to whatever host ports happen to be free, which you then have to look up. When a specific host port matters, `-p` is the one to use.
