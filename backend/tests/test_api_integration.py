import pytest
import io
import docx
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest.mark.asyncio
async def test_full_api_lifecycle():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 2. Create Session
        res = await client.post("/api/v1/sessions/", json={"title": "Computer Vision 101"})
        assert res.status_code == 200
        session_data = res.json()
        session_id = session_data["id"]
        assert session_id is not None
        assert session_data["title"] == "Computer Vision 101"

        # 3. List Sessions
        res = await client.get("/api/v1/sessions/")
        assert res.status_code == 200
        sessions = res.json()
        assert any(s["id"] == session_id for s in sessions)

        # 4. Get Session Detail
        res = await client.get(f"/api/v1/sessions/{session_id}")
        assert res.status_code == 200
        detail = res.json()
        assert detail["id"] == session_id
        assert len(detail["documents"]) == 0
        assert len(detail["messages"]) == 0
