A registry is only useful once something of yours is in it. The image built in this folder exists on one machine, under a name that means nothing anywhere else, and this note takes it from there to a place any server can pull it from.

Four things have to happen, and only one of them moves any data.

```mermaid
flowchart LR
    A["Create the repository<br/>on the registry"] --> B["Authenticate<br/>from the terminal"]
    B --> C["Give the image a name<br/>the registry will accept"]
    C --> D["Upload it"]
    classDef step fill:#7a5a1f,stroke:#b08a2e,stroke-width:1.5px,color:#fff
    classDef mech fill:#1f4f7a,stroke:#2f6ea6,stroke-width:1.5px,color:#fff
    classDef good fill:#1f6f3f,stroke:#2e9c5a,stroke-width:1.5px,color:#fff
    class A,B step
    class C mech
    class D good
```

## The repository has to exist first

A registry account is an account like any other, and inside it you create a repository — one per image, named for the thing it holds. For the service in this folder that is `order-service`, inside the account `bookcart`, which makes the full reference `bookcart/order-service`.

At creation you choose public or private, with the consequences the previous note described. A repository created and never pushed to is simply empty: it exists, it has no tags, and pulling from it fails.

## Authenticating

```bash
docker login
```

The command prompts for the account and a password or access token, and on success prints that the login succeeded. With no registry named it authenticates against Docker Hub; any other registry is named as an argument.

```bash
docker login registry.example.com
```

The credentials are stored on the machine so later pushes do not ask again. Where they are stored depends on the installation — the desktop application wires this to the operating system's keychain, which is why a machine with it installed and already signed in may log in without prompting at all.

> [!danger] **An access token is a credential and belongs nowhere near the repository.**
> Registry tokens end up in shell history, in screenshots, and in the environment of whatever process ran the login. Use a token scoped to the one thing it needs rather than an account password, revoke it when the machine it is on stops being yours, and never put one in a file that gets committed.

## The local name is not a registry name

The image on this machine is `order-service:v3`, the multi-stage build from earlier in this folder — the one that leaves the compiler behind and ships a runtime and a jar. Expanded by the rules from the previous note, that name means `docker.io/library/order-service:v3`, which is a claim to a repository in the namespace reserved for official images. It cannot be pushed, and it should not be.

Two things therefore have to change about the name, and only one of them is forced.

**The account is forced.** A pushed image has to carry the namespace that owns it, or the registry has nowhere to put it.

**The version is a choice, and this is the moment to make it.** `v1`, `v2` and `v3` were working names for three attempts at the same image on one laptop, which is all a local name ever has to be. A tag in a registry is read by other people and by other machines, it is what a deployment names, and it is what a rollback reaches for — so it stops being a counter and becomes a release version. `1.0.0` says first release, and the number can move in a way that `v3` cannot.

```bash
docker tag order-service:v3 bookcart/order-service:1.0.0
```

Tagging creates a name that refers to an existing image. It does not build anything, it does not copy anything, and it is instantaneous whatever the image's size.

```bash
docker images
```

```
REPOSITORY                 TAG     IMAGE ID       SIZE
order-service              v3      7f3a9c1d8e42   512MB
bookcart/order-service     1.0.0   7f3a9c1d8e42   512MB
```

Two rows, two names, one identifier. The identifier here is illustrative — yours will differ — but the fact that both rows carry the same one is the entire point, and it is worth confirming on your own machine rather than taking on trust. The size is the figure this folder measured after the base image was cut down to a runtime, and the two rows report it twice for one stored image.

> [!important] **The size column is reported per name and will mislead you if you add it up.**
> Both rows say 512MB and the machine has not used a gigabyte. The rows are two names for one stored image, so the storage is counted once. The same arithmetic trap applies across unrelated images that share base layers, which is most of them — the sum of the size column is an upper bound, not a measurement.

Deleting one of the two names leaves the image in place, because the other name still refers to it. Only when nothing refers to it any more does the stored data become a candidate for removal.

## Uploading it

```bash
docker push bookcart/order-service:1.0.0
```

The upload is per layer rather than per image, and the output names each one as it goes. Layers the registry already holds are not sent again, which the output states plainly:

```
195be5f8be1d: Layer already exists
```

That line is the layering from earlier in this folder paying off a second time. The first push of a Java service uploads the runtime base layer; the second push of the same service, with only the application changed, uploads the application layer and skips the rest. A code change costs a few megabytes on the wire, not five hundred.

Pushing one tag pushes one tag. To send every tag a local image carries:

```bash
docker push --all-tags bookcart/order-service
```

## What the registry then shows

The repository page lists the tag that was pushed, and opening the tag shows the image's layers individually — the instructions that produced them, and the size each one contributed. For the service here that is the runtime base, the working directory, the copied jar and the entry point, in the order the Dockerfile wrote them.

This is the clearest view of an image anybody gets, and it cuts both ways. It is genuinely useful for understanding why an image is the size it is. It is equally available to anybody who can pull the repository, which is everybody if the repository is public.

## Your application is the only thing you publish

The compose file names two images and only one of them went through any of this.

| | `order-service` | `mysql` |
|---|---|---|
| Who wrote the Dockerfile | You | The image's maintainers |
| Who builds it | You | Published already |
| Where it comes from | Your account on the registry | The official namespace |
| What you do to deploy it | Push it, then pull it | Name it |

A database, a cache, a message broker and a reverse proxy are third-party software. Somebody already built, versioned and published them, and the correct way to use one is to name a version in a file. Writing a Dockerfile for MySQL would mean taking on the job of building and maintaining a MySQL image, which is a real job that somebody else is already doing better.

> [!question] **So what is in the registry for the database, if you never pushed anything?**
> The same thing that is there for yours: an image somebody built and published. The asymmetry is not in how the images are stored or fetched — those are identical — but in who is responsible for producing them. You are responsible for exactly one image in this application, and the registry treats it no differently from any other.
