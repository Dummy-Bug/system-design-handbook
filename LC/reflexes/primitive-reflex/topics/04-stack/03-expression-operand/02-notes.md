# Stack Atom 03 — notes

## Evaluate RPN (LC 150) — the announced rep

The problem hands you an arithmetic expression already in postfix form and asks for its value. Postfix means every operator comes *after* the operands it works on, so as you scan left to right the operands pile up and an operator, when it appears, consumes the ones immediately before it. That "consume the most-recent values, leave one result behind" is the operand-stack move: push every number; on an operator pop the operands it needs, apply, push the result; at the end a single value is left.

```java
public int evalRPN(String[] tokens) {
    Deque<Integer> st = new ArrayDeque<>();
    for (String t : tokens) {
        if (isOperator(t)) {
            int x = st.pop();              // right operand — pushed last
            int y = st.pop();              // left operand  — pushed first
            st.push(apply(y, x, t));
        } else {
            st.push(Integer.parseInt(t));
        }
    }
    return st.pop();
}
```

The one place a clean solution can still go wrong is operand order for the non-commutative operators. The stack returns operands in reverse of how they were read, so the value popped *second* is the left-hand side of the operation. For `["a","b","-"]` (meaning `a - b`) you push `a`, push `b`, then pop `x = b` and `y = a`, and you must compute `y - x = a - b`, not `x - y`. Getting this backwards passes on `+` and `*` (commutative) and silently fails on `-` and `/` — exactly the kind of bug that survives weak testing, so the named rule is "second-popped is the left operand." (Java's `int` division already truncates toward zero, which is what LC 150 wants, so `/` needs no special handling.)

## Perturbation findings (the transferable part)

The suspicious specific in this problem is the input format: it arrives **already in postfix**. That one fact is doing enormous silent work, and perturbing it is what reveals the whole #3/#4 structure.

**Knob 1 — make the input infix instead.** Suppose the same tokens came in ordinary infix, `["3","+","4","*","2"]` meaning `3 + 4 * 2`. The natural instinct is to keep the stack but apply as you go: push `3`, push `+`, see `4` → pop `+` and `3`, compute `3+4 = 7`, push it; push `*`, see `2` → pop `*` and `7`, compute `7*2 = 14`. The scan returns **14**. But `3 + 4 * 2` is **11**, because `*` binds tighter than `+` and must be evaluated first. So the apply-as-you-go operand scan is simply *wrong* on infix. What broke is precedence: in infix you cannot decide to apply an operator the moment you see it, because a higher-precedence operator might come next and has to bind first. The operand stack alone has no machinery to defer the `+` until after the `*`.

**Knob 1, the real finding — what postfix was handing you for free.** The reason the original problem never needed precedence handling is that postfix has the precedence *already baked into the token order*. Convert `3 + 4 * 2` to postfix and you get `3 4 2 * +`: the `*` sits *before* the `+` in the stream precisely because it binds tighter. The conversion from infix to postfix *is* the act of resolving precedence; once it's done, every operator appears at exactly the position where both its operands are ready, so a dumb left-to-right pop-and-apply is guaranteed correct. Postfix doesn't eliminate the precedence work — it moves it earlier and does it once, before evaluation.

The deeper why, the schema to carry forward: precedence determines the shape of the **expression tree** (in `3 + 4 * 2`, the `*` node is a child of the `+` node, because `4*2` must resolve before feeding the `+`). The three notations are three traversals of that one tree — **preorder = prefix, inorder = infix, postorder = postfix**. Your RPN evaluator is doing a post-order evaluation of the tree without ever building the tree: children (operands) are seen and pushed before their parent (operator) fires. Precedence lives in the tree's shape; postfix has already linearized that shape; therefore evaluation is precedence-free. (This one-tree-three-traversals picture is the organizing schema for the whole conversion cluster — it's developed fully in atom #4, where it collapses all six conversion problems into "read the same tree in a different order." Seeded here, harvested there.)

**The boundary this draws — the #3/#4 split.** The labor of handling an arithmetic expression cleanly factors into two stages, and that factoring *is* the line between this atom and the next:

- **#4 — infix → postfix (operator-precedence / shunting-yard):** the machine that *resolves* precedence and parentheses. Its stack holds operators, and it pops them by precedence. This is the stage the infix perturbation just proved you can't skip.
- **#3 — postfix → value (this atom, operand stack):** precedence already resolved, so it's pure pop-and-apply.

So "input is postfix" silently hands you "precedence pre-resolved." The two atoms are two halves of one pipeline, which is why they're learned back-to-back: #4 produces exactly the form #3 consumes.

---

## Postfix → Infix (GfG) — the disguised rep, and the string payload

This is the same operand-stack move as RPN, with one change: the operands are sub-expression *strings* instead of numbers, and an operator doesn't compute — it concatenates. Push each operand string; on an operator, pop the two sub-expressions, wrap them with the operator in the middle, push the combined string back. The same "second-popped is the left operand" rule holds (`s1` is the left side).

```java
static String postToInfix(String exp) {
    Deque<String> st = new ArrayDeque<>();
    for (char c : exp.toCharArray()) {
        if (isOperator(c)) {
            String s2 = st.pop();                       // right sub-expression
            String s1 = st.pop();                       // left  sub-expression
            st.push("(" + s1 + c + s2 + ")");           // wrap and push back
        } else {
            st.push(String.valueOf(c));
        }
    }
    return st.pop();
}
```

So at the skeleton level this confirms the atom's central idea once more: the move is fixed (operator pops its k operands and pushes one result), and what changes between problems is only the **payload** and what "apply" means — a number and arithmetic for evaluation, a string and concatenation for conversion. Same primitive, different payload — the exact lesson from atom #2 (char → `(char,count)` → signed int), reappearing as number → sub-expression-string.

## Perturbation findings (the disguised rep) — why every combination must be parenthesized

The suspicious specific here is that the code wraps **every** sub-expression in parentheses: `"(" + s1 + c + s2 + ")"`. It's tempting to think that's cosmetic and you could emit the leaner `s1 + c + s2`. Perturb it: drop the parens and run it on the postfix `ab+c*`, whose tree is `(a+b) * c`.

- `a`, `b` push.
- `+` pops `b`, `a` → emits `a+b`, pushes it.
- `c` pushes.
- `*` pops `c`, pops `a+b` → emits `a+b*c`, pushes it.

The no-paren output is the infix string **`a+b*c`**. Here is the bug, and it's worth keeping verbatim:

> `a+b*c` is the infix result of converting the postfix `ab+c*`. The bug is that this output string is **unfaithful**: when anyone later reads or evaluates `a+b*c` under normal infix precedence, they get `a+(b*c)`, not the `(a+b)*c` we started from. The conversion silently changed the tree.

(Note `a+b*c` is itself *infix* — it's the converter's output, not a postfix string. The input was the postfix `ab+c*`; the comparison is between the faithful `((a+b)*c)` and the unfaithful `a+b*c`.)

The transferable principle, tied to the tree schema: postfix and infix encode the expression tree's structure in two *different* ways, and the conversion has to translate one encoding into the other.

- **Postfix encodes structure by position.** `ab+c*` is unambiguous and needs no parentheses ever — the token order alone says "+ binds before ×." Reading postfix can never recover the wrong tree.
- **Infix encodes structure by precedence rules**, which can only express the *default* tree shape for free. Any tree that deviates from default precedence — like forcing `+` to bind before `*` — must be pinned down with explicit parentheses, or infix's own precedence rules will silently re-group it.

So the parentheses are not decoration; they are how the output re-injects the grouping that infix would otherwise lose. Wrapping every combination is the safe universal rule that guarantees the output tree equals the input tree. This is the deeper face of "payload scales with what you do on pop": the number payload only ever had to carry a *value*, but the string payload has to carry the *grouping* — the structure itself — which is why conversion needs parens and evaluation never did.
