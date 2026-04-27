
> [!info] Last seen privacy — server-side enforcement, same mutual rule as read receipts
> Bob hides his last seen. The server stops serving it. The mutual rule applies.

---

## Bob turns off last seen

Bob goes to Settings → Privacy → Last Seen → Nobody.

From this point, when Alice opens a chat with Bob:

```
Alice opens conv_abc123
→ server checks: does Bob have last_seen privacy ON or OFF?
→ Bob has it OFF (hidden from everyone)
→ server: do not include last_seen in response
→ Alice sees: nothing where last seen used to be
```

Not "last seen a long time ago." Not a fake timestamp. Just blank — WhatsApp shows no last seen indicator at all for Bob.

---

## The mutual rule

Same principle as read receipts: **you cannot hide yourself while watching others.**

```
Bob turns off last seen
→ Alice cannot see Bob's last seen      ✓ (Bob wanted this)
→ Bob cannot see Alice's last seen      ✗ (Bob loses this)
```

Even though Alice has last seen ON — her timestamp is being recorded — Bob cannot see it. The server checks Bob's setting when serving him Alice's last seen and withholds it.

---

## Why this is the right product decision

Without the mutual rule:

```
Bob: last seen OFF
  → Bob browses WhatsApp silently — Alice never knows when he's active
  → Bob can see Alice was "last seen 2 minutes ago" — knows she's ignoring him
```

This is surveillance asymmetry again. Bob has full information about Alice's activity. Alice has none about Bob's. WhatsApp's product team decided this is not acceptable — same reasoning as read receipts. Privacy must be symmetric.

---

## The mutual rule applies at the conversation level

If Bob has last seen OFF:

```
ALL of Bob's contacts: cannot see his last seen
Bob: cannot see ANY contact's last seen
```

It's not per-conversation. It's all-or-nothing at the account level. Bob can't say "hide my last seen from Alice but show it to Carol." The setting applies globally.

---

## What about "Online" status?

Last seen privacy does NOT hide the "Online" indicator by default. If Bob is actively using WhatsApp, Alice can still see "Online" even if Bob has last seen hidden.

WhatsApp has a separate setting for this — hiding online status — which was added later (2022) after user demand. The design principle is the same: mutual rule applies. If you hide your online status, you can't see others' online status either.

For this design, treat last seen and online status as part of the same privacy layer — both server-enforced, both mutual.

> [!tip] Interview framing
> "Last seen privacy is enforced server-side. When Alice requests Bob's last seen, the server checks Bob's privacy setting and withholds the timestamp if it's hidden. The mutual rule means Bob also can't see Alice's last seen — the server applies the same check when Bob requests Alice's status. All-or-nothing at the account level."
