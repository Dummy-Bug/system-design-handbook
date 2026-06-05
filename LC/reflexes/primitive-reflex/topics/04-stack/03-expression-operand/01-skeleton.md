# Stack Atom 03 — Expression: operand stack

*2026-06-05 12:03*

## The problem (Evaluate Reverse Polish Notation, LC 150)

Given an arithmetic expression already in postfix (Reverse Polish) form as a token array — e.g. `["2","1","+","3","*"]` meaning `(2+1)*3` — evaluate it to a single integer. Operators are binary `+ - * /`; division truncates toward zero.

## ① Trigger

You're handed an expression where each operator's operands are the values produced just before it, and you have to combine them bottom-up. The thing an operator needs is "the last k results computed so far," and after it fires its result becomes an operand for something later. That last-k-results-with-LIFO-access pattern is a stack.

## ② Motivation — why a stack

You can't evaluate with a couple of plain variables, because the nesting depth is unbounded: `((((...))))` can stack arbitrarily many half-finished operands waiting for their operator. Each operator consumes the most-recent k operands and replaces them with one result, which then waits as an operand for a later operator. "Give me the most recent k values, replace them with one" is exactly push/pop on a stack. The stack holds operands; an operator is the event that pops them.

## ③ The move

- token is a number → push it (as a value).
- token is an operator → pop its k operands (k = 2 for binary), apply the operator, push the single result back.
- end of scan → exactly one value remains: the answer.

For non-commutative operators (`-`, `/`) the order matters: the operand popped **second** is the left-hand side. With `a b -` you push `a` then `b`, pop `x = b` then `y = a`, and compute `y - x = a - b`.

```java
Deque<Integer> st = new ArrayDeque<>();
for (String t : tokens) {
    if (isOperator(t)) {
        int x = st.pop();              // right operand (pushed last)
        int y = st.pop();              // left operand  (pushed first)
        st.push(apply(y, x, t));
    } else st.push(Integer.parseInt(t));
}
return st.pop();
```

## ④ Costumes

- Evaluate postfix → **number** payload (compute and push the result). LC 150.
- Postfix → Infix / Postfix → Prefix → **string** payload: on an operator, pop two sub-expression *strings*, wrap them with the operator (`"(" + y + op + x + ")"`), push the combined string. Identical move, the payload is a string instead of a number.
- Prefix-source versions = the same move with the scan **reversed** (right-to-left). Not a separate rep — one note covers them.

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| adjacent-collapse (#2) | collapse pops when the **top interacts with the incoming element** (data-driven, variable count); here you pop a **fixed arity** the moment an **operator token** arrives (operator-driven) |
| operator-precedence stack (#4) | this atom holds **operands** and *applies* them — it works only because the input is **postfix** (precedence already resolved); #4 holds **operators** and *resolves* precedence. Infix input forces #4 first (see notes, perturbation) |

## ⑥ Reflex check

Prompt: *expression in postfix, evaluate it — move?*
Answer: *operand stack; number → push, operator → pop its k operands (second-popped = left), apply, push result. One value left at the end. Works because postfix already froze precedence into token order.*
