Every note so far has been about putting things into Git. This one is about getting information back out, and about undoing what is already there.

The framing that makes it worth learning properly is not the developer's. It is the one from the class: **the application worked last Monday, today it is broken, and a hundred and fifty commits happened in between.** Nobody remembers what changed. Git does, and the questions it can answer are exactly the ones an incident needs:

- who changed something, and when
- what exactly changed
- which commit introduced the problem
- can an older state be recovered

This note covers the first three. Finding the bad commit efficiently is note `12`.

---

## Reading history

`git log --oneline` has been in use since note `02`. It answers **what happened, in order**:

```bash
git log --oneline
```

```
f7cc0b6 (HEAD -> master, origin/master) 17th commit modified deploy.txt
c2c58f1 16th commit modified deploy.txt
9f4c2ab 13th commit merged app.txt
4d3e91c 11th commit modified app.txt
```

Two things to keep in mind about what you are looking at:

> [!info] **`git log` shows the history of the branch you are on, not of the repository.** Commits on other branches are not missing or lost — they are simply not reachable from here. Note `07`'s `git log --oneline --graph --decorate --all` is the version that shows everything, and `--all` is doing that work.

> [!important] **Those short IDs are the real thing, abbreviated.** A commit ID is 40 characters, and `f7cc0b6` is its first seven. Git accepts an abbreviation anywhere a commit ID is expected, as long as it is unambiguous in this repository — and it will tell you rather than guess if it is not. Seven characters is the conventional display length because it is comfortably unique for repositories of ordinary size; Git lengthens it automatically as a repository grows.

### What one commit did

```bash
git show f7cc0b6
```

```
commit f7cc0b62a41d38e5907c2fb4816ade3095c17e28
Author: Your Name <you@example.com>
Date:   Thu Aug 20 22:41:07 2026 +0530

    17th commit modified deploy.txt

diff --git a/deploy.txt b/deploy.txt
index 3928a43..d81d813 100644
--- a/deploy.txt
+++ b/deploy.txt
@@ -5,3 +5,4 @@ fifth line of deploy.txt
 sixth line of deploy.txt
+seventh line of deploy.txt
```

The metadata from note `05` — author, date, message — followed by **the change the commit made**. One command answers who, when, why, which files and which lines.

> [!info] **`git show` was in the written course notes rather than the lecture**, which demonstrated `log` and `diff`. It is included because it is the natural third member of the set and the one you reach for during an incident: once `log` has named a suspicious commit, `show` is how you look at it.

### What changed between two points

```bash
git diff c2c58f1 f7cc0b6
```

```
diff --git a/deploy.txt b/deploy.txt
index 3928a43..d81d813 100644
--- a/deploy.txt
+++ b/deploy.txt
@@ -5,3 +5,4 @@ fifth line of deploy.txt
 sixth line of deploy.txt
+seventh line of deploy.txt
```

| In the output | Meaning |
|---|---|
| `a/deploy.txt` | the file as it was in the **first** commit you named |
| `b/deploy.txt` | the file as it is in the **second** |
| `+` | a line the second has that the first did not |
| `-` | a line the first had that the second does not |

Order matters: `git diff A B` reads as **what would have to change to get from A to B**. Swapping the arguments turns every `+` into a `-`.

Branches work as arguments too, which is the form that gets used in review:

```bash
git diff master feature-branch
```

> [!tip] **Getting the ID wrong is the normal first attempt, and the error is clear.** The class hit it live — a mis-copied ID produces a `fatal` naming the argument Git could not resolve. It is not a broken repository or a missing file, just an ID that matches nothing. Copy it from `git log --oneline` and try again.

---

## Undoing things

Note `06` established three places a change can live. Every undo command in Git is best understood as **which of those three it touches**:

```mermaid
flowchart LR
    WD["<b>working directory</b><br/><i>your files</i>"] -->|"git add"| IX["<b>staging area</b><br/><i>.git/index</i>"] -->|"git commit"| RP["<b>repository</b><br/><i>.git/objects</i>"]
```

### Unstaging something you added

You ran `git add` and changed your mind. The change is fine; you just do not want it in the next commit.

```bash
git reset deploy.txt
```

```
Unstaged changes after reset:
M	deploy.txt
```

The file is back to modified-but-not-staged. **Your edit is untouched** — this moved it out of the staging area, nothing more.

> [!info] **The modern spelling is `git restore --staged <file>`.** Same effect, clearer name. It arrived in **Git 2.23 (2019)** alongside `git switch` from note `07`, and for the same reason: `git reset` does several unrelated jobs depending on its arguments, which makes it easy to run the dangerous version by accident. Both work; the class used `git reset`.

### Discarding an edit entirely

```bash
git restore deploy.txt
```

No output, and the file goes back to whatever the last commit contains.

> [!danger] **This one is not recoverable.** Every other undo in this note moves something that Git has already recorded. An uncommitted edit was never recorded — there is no object, no reflog entry, nothing to recover from. `git restore` on a file you have spent an hour editing loses the hour.

### Undoing a commit

The class's example: the last commit was a mistake, but its changes are worth keeping.

```bash
git reset --soft HEAD~1
```

`HEAD~1` means **one commit before where I am now**. Nothing is printed, but `git status` shows what happened:

```
On branch master
Your branch is behind 'origin/master' by 1 commit, and can be fast-forwarded.

Changes to be committed:
	modified:   deploy.txt
```

The commit is gone from the branch, and **its changes are sitting in the staging area**, ready to be committed again differently. From there `git reset deploy.txt` moves them further back to unstaged, and `git restore deploy.txt` would discard them.

That is the whole design, and it is worth seeing as one table:

| Command | Branch pointer | Staging area | Working directory |
|---|---|---|---|
| `git reset --soft HEAD~1` | moves back | **keeps the changes staged** | untouched |
| `git reset HEAD~1` | moves back | changes become unstaged | untouched |
| `git reset --hard HEAD~1` | moves back | discarded | **discarded** |

> [!danger] **`--hard` is the one that destroys work.** It does not put your changes anywhere. The staging area is cleared, the working directory is rewritten to match the older commit, and any uncommitted edits are gone with no route back. The class named it exactly this way — the changes do not even reach staging.
>
> Committed work reset with `--hard` is still recoverable through `git reflog`, as note `09` described. **Uncommitted work is not.**

> [!info] **You can go back several commits, but you cannot pick one out of the middle.** `HEAD~3` moves back three, and this was asked directly in class: **`reset` moves the branch pointer to an earlier commit**, so it always discards a contiguous run from the tip. Undoing one old commit while keeping everything after it is a different operation — `git revert`, which writes a **new** commit that reverses the old one and leaves history intact.

### The part that needs a warning

After a `reset`, your branch is behind the remote. Pushing therefore requires a force push, exactly as in note `09` — and the class did this on `master`.

> [!danger] **Resetting and force-pushing a shared branch is the thing note `09` tells you not to do.**
>
> It works fine in a teaching repository with one user. On a branch other people have pulled, it is the same history rewrite as a bad rebase, with the same consequences: their clones still contain the commit you removed, their next push tries to put it back, and anything referencing it by hash now points nowhere.
>
> **On a shared branch, undo by adding a commit, not by removing one:**
> ```bash
> git revert <commit>
> ```
> This writes a new commit that undoes the named one. History grows instead of changing, so nobody else has to do anything. Reserve `reset` for commits that have never left your machine.

> [!info] **The instructor's framing of who does this, and it is worth keeping.** As a DevOps engineer you will rarely be the one reverting application commits — that is usually the developer's call. Your job is more often to **pinpoint** the change that caused the problem and hand it over. Which is exactly what note `12` is about.

---

## Summary

| Command | What it does |
|---|---|
| `git log --oneline` | compact history of the current branch |
| `git log --oneline --graph --decorate --all` | every branch, with structure |
| `git show <commit>` | one commit's metadata and its diff |
| `git diff <A> <B>` | what changed between two commits or branches |
| `git restore <file>` | discard an uncommitted edit — **not recoverable** |
| `git reset <file>` | unstage a file, keeping the edit |
| `git restore --staged <file>` | the modern spelling of the above |
| `git reset --soft HEAD~1` | undo a commit, keep its changes staged |
| `git reset --hard HEAD~1` | undo a commit and **destroy** its changes |
| `git revert <commit>` | undo a commit by adding a new one — safe on shared branches |

The rule that ties the undo commands together: **ask which of the three areas a command touches, and whether what it discards was ever committed.** Anything Git has recorded can be found again. Anything it has not is gone.

---

*Source: class 5 — 2026-08-21, recording part 4.*
