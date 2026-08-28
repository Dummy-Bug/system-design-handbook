Packets need somewhere to travel. Between your machine and the rest of the internet sits physical infrastructure and a company that owns it — worth knowing about, because the shape of today's internet is largely explained by what already existed when it arrived.

# Access networks

> [!important] An **access network** is the medium through which an end system connects to the internet.

Your machine is the end system. The access network is whatever it connects **through** to reach everything else.

```mermaid
flowchart LR
    A["End system<br/>laptop, phone"] --> B["Access network<br/>Wi-Fi, cable, fibre, satellite"]
    B --> C["The internet"]
```

# The card that makes it possible

Before any of that, the machine needs hardware capable of joining a network at all.

> [!important] A **network interface card**, also called a network interface adapter, is the hardware that lets a computer attach to a network.

Many kinds of network exist — wired, wireless, this technology or that — and the card is what presents a single consistent way for the machine to connect to any of them. When something says a network interface card is required, it means this: the hardware that puts the machine on a network.

# The kinds of connection

| Type | What it uses |
|---|---|
| **DSL** | Existing telephone lines |
| **Cable** | A dedicated cable line |
| **Fibre** | Fibre optic cable — the fastest of these |
| **Satellite** | A satellite link, no ground infrastructure needed |
| **Wi-Fi** | A wireless local link to one of the above |
| **Dial-up** | Telephone lines, older and slower than DSL |

Each carries data at a different rate, which is most of what distinguishes one internet connection from another.

# DSL, and why it mattered

**DSL** — **Digital Subscriber Line** — deserves singling out, because it explains the industry rather than just the technology.

> [!important] **DSL uses the existing telephone network to carry internet traffic.**

That is the whole idea, and it was decisive. Telephone wiring already reached most buildings — laid, paid for and working. Building a separate nationwide network for internet access would have been enormously expensive. Using the wires already in the ground was not.

## Which is why your phone company sold you internet

> [!important] DSL is generally provided by the **same company that supplies the telephone service** — because they own the wires it runs on.

And that is where the term you use every month comes from:

> **An ISP — Internet Service Provider — is a company that provides end users with internet access.**

The first ones were telephone companies. They already had the infrastructure and the customers; adding internet service on top was the obvious move. Later ISPs built cable and fibre, but the category was created by the fact that a telephone network already existed.

> [!info] Wireless followed the same logic. Early mobile internet used dongles with a SIM card, running over the existing mobile telephone network for the same reason DSL used the fixed one. Whatever was already there got used.

# Why this is worth knowing

You will not configure DSL. What is worth carrying is the pattern.

> [!important] **New infrastructure gets built on top of old infrastructure wherever possible**, because the old infrastructure is already paid for. The internet reached homes over telephone wires, and mobile internet reached phones over mobile telephone networks.

The same instinct shows up in software constantly — building on something that already exists rather than starting again — and it is the reason a great many technical decisions look arbitrary until you know what was there first.
