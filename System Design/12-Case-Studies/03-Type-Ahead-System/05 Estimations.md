## User Scale Assumptions

`Monthly Active Users (MAU) ≈ 1 Billion.`
`Daily Active Users (DAU) ≈ 20% of MAU ≈ 200 Million`

---

## Search Behavior Assumptions

`Average searches per user per day ≈ 5`

Total searches per day:

`200M users × 5 searches ≈ 1 Billion searches/day`

---

## Average QPS Calculation

Seconds per day:

`24 × 60 × 60 = 86,400 seconds`

Approximate baseline QPS:

`1,000,000,000 / 100,000 ≈ 10,000 QPS`

Rounded for engineering safety margin.

---

## Typeahead API Call Estimation (With Debouncing)

Because client uses debouncing:

- Not every keystroke triggers API call.
- User typically pauses typing multiple times.

Assumption:

`3 to 5 API calls per search interaction`

Worst case estimation:

`5 API calls × 10,000 QPS`

Result:

`≈ 50,000 Typeahead QPS (Average)`

---

## Write Path Load (Search Submission)

Assumption:

`50% of DAU generate new queries`

Calculation:

`50% × 200M DAU = 100M write events per day`

Average write QPS:

`100,000,000 / 100,000 ≈ 1000 QPS`

Write load is small compared to read traffic.

---

## Peak Traffic Estimation

Autocomplete traffic is bursty.

Apply peak multiplier:

`Peak factor ≈ 20x`

Peak QPS calculation:

`20 × 5 × 10,000`

Result:

`≈ 1,000,000 QPS (Peak)`

---

## Summary Table

| Metric                    | Value       |
| ------------------------- | ----------- |
| MAU                       | 1 Billion   |
| DAU                       | 200 Million |
| Daily Searches            | 1 Billion   |
| Average Typeahead QPS     | 50,000      |
| Write QPS (Search Submit) | 1000        |
| Peak QPS                  | ~1 Million  |

---