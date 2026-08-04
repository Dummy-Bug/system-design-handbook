import uvicorn
from fastapi import FastAPI, Query, HTTPException

from data import MENU_ITEMS

from models import MenuItem, MenuResponse

app = FastAPI()


@app.get("/menu", response_model=MenuResponse)
def get_menu(category: str | None = Query(default=None, description="Filter by chai, snacks, or combos")):
    if category:
        filtered = [item for item in MENU_ITEMS if item["category"].lower() == category.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No item found in category: {category}")
        return MenuResponse(count=len(filtered), items=filtered)

    return MenuResponse(count=len(MENU_ITEMS), items=MENU_ITEMS)


@app.get("/menu/{item_id}", response_model=MenuItem)
def get_item(item_id: int):
    for item in MENU_ITEMS:
        if item["id"] == item_id:
            return item

    raise HTTPException(status_code=404, detail=f"Menu item with ID {item_id} not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
