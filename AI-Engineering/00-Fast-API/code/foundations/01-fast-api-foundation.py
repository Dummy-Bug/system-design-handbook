from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(
    title="Swiggy Order Service",
    description="""
    This is internal API for managing orders.
    It will handle creation and tracking of delivery systems.
    """,
    version="1.2.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

@app.get("/")
def read_root():
    """
    Root endpoint - does a simple health check.
    """
    return {
        "message": "Welcome to Swiggy order service",
        "status": "healthy",
    }


@app.get("/about")
def about():
    """
    Returns API metadata.
    """
    return {
        "service": "order-service",
        "team": "backend platform",
        "region": "ap-south-1",
        "version": "1.2.2",
    }


@app.get("/orders")
def list_orders():
    """
    List recent orders.
    """
    return {
        "orders": [
            {"id": 1, "item": "Butter Chicken", "status": "delivered"},
            {"id": 2, "item": "Masala Dosa", "status": "preparing"},
            {"id": 3, "item": "Paneer Tikka", "status": "delivered"},
        ]
    }


@app.get("/order/status")
def get_order_status():
    """
    Admin stats - not tied to a specific order.
    """
    return {
        "orders_today": 340_233,
        "top_city": "Bengaluru",
    }


@app.get("/debug/request-info")
async def request_info(request: Request):
    """
    Inspect the raw request object.
    """
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "path_params": request.path_params,
        "query_params": dict(request.query_params),
    }


@app.get(
    "/orders/active",
    summary="Get active orders",
    description="""
    Returns all orders that are currently in the system being prepared,
    or are out for delivery.
    """,
    tags=["orders"],
    response_description="A list of active order objects",
    deprecated=False,
)
def get_active_order():
    """
    Returns all orders that are currently in the system being prepared.
    """
    return {
        "active_orders": [
            {"id": 1, "item": "Masala Dosa", "status": "out for delivery"},
        ]
    }


@app.get("/restaurants", tags=["restaurants"])
def list_restro():
    """
    List restaurants.
    """
    return {"restaurants": "test"}


if __name__ == "__main__":
    uvicorn.run("01-fast-api-foundation:app", host="127.0.0.1", port=8000, reload=True)