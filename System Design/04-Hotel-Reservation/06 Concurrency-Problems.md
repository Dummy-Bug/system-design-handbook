# Scenario 1

## Same User Clicks Book Multiple Times

### Problem (What Actually Happens)

- Double-clicks.
- Mobile retry on network drop.
- Browser auto-resubmits on refresh.
- Payment gateway timeout causes user to retry.
- Load balancer retries POST.

Result:
- Duplicate reservations.
- Double charge.
- Inventory corruption.

# Solution 1: Client-Side Click Prevention

### What We Do

When the user clicks **Reserve / Book**:

- Disable the button immediately.
- Show loading spinner.
- Block further clicks.
- Prevent form resubmission.
- Optionally debounce click events.

### Example Behavior

- Button becomes greyed out.
- Text changes to “Processing…”.
- Additional clicks are ignored until response arrives.

### Why This Is Added

- Prevents accidental double clicks.
- Reduces duplicate requests from impatient users.
- Improves perceived responsiveness.
- Lowers unnecessary backend traffic.

This is standard UX hygiene.

---

# Why This Solution Is Not Reliable

Client-side protection is **not security** and **not concurrency control**.

---

## 1. JavaScript Can Be Bypassed

User can:

- Disable JavaScript.
- Manually send HTTP requests using Postman or curl.
- Trigger requests from browser console.
- Replay the same request payload.

Result:

Backend still receives multiple booking requests.

---

## 2. Network Retries Ignore UI State

Even if UI is disabled:

- Browser may retry POST on timeout.
- Mobile apps retry automatically.
- Load balancer retries upstream calls.

UI state does not control network behavior.

---

## 3. Page Refresh Resubmits Forms

User presses:

`Ctrl + R`

Browser asks:

“Resend form data?”

If user accepts:

Same booking request is sent again.

---

## 4. Multi-Tab Problem

User opens two tabs:
- Clicks Book in both.
- UI prevention works per tab only.
- Backend still receives duplicates.

---

# Conclusion

Client-side disabling:

- Reduces accidental duplicates.
- Improves UX.
- Does NOT guarantee correctness.
- Does NOT prevent double booking.
- Must NEVER be the only protection.