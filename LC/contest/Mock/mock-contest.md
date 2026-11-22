# Mock Contest Rules

How mock contests are built, levelled and judged. Read this before generating a mock. Set 2026-11-20 after mocks 1 and 2. Each mock is logged as `mock-NN.md` inside a folder for the range it was run in, currently `1450-1600/`; when the band moves up, the new range gets its own folder and the numbering carries on.

**Since 2026-11-22 mocks are occasional, not the main format.** The main format is single timed problems from 1550-1599, with rules in `LC/CLAUDE.md`. Mocks run about once every week or two to check that the speed carries over. The mechanic coverage below is now counted from single problems as well as mocks.

## Building a mock

- **Format:** four unseen problems from 1450-1599, rating rising from Q1 to Q4, four different mechanics, no premium, nothing already solved, 90 minutes, all four handed over as bare links at once. Same protocol as a solve: silent logging, Steps 2 and 3 before every submit, a WA costs 5 minutes, and anything unsolved at 90 minutes gets the step-by-step explanation.
- **Cover the band, not one mechanic.** Greedy is about 23% of the LeetCode tags in 1500-1599, yet it filled about 4 of the first 10 problems seen in mocks 1-3, while sliding window, stack or monotonic stack, bit manipulation, matrix and DFS, BFS, tree or graph had not come up once (checked 2026-11-21). Pick first from the mechanics not yet solved twice without help in this band (see the move-up table), so the mocks cover it over time; the mechanic still has to be load-bearing.
- **Unopened problems go back into the pool.** A mock problem never opened, or read for under 5 minutes, is still unseen and can be dealt in a later mock in its band; one above the band waits for the band to move up. Its mechanic stays hidden until it is dealt again. Set by the user on 2026-11-21. As of then: minimum-time-to-make-rope-colorful (1574, mock 3 Q4) and number-of-subarrays-with-lcm-equal-to-k (1560, mock 2 Q1) are reusable now; largest-palindromic-number (1636, mock 2 Q4) waits for 1500-1649.
- **During a mock, Claude only logs.** A mock should feel like a proper LC contest, so while it runs Claude logs whatever the user says and nudges nowhere, including not asking for Steps 2 and 3 before a submit; this overrides the refuse-code-until-Steps-2-and-3 rule in `LC/CLAUDE.md` for mocks. Steps 2 and 3 stay the user's own discipline. Missed cases and skipped steps are named only in the analysis after the mock. Set by the user on 2026-11-21, after mock 3.
- **Difficulty is personal, not just rating.** Judge each problem on rating, acceptance rate, mechanic (owned bucket or weak spot), and whether it is a classic or a known trick for the user. After each mock the user gives one word per problem (EASY, MEDIUM, HARD, HELL); use those words to recalibrate what each level means.
- **Levels.**

| Level  | What it is                                                                             |
| ------ | -------------------------------------------------------------------------------------- |
| EASY   | lower half of the band, acceptance mostly 60% or more, owned buckets, 2-3 classics     |
| MEDIUM | ratings spread across the band, mixed acceptance rates, 1-2 classics, 1 weak spot      |
| HARD   | upper half of the band, acceptance mostly under 50%, 2 or more weak spots, 0-1 classic |
| HELL   | all four 1550-1599, acceptance under about 45%, weak spots, no classics                |
| MIXED  | some problems easy for the user and some hard, like a real contest's slope             |

- **Choosing the next level** (the user's rule, 2026-11-20):
  - **After a bad mock, never HARD or HELL.** The next one is EASY, MEDIUM or MIXED.
  - **Go by the trend, not one mock.** Read the last 2-3 mocks: poor for 2-3 in a row means take it down a little; good for 2-3 in a row means step it up.
  - **Calibration takes about 7 mocks.** Only then is it clear what EASY, MEDIUM and the rest actually mean for this user (EASY too easy, MEDIUM really medium, and so on); until then, choose cautiously and lean on the one-word labels.

- **The level is hidden.** Never say the level, or anything that gives it away, before or during a mock. Reveal it only in the debrief, after the user's one-word labels.
- **Supply:** unsolved counts on 2026-11-20, before removing premium: 1450-1499 78, 1500-1524 46, 1525-1549 45, 1550-1574 21, 1575-1599 11. The top is thin, so HELL can run only 2-3 times and HARD spreads its Q4s across 1550-1599.
- **History:** mock 1 (2026-11-19, 1479-1588, three classics) 3 of 4, no WA, 18-20 minutes each. Mock 2 (2026-11-20, 1560-1636, outside the band, no classics) 1 of 4, one WA; the user called it HARD to HELL-ish. Mock 3 (2026-11-21, 1477-1574) 2 of 4, three WAs, burned out by the end. Mock 4 (2026-11-22, 1523-1571, MIXED as built, MEDIUM by the user) 3 of 4, two WAs, Q4 AC after time.

## When to move the band up

Set 2026-11-20. Mocks are the gate, because Sunday contests are too uneven: across the last 60 weeklies the middle half of Q2s ran 1407-1608, and some go past 1700. Getting good in mocks shows up on Sunday later; mock 2 felt very similar to a Sunday contest.

| Signal            | Role                                                                                                                                     |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Mocks             | The gate. HARD mocks going well 2-3 times in a row: 3 or more solved, most in about 25 minutes or less                                   |
| Mechanic coverage | Also a gate. Every core mechanic solved twice and every middle one once, without help, in this band's mocks; see Mechanic coverage below |
| One-word labels   | Confirmation: problems at 1550-1599 have started to feel MEDIUM or EASY                                                                  |
| Sunday and rating | Not a gate, they lag. Rating still moves the band if it climbs to about 1580-1600                                                        |

Step up by about 50 points (to 1500-1649), and start the new band at MEDIUM or MIXED.

## Mechanic coverage

Set 2026-11-21, after mocks 1-3 turned out greedy-heavy. Winning mocks is not enough to move up; the mocks have to have covered the band. The list comes from the LeetCode tags of the 195 problems in 1500-1599 (`zerotrac-data/band_1500_1549_lctags.tsv` and `band_1550_1599_lctags.tsv`; 1450-1499 has no LeetCode tags locally). A problem can carry several tags, so the shares overlap. Tags that name the input rather than the idea (Array, String, Matrix, Design, Linked List, Iterator, Data Stream, Queue) are not mechanics.

- **Solved without help** means no hint, no step-by-step explanation and no editorial; a WA then AC still counts.
- **Each problem counts once,** under the idea that actually solves it, named in that mock's debrief. LeetCode's tags are noisy, so the debrief decides, not the tag.
- **Counted across all of the band's mocks,** not only the qualifying HARD ones. The tally is recounted from the mock logs at each debrief.

**Core, 2 solves without help each (26 in all):**

| Mechanic                                    | Share |
| ------------------------------------------- | ----: |
| Hash table / counting                       |   31% |
| Greedy                                      |   23% |
| Math, incl. number theory and combinatorics |   23% |
| Sorting, when the order is the key idea     |   18% |
| Two pointers                                |    8% |
| DP                                          |    8% |
| Sliding window                              |    8% |
| Bit manipulation                            |    8% |
| Prefix sum                                  |    8% |
| Enumeration                                 |    6% |
| DFS / BFS / tree / graph                    |    6% |
| Binary search                               |    6% |
| Stack / monotonic stack                     |    5% |

**Middle, 1 solve without help each (5 in all):**

| Mechanic           | Share |
| ------------------ | ----: |
| Simulation         |    5% |
| Heap               |    3% |
| Backtracking       |    3% |
| Trie               |    2% |
| Divide and conquer |    2% |

**Tail, not gated:** string matching, binary search tree, ordered set, union-find, game theory, sweep line, rolling hash and the rest, each 1.5% of the band or less. Some have only 2 problems in the whole of 1500-1599, too few to set up two solves.

**Standing after mocks 1-4 and the singles of 2026-11-22:** 11 of 31. Hash table / counting 1 (longest-palindrome-by-concatenating-two-letter-words 1557, single #41); simulation 1 of 1 (count-collisions-on-a-road 1581, re-solve of #30, counted because no unseen simulation problem is left in 1550-1599); Greedy 2 (minimum-deletions-to-make-array-beautiful 1510, maximum-points-after-enemy-battles 1591); prefix sum 1 (minimum-sum-of-mountain-triplets-ii 1479); DP 1 (climbing-stairs-ii 1560); binary search 1 (successful-pairs-of-spells-and-potions 1477); two pointers 1 (minimum-length-of-string-after-deleting-similar-ends 1502); bit manipulation 1 (maximum-xor-for-each-query 1523); sliding window 1 (length-of-longest-subarray-with-at-most-k-frequency 1535); DFS / BFS / tree 1 (time-needed-to-inform-all-employees 1561).
