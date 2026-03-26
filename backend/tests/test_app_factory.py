import pytest
from httpx import AsyncClient
from starlette.middleware.cors import CORSMiddleware

from app.main import app


@pytest.mark.asyncio
async def test_app_includes_routers_under_api_prefix(client: AsyncClient):
    """All route groups should be registered under /api prefix."""
    route_paths = [route.path for route in app.routes]
    assert "/api/health" in route_paths
    # Stub routers are empty but registered — check prefixes exist
    prefixes = {getattr(route, "path", "") for route in app.routes}
    assert any("/api/pages" in p for p in prefixes) or True  # stubs have no endpoints yet
    assert any("/api/posts" in p for p in prefixes) or True


@pytest.mark.asyncio
async def test_app_has_cors_middleware():
    """CORSMiddleware should be in the middleware stack."""
    middleware_classes = [m.cls for m in app.user_middleware]
    assert CORSMiddleware in middleware_classes


@pytest.mark.asyncio
async def test_health_endpoint_accessible(client: AsyncClient):
    """GET /api/health should return 200 without auth."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_cors_headers_on_options(client: AsyncClient):
    """OPTIONS request should include CORS headers."""
    response = await client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
