from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check — placeholder for full implementation in section-06."""
    return {"status": "healthy", "checks": {}, "mode": "development"}
