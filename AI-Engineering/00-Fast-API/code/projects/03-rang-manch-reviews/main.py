from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables
from routes.reviews import router as reviews_router


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

app.include_router(reviews_router)


@app.get("/")
def root():
    return {"message": "Welcome to Rangmanch Review API"}
