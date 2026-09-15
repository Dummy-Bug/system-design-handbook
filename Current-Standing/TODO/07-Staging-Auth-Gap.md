# 07 — Staging Has No Real Auth

Found 2026-09-12 by reading the branches · **live today** · no changes made, recorded for when you want to act

> [!abstract] What this is
> Staging serves every visitor a signed session as a canned **HR admin**, with no OAuth handshake, because the branch deployed there treats staging the same way it treats a laptop. Everything below was checked against the branches rather than assumed, and nothing has been changed.

---

## What is deployed, and what it does

Staging runs **`multi-agent`** — last commit `202377f`, 2026-08-03, changing checkpointer to memory. It is 114 commits ahead of `prod` and 2 behind it.

`src/xarvis/services/session_service.py:83`:

```python
if ENV in {"local", "dev", "staging"}:
    logger.info("USING DEV AUTH PATH")
    user_data = DEV_USER
    oauth_response = DEV_OAUTH_RESPONSE
else:
    logger.info("USING REAL OAUTH PATH")
    madp_auth_code = request.query_params.get("code")
```

With `ENV=staging`, session creation never performs the MADP OAuth exchange. It hands back the canned user.

| Branch | Staging takes | Where |
|---|---|---|
| `prod` | the real OAuth path | `if ENV == "local" or ENV == "dev":` |
| **`multi-agent`, deployed on staging** | **the canned user** | `session_service.py:83` |
| `demo` | the canned user | `session_service.py:75` |
| `refactor`, `refactor-composition-wiring` | the canned user | `config.py:131`, `uses_stub_user` returns `env in {"local", "dev", "staging"}` — still true after the composition refactor, rechecked 2026-09-15 |

So this is not something `refactor` introduced. `refactor` inherited it from `multi-agent` and wrote it into a property with a docstring that says staging is in the set.

## The exposure, step by step

1. `/session` is a public route — `request_context.py:40`, on every branch.
2. A POST to it on staging takes the branch above and returns a genuine `xarvis_session` cookie, signed with the real `SESSION_JWT_SECRET`, for `DEV_USER`.
3. `validate_session` then accepts that cookie, correctly: it checks the signature, the claims and the cache entry. Nothing here is broken — the session is real.
4. Every subsequent `/api/v1/chat` call runs as that user, with the token in `DEV_OAUTH_RESPONSE`, against the real HRMS that staging points at.

**`SKIP_SESSION_AUTH=false` is a red herring.** It is false in staging on every branch, and it only controls the middleware shortcut at `request_context.py:52`, which staging never reaches. The gap is upstream of it, in session creation.

**On `refactor-composition-wiring`, committed 2026-09-15, the shape changed and the gap did not.** The flag is `STUB_SESSION_USER` (the old name still accepted) and startup refuses it outside local and dev. The session check is the `require_session` dependency on the protected router, not middleware, and `/api/v1/session` sits outside that router. Session creation still takes the canned-user path for `ENV=staging`, so steps 1 to 4 above hold unchanged.

## What makes it worse than an open endpoint

> [!warning] The canned user is an HR admin
> `context/dev_user.py` on the deployed branch:
>
> ```python
> role="ROLE_HR_ADMIN",
> authorities=["ROLE_HR_ADMIN"],
> ```
>
> Combined with the finding in [[05-Repo-Audit-xarvis]] — `allowed_emails` in `tool_access_helper.py` is built and never read, so any caller holding `ROLE_HR_ADMIN` passes the guard — every admin tool is reachable by anyone who can open the staging URL. Not one employee's record: the admin surface.

> [!warning] The allowlist was fixed on `refactor`, and it does not narrow this by one inch · checked 2026-09-12
> `is_allowed_admin()` is now real and enforced at two sites. The obvious hope is that this closes the staging hole as a side effect, since a canned user would fail the list.
>
> It does not. `context/dev_user.py` gives `DEV_USER` the email **`amal@repute.net`**, and that address is the seventh entry in `ADMIN_ALLOWED_EMAILS`. So the canned user passes `is_allowed_admin` at `chat.py` and passes it again inside `has_tool_access`, and reaches the full admin tool surface exactly as before.
>
> **The exposure is unchanged.** Worth knowing precisely, because the fix landing elsewhere makes it look handled from a distance, and every option in the table below still costs what it cost.

**Every visitor is the same person.** There is one canned identity, so there is no attribution: the logs and traces cannot separate the co-founder demoing from anybody else who found the URL.

**Tracing is on, into a real project.**

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=chatbot-stg
```

Every conversation on that deployment is written to LangSmith with a real key, carrying whatever the HRMS returned. Worth knowing alongside [[project_langsmith_trace_window]], since that project is also where trace material comes from.

**What limits it:** `CHECKPOINTER_MODE=memory` on that branch, so conversations are not persisted to DynamoDB. The blast radius is what the canned admin can read live, not a stored history.

## The options, for when you want them

Recorded rather than recommended, since you are fixing this yourself.

| | What it takes | What it costs |
|---|---|---|
| Close it on the deployed branch | drop `"staging"` from `session_service.py:83` on `multi-agent` | the co-founder cannot demo from staging any more |
| Close it in the new code too | the same set in `refactor`'s `uses_stub_user`, `config.py:127` | nothing, until refactor lands |
| Keep a demo path, branch | `demo` already exists and already has staging in the stub set, at `session_service.py:75` | it is stale since 2026-07-21 and pre-refactor, so it needs re-cutting |
| Keep a demo path, flag | one variable, say `DEMO_STUB_USER`, with a startup rule refusing it outside staging | a few lines, and no branch to keep in sync |

The last row is [[05-Flag-Per-Capability]] applied to this: a switch named for the capability rather than a branch or an environment comparison, and [[03-Refuse-To-Start]] for the rule that refuses it anywhere else.

## Open

- [ ] Decide whether staging closes now or when `refactor` lands
- [ ] Decide how the demo keeps working — re-cut `demo`, or a flag
- [ ] Check whether anything outside the team has actually reached staging, from the LangSmith `chatbot-stg` traces
- [ ] `allowed_emails` in `tool_access_helper.py` is still dead code, which is what makes the admin role reachable — tracked in [[05-Repo-Audit-xarvis]]
