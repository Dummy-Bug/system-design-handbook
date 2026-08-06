#devops #linux #kernel #shell #syllabus

The first technical module of the course, and still deliberately theory. No commands are taught here — the aim is to understand *what you are typing into* before you start typing into it.

That ordering pays off immediately. Once you know that the terminal is only a window, that the shell is the program actually reading your input, and that the kernel is the only thing allowed to touch hardware, every command you learn afterwards has somewhere to attach itself.

> [!info] **Why a DevOps engineer starts here.** Servers overwhelmingly run Linux-based systems, and you reach them through a terminal rather than a screen and mouse. Every tool later in the course — Docker, Kubernetes, Jenkins — is ultimately started, configured and debugged from this environment.

---

## A · Getting to a Linux machine

**1. Why Linux, and how to get one**
Why servers run Linux, and the four practical routes to a Linux environment: a virtual machine, WSL on Windows, a dual boot, or a Mac. Why Ubuntu is the recommended distribution. → `01`

## B · What is underneath

**2. Operating systems and the kernel**
Why you cannot address hardware directly, and what the operating system manages on your behalf — CPU, memory, disk, keyboard, network. The kernel as the core of it, and its main responsibilities. → `02`

**3. Linux is a kernel; distributions are the operating system**
The distinction the module is built around. What a distribution adds on top of the kernel, and what the well-known ones are. → `03`

**4. User space and kernel space**
The privilege split, why a crashed application does not take the machine with it, and how a program asks for something it is not allowed to do itself — the system call. → `04`

## C · How you actually interact with it

**5. Terminal, shell, and the life of a command**
The terminal is a window, not an engine. The shell is what interprets your commands, and bash and zsh are the two you will meet. Then the full path a single command travels, from keypress to result, including where permission gets checked. → `05`

---

> [!warning] **This module corrects the lecture in three places.** Each is marked where it appears.
> - The walkthrough of `cd` describes the shell finding an executable file and asking the kernel to run it. That is accurate for `ls`, but **`cd` is a shell builtin** and cannot work that way. Explained in `05`.
> - `sudo` is described as the kernel asking for your password. **`sudo` is an ordinary user-space program**; the kernel enforces privileges but never prompts you. Explained in `04`.
> - Linux is called "a distribution" once before being corrected to "a kernel" later in the same session. Only the corrected version is taught here. → `03`

> [!tip] **Currency check (2026-08-05).** Stable material, with two moving parts. **WSL** is now on version 2, which runs a real Linux kernel inside a lightweight VM rather than translating system calls as WSL 1 did — worth knowing since the two behave differently. And distribution lineages shift: **CentOS** as a downstream rebuild of Red Hat Enterprise Linux was discontinued in favour of **CentOS Stream**, which sits upstream of RHEL instead. Verify before recommending either for a server.
