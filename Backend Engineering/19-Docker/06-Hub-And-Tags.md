**Almost nothing gets built from nothing.** Most images are pulled ready-made from a public pool, and choosing which one to pull is a decision worth making deliberately.

# Docker Desktop
is the application to install first, chosen for the operating system in use. Most of what is needed to run containers arrives with it, and it provides a window listing images and containers alongside the command line.

> [!info] **The window is convenient and the commands are the ones to learn.** Containers can be started, paused and deleted from it, but the moment the work happens over SSH on a server there is no window — only a terminal. Everything from here on is done with commands for that reason.

--- 
# Docker Hub
Is the registry — a large pool of ready-made images. Two comparisons both fit: it is what npm is to Node.js packages, a pool somebody else filled that you pull from; and it is GitHub for images, in that you push your own up to it as well. Some are **official images** maintained by the organisation behind the software itself, which come with clear documentation and follow current practice. Others are published by third parties. Anyone with an account can publish their own.

There is an image for nearly anything worth running: Node.js, Python, MySQL, MongoDB, Ruby on Rails, and bare distributions such as Ubuntu and Alpine Linux carrying nothing but the operating system's own files. Pull one and Docker can start a container in which that software is already installed and configured.

Size varies enormously between them, and it is worth knowing which you are pulling. **Alpine Linux is about 5 MB** — the libraries, shell and directory layout a program expects to find, and deliberately nothing more, which is why so many images are built on it. An Ubuntu image carries a far larger userland and costs accordingly. Neither contains a kernel; that is what makes 5 MB possible at all.

---

# Tags

A **tag** is a label naming one particular version of an image.

```text
node:20-alpine
│    │
│    └── the tag — which version of this image
└─────── the repository — which image
```

Pull an image without naming a tag and the output says it is using the default tag, `latest`, which points at the most recently published version. Naming a tag pins a specific one: `alpine:3.18.2` is that release and nothing else.

**A tag does not have to be a version number.** It can name a **variant** instead — the same software wrapped in a different amount of operating system. Since an image is a filesystem, that is what a variant tag is really choosing: how much filesystem comes with the thing you wanted.

| Tag | Download size | What the filesystem holds |
|---|---|---|
| `node:22` | 381 MB | A full Debian userland — shell, package manager, compilers, `git`, `curl` |
| `node:22-slim` | 76 MB | Debian with documentation, manual pages and rarely-used packages stripped out |
| `node:22-alpine` | 55 MB | Alpine's userland in place of Debian's |

**The Node.js is identical in all three.** What differs is everything around it, which is what `slim` means: not a smaller Node and not an older one, but a smaller machine for Node to sit in.

That cuts both ways. A smaller image is faster to pull, has less in it to keep patched, and leaves fewer programs lying about for anyone who gets in to make use of. But it also strips out the tools you reach for when something misbehaves — an Alpine-based image has no `bash` and no `curl`, so there is nothing to investigate with once you are inside one. And Alpine is built against a different C library from Debian's, so anything compiled against Debian's can fail outright there, which is a long afternoon if it is discovered late.

Every tag's page on Docker Hub links to the instructions it was built from, so what went into a variant can be read before it is pulled. That is the recipe rather than the result — it tells you what the build did, not what is sitting in the filesystem afterwards.

> [!info] Tags do for images what tags do for commits in Git — they give a memorable name to a specific version, so nobody has to remember an exact identifier.
