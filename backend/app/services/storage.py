import uuid
from datetime import timedelta
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from minio import Minio

from app.config import get_settings

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


class InvalidFileError(Exception):
    """Raised when an uploaded file fails validation."""
    pass


@lru_cache()
def get_minio_client() -> Minio:
    """Create and return a cached MinIO client for uploads."""
    settings = get_settings()
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_SSL,
    )
    ensure_bucket(client, settings.MINIO_BUCKET)
    return client


@lru_cache()
def get_external_minio_client() -> Minio:
    """MinIO client with external endpoint for presigned URLs reachable from browser."""
    settings = get_settings()
    return Minio(
        settings.MINIO_EXTERNAL_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_SSL,
    )


def create_minio_client() -> Minio:
    """Non-cached MinIO client for Celery workers (process safety)."""
    settings = get_settings()
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_SSL,
    )


def ensure_bucket(client: Minio, bucket_name: str) -> None:
    """Create the bucket if it does not exist."""
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


async def upload_image(file_content: bytes, filename: str, content_type: str, page_id: str) -> dict:
    """Validate and upload image to MinIO.

    Returns dict with 'image_key' and 'url' (presigned, browser-reachable).
    Raises InvalidFileError for invalid MIME type or oversized files.
    """
    if not content_type or not content_type.startswith("image/"):
        raise InvalidFileError(f"Invalid MIME type: {content_type}. Must be image/*")

    if len(file_content) > MAX_IMAGE_SIZE:
        raise InvalidFileError(
            f"File too large: {len(file_content)} bytes. Maximum: {MAX_IMAGE_SIZE} bytes (10 MB)"
        )

    ext = Path(filename).suffix.lstrip(".") if filename else "bin"
    image_key = f"{page_id}/{uuid.uuid4()}.{ext}"

    settings = get_settings()
    client = get_minio_client()
    buffer = BytesIO(file_content)

    client.put_object(
        settings.MINIO_BUCKET,
        image_key,
        buffer,
        length=len(file_content),
        content_type=content_type,
    )

    url = get_presigned_url(image_key)
    return {"image_key": image_key, "url": url}


def get_presigned_url(image_key: str) -> str:
    """Generate a presigned GET URL valid for 1 hour using external endpoint."""
    settings = get_settings()
    ext_client = get_external_minio_client()
    return ext_client.presigned_get_object(
        settings.MINIO_BUCKET,
        image_key,
        expires=timedelta(hours=1),
    )
