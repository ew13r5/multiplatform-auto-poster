from fastapi import APIRouter, File, Query, UploadFile

from app.services.storage import upload_image, InvalidFileError

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload")
async def upload_image_endpoint(
    file: UploadFile = File(...),
    page_id: str = Query(..., description="Page ID for key namespacing"),
):
    """Upload an image to MinIO storage."""
    content = await file.read()
    try:
        result = await upload_image(
            file_content=content,
            filename=file.filename or "image.bin",
            content_type=file.content_type or "",
            page_id=page_id,
        )
    except InvalidFileError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    return result
