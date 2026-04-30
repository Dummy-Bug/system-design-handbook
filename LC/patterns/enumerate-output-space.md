# Pattern: Enumerate the Output Space

When the output space is small and bounded (e.g. 3-digit numbers = 900 candidates), iterate over **possible outputs** and check feasibility against input — instead of iterating over input combinations and trying to count.

Trigger signals:
- Output is a number/string with bounded length
- Asked for *distinct* / *unique* count (uniqueness is free if you iterate over outputs directly)
- Combinatorics framing keeps producing nasty case splits or duplicate-handling math

## Problems

- [Find Numbers with Even Number of Digits](https://leetcode.com/problems/find-numbers-with-even-number-of-digits/)
- [Finding 3-Digit Even Numbers](https://leetcode.com/problems/finding-3-digit-even-numbers/description/)
- [Unique 3-Digit Even Numbers](https://leetcode.com/problems/unique-3-digit-even-numbers/description/)
