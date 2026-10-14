> [!abstract] Splitwise
> Flavor A (domain modeling), the most machine-coding-heavy problem in the core set · Requirements pulled out in a mock interview on 2026-10-14 · Companion: [[03 Splitwise Research]]

---

## 📄 Problem Statement

Design an expense-sharing application like Splitwise. Friends spend money together, often one person pays for everyone, and the app keeps track of who owes whom. By the end there must be working code with a `main` that shows every requirement.

This is the prompt as the interviewer gives it, deliberately vague. Everything below was pulled out by asking, or by being asked.

---

## ❓ Clarifying questions

### The journey

```mermaid
flowchart LR
    G[Create group] --> M[Add members] --> E[Add expense] --> B[See balances] --> S[Settle up] --> L[Leave group?]
    classDef step fill:#e3ecfb,stroke:#2e6fd8,color:#000
    class G,M,E,B,S,L step
```

| Lens | The question at each step | What it found here |
|---|---|---|
| **Who** does this? | the payer, the person typing it in, a member? | the person adding an expense may not be the one who paid |
| **How many**? | one group or none, two people or ten, one split rule or several? | expenses can sit inside a group or directly between people; three split rules, more later |
| **What if** it goes wrong? | numbers do not add up, money does not divide, a debtor leaves, two people type at once? | validation, a fixed rule for the leftover paisa, no leaving while in debt, no lost expense |

### The questions the interviewer asked back

The best requirements in this round came from the interviewer's questions, not from the first list of FRs. Each is a **what if** at one step of the journey, and next time it should be asked before the interviewer has to.

| Step | The question | The answer that became a requirement |
|---|---|---|
| Add members | Rahul owes 500 and gets removed. Who pays it? | Nobody else: a member cannot leave until their balance is zero. Splitting his debt among the others is unfair, since they did not eat his dinner. |
| Add expense | Percentages add to 90. What happens? | Rejected. PERCENT must add to 100 and EXACT to the amount. |
| Add expense | 100 split three ways is 33.33 each, which totals 99.99. Where does the last paisa go? | To the **first person in the split list**: 33.34, 33.33, 33.33. Not to the payer, since the payer may not be in the split; not random, since the same input must give the same output every time. |
| Add expense | Do you need a group to split a cab with one friend? | No: a direct expense between people is allowed without a group. |
| See balances | What exactly is on the screen? | Two queries, defined in FR6 and FR7. |
| Settle up | Can I pay back part of what I owe? | Yes, any amount, as a direct payment with no split. |
| Correct a mistake | 1000 typed instead of 100, and nothing is ever deleted. How is it fixed? | A new entry that cancels the wrong one. |
| Two people at once | Two expenses are added in the same group at the same moment. | Both must count; see NFR2. |

> [!warning] Asked by nobody: does a pair net out?
> Bob owes Eve 300 from one expense, and Eve owes Bob 500 from another. Is that shown as two lines, or as one line saying Eve owes Bob 200? The two best-known sample outputs disagree (see [[03 Splitwise Research]]), and it changes how balances are stored. It was not asked in the round; settle it at the start of the design.

---

## ✅ Functional Requirements

**Must have**

1. **Users.** People are created up front in `main`; each has an id and a name.
2. **Groups.** A user creates a group and adds other users to it.
3. **Expenses, in a group or not.** An expense has an amount, the person who paid, and the people it is split among. It can belong to a group, or sit directly between people with no group.
4. **Payer and adder can differ.** Whoever types the expense in need not be the one who paid.
5. **Three split rules.** EQUAL divides the amount evenly. EXACT gives each person a stated amount, which must add up to the total. PERCENT gives each person a stated percentage, which must add up to 100. An expense that breaks these is rejected.
6. **Two decimal places.** Every share is rounded to two decimals, and whatever is left over goes to the **first person in the split list**, so 100 split three ways is 33.34, 33.33, 33.33.
7. **Balances for one user.** One line for each person this user owes or is owed by, with the amount.
8. **All balances.** One line for every pair where money is owed, across everyone.
9. **Settle up.** One user pays another any amount directly. It is not split, and it reduces what is owed between the two.

**Nice to have, only if time is left**

10. **Remove a member.** Allowed only when that member's balance in the group is zero.
11. **Group view.** Balances within one group only.
12. **Simplify debts.** Pay the total directly instead of along chains, across all groups.

## ⚙️ Non-functional Requirements

1. **Money is always exact.** The shares of every expense add up to exactly its amount, and across the whole system what everyone is owed minus what everyone owes comes to zero. No user is ever asked to pay more than they owe because of a calculation.
2. **Two at once, both count.** Two people adding expenses that touch the same balance at the same moment must both land; neither may overwrite the other.
3. **Nothing is deleted.** A recorded expense or payment is never removed. A mistake is fixed by adding a new entry that cancels it.
4. **Ease of change.** A new split rule (for example, by shares, 2:1:1) is one new class, with no edits to the expense flow.

### Out of scope (do not build)

Editing or deleting expenses (corrections are new entries) · persistence · REST · login · notifications · currencies · categories · minimum number of payments to settle a group (LeetCode 465; talk about it, do not build it) · several servers.
