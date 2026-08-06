The theory is finished. From here the work is the actual job: developers and operations working together, tools built to make that possible, products shipped quickly and reliably. And the first thing that job requires is knowing how code gets onto a server.

Start with what a server even is, because the word sounds grander than the thing.

> **A server is just a computer.** There is nothing special about it. We call it a server because it *serves* requests — it stays switched on, connected, and answers when something asks it for data. That is the entire difference between a server and the laptop you are reading this on.

You deploy your code onto that computer. And that computer, overwhelmingly, is running a **Linux-based system**.

Not every server — but most of them. Which is why a DevOps engineer has to be able to work in one.

---

## How much Linux do you need?

Less than people expect. You do not need to become a systems programmer.

What you need is to be able to open a terminal on a Linux machine and get things done in it — move around the file system, look at files, run programs, adjust configuration. Basic, everyday interaction through the shell.

That is the target for this module and the next one or two: enough Linux to work, not enough to write an operating system.

---

## Getting a Linux machine

You need somewhere to practise. There are four routes, and which one you take depends on what you already own.

### If you are on Windows

You have two good options.

**WSL — Windows Subsystem for Linux.** This is the lighter of the two. It gives you a Linux environment running inside Windows without the overhead of a full virtual machine, and your Linux commands run in it directly.

**A virtual machine (VM).** Software that runs a complete second computer inside your existing one — its own operating system, its own file system, fully separate from Windows.

> [!tip] **Choose by how much machine you have.** A VM consumes noticeably more memory than WSL, because it is running an entire operating system alongside the one you already have. If your Windows machine is not particularly powerful, **use WSL**. If it is, a VM gives you a more complete environment — effectively a whole separate computer to work in.

**Dual boot** is the third option: install Ubuntu alongside Windows and choose between them when the machine starts. It gives you the real thing with no overhead at all, but it is the most disruptive to set up — and for one or two lectures' worth of use, it is likely more than you need.

### If you are on a Mac

You are mostly fine already. macOS is **Unix-based**, and Linux comes from the same lineage, so the majority of commands work unchanged in the macOS terminal.

"Mostly" is doing some work in that sentence, though. Some commands differ between the two, and occasionally a flag behaves differently. So it is still worth installing a virtual machine for the parts where the difference matters.

### If you are already on Linux

Nothing to do. You are in the best position of anyone.

---

## Which distribution

**Ubuntu**, unless you have a reason to prefer something else.

The reason is simply that it is the most user-friendly of the widely used options, and everything in this course will work on it. What a "distribution" actually *is* — and why that word rather than "operating system" — is the subject of the next two notes.

> [!important] **Not all servers run Ubuntu.** Real servers run all sorts of distributions, chosen for all sorts of reasons. But the thing that matters underneath — the kernel — is common across them, so what you learn on Ubuntu transfers.

> [!warning] **On using a work machine.** If you are thinking of installing this on a company laptop, check your organisation's policy first. Installing virtualisation software or a Linux subsystem on managed hardware is the kind of thing that is often restricted, and a personal machine avoids the question entirely.

---

Setting this up is homework, not classwork. Have a working Linux environment ready before the next session — commands start there, and they are much easier to learn while typing them yourself than while watching someone else type them.
