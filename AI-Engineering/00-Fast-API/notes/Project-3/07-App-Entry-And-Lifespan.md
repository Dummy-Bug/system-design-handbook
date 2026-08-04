The lifespan pattern wired into this project's actual entry point — `main.py`, for the first time genuinely running this app end to end.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    print("Database tables created")
    yield
    print("Shutting down the app")


app = FastAPI(
    title="Rangmanch Reviews API",
    description="Theater reviews API for Pune's Rang Manch",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "Welcome to Rangmanch Review API"}
```

Running this with `uvicorn main:app --reload` produces the `rangmanch.db` SQLite file — visible directly in the project directory once the app has started, created by `create_db_and_tables()` firing inside `lifespan` before the app is considered ready to serve requests. No route has to be hit first; the table exists the moment the server finishes booting.

Still just one route — `/` — same shape as the very first route in every earlier project. What's different about this file isn't the route count, it's that the app now genuinely owns a persistent database, set up automatically as part of starting up, rather than in-memory data or a hand-run setup step.

The actual review routes — `POST`/`GET`/`PATCH`/`DELETE` on `/reviews` — come next, and per the plan for this project, they won't live directly in this file: the next step is splitting routes into their own module rather than continuing to grow `main.py` indefinitely.
