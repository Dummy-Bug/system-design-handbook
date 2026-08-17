# Customized serialization

> The most valuable, the most difficult concept in the whole of serialization.

**In default serialization everything is taken care of by the JVM — the programmer's role is very small.** Customized serialization is what you do when that is not good enough.

**This part is only the problem.** How to solve it is part `07`.

---

# The problem

```java
class Account implements Serializable {
    String username = "Durga";
    transient String password = "Anushka";
}
```

**Between username and password, which is sensitive?** The password. Username we can write anywhere, but password we should not write anywhere — so, following part `03`, it is declared `transient`.

Now serialize the object and read it straight back:

```java
Account a1 = new Account();
System.out.println(a1.username + " ... " + a1.password);

// serialize, then deserialize
Account a2 = (Account) ois.readObject();
System.out.println(a2.username + " ... " + a2.password);
```

Measured on JDK 25:

```
before serialization : Durga ... Anushka
after deserialization: Durga ... null

file contains 'Durga'?   true
file contains 'Anushka'? false
```

> **Before serialization the account object can provide proper username and password. After deserialization it can provide only the username — not the password.**

**The password is gone. `null`.** And the file confirms why: `Anushka` is genuinely not in it.

## Naming the problem

> **In default serialization there may be a chance of loss of information because of the `transient` keyword. To recover this loss of information, we should go for customized serialization.**

> With only the username, what can my receiver do? Nothing. Compulsorily he requires the password — but for security reasons he is unable to get it.

## The exact constraint

**This is what makes it hard, and it is worth stating precisely before any solution appears:**

| Requirement | |
|---|---|
| The `password` variable | **must stay `transient`** |
| The file | **must contain `null` only** |
| The receiver | **must get the original password, `Anushka`, as it is** |

> I have to do some magic. This magic is nothing but customized serialization.

---

# The mango box

His analogy for what that magic is. **It is a true story told in two halves, and the first half is the one that fails.**

> [!info] **Part one — the three lakhs that never travelled.**
> A few years ago, one Friday, his father called from their native place, 320–330 km from Hyderabad: **Do you have the money? I require some money.** — Yes. How much? — **Almost three lakhs.**
>
> No problem, I have the money. Father, can you please come and take the money?
>
> **No, I'm a bit busy. Can you please come to our native place and hand over the money?**
>
> At the time he was handling **six SCJP batches a day, morning 7 to evening 9, continuously packed**. Dad, not possible for me — cancelling six classes and then coming to native place is not good. Can you please come and take the money, because you require the money? — said, he admits, **a bit strongly**.
>
> **Do something. I require the money, but it is not possible for me to come.** Call disconnected.
>
> Half an hour later, another call: **Check whether Shenu is coming to our native place or not.** Shenu is his cousin, working at a software company in Hyderabad, who travels to their native place most weekends. If Shenu is coming, why don't you send it through him?
>
> So he calls Shenu — yes, he's going. He comes to the class at 9:00, they go to the house, have dinner, and Shenu is ready to catch the 11 pm bus. **Then he takes out three lakhs wrapped in paper.** Shenu, can you please hand over this packet to my father?
>
> **What does this packet contain?** — Money. — **How much?** — Three lakhs.
>
> Can you please hold on. — and Shenu comes back with: **Sorry, I can't carry the money. Night time — if it gets misplaced, who is responsible? Security reason. Please don't ask me to carry money.**
>
> He tries to convince him. He calls his father, and his father tries to convince him over the phone. **Shenu does not budge.** He travels that night carrying nothing.
>
> **The next morning his father made the 320 km journey himself.** The day was gone.

> [!info] **Part two — the seven lakhs that did travel.**
> Three or four months later, the same call. **Do you have the money?** — How much? Last time you asked for three lakhs. — **This time, seven lakhs.**
>
> The same argument, in the same order. Can you please come and take it? — **Last time also I only came. At least this time, can you please come?** — Not possible, I don't want to cancel my classes. — and with **full irritation**: **Do something. I require the money.** Call disconnected. Half an hour later: **Is Shenu going? Send it through him.** — Last time Shenu wasn't interested. How can I ask him to carry money again? — **Do something.** Disconnected, in full angry mode.
>
> So he calls Shenu. And Shenu, before anything else, sets his terms: **Are you asking because you have work? I'm going — but don't force me to carry money or gold.**
>
> Not money, not gold. A small work is there.
>
> Same evening, same routine — class, house, dinner, ready to leave at 11. **This time he hands over a big box.**
>
> **What is inside?** — My mother is a bit fancy about mangoes, and in our native place the mangoes haven't come yet. She requested me to send mangoes. It is a box of mangoes only.
>
> **Are you sure?** — because sending mangoes 320 km is not a thing people normally do. So he may have the doubt. **He opens the top of the box and shows him: all mangoes.** — Okay, no problem.
>
> They go to the bus stop, and he places the box carefully near Shenu's seat: Take special care, otherwise these mangoes will be damaged. — **I will take care, not required to worry.**
>
> **The bus leaves. Then he calls his father.** Father, I sent a box of mangoes through Shenu. Can you please collect that box at the bus stop itself?
>
> **His father starts firing.** I asked for seven lakhs and you send a box of mangoes? What are you thinking?
>
> — **In that box of mangoes, at the bottom, there is a polythene cover. Inside it I kept the seven lakhs.** And collect it at the bus stop, not at his house — because if Shenu takes the box home and they open it, there is a problem.
>
> **Does Shenu know about this?** — No. — **At least can you convey it to him now?** — If I call him now he may stop the bus in the middle and get down. That's a big problem. Let it continue.
>
> **At 3:30 in the morning his father was at the bus stop.** He took the box, opened it, threw the mangoes out — my mother is going to take care about the mangoes, my father takes care about this cover — and after opening **three layers** of packing, there was the money.
>
> **Up to today also, Shenu doesn't know that night he carried seven lakhs.** Maybe in the future he has to believe me — that's why I didn't tell him.

## What the story is actually about

> **At the sender side and the receiver side, if we do some extra work, then we can recover the loss of information. This extra work is customized serialization.**

| In the story | In serialization |
|---|---|
| the money | the **value we must not write directly** |
| Shenu refusing to carry money | the **`transient` keyword** — this channel will not take it |
| **2–3 hours** packing it into a mango box | the **extra work at the sender side** |
| what actually travelled — **a box of mangoes** | what the file contains — **not the password** |
| his father unpacking three layers at 3:30 am | the **extra work at the receiver side** |
| the seven lakhs arriving intact | the **original value recovered** |

```mermaid
flowchart LR
    A["<b>sender</b><br/>real value"] -->|"extra work<br/><i>disguise it</i>"| B["<b>the file</b><br/>carries something else"]
    B -->|"extra work<br/><i>undo the disguise</i>"| C["<b>receiver</b><br/>real value recovered"]
```

> [!important] **The three properties that make the trick work are exactly the three constraints.** Shenu still carried no money (the variable stays `transient`). The box genuinely was a box of mangoes (the file genuinely contains `null`). And seven lakhs still arrived (the receiver gets the original value).
>
> **That is why customized serialization is not just make it non-transient.** The point is to satisfy all three at once.

---

# What this part established

| | |
|---|---|
| Default serialization | everything handled by the **JVM**, programmer's role is small |
| The problem | **loss of information**, caused by `transient` |
| Demonstrated | `Durga ... Anushka` before, **`Durga ... null`** after |
| The file genuinely | does **not** contain the password |
| The fix | **customized serialization** |
| Constraint 1 | the variable **stays `transient`** |
| Constraint 2 | the file **still contains `null`** |
| Constraint 3 | the receiver **still gets the original value** |
| The analogy | **the seven lakhs inside the mango box** |
| The definition | **extra work at the sender side and receiver side** to recover the lost information |
