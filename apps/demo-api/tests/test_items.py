from httpx import AsyncClient
from app.main import app, ITEMS


async def test_create_and_list_items():
    ITEMS.clear()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/items", json={"id": 1, "name": "Test", "price": 10.5})
        assert resp.status_code == 201

        resp = await ac.get("/items")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Test"
