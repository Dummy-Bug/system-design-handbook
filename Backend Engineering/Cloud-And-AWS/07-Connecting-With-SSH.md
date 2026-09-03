**[[06-Launching-An-Instance]] ended with a machine in the running state and a `.pem` file on disk.** Those two things are enough to get a terminal on a computer in another city, and the tool that does it is SSH.

# What SSH is

**SSH stands for secure shell.** It is a cryptographic network protocol for running operating system services securely over a network that is not itself secure — which the internet is not. Its two best-known uses are **remote login** and **executing commands on a remote machine**.

Remote login means exactly what it sounds like: a shell on a machine you have no physical access to. All it requires is that the machine is reachable on the internet and that you know its address.

**It is a command-line tool, so it runs from a terminal.** On macOS or Linux that is the terminal you already use. On Windows it is Command Prompt, Git Bash, or Windows Terminal — any of the three.

Three things are needed, and you now have all of them:

| Needed | Where it comes from |
| --- | --- |
| The private key | The `.pem` file downloaded when the key pair was created |
| The machine's address | Its public IPv4 address, in the console |
| The username | Fixed by the AMI — an Ubuntu machine's user is `ubuntu` |

# Finding the address

EC2 dashboard, then **Instances**, then the instance ID. That opens the full configuration for that machine, and the field to copy is the **public IPv4 address**.

**Public is the operative word.** To reach any machine across the internet you need its public address — the IPv4 one here, or its public IPv6 address where the machine has one. A private address is not routable from outside its own network.

# The key has to be locked down first

This step is skipped constantly and the connection then fails for reasons that look unrelated.

**SSH refuses to use a private key that other people can read.** From its own documentation:

> ssh will simply ignore a private key file if it is accessible by others.

A file freshly downloaded from a browser is not locked down. Fixing it is one command:

```bash
1  chmod 400 devops-practice.pem
```

**`chmod` sets read, write and execute permissions.** `400` means read for you, nothing for anyone else — not write, not execute, and nothing at all for other users.

Checking with `ls -lh` shows the result in the leftmost column:

```text
-r--------  1 home  wheel  1.7K  3 Sep 10:33 devops-practice.pem
```

Contrast `700`, which grants yourself read, write and execute:

```text
-rwx------  1 home  wheel  1.7K  3 Sep 10:33 devops-practice.pem
```

That is more than the key needs. Read is enough, so read is all it gets.

> [!info]- **Where the number comes from**
> Each digit is one octet of permissions, and the first digit is you, the file's owner. Write the digit in binary and each bit is one permission, in the order read, write, execute.
>
> ```text
> 4  →  100  →  read only
> 7  →  111  →  read, write and execute
> ```
>
> So `400` is read for the owner and zero for everyone else, and `700` is everything for the owner and zero for everyone else. The remaining two digits are the file's group and all other users, and for a private key both should stay `0`.

# Connecting

```bash
1  ssh -i devops-practice.pem ubuntu@13.234.56.78
```

Three parts, and each earns its place:

- **`ssh`** — use the secure shell protocol
- **`-i devops-practice.pem`** — the identity file. Without it, SSH would try its usual credentials; `-i` says authenticate with this specific private key instead
- **`ubuntu@13.234.56.78`** — the username on the remote machine, then its public address

**The username is decided by the AMI, not by you.** Every Ubuntu instance uses `ubuntu`. Other images use other names, and using the wrong one fails authentication even with a perfectly good key.

> [!info] `-l` is another way to give the username — `ssh -i key.pem -l ubuntu 13.234.56.78` does the same thing as the `user@host` form. SSH has a long list of flags like this, each configuring some part of what the protocol does.

The first connection asks whether you are sure you want to connect, because it has never seen this host before. Answer yes.

Then the prompt changes. Ubuntu prints its welcome message — system load, memory usage, and how much disk is free, something like 6.71 GB on a fresh free-tier machine — and you are somewhere else.

# Checking you actually got there

The prompt looks different, but the reliable test is to ask:

```bash
1  whoami
```

**On the remote machine it prints `ubuntu`.** In your own terminal it prints your own username. That difference is the whole check, and it is worth running whenever you are unsure which of two terminals is which.

From there it is an ordinary Linux machine — `ls` to list, `ls -a` to include hidden files, `pwd` for the current directory.

# The first thing to run

```bash
1  sudo apt-get update
```

**This refreshes the package lists** on a freshly provisioned machine, whose image was built some time ago. Do it before installing anything, or you will be installing against a stale catalogue.

It finishes remarkably quickly, and for a reason worth noticing: **the network in a data center is far faster than the one at your desk.** The machine is not downloading over your connection — it is downloading over Amazon's.

And that is the whole point of the exercise. A Linux machine in another city, under your control, from where you are sitting.
