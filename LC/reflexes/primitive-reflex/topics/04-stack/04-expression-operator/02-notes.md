# Stack Atom 04 — notes

## Infix → Postfix (GfG) — the announced rep

The job is to turn an infix expression into postfix while honoring precedence, associativity, and parentheses. The defining difficulty — the thing that makes this non-trivial in a way #3 wasn't — is that you cannot emit an operator the instant you read it. In `a + b * c`, when you reach the `+` you don't yet know whether the next operator binds tighter (it does: `*`), and if it does, the `*` has to be emitted *before* the `+`. So operators have to be deferred and released in precedence order. Operands have no such problem: an operand's position in the output is already final, so operands stream straight to the output. That asymmetry is the whole atom — the stack holds the **waiting operators**.

The release rule: when a new operator `c` arrives, first flush every operator already on the stack that should bind before `c`, then push `c`. "Should bind before" means the stack-top operator has strictly higher precedence, or equal precedence with `c` left-associative (see the associativity section below). Parentheses are a self-contained sub-rule: `(` is pushed as a barrier, and `)` flushes operators back to the matching `(` and discards it. At the end, whatever operators remain are flushed.

```java
class Solution {

    private static int prec(char c) {
        if (c == '^') return 3;
        if (c == '*' || c == '/') return 2;
        if (c == '+' || c == '-') return 1;
        return -1;                       // '(' or anything non-operator
    }

    private static boolean isOperator(char c) {
        return c == '+' || c == '-' || c == '*' || c == '/' || c == '^';
    }

    public static String infixToPostfix(String s) {
        StringBuilder out = new StringBuilder();
        Deque<Character> stack = new ArrayDeque<>();

        for (char c : s.toCharArray()) {
            if (c == '(') {
                stack.push(c);
            } else if (c == ')') {
                while (!stack.isEmpty() && stack.peek() != '(') {
                    out.append(stack.pop());
                }
                stack.pop();                          // discard the '('
            } else if (isOperator(c)) {
                while (!stack.isEmpty() && stack.peek() != '('
                       && (prec(stack.peek()) > prec(c)
                           || (prec(stack.peek()) == prec(c) && c != '^'))) {
                    out.append(stack.pop());
                }
                stack.push(c);
            } else {
                out.append(c);                        // operand
            }
        }
        while (!stack.isEmpty()) {
            out.append(stack.pop());
        }
        return out.toString();
    }
}
```

### Step 2 — worked example `(a+b)*c^d-e`

Stack shown with top on the left.

| read | action | output | stack |
|---|---|---|---|
| `(` | push barrier | | `(` |
| `a` | operand → out | `a` | `(` |
| `+` | top is `(` → push | `a` | `+ (` |
| `b` | operand → out | `ab` | `+ (` |
| `)` | flush to `(`: pop `+`; discard `(` | `ab+` | |
| `*` | empty → push | `ab+` | `*` |
| `c` | operand → out | `ab+c` | `*` |
| `^` | prec(`*`)=2 < prec(`^`)=3 → push | `ab+c` | `^ *` |
| `d` | operand → out | `ab+cd` | `^ *` |
| `-` | pop `^` (3>1), pop `*` (2>1), push `-` | `ab+cd^*` | `-` |
| `e` | operand → out | `ab+cd^*e` | `-` |
| end | flush | `ab+cd^*e-` | |

Result `ab+cd^*e-` = `((a+b)*(c^d))-e`. ✓

### Step 3 — edge cases
1. Single operand `a` → `a`.
2. Equal-precedence left-assoc `a-b-c` → `ab-c-` (equal precedence *does* pop for `+ - * /`).
3. Right-assoc `a^b^c` → `abc^^` (equal precedence does *not* pop for `^`).
4. Redundant parens `((a))` → `a` (`)` flushes only to the nearest `(`).
5. Parens overriding precedence `(a+b)*c` → `ab+c*`.
6. Single-char operands assumed (GfG constraint); multi-digit numbers would need token grouping.

Verified against all three problem examples: `a*(b+c)/d`→`abc+*d/`, `a+b*c+d`→`abc*+d+`, `(a+b)*(c+d)`→`ab+cd+*`.

## Associativity — the tiebreaker (the load-bearing subtlety)

Precedence and associativity answer two different questions, and conflating them is the classic bug here.

- **Precedence** decides between operators of *different* levels: `*` binds before `+`, so in `a+b*c` the `*` wins.
- **Associativity** is the tiebreaker for operators of the *same* level, where precedence says nothing. `a - b - c` could mean `(a-b)-c` or `a-(b-c)`; associativity picks. Left-associative (`+ - * /`) means the **left** operator binds first → `(a-b)-c`. Right-associative (`^`) means the **right** binds first → `a^(b^c)`.

On the stack this becomes a rule about the equal-precedence case. When a new operator arrives and an equal-precedence operator already sits on the stack (it is, by construction, to the *left* of the incoming one):

- left-assoc → the left one binds first → **pop it now** (emit before the new one).
- right-assoc → the right one binds first → **don't pop** → let the new one stack on top so it's emitted first.

That is the single clause `prec(top) == prec(c) && c != '^'`. Because `^` is the only right-associative operator, `c != '^'` exactly means "incoming operator is left-associative." So equal precedence pops for `+ - * /` and skips for `^`:

- `a-b-c`: the second `-` sees an equal `-` on top, `c != '^'` is true → pop → `ab-c-` = `(a-b)-c`. ✓
- `a^b^c`: the second `^` sees an equal `^` on top, `c != '^'` is false → don't pop, push on top → `abc^^` = `a^(b^c)`. ✓

If you dropped the `c != '^'` and treated `^` as left-assoc, `a^b^c` would wrongly produce `ab^c^` = `(a^b)^c`. That one clause is the entire difference between right- and left-associativity. Strictly higher precedence always pops regardless of associativity — associativity only ever decides the *equal*-precedence case.

## The tree schema (harvested) — one tree, three traversals

This is the organizing picture seeded back in #3, now paying off across the whole expression cluster. Every arithmetic expression is a binary tree: operators are internal nodes, operands are leaves, and the *shape* of the tree is exactly what precedence and associativity determine (`*` is a child of `+` in `a+b*c` because `b*c` must resolve first). The three notations are simply three traversals of that one tree:

- **preorder** (node, left, right) = **prefix**
- **inorder** (left, node, right) = **infix**
- **postorder** (left, right, node) = **postfix**

That single fact collapses the entire conversion family. Postfix→Infix (atom #3's disguised rep) was reading a post-order encoding and re-emitting it in-order — and it needed parentheses precisely because in-order alone loses the tree shape unless you reinject it. Infix→Postfix (this atom) is the reverse: take the in-order form and re-emit it post-order, and the operator-precedence stack is the machine that recovers the tree shape from infix's precedence rules and linearizes it post-order — all without ever materializing the tree. Evaluation (RPN, #3) is post-order evaluation of the same tree. So #3 and #4 aren't two unrelated tricks; they're two traversals of one structure, which is why the operator stack here produces exactly the postfix the operand stack there consumes.

---

## Basic Calculator II (LC 227) — the disguised rep (the #3 ⊕ #4 synthesis)

The problem: evaluate an infix expression with `+ - * /`, non-negative integers, and spaces — but **no parentheses**. The first approach that falls out, once you've done #3 and #4, is the literal pipeline: run shunting-yard to turn the infix into postfix (#4), then evaluate the postfix (#3). That is completely correct and O(n) — and it's worth saying plainly that this two-pass pipeline is a perfectly good interview answer, because it's the honest thing a chunked #3+#4 hands you for free.

But it's not the best for *this* problem, and the reason is the one specific thing 227 is missing: parentheses. The cleaner model is to see the whole expression as a **sum of terms**, where a "term" is a maximal `*`/`/` chain. `3 + 2*2` is `term(3) + term(2*2)` = `3 + 4`. Because there are no parentheses, every `+`/`-` simply starts a new term, and the answer is just the sum of all terms. That single observation gives a one-pass solution with an operand stack:

- `+` → start a new term → push `num`.
- `-` → start a new negative term → push `-num`.
- `*` → this number extends the current term → pop the top, multiply, push back.
- `/` → same → pop the top, divide, push back.
- at the end → sum the stack.

The `+`/`-` numbers sit on the stack as waiting terms; the `*`/`/` numbers fold immediately into the top term, so each term is fully resolved before the final sum — which is how precedence gets handled in a single forward pass. The operator itself never goes on the stack; it lives in a single variable `op` that holds the most recent operator, used exactly one step later (when the next number finishes).

```java
public int calculate(String s) {
    if (s == null || s.isEmpty()) return 0;
    Deque<Integer> stack = new ArrayDeque<>();
    int num = 0;
    char op = '+';                                   // operator preceding the current number
    int n = s.length();
    for (int i = 0; i < n; i++) {
        char c = s.charAt(i);
        if (Character.isDigit(c)) num = num * 10 + (c - '0');   // build multi-digit
        // flush at a real operator, OR at the very end (even if the last char is a space)
        if ((!Character.isDigit(c) && !Character.isWhitespace(c)) || i == n - 1) {
            if (op == '+')      stack.push(num);
            else if (op == '-') stack.push(-num);
            else if (op == '*') stack.push(stack.pop() * num);
            else if (op == '/') stack.push(stack.pop() / num);
            op = c;
            num = 0;
        }
    }
    int result = 0;
    while (!stack.isEmpty()) result += stack.pop();
    return result;
}
```

The recurring bug worth keeping: the flush condition must fire at the **end of the string even when the last character is a space**. An earlier version guarded the flush with `&& ch != ' '`, which silently dropped the final number on inputs like `" 3/2 "` (a real LC 227 test) — it returned `3` instead of `1`, because the trailing space met `i == len-1` but failed the space guard, so the `2` was never folded by `/`. The fix is to let the end-of-string condition flush regardless of the character; setting `op` to a space on that last step is harmless since the loop is over. (Also note `-3/2 = -1` is correct: Java truncates toward zero, so pushing `-num` then dividing matches "truncate toward zero".)

There's a tighter O(1)-space version that drops the stack entirely — keep a running `result` and the value of the `lastTerm`; on `+`/`-` add `lastTerm` into `result` and set `lastTerm = ±num`; on `*`/`/` do `lastTerm = lastTerm */ num`; add the final `lastTerm` at the end. Same idea, the stack was only ever holding terms that get summed, so a single accumulator suffices.

## Perturbation findings (227) — the load-bearing "no parentheses"

The suspicious specific in 227 is precisely what it *omits*: parentheses. That absence is doing all the work. With no parens, the expression is one flat sum of terms, so a single forward pass with one operand stack (or even O(1)) is enough — there is never any nested scope to remember.

Perturb it: add parentheses back, e.g. `1 + (4 + 5*2) - 3`. Now the flat sum-of-terms model breaks, because a parenthesised group is a self-contained sub-expression whose value isn't known until its `)`, and it must be fully resolved before it can combine with the outer terms. The single shared stack and end-of-string sum no longer correspond to one flat expression. What you need is to **save the outer computation in progress when you hit `(`** (the result-so-far and the pending sign), start the inner expression fresh, and then on `)` **fold the inner value back into the saved outer state**. That "save the parent's partial work on open, fold the child's result in on close" is a distinct primitive — **nested-structure fold-up**, atom #5. Basic Calculator I (224, `+ −` with parens) and Basic Calculator III (772, the full set) are exactly 227 *plus* this fold-up step.

So the boundary is clean: the single-pass operand-stack solution works **because there is no nesting**. Nesting is a different primitive, and adding parentheses is the perturbation that crosses from this atom into #5. (This is the same shape as the #3 perturbation, where "input is postfix" silently handed you "precedence pre-resolved" — here "no parentheses" silently hands you "no nesting".)

> **Logging honesty:** the disguised rep was *guided*. The user self-derived the two-pass convert→evaluate pipeline cold (a valid answer), but the single-pass sum-of-terms solution came from being walked through the model, pseudocode, and traces, and the trailing-space bug was diagnosed jointly. So this is acquisition, not a cold ownership rep — the cold certificate for atom #4 is still owed on a Phase-2 blind deal.
