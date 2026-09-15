#config #pydantic #pydantic-settings #deployment #python

**One setting names where the service is running, and then everything else is worked out from it.** That is convenient until a capability needs to move on its own — at which point a condition that records where the service is cannot say what it is allowed to do.

# A Flag Per Capability

> [!info] A gate is any line that decides whether some behaviour happens: seeding demo data, enabling an agent, calling the real payment API. This note is about what a gate should read — the place the service is running, or a switch named for the behaviour itself.

## One value decides everything else

A service that runs in more than one place needs one setting naming the place, held to a fixed set so a typo cannot invent a fifth environment — which is [[02-Names-And-Types]] applied to the most important field in the file.

`src/config_lab/note05/a_one_value_many_gates.py`:

```python
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: Literal["local", "dev", "staging", "prod"] = "local"


settings = Settings()

print(f"ENV={settings.env}")
print("  seed demo data          ", settings.env != "prod")
print("  show errors in responses", settings.env != "prod")
print("  onboarding agent enabled", settings.env != "prod")
print("  use the real payment API", settings.env == "prod")
```

```
$ ENV=staging uv run python src/config_lab/note05/a_one_value_many_gates.py
ENV=staging
  seed demo data           True
  show errors in responses True
  onboarding agent enabled True
  use the real payment API False

$ ENV=prod uv run python src/config_lab/note05/a_one_value_many_gates.py
ENV=prod
  seed demo data           False
  show errors in responses False
  onboarding agent enabled False
  use the real payment API True
```

**One string decided four behaviours**, and four is a small number for a real service: test data, error verbosity, which payment endpoint, which agents run, how much is logged, whether a scheduler starts. Nothing else in the configuration has that reach, which makes `env` the highest-leverage line in the file in both directions — one value sets a hundred behaviours correctly, or moves all hundred at once.

**Read the two columns again.** Every gate flipped at the same moment, because every gate is the same comparison written out again. So the only lever anybody has is `ENV` itself, and pulling it moves all four together. There is no way to change one of those answers without changing the others, or without editing code.

## What `env != "prod"` is really saying

The line reads: on everywhere except production. The assumption underneath is that production is the place this behaviour does not belong — a convenience of the lesser environments, like demo data, and production is the careful one that goes without.

For `seed demo data` that is exactly right, and the condition is honest.

But the same line comes out of a completely different situation: **production has not adopted the feature yet.** The onboarding agent runs in dev and staging, is being trialled, goes live next quarter. Today its behaviour is identical — on everywhere except prod — so the same condition gets written, and it is correct.

| What is actually true | What `env != "prod"` does today | What happens in six months |
|---|---|---|
| a development convenience | right | still right, forever |
| not adopted in production yet | right, by coincidence | wrong the day production adopts it |

**The condition records where the service is. It does not record why the gate exists**, and the why is the only thing that says whether the line is finished or temporary.

So when production does adopt the feature, the work is not the edit — it is finding the edits. A grep for `!= "prod"` returns every gate of both kinds, identical lines with opposite answers, and the information needed to decide is not in the code at all.

In a real service those gates are scattered across modules and assigned to names, rather than printed together as the lab file does. They look like this, and the comments are what nobody wrote:

```python
seed_demo_data     = env != "prod"     # must stay exactly as it is
verbose_errors     = env != "prod"     # must stay exactly as it is
onboarding_enabled = env != "prod"     # must go
```

> [!warning] A missed gate is a half-enabled feature, and it is invisible where you work
> Turn it on in the two places you found and miss the third, and production runs the feature inconsistently — some requests take the new path, some do not.
>
> In development every one of those gates is on, so all three code paths behave identically and there is nothing to notice locally. The inconsistency exists only in the environment you cannot poke at. And because the gates are code, both the change and the correction are a commit, a review, a build and a deploy.

## A flag named for the capability

The fix is to stop deriving the answer from something correlated with it and state it instead: a field named for the behaviour it controls.

`src/config_lab/note05/b_a_flag_per_capability.py`:

```python
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: Literal["local", "dev", "staging", "prod"] = "local"
    onboarding_enabled: bool = False


settings = Settings()

print(f"ENV={settings.env}  ONBOARDING_ENABLED={settings.onboarding_enabled}")
print("  seed demo data          ", settings.env != "prod")
print("  show errors in responses", settings.env != "prod")
print("  onboarding agent enabled", settings.onboarding_enabled)
```

```
$ ENV=prod uv run python src/config_lab/note05/b_a_flag_per_capability.py
ENV=prod  ONBOARDING_ENABLED=False
  seed demo data           False
  show errors in responses False
  onboarding agent enabled False

$ ENV=prod ONBOARDING_ENABLED=true uv run python src/config_lab/note05/b_a_flag_per_capability.py
ENV=prod  ONBOARDING_ENABLED=True
  seed demo data           False
  show errors in responses False
  onboarding agent enabled True
```

**Production adopted the feature by setting one variable.** No code change, no commit, no build, no deploy — and demo data stayed off, because it was never welded to the same lever.

Notice what did not change. The other two gates are still derived from `env`, and correctly so: for them the environment genuinely is the reason. The rule is not that `env` comparisons are wrong, it is that they should appear where the place really is the answer.

| | `if env != "prod"` | `if settings.onboarding_enabled` |
|---|---|---|
| What the line says | where the service is | what the service may do |
| Rolling out to production | edit code, review, build, deploy | set one variable |
| Rolling back | the same, again | set it back |
| Finding every place it applies | grep a condition shared with unrelated gates | grep the capability's own name |
| A reader six months later | cannot tell a permanent rule from rollout state | reads the name |

**And one case a derived condition cannot express at all.** Some capabilities have no settings of their own — no endpoint, no table, no credential — so there is no key whose presence could imply them. A feature that is pure behaviour has nothing to derive from, and a flag is the only way to say it is on.

> [!important] The test for any gate
> Ask what actually decides this behaviour. If the honest answer is the place — demo data, verbose errors, a sandbox payment endpoint — then compare `env`, and prefer naming the environments where it is allowed rather than the one where it is not, as [[03-Refuse-To-Start]] argues.
>
> If the honest answer is anything else — it is being rolled out, it depends on a customer, it is off while a bug is investigated — then the environment is a stand-in for the real reason, and it will be wrong on the day those two stop agreeing.

## Two switches that sound alike are not the same switch

The previous section moved one capability off `env`. This one is about the gates that stay, because several of them can read the same field and still mean different things.

Both are written as properties: read like an attribute — `settings.uses_stub_user`, no parentheses — and computed from `env` every time they are read.

`src/config_lab/note05/c_two_switches_that_sound_alike.py`:

```python
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: Literal["local", "dev", "staging", "prod"] = "local"

    @property
    def uses_stub_user(self) -> bool:
        """A canned user instead of a real handshake. Staging is inside this set."""
        return self.env in {"local", "dev", "staging"}

    @property
    def may_skip_session_auth(self) -> bool:
        """No authentication check at all. Staging is deliberately outside this set."""
        return self.env in {"local", "dev"}


settings = Settings()

print(
    f"ENV={settings.env:<8}"
    f" uses_stub_user={settings.uses_stub_user!s:<6}"
    f" may_skip_session_auth={settings.may_skip_session_auth}"
)
```

```
$ ENV=local uv run python src/config_lab/note05/c_two_switches_that_sound_alike.py
ENV=local    uses_stub_user=True   may_skip_session_auth=True

$ ENV=dev uv run python src/config_lab/note05/c_two_switches_that_sound_alike.py
ENV=dev      uses_stub_user=True   may_skip_session_auth=True

$ ENV=staging uv run python src/config_lab/note05/c_two_switches_that_sound_alike.py
ENV=staging  uses_stub_user=True   may_skip_session_auth=False

$ ENV=prod uv run python src/config_lab/note05/c_two_switches_that_sound_alike.py
ENV=prod     uses_stub_user=False  may_skip_session_auth=False
```

**Staging is the one row where they part.** Local and dev agree, staging splits, and production agrees again — so three of the four rows say the two switches are the same switch. Anybody reasoning from local, dev or production reaches that conclusion and is right three times out of four.

They are not the same question:

| | `uses_stub_user` | `may_skip_session_auth` |
|---|---|---|
| What it decides | which user a session is for | whether anything is checked at all |
| Environments | `local`, `dev`, `staging` | `local`, `dev` |
| Why staging differs | there is no identity provider to call | staging is reachable, so a request with no authentication must still be refused |
| Cost of getting it wrong | a canned user in a real environment | an unauthenticated environment, reachable from outside |

One is about where the user comes from. The other is about whether anyone is checked. Both read `env`, both sound like the authentication shortcut, and they differ on the single environment that is both real and exposed.

> [!danger] Merging them is a one-line change that opens a hole
> A tidy-minded reader sees two properties over `env` doing nearly the same thing and folds them into one, called something like `is_development`. Staging silently gains the right to skip authentication, every test still passes, and nothing anywhere recorded that the two sets were deliberately different.
>
> This is the one place in this folder where a comment is load-bearing rather than decoration. **The sets have to be written down next to the code**, because the names cannot carry them and no test will miss them.
>
> The file above already does it: each property carries a one-line docstring naming its set and saying where staging falls. That sentence is the only thing standing between a tidy refactor and an unauthenticated environment.

And the same holds for gates that are not about authentication at all. A single environment usually sits at a different point on every axis — real enough to need authentication, not real enough to need durable storage, not yet chosen for a feature being rolled out — so its answers form a row, not a single verdict:

| A staging deployment | Where it lands |
|---|---|
| authentication | required, like production |
| stored checkpoints | in memory, like development |
| a feature being rolled out | on, while production is still off |

**No single word describes that row**, which is the whole argument of this note arriving from the other direction. `if env != "prod"` tries to answer three unrelated questions with one comparison, and a deployment that is production-like in one respect and development-like in another will be wrong on at least one of them.
