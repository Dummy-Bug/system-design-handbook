# Stack Atom 02 — notes

## Why a stack — the ladder (two-pointer + removed-set → last survivor → stack)

The problem (Remove All Adjacent Duplicates, LC 1047) is: given a lowercase string, repeatedly remove any two adjacent equal letters. The catch that makes it interesting is that a removal can create a brand-new adjacency — once you delete a pair, the two letters that were sitting on either side of it become neighbors, and they might now be equal and have to go too. So the removals cascade, and you keep going until no adjacent equal pair is left. `"abbaca"` → remove `bb` → `"aaca"` → the two `a`s that were separated by `bb` are now adjacent → remove `aa` → `"ca"`.

The first idea that occurs to most people is to simulate it directly on the array with two pointers and a record of what's been deleted — say a `boolean[] removed`, or a set of removed indices. You scan with a pointer; when the current character equals the previous *surviving* character, you mark both as removed. The trouble is the phrase "previous surviving character." After some deletions, the character just before position `i` might itself be removed, and the one before that, and so on — so to find the previous survivor you have to scan backwards over a run of already-removed slots. On an input like `"aaaa…a"` that backward scan happens at almost every step, and the whole thing degrades to O(n²). The removed-set works, it's just paying to re-discover where the previous survivor is, over and over.

That cost is the clue. Look at what the algorithm actually needs at each step: only ever the single *most recent surviving character*, the one the incoming letter will be compared against. And when a pair annihilates, the new "most recent survivor" is whatever survivor came just before the pair — the one that was hidden behind it. "Give me the most recent survivor in O(1), and when I drop it expose the one before it in O(1)" is the exact contract of a stack. Last-in, first-out is precisely the access pattern, so the backward scan disappears: the previous survivor is always just the new top.

It's worth being clear about why a *set* of survivors would be the wrong structure, since it's a tempting alternative. Survivors are not distinct — the same letter can legitimately survive more than once, like the two `a`s kept in `"aba"`. A set collapses duplicates and forgets order, and here both the multiplicity and the order matter (the answer is a specific string, in sequence). So the survivors have to be held in an ordered, duplicate-preserving structure with cheap access to the most recent one — again, a stack.

## Remove All Adjacent Duplicates (LC 1047) — the announced rep, and the StringBuilder trick

Because the survivors are characters and you want them back as a string in order, the cleanest "stack" here isn't `ArrayDeque` at all — it's a `StringBuilder` used as a stack. Its end is the top: `append(ch)` is push, `charAt(len-1)` is peek, `deleteCharAt(len-1)` is pop. The big payoff is that the builder already holds the survivors bottom-to-top in left-to-right order, so `toString()` is the answer with no reversal step. (Had you pushed onto an `ArrayDeque`, iterating it would give you the survivors top-first and you'd have to reverse — the same "list/builder-as-stack to skip the reverse" choice that comes back in Asteroid Collision below.)

```java
StringBuilder sb = new StringBuilder();
for (char ch : s.toCharArray()) {
    int n = sb.length();
    if (n == 0 || sb.charAt(n - 1) != ch) sb.append(ch);  // no match (or empty) → push survivor
    else sb.deleteCharAt(n - 1);                           // matches top → annihilate the pair
}
return sb.toString();
```

A full trace on `"abbaca"` shows the cascade falling out for free, because after a pop the next comparison is automatically against the newly-exposed top:

| read | builder before | top vs read | action | builder after |
|---|---|---|---|---|
| `a` | `` (empty) | — | push | `a` |
| `b` | `a` | `a` ≠ `b` | push | `ab` |
| `b` | `ab` | `b` = `b` | pop | `a` |
| `a` | `a` | `a` = `a` | pop | `` (empty) |
| `c` | `` (empty) | — | push | `c` |
| `a` | `c` | `c` ≠ `a` | push | `ca` |

Result `"ca"`. Notice the cascade was never coded explicitly: deleting the `bb` left `a` on top, and the very next `a` read compared against that exposed `a` and annihilated it. The stack makes "re-check the newly-adjacent survivors" automatic.

(`toCharArray()` vs `charAt(i)` is not load-bearing — the for-each just reads a little cleaner; `charAt` is equally fine.)

## Perturbation findings (the transferable part) — the two 1047 knobs

**Knob 1 — the cascade is the load-bearing assumption.** The suspicious specific in 1047 is that removals chain: kill one pair and you must re-examine the survivors it just made adjacent. Perturb that away and imagine a weaker rule — make a single left-to-right pass, remove an adjacent equal pair when you see one, but do *not* re-check the newly-formed neighbors afterward. On `"abba"` that weaker rule removes `bb` and stops at `"aa"`, whereas the real problem cascades all the way to `""`. The diagnostic part: in this weaker version the stack is the *wrong* tool — it would over-remove, because a stack's whole purpose is to re-confront the exposed survivor. The right tool for the no-cascade version is a one-pass two-pointer that simply appends the characters that aren't part of an immediate pair. So the cascade is exactly what earns the stack its place; remove it and the problem drops one rung back down the ladder to a linear scan. A perturbation that changes which tool is correct is the most useful kind — it draws the boundary of where the atom applies.

**Knob 2 — the stack's payload scales with the pop-decision.** The second specific is "a *pair* annihilates," i.e. exactly two equal in a row. Perturb the count: remove runs of exactly `k` equal in a row (this is the real LC 1209). The skeleton doesn't change at all — it's still "compare incoming against the top, resolve, cascade" — but what the stack *holds* has to grow. For pairs, storing the bare character was enough, because presence on top was the entire pop-decision. For `k`, the pop-decision needs to know how many copies have stacked up, so each entry becomes a `(char, count)`: when the incoming char equals the top's char you increment its count (or push `(ch, 1)` if it differs), and when a count reaches `k` you pop that whole entry. The lesson is that the payload is sized precisely to whatever the pop-rule has to read — nothing more, nothing less. Pair-collapse reads presence; k-collapse reads a count. (Asteroid Collision, below, is the next notch on this same axis: its pop-rule reads a sign and a magnitude, so the payload is the signed integer itself.)

---

## Asteroid Collision (LC 735) — the disguised rep

Same adjacent-collapse skeleton, but the pop-rule is no longer "top equals incoming." Here the sign of a number encodes a direction — positive moves right, negative moves left — and the magnitude is the asteroid's size. Two asteroids collide only when they're approaching each other, and on a collision the smaller one is destroyed; equal sizes destroy both. You scan left to right and report the asteroids that survive, in order.

The reason this is a stack at all comes from working out *which* pairs can actually collide. Walk the four combinations. Two positives are both moving right, same direction, never meet. Two negatives, both left, never meet. A negative already resting in the structure with a positive arriving after it — the negative is to the left moving further left, the positive is to the right moving further right — they move apart, never meet. The *only* pairing that collides is a positive sitting on top of the stack with a negative arriving next: the positive is to the left moving right, the incoming negative is to the right moving left, so they close on each other. That asymmetry is the whole problem.

Now the LIFO part. When a negative arrives, the question it asks is "is there a surviving positive somewhere to my left for me to hit?" It doesn't hit just any positive — it hits the *nearest* surviving one first. If it wins that fight, the positive that was behind that one is now exposed, and the negative faces it next. "Nearest surviving thing on the left, and killing it exposes the one before it" is exactly a stack, and the repeated fighting is the cascade — the `while` loop. So the move is identical to Remove All Adjacent Duplicates in shape; only the pop-test changed from equality to a sign-and-magnitude comparison, and the three outcomes of one collision (top dies / both die / incoming dies) all live in that loop.

The clean form keeps all three collision outcomes in one place with a single `alive` flag, instead of splitting them across the loop condition and post-loop checks:

```java
public int[] asteroidCollision(int[] asteroids) {
    List<Integer> st = new ArrayList<>();
    for (int a : asteroids) {
        boolean alive = true;
        // a collision is only ever (positive on top) vs (negative incoming)
        while (alive && a < 0 && !st.isEmpty() && st.get(st.size() - 1) > 0) {
            int top = st.get(st.size() - 1);
            if (top < -a)       st.remove(st.size() - 1);                 // top smaller → top dies, keep checking
            else if (top == -a) { st.remove(st.size() - 1); alive = false; } // equal → both die
            else                alive = false;                           // top bigger → a dies
        }
        if (alive) st.add(a);
    }
    int[] res = new int[st.size()];
    for (int i = 0; i < res.length; i++) res[i] = st.get(i);
    return res;
}
```

Two implementation points worth keeping. First, the explicit "incoming dies" branch (`else alive = false`) matters: in a version that leans on the loop condition alone, that outcome is silent ("none of the checks fired"), which is the kind of implicit case that breaks on a re-read. Second, `ArrayList`-as-stack is the *correct* backing here, not `ArrayDeque`. The stack read bottom-to-top is already the answer left-to-right, so iterating the list gives the output directly — no reverse. (Same "list-as-stack to skip the reverse" choice as the announced rep.) Inside the loop, `-a` is the incoming magnitude since `a` is known negative there, which reads cleaner than `Math.abs(a)`.

## Perturbation findings (the transferable part)

The suspicious specific to probe is the rule on equal magnitude — "both are destroyed." Why that, and not something gentler like "both survive"? Pulling on it two ways exposes the real load-bearing assumption, and it's not about equality at all.

**Reading (a): "both survive, keep their directions" (pass-through).** This isn't merely harder — it's incoherent, so it could never be the rule. If the incoming negative survives and you push it onto a surviving positive, the stack now holds `[..., +5, -5]`: a right-mover with a left-mover directly to its right. Those two are *approaching*. You'd be recording, as a settled final state, two asteroids that are in fact mid-collision. The configuration contradicts itself. So "both live, same direction" is impossible — which is the deeper reason an equal-magnitude collision *has* to resolve to something (here, both die).

**Reading (b): "both reverse" (bounce).** This one is coherent and even solvable, but it leaves the atom. When the incoming negative and the top positive bounce, the positive becomes a left-mover and is now sitting in the stack with more positives behind it — and those are suddenly approaching it. An asteroid that was buried and settled has woken up and started traveling *backward* over things behind it. Concretely you end up having to re-inject the bounced asteroids and run their collisions again, which is a simulation that can revisit elements, not the single clean forward pass.

That contrast names the assumption the clean stack actually rests on. In the real problem, *every* outcome of a collision moves the incoming asteroid in the **same direction it was already going** — it either dies, or it keeps going left eating positives. Nothing ever turns around. That direction-preserving property is exactly what keeps the stack "settled": once an element is buried under a same-direction element, it is finished forever, so one forward pass suffices. Annihilate-on-equal isn't an arbitrary physics choice; it's the special case that preserves this. The instant an outcome could *reverse* a direction, settledness breaks, a buried element can re-collide, and you're no longer in the adjacent-collapse atom.

This is the same family lesson as the two 1047 knobs, stated one level up: the stack stays clean only while every keep-or-pop decision is local and forward. The cascade (1047 knob 1) is fine because it only ever looks at the current top; the growing payload (1047 knob 2) is fine because it still reads only the top; and Asteroid Collision is fine because every outcome preserves direction. Break locality or break forwardness — a reversal does the latter — and the primitive no longer applies.
