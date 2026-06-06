# Stack Atom 04 — Expression: operator-precedence stack (shunting-yard)

*2026-06-05 12:41*

## The problem (Infix → Postfix, GfG)

Given an arithmetic expression in infix form — operators between operands, with precedence, associativity, and parentheses — produce the equivalent postfix string. `a*(b+c)/d` → `abc+*d/`. Operators: `+ - * / ^`; operands single chars `a–z A–Z 0–9`.

## ① Trigger

You must linearize an infix expression while honoring precedence and parentheses, and you *cannot* emit an operator the moment you read it — a higher-precedence operator might come next and has to bind first. So operators have to **wait**, and be released in the right order. A stack that holds the deferred operators, flushed by precedence, is the tool. (This is the other half of the #3 pipeline: this atom *produces* the postfix that #3 consumes.)

## ② Motivation — why an operator stack (contrast with #3)

Atom #3 held **operands** and applied them; this atom holds **operators** and defers them. The reason you can't just stream operators to the output like operands: operator output order must match precedence, which you don't know until you've seen what comes after. So you park each operator on a stack and only flush it when an operator of equal-or-higher binding force arrives (or a `)` / end closes its scope). Operands have no such waiting — their position is already final, so they go straight to output.

## ③ The move

- operand → append to output.
- `(` → push (a barrier).
- `)` → pop operators to output until `(`, then discard the `(`.
- operator `c` → while the stack top is an operator that should bind before `c`, pop it to output; then push `c`. ("Should bind before" = top has higher precedence, **or** equal precedence and `c` is left-associative.)
- end of scan → flush all remaining operators to output.

```java
while (!stack.isEmpty() && stack.peek() != '('
       && (prec(stack.peek()) > prec(c)
           || (prec(stack.peek()) == prec(c) && c != '^')))   // ^ = only right-assoc
    out.append(stack.pop());
stack.push(c);
```

## ④ Costumes

- Infix → Postfix (GfG) — output is postfix.
- Infix → Prefix — reverse the input, swap `(`↔`)`, run the same algorithm, reverse the result (mirror; one note, not a separate rep).
- Basic Calculator II (227) — same precedence machinery, but instead of *emitting* operators you *apply* them to an operand stack on the fly (synthesis of #3 + #4).

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| operand stack (#3) | #3 holds operands and *applies* on an operator token (input already postfix); this holds **operators** and *defers* them by precedence (input is infix, precedence not yet resolved) |
| matching (#1) | matching's whole job is the parentheses; here parens are one sub-rule (`)` flushes to `(`) inside a larger precedence machine |

## ⑥ Reflex check

Prompt: *infix expression → postfix, respecting precedence + parens — move?*
Answer: *operator-precedence stack. operand → output; `(` → push; `)` → flush to `(`; operator → flush all stack operators that bind first (higher prec, or equal prec & left-assoc), then push; end → flush. Operators wait because their output order depends on what comes after.*
