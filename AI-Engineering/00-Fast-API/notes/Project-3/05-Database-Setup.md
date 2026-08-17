The engine-and-session pattern applied to this project — a `database.py` holding everything the rest of the app needs to actually talk to SQLite.

```python
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///rangmanch.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

`sqlite:///rangmanch.db` — the `sqlite://` protocol prefix, three slashes, then a filename. SQLite needs no separate server process or credentials to configure; this single line is enough to have a working database, and running the app will create `rangmanch.db` as an actual file in the project directory the first time the tables get created.

`DATABASE_URL` is hardcoded directly in the file for now — fine for a local SQLite file during development, but worth flagging as a placeholder: a real deployment would keep this in an environment variable instead, so the actual connection string (especially for something like a hosted Postgres URL, which typically embeds credentials) never sits in version control. That move hasn't happened yet in this project; the code above is where it currently lives.

Nothing else about this file is project-specific — `create_db_and_tables` and `get_session` are exactly the general pattern from the Foundations note, applied with this project's engine.
