from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Swiggy orders service",
        "status": "healthy"
    }


## from root run the following -- uvicorn main:app --reload