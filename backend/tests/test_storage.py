import pytest
from unittest.mock import MagicMock, patch
from app.services.storage import upload_image, InvalidFileError, MAX_IMAGE_SIZE


@pytest.mark.asyncio
async def test_upload_rejects_non_image_mime():
    with pytest.raises(InvalidFileError, match="Invalid MIME type"):
        await upload_image(b"data", "file.txt", "text/plain", "page1")


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file():
    big_data = b"x" * (MAX_IMAGE_SIZE + 1)
    with pytest.raises(InvalidFileError, match="File too large"):
        await upload_image(big_data, "big.jpg", "image/jpeg", "page1")


@pytest.mark.asyncio
async def test_upload_returns_key_format():
    mock_client = MagicMock()
    mock_client.bucket_exists.return_value = True
    mock_ext_client = MagicMock()
    mock_ext_client.presigned_get_object.return_value = "http://localhost:9000/signed-url"

    with patch("app.services.storage.get_minio_client", return_value=mock_client), \
         patch("app.services.storage.get_external_minio_client", return_value=mock_ext_client), \
         patch("app.services.storage.get_settings") as mock_settings:
        mock_settings.return_value.MINIO_BUCKET = "post-images"
        result = await upload_image(b"imgdata", "photo.jpg", "image/jpeg", "page123")

    assert result["image_key"].startswith("page123/")
    assert result["image_key"].endswith(".jpg")
    assert result["url"] == "http://localhost:9000/signed-url"
    mock_client.put_object.assert_called_once()


def test_get_minio_client_returns_instance():
    with patch("app.services.storage.get_settings") as mock_settings:
        mock_settings.return_value.MINIO_ENDPOINT = "localhost:9000"
        mock_settings.return_value.MINIO_ACCESS_KEY = "admin"
        mock_settings.return_value.MINIO_SECRET_KEY = "admin"
        mock_settings.return_value.MINIO_USE_SSL = False
        mock_settings.return_value.MINIO_BUCKET = "test"
        with patch("app.services.storage.Minio") as MockMinio:
            mock_instance = MagicMock()
            mock_instance.bucket_exists.return_value = True
            MockMinio.return_value = mock_instance
            from app.services.storage import get_minio_client
            get_minio_client.cache_clear()
            client = get_minio_client()
            assert client is not None
            get_minio_client.cache_clear()
