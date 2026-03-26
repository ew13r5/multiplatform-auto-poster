from fastapi import APIRouter

router = APIRouter(prefix="/pages", tags=["pages"])


@router.get("")
async def list_pages():
    """List connected pages — stub, full implementation in section-05."""
    return {"pages": []}
